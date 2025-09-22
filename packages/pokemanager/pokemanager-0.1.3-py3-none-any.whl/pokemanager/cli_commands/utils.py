"""Utility classes and functions for CLI commands."""

from argparse import Action, Namespace
from pathlib import Path
from shutil import rmtree

from pokemanager import config_file
from pokemanager.cli_commands.cli_config import default_config, get_config


class ConfigAction(Action):
    """Custom action to handle configuration settings."""

    def __init__(self, option_strings, dest, **kwargs):
        super().__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
        setattr(namespace, "configuration", getattr(namespace, "configuration", {}) | {self.dest: values})


def clean(_: Namespace):
    """Clean pokemanager files."""
    print("Cleaning pokemanager files...")
    while True:
        del_data = input("Are you sure you want to delete your application data? (y/N): ").strip().lower() or "n"
        if del_data in ("y", "n"):
            break
    if del_data == "y":
        print("Deleting application data...")
        rmtree(get_config("appdata"), ignore_errors=True)
    while True:
        del_config = input("Are you sure you want to delete your configuration? (y/N): ").strip().lower() or "n"
        if del_config in ("y", "n"):
            break
    if del_config == "y":
        print("Deleting configuration...")
        config_file.unlink(missing_ok=True)
    print("Clean complete.")


def init(_: Namespace):
    """Initialize pokemanager."""
    print("Initializing pokemanager...")
    if not config_file.exists():
        print(f"Creating default configuration file at {config_file}")
        config_file.parent.mkdir(parents=True, exist_ok=True)
        default_config()
    appdata: Path = get_config("appdata")
    print(f"Using application data directory at {appdata}")
    appdata.mkdir(parents=True, exist_ok=True)

    print("Initialization complete.")
