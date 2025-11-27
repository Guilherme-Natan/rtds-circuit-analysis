import argparse


def create_parser():
    """Creates the parser for printing the vitis code.

    Returns:
        The parser.
    """

    parser = argparse.ArgumentParser(
        description="Prints the Vitis HLS cpp code, for implementing the circuit state equations in a FPGA",
        epilog=(
            'If you want to output it to a file, it is recommended to use the ">" output redirect operator. '
            "See the docs for more details: https://rtds-circuit-analysis.readthedocs.io/en/stable/vitis.html"
        ),
        usage="%(prog)s [netlist.cir] [-T [TIMESTEP]] [-F [FIXED_BITS]] [-P [POINT_BITS]] (-f | -b | -t)",
    )
    parser.add_argument(
        "filepath",
        type=str,
        nargs="?",
        help="Path for the netlist",
    )

    requiredNamed = parser.add_argument_group("Required Named Arguments")

    requiredNamed.add_argument(
        "-T",
        "--time-step",
        nargs="?",
        metavar="TIMESTEP",
        help="Sets the time step used in the simulation. Not necessary if .STEP is set in the netlist.",
    )

    requiredNamed.add_argument(
        "-F",
        "--fixed",
        nargs="?",
        metavar="BITS",
        help="Number of bits allocated to the fixed number type, in total",
    )

    requiredNamed.add_argument(
        "-P",
        "--point",
        nargs="?",
        metavar="BITS",
        help="Number of bits before the point, **including** the sign bit",
    )

    oneAndOnlyONe = parser.add_argument_group(
        "Mutually Exclusive Required Arguments",
        description="You should add **one** and **only one** of the options below",
    )

    oneAndOnlyONe.add_argument(
        "-f",
        "--forward",
        action="store_true",
        help="Uses the forward method for the discrete state equations.",
    )

    oneAndOnlyONe.add_argument(
        "-b",
        "--backward",
        action="store_true",
        help="Uses the backward method for the discrete state equations.",
    )

    oneAndOnlyONe.add_argument(
        "-t",
        "--trapezoidal",
        action="store_true",
        help="Uses the trapezoidal method for the discrete state equations.",
    )

    # parser.add_argument(
    #     "-i",
    #     "--currents",
    #     nargs="*",
    #     metavar="COMPONENTS",
    #     help="Components to add their currents as an output for the FPGA",
    # )

    # parser.add_argument(
    #     "-v",
    #     "--component-voltages",
    #     nargs="*",
    #     metavar="COMPONENTS",
    #     help="Components to add their voltages as an output for the FPGA",
    # )

    # parser.add_argument(
    #     "-n",
    #     "--node-voltages",
    #     nargs="*",
    #     metavar="NODES",
    #     help="Nodes to add their voltages as an output for the FPGA",
    # )

    # HACK: Move the optional arguments to the ending of the help command
    # optional_args = parser._action_groups.pop(1)
    # parser._action_groups.append(optional_args)

    return parser
