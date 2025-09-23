"""
Handles the dynamic, attribute-based access to asset paths.
"""

from __future__ import annotations

from pathlib import Path
from typing import Self


class DynamicAssetGroup(Path):
    """
    Represents a directory or file in the asset hierarchy, enabling dynamic
    attribute access while behaving exactly like a `pathlib.Path`.

    This class is the core of Rune's intuitive API, translating attribute
    access like `assets.images.player` into file system paths.
    """

    def __new__(cls, *args) -> Self:
        """
        Constructs the DynamicAssetGroup as a Path-like object.

        This method intercepts the arguments to prevent recursion when pathlib
        internal methods (like joinpath) attempt to create a new instance of
        this subclass.
        """
        # Convert any DynamicAssetGroup instances in args to strings to break recursion
        str_args = [str(arg) if isinstance(arg, DynamicAssetGroup) else arg for arg in args]
        return super().__new__(cls, *str_args)

    def __getattr__(self, name: str) -> Self:
        """
        Dynamically access a file or subdirectory within this asset group.

        Args:
            name: The name of the file or directory to access.

        Returns:
            A new `DynamicAssetGroup` instance representing the target path.
        """
        # Do not interfere with internal attributes of the Path class.
        if name.startswith("_"):
            raise AttributeError(
                f"'{type(self).__name__}' object has no attribute '{name}'"
            )
        # First, check for a directory with the exact name
        target_path = self / name
        if target_path.is_dir():
            return self.__class__(target_path)

        # If not a directory, search for a file with a matching name (extension-insensitive)
        # This is what allows for `assets.images.player` instead of `assets.images.player_png`
        if self.is_dir():
            for item in self.iterdir():
                if item.is_file() and item.stem.lower() == name.lower():
                    return self.__class__(item)

        # Fallback for cases where the user might include the extension
        if target_path.exists():
            return self.__class__(target_path)

        # todo: Add typo suggestions and proper error handling with AssetNotFoundError
        raise AttributeError(f"Asset '{name}' not found in '{self}'")

    def __repr__(self) -> str:
        return f"<DynamicAssetGroup path='{super().__repr__()}'>"