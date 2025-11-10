"""Module with functions related to finding inconsistences within the components for the circuit"""

from rtds_circuit_analysis.parse_netlist import Component
from rtds_circuit_analysis.utils import error_message, flatten


def check_value_first_letter(components: list[Component]):
    """Check if the literals for the values of each component start with the same letter as their type. For example,
    capacitors literals should start with C, voltage sources with V, etc.

    Args:
        components (Component): List of components.
    """
    for component in components:
        # NOTE: This will cause issues in the future, when dealing with dependant sources
        if not component.value.free_symbols:
            continue  # If the value is just a number, no literal symbols
        symbol = str(next(iter(component.value.free_symbols)))
        symbol_first_letter = symbol[0]
        if component.type != symbol_first_letter:
            error_message(
                f"Expected first letter for symbol '{symbol}' to equal '{component.type}', for component "
                f"'{component.name}' with value '{component.value}'. \n"
                f"\033[1mHint\033[22m: Rewrite the value's symbol as '{component.type}{symbol}'."
            )


def check_duplicates(components: list[Component]):
    """Check if there are two components with the same name.

    Args:
        components (list[Component]): List of components.
    """
    duplicate_dict = {}
    for component in components:
        if component.name not in duplicate_dict:
            duplicate_dict[component.name] = component
            continue
        duplicate = duplicate_dict[component.name]
        error_message(f"Netlist with two components with the same name:\n'{component}', and '{duplicate}'")


def check_ground(components: list[Component]):
    node_list = flatten(component.nodes for component in components)
    if any(node == "0" for node in node_list):
        return
    error_message("No ground node in your circuit found. \n\033[1mHint\033[22m: Change one of your node names to '0'.")


def parse_data(components: list[Component]):
    """Looks for inconsistencies in the list of components for the circuit.

    Args:
        components (list[Component]): List of components.
    """
    check_value_first_letter(components)
    check_duplicates(components)
    check_ground(components)
