"""A module for detecting the current operating system."""

from bear_dereth.platform_utils import (
    OS,
    OSInfo,
    get_os_info,
    get_platform,
    is_linux,
    is_macos,
    is_windows,
    linux_helper,
)

DARWIN = OS.DARWIN
LINUX = OS.LINUX
WINDOWS = OS.WINDOWS
BSD = OS.BSD
OTHER = OS.OTHER


__all__ = [
    "DARWIN",
    "LINUX",
    "OS",
    "OTHER",
    "WINDOWS",
    "OSInfo",
    "get_os_info",
    "get_platform",
    "is_linux",
    "is_macos",
    "is_windows",
    "linux_helper",
]
