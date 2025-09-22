"""CLI commands for managing configuration."""

from argparse import Namespace
from pathlib import Path
from tomllib import load

from pokemanager import config_file, default_data_dir


def config(args: Namespace):
    """Configure the package."""
    print("Configuring pokemanager...")
    if not hasattr(args, "configuration"):
        if args.verbosity:
            print("No configuration changes provided.")
            print(args)
        return
    for key, value in args.configuration.items():
        if value is None:
            if args.verbosity:
                print(f"CONFIG: {key} = ", end="")
            print(get_config(key))
        else:
            set_config(key, value)
            if args.verbosity:
                print(f"{type(value)=}")
                print(f"Setting {key} to {value.resolve() if hasattr(value, 'resolve') else value}")


def default_config():
    """Create a default configuration file."""
    with config_file.open("w", encoding="utf-8") as f:
        f.write("# pokemanager configuration file\n")
        f.write("# created by pokemanager\n")
        f.write("\n")
        f.write(f"appdata = '{default_data_dir}'\n")


def get_config(key: str) -> str:
    """Get a configuration value."""
    with config_file.open("rb") as f:
        return load(f)[key]
        # data = load(f)
        # match key:
        #     case "appdata":
        #         return Path(data[key]).expanduser().resolve()
        #     case _:
        #         return data[key]


def set_config(key: str, value: str):
    """Set a configuration value."""
    with config_file.open("r+b", encoding="utf-8") as f:
        data = load(f)
        data[key] = str(value)
        f.seek(0)
        f.truncate()
        f.write("# pokemanager configuration file\n")
        f.write("# created by pokemanager\n")
        f.write("\n")
        for k, v in data.items():
            f.write(f"{k} = '{v}'\n")


def locate_config_file(_: Namespace) -> Path:
    """Locate the configuration file."""
    print(f"Configuration file located at: {config_file}")
    return config_file
