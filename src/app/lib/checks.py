import os
import platform
import sys

PLATFORM_LINUX: bool = platform.system() == "Linux"
PLATFORM_MACOS: bool = platform.system() == "Darwin"
PLATFORM_WINDOWS: bool = platform.system() == "Windows"


def ansi_support() -> bool:
    """
    Check if the terminal supports ANSI escape codes
    """
    plat = platform.system()
    supported_platform = plat != "Windows" or "ANSICON" in os.environ
    is_a_tty = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported_platform and is_a_tty
