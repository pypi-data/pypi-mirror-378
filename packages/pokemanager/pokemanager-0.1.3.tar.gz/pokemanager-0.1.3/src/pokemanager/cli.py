r"""CLI.

pkm [OPTION] [COMMAND]

[OPTION]
--version, -v
--help, -h

[COMMAND]
init
    "Initialize pokemanager."
config [CONFIG_KEY] [CONFIG_VALUE]
    locate
        "Locate the config file."
    --appdata [PATH]
        "Where the application data is stored."
        default: "~/.local/share/pokemanager/" or "C:\\Users\\<username>\\AppData\\Roaming\\"
fetch [GOOGLE_SHEET_URL] [CATEGORY] [BOX_NAME]
    "Fetch box data from Google Sheets."
box
    list
        "List all boxes."
    add [BOX_NAME]
        "Add a new box."
    remove [BOX_NAME]
        "Remove a box."
    rename [OLD_BOX_NAME] [NEW_BOX_NAME]
        "Rename a box."
    config [BOX_NAME] [CONFIG_KEY] [CONFIG_VALUE]
        "Configure a box."
    export [BOX_NAME] [FILE_PATH]
        "Export a box to a file."
    import [FILE_PATH]
        "Import a box from a file."
pokemon
    add [BOX_NAME] [POKEMON_DATA]
        "Add a Pokémon to a box."
    remove [BOX_NAME] [POKEMON_ID]
        "Remove a Pokémon from a box."
    move [FROM_BOX_NAME] [TO_BOX_NAME] [POKEMON_ID]
        "Move a Pokémon from one box to another."
    list [BOX_NAME]
        "List all Pokémon in a box."
    find [SEARCH_CRITERIA]
        "Find Pokémon across all boxes based on criteria."
    export [BOX_NAME] [FILE_PATH]
        "Export Pokémon from a box to a file."
    import [FILE_PATH] [BOX_NAME]
        "Import Pokémon from a file to a box."
    edit [BOX_NAME] [POKEMON_ID] [NEW_POKEMON_DATA]
        "Edit a Pokémon's data in a box."
"""

import argparse
from pathlib import Path

from pokemanager._version import __version__
from pokemanager.cli_commands import cli_box, cli_config, cli_fetch, cli_pokemon, utils


