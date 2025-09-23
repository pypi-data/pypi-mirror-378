"""
This module makes the console logging functions available for easy import.

Instead of importing from `rune.tools.console`, you can now import directly
from `rune.tools`.

Example:
    from rune.tools import log_info
"""

from .console import (
    console,
    log_info,
    log_warning,
    log_error,
    log_success,
    log_debug,
)

__all__ = [
    "console",
    "log_info",
    "log_warning",
    "log_error",
    "log_success",
    "log_debug",
]
