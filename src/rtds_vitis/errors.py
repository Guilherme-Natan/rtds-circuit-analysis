from functools import partial
from typing import TYPE_CHECKING

from rtds_circuit_analysis.utils import error_message

if TYPE_CHECKING:
    import argparse

    from rtds_circuit_analysis import Circuit


def _full_error_message(text: str, more_info: str):
    """Helper function for the full error message

    Args:
        text (str): The text to display in the first line
        more_info (str): The text to display in the second line
    """

    error_message(f"{text}\n{more_info}")


def check_for_errors(args: "argparse.Namespace", app_name: str, circuit: "Circuit"):
    """Check for errors for the arguments in the Vitis cli.

    Args:
        args (argparse.Namespace): The arguments given in the cli.
        app_name (str): The name for the program
        circuit (list[sp.Expr]): List of states equations for the circuit
    """

    more_info = (
        f"For information on how to use this program, run the command \033[1m{app_name} -h\033[0m, and also look at the"
        " README, and the docs: https://rtds-circuit-analysis.readthedocs.io/en/stable."
    )
    full_error_message = partial(_full_error_message, more_info=more_info)

    if not circuit.states:
        full_error_message(
            f"The circuit '{args.filepath}' is stateless! No equations could be generated for it.",
        )

    if not circuit.time_step:
        full_error_message(
            "You need to supply the time step, with the '-T' flag.",
        )
    if not args.fixed:
        full_error_message(
            "You need to supply the number of bits for the fixed point type, with the '-F' flag.",
        )
    if not args.point:
        full_error_message(
            "You need to supply the number of bits behind the point for the fixed point type, with the '-P' flag.",
        )

    methods = [args.forward, args.backward, args.trapezoidal]

    if not any(methods):
        full_error_message(
            "You need to pass at least one method, with the flags '-f'/'--forward', '-b'/'--backward', "
            "or '-t'/'--trapezoidal'",
        )
    elif sum(methods) > 1:  # If more than one is selected
        full_error_message(
            "You selected two or more method flags ('-f'/'--forward', '-b'/'--backward',  and '-t'/'--trapezoidal'). "
            "Please only add one method flag.",
        )
