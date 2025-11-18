"""Module for functions used in multiple parts of the script."""

import sys


def flatten(matrix: list[list]) -> list:
    """Flattens a list of lists into a list.

    Args:
        matrix (list[list]): List of lists

    Returns:
        list: Flatted list
    """
    return [x for xs in matrix for x in xs]


def error_message(error_msg: str):
    """Quits the program, displaying an error message first

    Args:
        error_msg (str): Info to display before leaving
    """
    print(f"\033[1mError\033[22m: {error_msg}")
    sys.exit(1)
