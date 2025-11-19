import sys
from typing import TYPE_CHECKING

import sympy as sp

if TYPE_CHECKING:
    from argparse import Namespace

    from rtds_circuit_analysis import Circuit


def get_equations(circuit: "Circuit", args: "Namespace") -> dict[str, sp.Eq]:
    """Get the equations for the circuit, accordingly to the chosen method

    Args:
        circuit (Circuit): The circuit object.
        args (Namespace): The command line arguments

    Returns:
        dict[str, sp.Eq]: The dict that relates each component to its sympy equation.
    """
    # Get expression for the method chosen
    if args.forward:
        expressions = circuit.forward
    elif args.backward:
        expressions = circuit.backward
    else:
        expressions = circuit.trapezoidal

    # Generate the equations
    equations = expressions.copy()
    for component, expression in expressions.items():
        # Generates the left hand side for the equation
        lhs = component
        match lhs[0]:
            case "C":
                lhs = "V" + lhs
            case "L":
                lhs = "I" + lhs
        lhs += "_{n}"
        lhs = sp.Symbol(lhs)

        # Stores the equation in the dictionary
        equations[component] = sp.Eq(lhs, expression)

    return equations


def get_parameters(equations: dict[str, sp.Eq]) -> list[str]:
    """The parameter for the circuit, that is, the values for the resistors, capacitors and inductors that are literal,
    instead of numeric.

    Args:
        equations (dict[str, sp.Eq]): Dict that relates each component to its equation.

    Returns:
        list[str]: List of parameters, where the values for resistors comes first, then inductors, and finally
        capacitors.
    """
    # Get list of parameters from the equations (resistor, capacitor and inductors literal values)
    parameters = set()
    for equation in equations.values():
        symbols = equation.free_symbols
        parameters.update(str(symbol) for symbol in symbols if str(symbol)[0] in ("R", "C", "L"))
    parameters = list(parameters)

    # Sorts the list, r first, then l, then c
    priority_rlc = {"R": 0, "L": 1, "C": 2}
    parameters.sort(key=lambda symbol: (priority_rlc[symbol[0]], symbol))

    return parameters


def get_cpp_headers(fixed: str, point: str) -> str:
    """Layout the required information at the start of every vitis cpp file.

    Args:
        fixed (str): Number of bits the fixed point representation should have.
        point (str): Number of bits behind the point the fixed point representation should have (including the sign).

    Returns:
        str: The cpp header
    """

    return (
        "#include <ap_fixed.h>\n"
        "#include <ap_int.h>\n"
        f"typedef ap_fixed<{fixed}, {point}, AP_TRN, AP_WRAP> data_t;\n"
        "typedef ap_uint<1> uint1_t;\n"
    )


def get_cpp_parameters(parameters: list[str]) -> str:
    """Transforms the list of parameters into a list of "#define"s in cpp, so the user can manually change it later.

    Args:
        parameters (list[str]): _description_

    Returns:
        str: _description_
    """

    max_whitespaces = 1 + max(len(parameter) for parameter in parameters)
    output = "\n"
    for parameter in parameters:
        whitespaces = " " * (max_whitespaces - len(parameter))
        output += f"#define {parameter}{whitespaces}data_t(CHANGEME)\n"

    return output


def print_vitis_code(circuit: "Circuit", args: "Namespace"):
    """Prints the cpp vitis code, for implementing the circuit in an FPGA.

    Args:
        circuit (Circuit): The circuit's class
        args (Namespace): The arguments for the rtds-vitis command line code
    """

    # C headers
    code = get_cpp_headers(args.fixed, args.point)

    # Find the equations that generate the circuit, and its parameters
    equations = get_equations(circuit, args)
    parameters = get_parameters(equations)

    # Generate CHANGEME data_t entries when some component values are literals
    if parameters:
        code += get_cpp_parameters(parameters)

    print(code)

    if parameters:
        print(
            "\033[33mWARNING: Components with literal values found. You'll need to replace all the "
            "'CHANGEME's in the cpp code with their respective numeric values\033[0m",
            file=sys.stderr,
        )
