"""Functions related finding all the system variables for the circuit"""

from typing import Generator

import networkx as nx
import sympy as sp

from rtds_circuit_analysis import equivalent_circuit
from rtds_circuit_analysis.parse_netlist import Component
from rtds_circuit_analysis.utils import flatten


def find_loops(components: list[Component]) -> list[list[Component]]:
    """Finds the loops for the circuit.

    Args:
        components (list[Component]): List of components for the circuit.

    Returns:
        list[list[Component]]: List of loops. Each loop is a list of components, in the order they appear in the loop.
    """

    component_graph = nx.Graph()
    for component in components:
        component_graph.add_edge(component.nodes[0], component)
        component_graph.add_edge(component.nodes[1], component)

    cycle_basis = nx.minimum_cycle_basis(component_graph)

    loops = []
    for cycle in cycle_basis:
        loop = [component for component in cycle if isinstance(component, Component)]
        loops.append(loop)

    return loops


def is_in_same_direction(component: Component, adjacent_component: Component) -> bool:
    """Checks if this component is in the same as an adjacent component.

    Args:
        adjacent_component (Self): The component to compare direction with.

    Returns:
        bool: True if is in the same direction.
    """
    if adjacent_component.nodes[0] == component.nodes[0] or adjacent_component.nodes[1] == component.nodes[1]:
        return False
    return True


def find_direction_sequence(loop: list[Component]) -> list[int]:
    """Finds the list of voltage polarities for the loop.

    This list always starts with 1, and the following values are either 1 or -1 depending on the direction of the
    subsequent components related to the first. If a subsequent component is in the same direction as the first, the
    direction is 1; if they are in opposite directions, the value is -1. The direction is defined in the netlist file,
    and is best explained with examples.

    Assuming this is in the netlist:
    R1 1 2 100
    R2 2 3 100
    The "tail" of R1 is connected to the "head" of R2 through 2, so they are in the same direction. Thus, assuming the
    direction for R1 is 1, the direction list for this section would've been [1, 1].

    Now for this:
    R1 1 2 100
    R2 3 2 100
    These resistors do not have a matching head-tail pair (only their tails match), so they are in opposite directions.
    Thus, assuming the direction for R1 is 1, the direction list for this section would've been [1, -1].

    Args:
        loop (list[Component]): List of components.

    Returns:
        list[int]: List of directions for each component.
    """
    direction = 1
    voltage_polarity_sequence = [direction]
    previous_component = loop[0]
    for component in loop[1:]:
        if not is_in_same_direction(component, previous_component):
            direction *= -1
        voltage_polarity_sequence.append(direction)
        previous_component = component
    return voltage_polarity_sequence


def find_loop_equations(loops: list[list[Component]]) -> list[sp.Expr]:
    """Finds the Kirchhoff Voltage Law equation for each loop

    Args:
        loops (list[list[Component]]): List of loops

    Returns:
        list[sp.Expr]: List of equations for each loop. It isn't explicit in each list element, but every expression is
        equal to zero (accordingly to the KVL).
    """

    loop_equations = []
    for loop in loops:
        polarity_sequence = find_direction_sequence(loop)
        loop_equation = 0
        for component, polarity in zip(loop, polarity_sequence):
            if component.type == "R":
                loop_equation -= component.value * component.current * polarity
            else:
                loop_equation -= component.voltage * polarity
        loop_equations.append(loop_equation)
    return loop_equations


def find_node_graph(components: list[Component]) -> nx.MultiDiGraph:
    """Finds a graph representation for a circuit, where every circuit node corresponds to a vertex, and every component
    to an edge. Each edge is assigned a key, corresponding to the order which component appears on the netlist (starting
    at 0).

    Args:
        components (list[Component]): List of components for the circuit

    Returns:
        nx.MultiDiGraph: Graph representation for the circuit
    """
    active_group = set(("V", "I"))
    node_graph = nx.MultiDiGraph()
    for i, component in enumerate(components):
        current_from, current_to = component.nodes
        if component.type in active_group:
            current_from, current_to = current_to, current_from
        node_graph.add_edge(current_from, current_to, key=i)

    return node_graph


def find_incidence_matrix(node_graph: nx.DiGraph) -> sp.Matrix:
    """Finds the incidence matrix for a graph. The edges corresponds to each line of the matrix accordingly to their
    key.

    Args: node_graph (nx.DiGraph): The digraph to find the incidence matrix

    Returns: sp.Matrix: The incidence matrix
    """
    incidence_matrix = nx.incidence_matrix(
        node_graph,
        edgelist=sorted(node_graph.edges, key=lambda edge: edge[2]),
        oriented=True,
    )

    incidence_matrix = sp.Matrix(incidence_matrix.toarray())
    incidence_matrix = incidence_matrix.applyfunc(sp.Integer)

    return incidence_matrix


def find_current_equations(circuit: list[Component], incidence_matrix: sp.Matrix) -> list[sp.Expr]:
    """Finds the Kirchhoff Current Law equation for each node

    Args:
        circuit (list[Component]): List of components for the circuit
        incidence_matrix (sp.Matrix): Incidence matrix for the graph representation of the circuit

    Returns:
        list[sp.Expr]: List of equations for each node. It isn't explicit in each list element, but every expression is
        equal to zero (accordingly to the KVL).
    """

    currents = [component.current for component in circuit]
    currents = sp.Matrix(currents)

    current_equations = (incidence_matrix * currents).tolist()
    current_equations = flatten(current_equations)

    return current_equations


