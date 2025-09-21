"""Utility functions for pokemanager.

This module provides helper functions such as combinations for list processing.
"""

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
        head: list[Any] = collection[i:i+1]
        tail: list[list[Any]] = combinations(collection[i+1:], combination_length - 1)
        for t in tail:
            result.append(head + t)
    return result
