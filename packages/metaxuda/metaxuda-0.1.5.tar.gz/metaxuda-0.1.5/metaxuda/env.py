# env.py
import os
import sys
from pathlib import Path
import ctypes

# Path to bundled native libs
NATIVE_DIR = Path(__file__).resolve().parent / "native"
CUDA_DRIVER = (NATIVE_DIR / "libcuda.dylib").resolve()
CUDART = (NATIVE_DIR / "libcudart.dylib").resolve()
NVVM = (NATIVE_DIR / "libnvvm.dylib").resolve()

def relaunch_with_dyld():
    """
    Relaunch current script with DYLD_LIBRARY_PATH set so macOS SIP respects it.
    """
    dyld_path = str(NATIVE_DIR)
    env = os.environ.copy()
    env["DYLD_LIBRARY_PATH"] = f"{dyld_path}:{env.get('DYLD_LIBRARY_PATH', '')}"
    env["NUMBA_CUDA_DRIVER"] = str(CUDA_DRIVER)

    # Prevent infinite recursion
    if env.get("_METAXUDA_RELAUNCHED") == "1":
        return False

    env["_METAXUDA_RELAUNCHED"] = "1"

    # Relaunch same Python interpreter with same args
    os.execvpe(sys.executable, [sys.executable] + sys.argv, env)
    return True

def setup_environment():
    """
    Ensure CUDA shim is injected before Numba initializes.
    """
    if relaunch_with_dyld():
        sys.exit(0)  # we never reach here after execvpe

    # Preload shims into current process
    for lib in [CUDA_DRIVER, CUDART, NVVM]:
        try:
            ctypes.CDLL(str(lib), mode=ctypes.RTLD_GLOBAL)
        except OSError:
            pass