"""Functions related to checking for errors in the command line arguments."""

import os
from typing import TYPE_CHECKING

from rtds_circuit_analysis.utils import error_message

if TYPE_CHECKING:
    import argparse


def check_for_errors(args: "argparse.Namespace", app_name: str):
    """Check for errors for the arguments in the cli.

    Args:
        args (argparse.Namespace): The arguments given in the cli.
        app_name (str): The name for the program
    """

    more_info = (
        f"For information on how to use this program, run the command {app_name} -h, and also look at the README"
    )
    filepath = args.filepath

    if not filepath:
        error_message(f"You did not enter the path to a netlist...\n{more_info}")

    if not os.path.exists(filepath):
        error_message(f'File "{filepath}" not found!\n{more_info}')
