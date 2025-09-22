"""Pokemanager package initialization."""

import sys
from os import getenv
from pathlib import Path

# determine os specific config file and default data directory
if sys.platform.startswith("win"):
    config_file = Path(getenv("LOCALAPPDATA", "~\\AppData\\Local") + "\\pokemanager.toml").expanduser().resolve()
    default_data_dir = Path(getenv("APPDATA", "~\\AppData\\Roaming") + "\\pokemanager").expanduser().resolve()
elif sys.platform.startswith("linux"):
    config_file = Path(getenv("XDG_CONFIG_HOME", "~/.config") + "/pokemanager.toml").expanduser().resolve()
    default_data_dir = Path(getenv("XDG_DATA_HOME", "~/.local/share") + "/pokemanager").expanduser().resolve()
elif sys.platform.startswith("darwin"):
    config_file = Path("~/Library/Application Support/pokemanager/config.toml").expanduser().resolve()
    default_data_dir = Path("~/Library/Application Support/pokemanager").expanduser().resolve()
else:
    raise NotImplementedError(f"Unsupported platform: {sys.platform}")
