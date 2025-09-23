import importlib.metadata

__version__ = importlib.metadata.version("smem-mention")

from mem0.client.main import AsyncMemoryClient, MemoryClient  # noqa
from mem0.memory.main import AsyncMemory, Memory  # noqa
