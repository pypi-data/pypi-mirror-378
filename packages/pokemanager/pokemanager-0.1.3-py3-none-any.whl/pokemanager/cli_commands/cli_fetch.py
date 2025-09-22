"""CLI commands for fetching data from Google Sheets."""

from argparse import Namespace


def fetch(args: Namespace):
    """Fetch a box from a Google Sheet."""
    print("Fetching box...")
    print(f"Google Sheet URL: {args.google_sheet_url}")
    print(f"Box Name: {args.box_name}")
    print(f"Category: {args.category}")
    raise NotImplementedError("Fetch command is not yet implemented.")
