"""CLI commands for managing boxes."""

from argparse import Namespace

from pokemanager.data import Box
from pokemanager.main import AppData


def box(commands: list[str]):
    """Manage boxes."""
    print("Managing boxes...")


def box_list(commands: Namespace):
    """List all boxes."""
    print("Listing all boxes...")
    for box_name, box in AppData().boxes.items():
        print(f"- {box_name}: {len(box.pokemon)} Pokémon")


def box_add(commands: Namespace):
    """Add a new box."""
    print(f"Adding box: {commands.name}")
    new_box = Box(name=commands.name, pokemon=[])
    AppData.save_box(new_box)


def box_remove(commands: Namespace):
    """Remove a box."""
    print(f"Removing box: {commands.name}")
    AppData.delete_box(commands.name)


def box_rename(commands: Namespace):
    """Rename a box."""
    print(f"Renaming box from {commands.old_name} to {commands.new_name}")
    box = AppData().boxes[commands.old_name]
    renamed_box = Box(name=commands.new_name, pokemon=box.pokemon)
    AppData.save_box(renamed_box)
    AppData.delete_box(commands.old_name)


def box_config(commands: Namespace):
    """Configure a box."""
    print(f"Configuring box {commands.name}: setting {commands.config_key} to {commands.config_value}")
    raise NotImplementedError("Box config not implemented yet.")


def box_export(commands: Namespace):
    """Export a box to a file."""
    print(f"Exporting box {commands.name} to file {commands.file_path.name}")
    raise NotImplementedError("Box export not implemented yet.")


def box_import(commands: Namespace):
    """Import a box from a file."""
    print(f"Importing box from file {commands.file_path.name}")
    raise NotImplementedError("Box import not implemented yet.")
