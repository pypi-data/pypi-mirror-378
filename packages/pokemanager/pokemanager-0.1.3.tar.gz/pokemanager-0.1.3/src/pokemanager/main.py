"""."""

from pathlib import Path
from pickle import dump as pkl_dump
from pickle import load as pkl_load
from tomllib import load as toml_load

from pokemanager import config_file
from pokemanager.data import Box
from pokemanager.utils import slugify


class AppData:
    """AppData management class."""

    boxes: dict[str, Box]

    def __init__(self):
        """Initialize AppData."""
        self.boxes = self.load_boxes()

    @staticmethod
    def get_appdata() -> Path:
        """Get appdata path."""
        with config_file.open("rb") as f:
            return Path(toml_load(f)["appdata"]).expanduser().resolve()

    @classmethod
    def load_boxes(cls) -> dict[str, Box]:
        """Load boxes from the data directory."""
        boxes: dict[str, Box] = {}
        print("Loading boxes...")
        for box_file in cls.get_appdata().joinpath("boxes").glob("*.pkl"):
            print(f"Loading box from {box_file}")
            with box_file.open("rb") as f:
                box: Box = pkl_load(f)
                print(f"Loaded box: {box.name} with {len(box.pokemon)} Pokémon")
                boxes[box.name] = box
        print(f"Loaded {len(boxes)} boxes.")

        return boxes

    @classmethod
    def save_box(cls, box: Box) -> None:
        """Save a box to the data directory."""
        box_file: Path = cls.get_appdata().joinpath("boxes", f"{slugify(box.name)}.pkl")
        print(f"Saving box to {box_file}")
        box_file.parent.mkdir(parents=True, exist_ok=True)
        with box_file.open("wb") as f:
            pkl_dump(box, f)
        print(f"Saved box: {box.name} with {len(box.pokemon)} Pokémon")

    @classmethod
    def delete_box(cls, box_name: str) -> None:
        """Delete a box from the data directory."""
        box_file: Path = cls.get_appdata().joinpath("boxes", f"{slugify(box_name)}.pkl")
        if box_file.exists():
            print(f"Deleting box file {box_file}")
            box_file.unlink()
            print(f"Deleted box file {box_file}")
        else:
            print(f"Box file {box_file} does not exist, nothing to delete.")
