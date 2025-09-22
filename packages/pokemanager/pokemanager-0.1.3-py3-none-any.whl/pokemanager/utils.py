"""Utility functions for pokemanager."""

import re
import unicodedata
from typing import Any


def combinations(collection: list[Any], combination_length: int) -> list[list[Any]]:
    """Generate all combinations of a specified length from the input collection."""
    if combination_length > len(collection) or combination_length < 1:
        return []
    if combination_length == len(collection):
        return [collection]
    if combination_length == 1:
        return [[element] for element in collection]
    result: list[list[Any]] = []
    for i in range(len(collection) - combination_length + 1):
        head: list[Any] = collection[i : i + 1]
        tail: list[list[Any]] = combinations(collection[i + 1 :], combination_length - 1)
        for t in tail:
            result.append(head + t)
    return result


def slugify(value: Any, allow_unicode: bool = False):
    """Slugify a string.

    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")
