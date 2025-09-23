from .env import setup_environment
setup_environment()

from .patch import patch_libdevice, get_libcudart_path
from .buffer import GPUMemoryBuffer
from .stream import GPUStream, DEFAULT_STREAM
from .pipeline import run_pipeline

__version__ = "0.1.5"

patch_libdevice()

__all__ = [
    "GPUMemoryBuffer",
    "GPUStream",
    "DEFAULT_STREAM",
    "run_pipeline",
    "get_libcudart_path",
]