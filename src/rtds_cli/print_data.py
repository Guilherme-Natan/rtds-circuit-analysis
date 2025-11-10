from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rtds_circuit_analysis import Circuit


def print_data(circuit: "Circuit", arguments: dict[str, list[str] | None]):
    """Prints the data for the circuit, accordingly to the command line arguments

    Args:
        circuit (Circuit): The circuit.
        arguments (dict[str, list[str]  |  None]): The arguments, containing information related to what to print.
    """
    # If no argument is passed, print everything
    if all(arg is None for arg in arguments.values()):
        circuit.print_all()
        return

    print_methods = {
        "node_voltages": circuit.print_node_voltages,
        "component_voltages": circuit.print_component_voltages,
        "currents": circuit.print_currents,
        "states": circuit.print_states,
        "forward": circuit.print_forward,
        "backward": circuit.print_backward,
        "trapezoidal": circuit.print_trapezoidal,
    }

    for arg, components_or_nodes in arguments.items():
        if components_or_nodes is None:
            continue
        print_method = print_methods[arg]
        print_method(*components_or_nodes)
