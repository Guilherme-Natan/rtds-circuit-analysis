"""Module related to the creation of the parses"""

import argparse


def create_parser():
    """Creates the parser for the cli.

    Returns:
        The parser.
    """
    parser = argparse.ArgumentParser(
        description="Finds the equations that describe a circuit written as a netlist",
        usage="%(prog)s [filepath] [options]",
    )
    parser.add_argument(
        "filepath",
        type=str,
        nargs="?",
        help="Path for the netlist",
    )

    parser.add_argument(
        "-i",
        "--currents",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the currents for each of the COMPONENTS. If COMPONENTS are not specified, prints the currents"
        "through all components.",
    )

    parser.add_argument(
        "-v",
        "--component-voltages",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the voltages for each of the COMPONENTS. If COMPONENTS are not specified, prints the voltage drops"
        "across all components",
    )

    parser.add_argument(
        "-n",
        "--node-voltages",
        nargs="*",
        metavar="NODES",
        help="Prints the voltages for each of the NODES. If NODES are not specified, prints the voltages at all nodes",
    )

    parser.add_argument(
        "-s",
        "--states",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the continuous state equations for each of the COMPONENTS. If COMPONENTS are not specified, prints"
        "the state equations through all energy storing components.",
    )

    parser.add_argument(
        "-f",
        "--forward",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the discrete state equations for each of the COMPONENTS, using the forward method. If COMPONENTS"
        "are not specified, prints the state equations through all energy storing components.",
    )

    parser.add_argument(
        "-b",
        "--backward",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the discrete state equations for each of the COMPONENTS, using the backward method. If COMPONENTS"
        "are not specified, prints the state equations through all energy storing components.",
    )

    parser.add_argument(
        "-t",
        "--trapezoidal",
        nargs="*",
        metavar="COMPONENTS",
        help="Prints the discrete state equations for each of the COMPONENTS, using the trapezoidal method. If"
        "COMPONENTS are not specified, prints the state equations through all energy storing components.",
    )

    parser.add_argument(
        "-T",
        "--time-step",
        nargs="?",
        metavar="TIMESTEP",
        help='Sets the time step for the discrete methods. If not set, the discrete methods will have "Ts" as a literal'
        "for the timestep. Will take precedence over the netlist's .STEP, if set.",
    )

    return parser
