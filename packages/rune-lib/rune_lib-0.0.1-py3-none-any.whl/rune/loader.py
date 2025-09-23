"""
Central orchestrator for the Rune asset management system.

This module is responsible for the singleton pattern, lazy initialization,
and caching of asset paths.
"""
from __future__ import annotations

import threading
from pathlib import Path

from .discovery import DiscoveryManager
from .group import DynamicAssetGroup


class ManifoldLoader:
    """
    A thread-safe singleton that provides the main entry point (`assets`)
    to the asset management system.

    It discovers asset directories upon first access and provides a dynamic
    API to traverse them.
    """

    _instance: ManifoldLoader | None = None
    _lock = threading.Lock()

    def __new__(cls) -> ManifoldLoader:
        if cls._instance is None:
            with cls._lock:
                # Double-checked locking
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized") or not self._initialized:
            self._discovery_manager = DiscoveryManager()
            self._asset_groups: dict[str, DynamicAssetGroup] = {}
            self._initialized = False

    def _initialize(self):
        """
        Performs the initial discovery of the project root and asset directories.
        This method is called only on the first attempt to access an asset.
        """
        if not self._initialized:
            # For the MVP, we'll use a simplified discovery process.
            # A more robust implementation will be added in Phase 2.
            project_root = self._discovery_manager.find_project_root()
            
            # Search for common asset directory names
            for dir_name in ["assets", "resources"]:
                assets_dir = project_root / dir_name
                if assets_dir.is_dir():
                    for item in assets_dir.iterdir():
                        if item.is_dir():
                            self._asset_groups[item.name] = DynamicAssetGroup(item)
                    break  # Stop after finding the first valid directory
            
            self._initialized = True

    def __getattr__(self, name: str) -> DynamicAssetGroup:
        """
        Provides dynamic access to top-level asset directories.

        Triggers the discovery process on the first access.

        Args:
            name: The name of the top-level asset directory (e.g., "images").

        Returns:
            A `DynamicAssetGroup` representing the requested directory.
        """
        if not self._initialized:
            self._initialize()

        if name in self._asset_groups:
            return self._asset_groups[name]

        # todo: Raise a proper AssetNotFoundError with suggestions
        raise AttributeError(f"'{name}' asset group not found.")

    def __repr__(self) -> str:
        return f"<ManifoldLoader initialized={self._initialized}>"
