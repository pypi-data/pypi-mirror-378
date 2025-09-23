"""Functions to get system-related boolean values and environment information."""

from bear_dereth.system_bools import (
    get_current_dir,
    get_editor,
    get_home,
    get_python_version,
    get_shell,
    get_terminal,
    get_username,
    has_homebrew,
    has_nix,
    has_uv,
)

__all__ = [
    "get_current_dir",
    "get_editor",
    "get_home",
    "get_python_version",
    "get_shell",
    "get_terminal",
    "get_username",
    "has_homebrew",
    "has_nix",
    "has_uv",
]
