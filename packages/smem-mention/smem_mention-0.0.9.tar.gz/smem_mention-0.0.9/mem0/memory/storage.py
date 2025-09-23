import logging
import sqlite3
import threading
import uuid
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from psycopg2 import sql
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

logger = logging.getLogger(__name__)


class SQLiteManager:
    def __init__(self, db_path: str = ":memory:"):
        self.db_path = db_path
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self._lock = threading.Lock()
        self._migrate_history_table()
        self._create_history_table()

    def _migrate_history_table(self) -> None:
        """
        If a pre-existing history table had the old group-chat columns,
        rename it, create the new schema, copy the intersecting data, then
        drop the old table.
        """
        with self._lock:
            try:
                # Start a transaction
                self.connection.execute("BEGIN")
                cur = self.connection.cursor()

                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='history'")
                if cur.fetchone() is None:
                    self.connection.execute("COMMIT")
                    return  # nothing to migrate

                cur.execute("PRAGMA table_info(history)")
                old_cols = {row[1] for row in cur.fetchall()}

                expected_cols = {
                    "id",
                    "memory_id",
                    "old_memory",
                    "new_memory",
                    "event",
                    "created_at",
                    "updated_at",
                    "is_deleted",
                    "actor_id",
                    "role",
                }

                if old_cols == expected_cols:
                    self.connection.execute("COMMIT")
                    return

                logger.info("Migrating history table to new schema (no convo columns).")

                # Clean up any existing history_old table from previous failed migration
                cur.execute("DROP TABLE IF EXISTS history_old")

                # Rename the current history table
                cur.execute("ALTER TABLE history RENAME TO history_old")

                # Create the new history table with updated schema
                cur.execute(
                    """
                    CREATE TABLE history (
                        id           TEXT PRIMARY KEY,
                        memory_id    TEXT,
                        old_memory   TEXT,
                        new_memory   TEXT,
                        event        TEXT,
                        created_at   DATETIME,
                        updated_at   DATETIME,
                        is_deleted   INTEGER,
                        actor_id     TEXT,
                        role         TEXT
                    )
                """
                )

                # Copy data from old table to new table
                intersecting = list(expected_cols & old_cols)
                if intersecting:
                    cols_csv = ", ".join(intersecting)
                    cur.execute(f"INSERT INTO history ({cols_csv}) SELECT {cols_csv} FROM history_old")

                # Drop the old table
                cur.execute("DROP TABLE history_old")

                # Commit the transaction
                self.connection.execute("COMMIT")
                logger.info("History table migration completed successfully.")

            except Exception as e:
                # Rollback the transaction on any error
                self.connection.execute("ROLLBACK")
                logger.error(f"History table migration failed: {e}")
                raise

    def _create_history_table(self) -> None:
        with self._lock:
            try:
                self.connection.execute("BEGIN")
                self.connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS history (
                        id           TEXT PRIMARY KEY,
                        memory_id    TEXT,
                        old_memory   TEXT,
                        new_memory   TEXT,
                        event        TEXT,
                        created_at   DATETIME,
                        updated_at   DATETIME,
                        is_deleted   INTEGER,
                        actor_id     TEXT,
                        role         TEXT
                    )
                """
                )
                self.connection.execute("COMMIT")
            except Exception as e:
                self.connection.execute("ROLLBACK")
                logger.error(f"Failed to create history table: {e}")
                raise

    def add_history(
        self,
        memory_id: str,
        old_memory: Optional[str],
        new_memory: Optional[str],
        event: str,
        *,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        is_deleted: int = 0,
        actor_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> None:
        with self._lock:
            try:
                self.connection.execute("BEGIN")
                self.connection.execute(
                    """
                    INSERT INTO history (
                        id, memory_id, old_memory, new_memory, event,
                        created_at, updated_at, is_deleted, actor_id, role
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        str(uuid.uuid4()),
                        memory_id,
                        old_memory,
                        new_memory,
                        event,
                        created_at,
                        updated_at,
                        is_deleted,
                        actor_id,
                        role,
                    ),
                )
                self.connection.execute("COMMIT")
            except Exception as e:
                self.connection.execute("ROLLBACK")
                logger.error(f"Failed to add history record: {e}")
                raise

    def get_history(self, memory_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            cur = self.connection.execute(
                """
                SELECT id, memory_id, old_memory, new_memory, event,
                       created_at, updated_at, is_deleted, actor_id, role
                FROM history
                WHERE memory_id = ?
                ORDER BY created_at ASC, DATETIME(updated_at) ASC
            """,
                (memory_id,),
            )
            rows = cur.fetchall()

        return [
            {
                "id": r[0],
                "memory_id": r[1],
                "old_memory": r[2],
                "new_memory": r[3],
                "event": r[4],
                "created_at": r[5],
                "updated_at": r[6],
                "is_deleted": bool(r[7]),
                "actor_id": r[8],
                "role": r[9],
            }
            for r in rows
        ]

    def reset(self) -> None:
        """Drop and recreate the history table."""
        with self._lock:
            try:
                self.connection.execute("BEGIN")
                self.connection.execute("DROP TABLE IF EXISTS history")
                self.connection.execute("COMMIT")
                self._create_history_table()
            except Exception as e:
                self.connection.execute("ROLLBACK")
                logger.error(f"Failed to reset history table: {e}")
                raise

    def close(self) -> None:
        if self.connection:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()


class PostgreSQLManager:
    def __init__(self, connection_uri: str):
        if not PSYCOPG2_AVAILABLE:
            raise ImportError("psycopg2 is required for PostgreSQL support. Install it with: pip install psycopg2-binary")
        
        self.connection_uri = connection_uri
        self.connection = None
        self._lock = threading.Lock()
        self._parsed_uri = self._parse_connection_uri(connection_uri)
        self._ensure_database_exists()
        self._connect()
        self._migrate_history_table()
        self._create_history_table()

    def _parse_connection_uri(self, connection_uri: str) -> Dict[str, str]:
        """Parse PostgreSQL connection URI and extract components."""
        try:
            parsed = urlparse(connection_uri)
            return {
                'host': parsed.hostname or 'localhost',
                'port': str(parsed.port or 5432),
                'user': parsed.username,
                'password': parsed.password,
                'database': parsed.path.lstrip('/') if parsed.path else None,
                'scheme': parsed.scheme
            }
        except Exception as e:
            logger.error(f"Failed to parse connection URI: {e}")
            raise

    def _ensure_database_exists(self) -> None:
        """Check if the target database exists and create it if it doesn't."""
        target_db = self._parsed_uri['database']
        if not target_db:
            logger.warning("No database specified in connection URI, skipping database creation check")
            return

        # Create connection parameters for the 'postgres' database (guaranteed to exist)
        admin_params = {
            'host': self._parsed_uri['host'],
            'port': self._parsed_uri['port'],
            'user': self._parsed_uri['user'],
            'password': self._parsed_uri['password']
        }

        # Remove None values from params
        admin_params = {k: v for k, v in admin_params.items() if v is not None}

        try:
            # Connect to postgres database to check if target database exists
            admin_conn = psycopg2.connect(**admin_params)
            admin_conn.autocommit = True  # Required for CREATE DATABASE
            
            with admin_conn.cursor() as cur:
                # Check if the target database exists
                cur.execute(
                    "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
                    (target_db,)
                )
                exists = cur.fetchone()

                if not exists:
                    # Create the database if it doesn't exist
                    logger.info(f"Creating database '{target_db}'...")
                    cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(target_db)))
                    logger.info(f"Database '{target_db}' created successfully.")
                else:
                    logger.debug(f"Database '{target_db}' already exists.")

            admin_conn.close()

        except Exception as e:
            logger.error(f"Failed to ensure database exists: {e}")
            raise

    def _connect(self) -> None:
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(self.connection_uri)
            self.connection.autocommit = False
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise

    def _ensure_connection(self) -> None:
        """Ensure the connection is alive, reconnect if necessary."""
        if self.connection is None or self.connection.closed:
            self._connect()

    def _migrate_history_table(self) -> None:
        """
        If a pre-existing history table had the old group-chat columns,
        rename it, create the new schema, copy the intersecting data, then
        drop the old table.
        """
        with self._lock:
            try:
                self._ensure_connection()
                with self.connection:
                    with self.connection.cursor() as cur:
                        # Check if history table exists
                        cur.execute("""
                            SELECT EXISTS (
                                SELECT FROM information_schema.tables 
                                WHERE table_name = 'history'
                            )
                        """)
                        
                        if not cur.fetchone()[0]:
                            return  # nothing to migrate

                        # Get existing columns
                        cur.execute("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'history'
                        """)
                        old_cols = {row[0] for row in cur.fetchall()}

                        expected_cols = {
                            "id",
                            "memory_id",
                            "old_memory",
                            "new_memory",
                            "event",
                            "created_at",
                            "updated_at",
                            "is_deleted",
                            "actor_id",
                            "role",
                        }

                        if old_cols == expected_cols:
                            return

                        logger.info("Migrating history table to new schema (no convo columns).")

                        # Clean up any existing history_old table from previous failed migration
                        cur.execute("DROP TABLE IF EXISTS history_old")

                        # Rename the current history table
                        cur.execute("ALTER TABLE history RENAME TO history_old")

                        # Create the new history table with updated schema
                        cur.execute("""
                            CREATE TABLE history (
                                id           TEXT PRIMARY KEY,
                                memory_id    TEXT,
                                old_memory   TEXT,
                                new_memory   TEXT,
                                event        TEXT,
                                created_at   TIMESTAMP,
                                updated_at   TIMESTAMP,
                                is_deleted   BOOLEAN DEFAULT FALSE,
                                actor_id     TEXT,
                                role         TEXT
                            )
                        """)

                        # Copy data from old table to new table
                        intersecting = list(expected_cols & old_cols)
                        if intersecting:
                            cols_csv = ", ".join(intersecting)
                            cur.execute(f"INSERT INTO history ({cols_csv}) SELECT {cols_csv} FROM history_old")

                        # Drop the old table
                        cur.execute("DROP TABLE history_old")

                        logger.info("History table migration completed successfully.")

            except Exception as e:
                logger.error(f"History table migration failed: {e}")
                if self.connection:
                    self.connection.rollback()
                raise

    def _create_history_table(self) -> None:
        with self._lock:
            try:
                self._ensure_connection()
                with self.connection:
                    with self.connection.cursor() as cur:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS history (
                                id           TEXT PRIMARY KEY,
                                memory_id    TEXT,
                                old_memory   TEXT,
                                new_memory   TEXT,
                                event        TEXT,
                                created_at   TIMESTAMP,
                                updated_at   TIMESTAMP,
                                is_deleted   BOOLEAN DEFAULT FALSE,
                                actor_id     TEXT,
                                role         TEXT
                            )
                        """)
            except Exception as e:
                if self.connection:
                    self.connection.rollback()
                logger.error(f"Failed to create history table: {e}")
                raise

    def add_history(
        self,
        memory_id: str,
        old_memory: Optional[str],
        new_memory: Optional[str],
        event: str,
        *,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None,
        is_deleted: int = 0,  # Keep int type for compatibility but convert to bool
        actor_id: Optional[str] = None,
        role: Optional[str] = None,
    ) -> None:
        with self._lock:
            try:
                self._ensure_connection()
                with self.connection:
                    with self.connection.cursor() as cur:
                        # Convert integer is_deleted to boolean for PostgreSQL
                        is_deleted_bool = bool(is_deleted)
                        
                        cur.execute("""
                            INSERT INTO history (
                                id, memory_id, old_memory, new_memory, event,
                                created_at, updated_at, is_deleted, actor_id, role
                            )
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """, (
                            str(uuid.uuid4()),
                            memory_id,
                            old_memory,
                            new_memory,
                            event,
                            created_at,
                            updated_at,
                            is_deleted_bool,  # Use converted boolean value
                            actor_id,
                            role,
                        ))
            except Exception as e:
                if self.connection:
                    self.connection.rollback()
                logger.error(f"Failed to add history record: {e}")
                raise

    def get_history(self, memory_id: str) -> List[Dict[str, Any]]:
        with self._lock:
            try:
                self._ensure_connection()
                with self.connection.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT id, memory_id, old_memory, new_memory, event,
                               created_at, updated_at, is_deleted, actor_id, role
                        FROM history
                        WHERE memory_id = %s
                        ORDER BY created_at ASC, updated_at ASC
                    """, (memory_id,))
                    rows = cur.fetchall()

                return [
                    {
                        "id": row["id"],
                        "memory_id": row["memory_id"],
                        "old_memory": row["old_memory"],
                        "new_memory": row["new_memory"],
                        "event": row["event"],
                        "created_at": row["created_at"],
                        "updated_at": row["updated_at"],
                        "is_deleted": row["is_deleted"],
                        "actor_id": row["actor_id"],
                        "role": row["role"],
                    }
                    for row in rows
                ]
            except Exception as e:
                logger.error(f"Failed to get history: {e}")
                raise

    def reset(self) -> None:
        """Drop and recreate the history table."""
        with self._lock:
            try:
                self._ensure_connection()
                with self.connection:
                    with self.connection.cursor() as cur:
                        cur.execute("DROP TABLE IF EXISTS history")
                        cur.execute("""
                                    CREATE TABLE IF NOT EXISTS history (
                                        id           TEXT PRIMARY KEY,
                                        memory_id    TEXT,
                                        old_memory   TEXT,
                                        new_memory   TEXT,
                                        event        TEXT,
                                        created_at   TIMESTAMP,
                                        updated_at   TIMESTAMP,
                                        is_deleted   BOOLEAN DEFAULT FALSE,
                                        actor_id     TEXT,
                                        role         TEXT
                                    )
                                """)
            except Exception as e:
                if self.connection:
                    self.connection.rollback()
                logger.error(f"Failed to reset history table: {e}")
                raise

    def close(self) -> None:
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None

    def __del__(self):
        self.close()
