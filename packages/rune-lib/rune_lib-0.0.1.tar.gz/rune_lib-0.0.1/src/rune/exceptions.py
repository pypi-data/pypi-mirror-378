"""Custom exception types for the Rune library."""

from pathlib import Path


class ManifoldError(Exception):
    """Base exception for all Rune errors."""


class AssetNotFoundError(ManifoldError):
    """Raised when a requested asset cannot be found."""

    def __init__(self, asset_name: str, search_path: Path, suggestions: list[str] | None = None):
        self.asset_name = asset_name
        self.search_path = search_path
        self.suggestions = suggestions or []

        message = f"Asset '{asset_name}' not found in {search_path}"
        if self.suggestions:
            message += f". Did you mean: {', '.join(self.suggestions)}?"

        super().__init__(message)


class ProjectRootNotFoundError(ManifoldError):
    """Raised when the project root cannot be determined."""


class ConfigurationError(ManifoldError):
    """Raised when the configuration is invalid."""
