"""
Integration tests for the Rune library.

This test suite creates a temporary directory structure to validate
the core functionality of Rune in an isolated environment.
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add the source directory to the Python path for direct script execution
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from rune.loader import ManifoldLoader


class TestManifoldIntegration(unittest.TestCase):
    """Validates end-to-end functionality of the Rune asset loader."""

    def setUp(self):
        """Set up a temporary directory with a mock project structure."""
        # Create a temporary directory
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = Path.cwd()
        os.chdir(self.test_dir)

        # Create a mock asset structure
        self.resources_path = Path("resources")
        self.images_path = self.resources_path / "images"
        self.images_path.mkdir(parents=True)

        # Create a dummy file
        (self.images_path / "icon.png").touch()

    def tearDown(self):
        """Clean up the temporary directory and restore the CWD."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def test_asset_discovery_and_access(self):
        """
        Tests if Rune can discover and provide access to a test asset.
        """
        # Instantiate a new loader to ensure it discovers the temp environment
        assets = ManifoldLoader()

        # 1. Test directory group access
        images_group = assets.images
        self.assertEqual(images_group, self.images_path.resolve())

        # 2. Test file access
        icon_path = assets.images.icon
        expected_path = (self.images_path / "icon.png").resolve()
        self.assertEqual(icon_path, expected_path)
        self.assertTrue(icon_path.exists())

        # 3. Test path joining with the '/' operator
        icon_path_join = assets.images / "icon.png"
        self.assertEqual(icon_path_join, expected_path)


if __name__ == "__main__":
    unittest.main()
