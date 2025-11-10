from typing import TYPE_CHECKING

from rtds_circuit_analysis.parse_netlist import Component

if TYPE_CHECKING:
    import sympy as sp


def object_value_association(
    lhs: str,
    rhs: "sp.Expr",
    is_state: bool,
    lhs_is_derivative: bool,
    is_discrete: bool,
) -> str:
    """Find an association between a component/state and its value.

    Args:
        lhs (str): The left hand side of the association
        rhs (sp.Expr): The right hand side of the association
        is_state (bool): If it a state equation.
        lhs_is_derivative (bool): If the left hand side of the equation is a derivative.
        is_discrete (bool): If it is an discrete equation.

    Returns:
        str: The association.
    """
    if is_state:
        match lhs[0]:
            case "C":
                lhs = "V" + lhs
            case "L":
                lhs = "I" + lhs

    if lhs_is_derivative:
        lhs = f"d{lhs}/dt"

    if is_discrete:
        lhs += "_{n}"

    middle_symbol = "=" if is_state else "-->"

    return f"{lhs} {middle_symbol} {rhs}"


def component_or_node_value_associations(
    component_or_node_value_table: dict[str, "sp.Expr"],
    filter_list: list[str],
    is_state: bool,
    lhs_is_derivative: bool,
    is_discrete: bool,
) -> str:
    """Prettify the associations (relations or equations) between each component/node and its value.

    Args:
        component_or_node_value_table (dict[str, sp.Expr]): Table that relates each component/node to its value.
        filter_list (list[str]): List of the components/nodes to output.
        is_state (bool): If each association (relation between the component and its value) will be a state equation.
        lhs_is_derivative (bool): If the left hand side of each association is a derivative.
        is_discrete (bool): If each association is an discrete equation.

    Returns:
        str: The associations.
    """
    formatted_associations = ""

    for component_or_node in component_or_node_value_table:
        if component_or_node not in filter_list:
            continue
        formatted_associations += (
            object_value_association(
                component_or_node,
                component_or_node_value_table[component_or_node],
                is_state,
                lhs_is_derivative,
                is_discrete,
            )
            + "\n"
        )

    return formatted_associations.strip()


def separate_existent(
    components_or_nodes_in_circuit: list[str],
    components_or_nodes_to_separate: list[str],
) -> tuple[list[str], list[str]]:
    """Separates the components between the ones that are in the circuit, and the ones that aren't

    Args:
        components_or_nodes_in_circuit (list[str]): The ones that exist in the circuit.
        components_or_nodes_to_separate (list[str]): The ones to separate


    Returns:
        tuple[list[str], list[str]]: The components that are in the circuit, and the ones that aren't
    """
    existent_components_or_nodes, nonexistent_components_or_nodes = [], []
    for component_or_node in components_or_nodes_to_separate:
        component_or_node = component_or_node.upper()

        if component_or_node in components_or_nodes_in_circuit:
            existent_components_or_nodes.append(component_or_node)
        else:
            nonexistent_components_or_nodes.append(component_or_node)

    return existent_components_or_nodes, nonexistent_components_or_nodes


def format_output(
    component_or_node_value_table: dict[str, "sp.Expr"],
    components_or_nodes: list[str] | None,
    is_state: bool = False,
    lhs_is_derivative: bool = False,
    is_discrete: bool = False,
) -> str:
    """Prettify the output for each component/nodes parameters, or state equations.

    Args:
        component_or_node_value_table (dict[str, sp.Expr]): Table that relates each component/node to its value.
        components_or_nodes (list[str] | None): List of components or nodes to format the output.
        is_state (bool, optional): If each association (relation between the component and its value) will be a state
        equation. Defaults to False.
        lhs_is_derivative (bool, optional): If the left hand side of each association is a derivative. Defaults to
        False.
        is_discrete (bool, optional): If each association is an discrete equation. Defaults to False.

    Returns:
        str: The formatted string, ready for printing
    """

    # If the table is empty, then there are no states for the circuit
    if not component_or_node_value_table:
        return "This circuit is stateless\n"

    # If no components/nodes are given, get the requested parameters for every component/node
    if not components_or_nodes:
        components_or_nodes = list(component_or_node_value_table.keys())
        non_existent_components_or_nodes = None
    # Otherwise, separate the existing given components/nodes to the non_existing ones
    else:
        components_or_nodes, non_existent_components_or_nodes = separate_existent(
            list(component_or_node_value_table), components_or_nodes
        )

    # Finds the associations for each given component/node to its value
    formatted_output = component_or_node_value_associations(
        component_or_node_value_table, components_or_nodes, is_state, lhs_is_derivative, is_discrete
    )

    if non_existent_components_or_nodes:
        # This "if" is to keep the message of invalid components/nodes close to the "title" of each print method, if
        # every component is invalid.
        if formatted_output:
            formatted_output += "\n"

        formatted_output += (
            "The following components/nodes either don't exist in the circuit, "
            "or are not valid for the requested method:\n"
        )
        formatted_output += f"* {", ".join(non_existent_components_or_nodes)} *"

    formatted_output += "\n"

    return formatted_output
