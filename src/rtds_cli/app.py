from rtds_circuit_analysis import Circuit
from rtds_cli.create_parser import create_parser
from rtds_cli.errors import check_for_errors
from rtds_cli.print_data import print_data


def app():
    parser = create_parser()
    args = parser.parse_args()

    check_for_errors(args, parser.prog)

    time_step = args.time_step if args.time_step else None
    circuit = Circuit(args.filepath, time_step)

    args_dict = vars(args)
    del args_dict["filepath"], args_dict["time_step"]
    print_data(circuit, args_dict)
