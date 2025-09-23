"""
A simple script to demonstrate the basic functionality of the Rune library.

This script showcases how to access nested asset directories and files
using the intuitive, attribute-based API provided by Rune and the new
styled logging system.
"""

import sys
from pathlib import Path

# Add the source directory to the Python path.
# This allows us to run this example script directly without installing the package.
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root / "src"))

from rune import assets
from rune.tools import console, log_info, log_success, log_warning, log_error

def main():
    """
    Demonstrates accessing various assets using the Rune API.
    """
    console.rule("[bold green]Rune Asset Access Demonstration[/]", style="green")

    # Rune works by discovering a top-level "assets" or "resources" directory.
    # Let's access the "images" group within it.
    log_info("Accessing a directory group:")
    images_group = assets.images
    console.print(f"  - assets.images -> [path]{images_group}[/path]")

    # You can access nested groups in the same way.
    log_info("Accessing a nested directory group:")
    ui_images_group = assets.images.ui
    console.print(f"  - assets.images.ui -> [path]{ui_images_group}[/path]")

    # To get the path to a specific file, access it like an attribute.
    # The file extension is optional but can be included.
    log_info("Accessing a specific file:")
    player_sprite_path = assets.images.sprites.player
    console.print(f"  - assets.images.sprites.player -> [path]{player_sprite_path}[/path]")
    log_success(f"Path exists: {player_sprite_path.exists()}")

    # The '/' operator can also be used for path joining, just like with pathlib.
    log_info("Accessing a file using the '/' operator:")
    theme_music_path = assets.audio.music / "theme.mp3"
    console.print(f"  - assets.audio.music / 'theme.mp3' -> [path]{theme_music_path}[/path]")
    log_success(f"Path exists: {theme_music_path.exists()}")

    # Accessing a data file.
    log_info("Accessing a data file:")
    config_file_path = assets.data.config
    console.print(f"  - assets.data.config -> [path]{config_file_path}[/path]")
    log_success(f"Path exists: {config_file_path.exists()}")

    # Demonstrate error handling for a missing asset.
    log_info("Attempting to access a missing asset:")
    try:
        missing_asset = assets.images.non_existent_file
    except AttributeError as e:
        log_error("Asset access failed as expected.", e=e)

    console.rule("[bold green]End of Demonstration[/]", style="green")


if __name__ == "__main__":
    main()
