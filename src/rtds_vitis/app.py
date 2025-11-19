import rtds_cli.errors as rtds_cli
from rtds_circuit_analysis import Circuit
from rtds_vitis.create_parser import create_parser
from rtds_vitis.errors import check_for_errors
from rtds_vitis.vitis_code import print_vitis_code


def app():
    parser = create_parser()
    args = parser.parse_args()

    # Check for the same errors as the rtds-circuit-analysis command
    rtds_cli.check_for_errors(args, parser.prog)

    circuit = Circuit(args.filepath, args.time_step)

    # Check for erros exclusive for this program
    check_for_errors(args, parser.prog, circuit)

    print_vitis_code(circuit, args)
