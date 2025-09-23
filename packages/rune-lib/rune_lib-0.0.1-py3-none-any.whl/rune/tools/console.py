"""
Provides a centralized, styled console output system using the rich library.

This module offers a pre-configured rich Console instance and several helper
functions for logging messages with different styles (e.g., info, warning, error).
This ensures a consistent and visually appealing terminal output across the project.
"""

from rich.console import Console
from rich.theme import Theme

# Pre-configured theme for consistent styling
manifold_theme = Theme({
    "info": "cyan",
    "warning": "yellow",
    "error": "bold red",
    "success": "green",
    "debug": "dim",
    "path": "italic blue",
})

# Global console instance to be used throughout the project
console = Console(theme=manifold_theme)


def log_info(message: str):
    """Logs an informational message."""
    console.print(f"[info]INFO:[/] {message}")


def log_warning(message: str):
    """Logs a warning message."""
    console.print(f"[warning]WARNING:[/] {message}")


def log_error(message: str, e: Exception | None = None):
    """Logs an error message and optionally prints the exception."""
    console.print(f"[error]ERROR:[/] {message}")
    if e:
        console.print_exception(show_locals=False)


def log_success(message: str):
    """Logs a success message."""
    console.print(f"[success]SUCCESS:[/] {message}")


def log_debug(message: str):
    """Logs a debug message, intended for verbose output."""
    console.print(f"[debug]DEBUG:[/] {message}")