def find_unknowns(circuit: list[Component]) -> list[sp.Symbol]:
    """Finds the unknown variables for the circuit. They are currents for resistors, capacitors and voltage sources, and
    voltages for inductors and current sources.

    Args:
        circuit (list[Component]): List of components for the circuit

    Returns:
        list[sp.Symbol]: List of unknowns
    """
    unknowns = []
    for component in circuit:
        if component.type in ("I", "L"):
            unknowns.append(component.voltage)
        else:
            unknowns.append(component.current)
    return unknowns


def associate_values(components: list[Component], solutions: list[sp.Expr]):
    """Associates the calculated current/voltage results with each of their respective components.

    Args:
        components (list[Component]): List of components in the circuit.
        solutions (list[sp.Expr]): Calculated current/voltage values.
    """
    for component, solution in zip(components, solutions):
        match component.type:
            case "V" | "C":
                component.current = sp.simplify(solution)
            case "I" | "L":
                component.voltage = sp.simplify(solution)
            case "R":
                component.current = sp.simplify(solution)
                component.voltage = component.value * component.current


def find_node_voltages(components: list[Component], node_breadth_sequence: Generator[tuple[str]]) -> dict[str, sp.Expr]:
    """Find the voltage on each node of the circuit.

    Args:
        components (list[Component]): List of components for the circuit.
        node_breadth_sequence (Generator[tuple[str]]): A generator that performs a breath first search for the circuit,
        where the first element in the tuple corresponds to a node where the voltage is already known, and the second
        one to a voltage we want to calculate

    Returns:
        dict[str, sp.Expr]: A dictionary that relates each node name to each voltage on it.
    """
    voltage_drop = {}
    for component in components:
        voltage_drop[component.nodes] = component.voltage
        voltage_drop[tuple(reversed(component.nodes))] = -component.voltage

    node_voltages = {}
    node_voltages["0"] = 0
    for nodes in node_breadth_sequence:
        start_node, goal_node = nodes[0], nodes[1]
        node_voltages[goal_node] = node_voltages[start_node] - voltage_drop[nodes]
    del node_voltages["0"]

    return node_voltages


def find_component_values(components: list[Component]) -> tuple[dict[str, sp.Expr], dict[str, sp.Expr]]:
    """Creates two dictionaries, that relates each component's name to its voltage/current.

    Args:
        components (list[Component]): List of components for the circuit.

    Returns:
        tuple[dict[str, sp.Expr], dict[str, sp.Expr]]: Two dictionaries, that relates the components to their
        voltages/currents.
    """
    voltages = {}
    currents = {}
    for component in components:
        voltages[component.name] = component.voltage
        currents[component.name] = component.current

    return voltages, currents


def find_states(components: list[Component]) -> dict[str, sp.Expr]:
    """Find the state equations that describes the circuit. It uses the voltage for capacitors and current for inductors
    as state variables.

    Args:
        components (list[Component]): List of components for the circuit

    Returns:
        dict[str, sp.Expr]: Dictionary that relates each energy storing component to its state equation. It isn't
        explicit in each value of this dict, but each expression is equal to the energy storing element's
        voltage/current derivate (for capacitors/inductors, respectively).
    """
    states = {}
    for component in components:
        match component.type:
            case "C":
                states[str(component.name)] = sp.simplify(component.current / component.value)
            case "L":
                states[str(component.name)] = sp.simplify(component.voltage / component.value)
    return states


def filter_dict_by_key_first_char(dictionary: dict[str, any], to_remove: tuple[str]):
    """Remove all items from a dict, where the first character in the key matches one of the values in a tuple.

    Args:
        values (dict[str, any]): The dictionary to remove their itens.
        to_remove (tuple[str]): The tuple to match the first character of each key with.
    """
    for key in dictionary.copy():
        if key[0] in to_remove:
            del dictionary[key]


def simplify_results(*dictionaries: list[dict[str, sp.Expr]]):
    """Simplify the sympy expressions for every value in a dictionary.

    Args:
        *dictionaries (list[dict[str, sp.Expr]]): List of dictionaries to simplify each.
    """

    for dictionary in dictionaries:
        for key in dictionary:
            dictionary[key] = sp.simplify(dictionary[key])


def solve_circuit(
    circuit: list[Component],
) -> tuple[list[Component], dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr]]:
    """_summary_

    Args:
        circuit (list[Component]): List of components for the circuit.

    Returns:
        tuple[list[Component], dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr]]: The
        system variables for the circuit, and the updated list of components (where all the attributes for current and
        voltage are set up).

    """

    circuit = equivalent_circuit.condense_circuit(circuit)
    # Set up the loop equations
    loops = find_loops(circuit)
    loop_equations = find_loop_equations(loops)

    # Set up the node equations
    node_graph = find_node_graph(circuit)
    incidence_matrix = find_incidence_matrix(node_graph)
    current_equations = find_current_equations(circuit, incidence_matrix)

    # Solves the equations
    unknowns = find_unknowns(circuit)
    equations = loop_equations + current_equations
    solutions = list(sp.linsolve(equations, *unknowns))[0]
    associate_values(circuit, solutions)

    states = find_states(circuit)

    circuit = equivalent_circuit.expand_circuit(circuit)

    component_voltages, currents = find_component_values(circuit)
    filter_dict_by_key_first_char(component_voltages, ("V", "C"))
    filter_dict_by_key_first_char(currents, ("I", "L"))

    node_breadth_sequence = nx.bfs_edges(node_graph.to_undirected(), "0")
    node_voltages = find_node_voltages(circuit, node_breadth_sequence)

    simplify_results(currents, component_voltages, node_voltages, states)

    return circuit, currents, component_voltages, node_voltages, states
