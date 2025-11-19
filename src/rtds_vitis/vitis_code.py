from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

    from rtds_circuit_analysis import Circuit


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


def print_vitis_code(circuit: "Circuit", args: "Namespace"):
    """Prints the cpp vitis code, for implementing the circuit in an FPGA.

    Args:
        circuit (Circuit): The circuit's class
        args (Namespace): The arguments for the rtds-vitis command line code
    """

    # C headers
    code = get_cpp_headers(args.fixed, args.point)

    print(code)
