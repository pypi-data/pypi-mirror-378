"""
Handles the logic for discovering the project root and asset directories.

This module implements the "zero-configuration" philosophy by searching for
common project markers and asset folder names.
"""
from pathlib import Path


class DiscoveryManager:
    """
    Manages the discovery of the project's root directory and asset folders.
    """

    def find_project_root(self, start_path: Path | None = None) -> Path:
        """
        Searches upward from a starting path to find the project root.

        For the MVP, this is a simplified implementation that assumes the
        current working directory is the project root. A more robust search
        for markers like `.git` or `pyproject.toml` will be added later.

        Args:
            start_path: The path to start searching from. Defaults to the
                        current working directory.

        Returns:
            The discovered project root path.
        """
        return Path.cwd()