def main():
    """Main entry point for the CLI."""
    # pokemanager / pkm command
    parser = argparse.ArgumentParser(description="your very own command-line PC")
    parser.add_argument("-v", "--verbosity", action="count", default=0, help="increase output verbosity")
    parser.add_argument("--version", action="version", version=f"pokemanager version {__version__}")
    subparsers = parser.add_subparsers(help="subcommand help")

    # init subcommand
    parser_init = subparsers.add_parser("init", help="initialize pokemanager")
    parser_init.set_defaults(func=utils.init)

    # clean subcommand
    parser_clean = subparsers.add_parser("clean", help="clean your system from pokemanager files")
    parser_clean.set_defaults(func=utils.clean)

    # config subcommand
    parser_config = subparsers.add_parser("config", help="configure the package")
    parser_config.add_argument(
        "--appdata",
        nargs="?",
        type=Path,
        action=utils.ConfigAction,
        help="where the application data is stored or change the path",
    )
    parser_config.set_defaults(func=cli_config.config)
    subparsers_config = parser_config.add_subparsers(help="subcommand help")

    ## locate subcommand
    parser_config_locate = subparsers_config.add_parser("locate", help="locate the config file")
    parser_config_locate.set_defaults(func=cli_config.locate_config_file)

    # fetch subcommand
    parser_fetch = subparsers.add_parser("fetch", help="fetch a box")
    parser_fetch.add_argument("google_sheet_url", type=str, help="url to a compatible Google Sheet")
    parser_fetch.add_argument("box_name", type=str, help="name of the box to save the data to")
    parser_fetch.add_argument("category", type=str, help="category of the sheet and box")
    parser_fetch.set_defaults(func=cli_fetch.fetch)

    # box subcommand
    parser_box = subparsers.add_parser("box", help="manage boxes")
    parser_box.set_defaults(func=lambda _: parser_box.print_help())  # type: ignore
    subparsers_box = parser_box.add_subparsers(help="subcommand help")

    ## list subcommand
    parser_box_list = subparsers_box.add_parser("list", help="list all boxes")
    parser_box_list.set_defaults(func=cli_box.box_list)
    ## add subcommand
    parser_box_add = subparsers_box.add_parser("add", help="add a new box")
    parser_box_add.add_argument("name", type=str, help="name of the new box")
    parser_box_add.set_defaults(func=cli_box.box_add)
    ## remove subcommand
    parser_box_remove = subparsers_box.add_parser("remove", help="remove a box")
    parser_box_remove.add_argument("name", type=str, help="name of the box")
    parser_box_remove.set_defaults(func=cli_box.box_remove)
    ## rename subcommand
    parser_box_rename = subparsers_box.add_parser("rename", help="rename a box")
    parser_box_rename.add_argument("old_name", type=str, help="current name of the box")
    parser_box_rename.add_argument("new_name", type=str, help="new name of the box")
    parser_box_rename.set_defaults(func=cli_box.box_rename)
    ## config subcommand
    parser_box_config = subparsers_box.add_parser("config", help="configure a box")
    parser_box_config.add_argument("name", type=str, help="name of the box")
    parser_box_config.add_argument("config_key", type=str, help="configuration key")
    parser_box_config.add_argument("config_value", type=str, help="configuration value")
    parser_box_config.set_defaults(func=cli_box.box_config)
    ## export subcommand
    parser_box_export = subparsers_box.add_parser("export", help="export a box to a file")
    parser_box_export.add_argument("name", type=str, help="name of the box")
    parser_box_export.add_argument("file_path", type=argparse.FileType("w"), help="path to the file to export to")
    parser_box_export.set_defaults(func=cli_box.box_export)
    ## import subcommand
    parser_box_import = subparsers_box.add_parser("import", help="import a box from a file")
    parser_box_import.add_argument("file_path", type=argparse.FileType("r"), help="path to the file to import from")
    parser_box_import.set_defaults(func=cli_box.box_import)

    # pokemon subcommand
    parser_pokemon = subparsers.add_parser("pokemon", help="manage Pokémon")
    parser_pokemon.set_defaults(func=lambda _: parser_pokemon.print_help())  # type: ignore
    subparsers_pokemon = parser_pokemon.add_subparsers(help="subcommand help")

    ## add subcommand
    parser_pokemon_add = subparsers_pokemon.add_parser("add", help="add a Pokémon to a box")
    parser_pokemon_add.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_add.add_argument("pokemon_data", type=str, help="Pokémon data")
    parser_pokemon_add.set_defaults(func=cli_pokemon.pokemon_add)

    ## remove subcommand
    parser_pokemon_remove = subparsers_pokemon.add_parser("remove", help="remove a Pokémon from a box")
    parser_pokemon_remove.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_remove.add_argument("pokemon_id", type=str, help="ID of the Pokémon")
    parser_pokemon_remove.set_defaults(func=cli_pokemon.pokemon_remove)

    ## move subcommand
    parser_pokemon_move = subparsers_pokemon.add_parser("move", help="move a Pokémon from one box to another")
    parser_pokemon_move.add_argument("from_box_name", type=str, help="source box name")
    parser_pokemon_move.add_argument("to_box_name", type=str, help="destination box name")
    parser_pokemon_move.add_argument("pokemon_id", type=str, help="ID of the Pokémon")
    parser_pokemon_move.set_defaults(func=cli_pokemon.pokemon_move)

    ## list subcommand
    parser_pokemon_list = subparsers_pokemon.add_parser("list", help="list all Pokémon in a box")
    parser_pokemon_list.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_list.set_defaults(func=cli_pokemon.pokemon_list)

    ## find subcommand
    parser_pokemon_find = subparsers_pokemon.add_parser("find", help="find Pokémon across all boxes based on criteria")
    parser_pokemon_find.add_argument("search_criteria", type=str, help="search criteria")
    parser_pokemon_find.set_defaults(func=cli_pokemon.pokemon_find)

    ## export subcommand
    parser_pokemon_export = subparsers_pokemon.add_parser("export", help="export Pokémon from a box to a file")
    parser_pokemon_export.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_export.add_argument("pokemon_id", type=str, help="ID of the Pokémon")
    parser_pokemon_export.add_argument("file_path", type=argparse.FileType("w"), help="path to the file to export to")
    parser_pokemon_export.set_defaults(func=cli_pokemon.pokemon_export)

    ## import subcommand
    parser_pokemon_import = subparsers_pokemon.add_parser("import", help="import Pokémon from a file to a box")
    parser_pokemon_import.add_argument("file_path", type=argparse.FileType("r"), help="path to the file to import from")
    parser_pokemon_import.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_import.set_defaults(func=cli_pokemon.pokemon_import)

    ## edit subcommand
    parser_pokemon_edit = subparsers_pokemon.add_parser("edit", help="edit a Pokémon's data in a box")
    parser_pokemon_edit.add_argument("box_name", type=str, help="name of the box")
    parser_pokemon_edit.add_argument("pokemon_id", type=str, help="ID of the Pokémon")
    parser_pokemon_edit.add_argument("new_pokemon_data", type=str, help="new Pokémon data")
    parser_pokemon_edit.set_defaults(func=cli_pokemon.pokemon_edit)

    args = parser.parse_args()
    v = args.verbosity
    if hasattr(args, "func"):
        if v:
            print("Executing function:", args.func.__name__)
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
