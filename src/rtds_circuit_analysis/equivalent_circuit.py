"""Functions related to assembling and disassembling equivalent capacitors/inductors"""

from collections import Counter, defaultdict
from copy import deepcopy
from typing import DefaultDict, ValuesView

import sympy as sp

from rtds_circuit_analysis.parse_netlist import Component
from rtds_circuit_analysis.utils import flatten


class EquivalentComponent(Component):
    """Represents an equivalent component (capacitor or inductor)"""

    def __init__(self, components, directions, equivalent_value):
        self.originals = components
        self.inverted_flags = directions
        super().__init__(components[0].name, components[0].nodes, equivalent_value)

    def __str__(self):
        component_type_table = dict(zip("CL", ("Capacitor", "Inductor")))
        return (
            f"Equivalent {component_type_table[self.type]}, made up originally of the components "
            f"{', '.join([i.name for i in self.originals])}, connected to the nodes "
            f"{self.nodes[0]} and {self.nodes[1]}, with value of {self.value}"
        )

    def __repr__(self):
        return (
            f"EquivalentComponent({self.name}, {self.nodes}, {self.value}, {[i.name for i in self.originals]}, "
            f"{self.inverted_flags})"
        )


def sorted_components(components_groups: ValuesView[list[Component]]) -> list[list[Component]]:
    """Sorts components based on their name, alphabetically

    Args:
        components_groups (ValuesView[list[Component]]): Multiple groups of components, to sort individually

    Returns:
        list[list[Component]]: Sorted groups of components
    """
    sorted_components_groups = []
    for components in components_groups:
        sorted_components_groups.append(sorted(components, key=lambda component: component.name))
    return sorted_components_groups


def equivalent_components(
    components_groups: list[list[Component]], directions_groups: list[list[bool]]
) -> list[EquivalentComponent]:
    """Give multiple groups of components and their directions, return their equivalent components

    Args:
        components_groups (list[list[Component]]): Groups of multiple components
        directions_groups (list[list[bool]]): Their directions

    Returns:
        list[EquivalentComponent]: List of equivalent components
    """
    equivalent_comps = []
    for components, directions in zip(components_groups, directions_groups):
        value = sum(i.value for i in components)
        equivalent_comps.append(EquivalentComponent(components, directions, value))
    return equivalent_comps


def remove_originals(
    circuit: list[EquivalentComponent | Component], equivalent_comps: list[EquivalentComponent]
) -> list[Component | EquivalentComponent]:
    """Removes all the original components that make up an equivalent component, from a list of components

    Args:
        circuit (list[Component]): The list to have its components removed
        equivalent_comps (list[EquivalentComponent]): The equivalent components

    Returns:
        list[Equivalent | Component]: List without the original components
    """
    for equivalent_component in equivalent_comps:
        for original in equivalent_component.originals:
            circuit.remove(original)
        circuit.append(equivalent_component)
    return circuit


def find_equivalent_capacitors(circuit: list[EquivalentComponent | Component]) -> list[Component | EquivalentComponent]:
    """Finds all the capacitors that are in parallel in a circuit, and condenses them to a single equivalent capacitor.

    Args:
        circuit (list[EquivalentComponent  |  Component]): List of the original components.

    Returns:
        list[Component | EquivalentComponent]: List of the components, with the capacitors in parallel turned into a
        single capacitor.
    """

    def find_capacitors_for_each_nodes(circuit: list[Component]) -> DefaultDict[tuple[str], list[Component]]:
        """Given a list of components, returns a dictionary that relates a pair of nodes as the key, and a list of
        capacitors connected to these nodes as the value.

        Args:
            circuit (list[Component]): List of components.

        Returns:
            DefaultDict[tuple[str], list[Component]]: Dictionary that relates the nodes and the capacitors.
        """

        capacitors_for_each_nodes = defaultdict(list)
        for component in circuit:
            if component.type == "C":
                capacitors_for_each_nodes[tuple(sorted(component.nodes))].append(component)
        return capacitors_for_each_nodes

    def remove_non_parallel_capacitors(
        capacitors_for_each_nodes: DefaultDict[tuple[str], list[Component]],
    ) -> DefaultDict[tuple[str], list[Component]]:
        """Removes all capacitors that does not have any capacitor in parallel to itself.

        Args:
            capacitors_for_each_nodes (DefaultDict[tuple[str], list[Component]]): Dictionary that relates the nodes and
            the capacitors.

        Returns:
            DefaultDict[tuple[str], list[Component]]: Dictionary, with nodes related to a single capacitor removed.
        """
        for nodes in list(capacitors_for_each_nodes):
            if len(capacitors_for_each_nodes[nodes]) == 1:
                del capacitors_for_each_nodes[nodes]
        return capacitors_for_each_nodes

    def get_directions_relative_to_first(capacitors_groups: list[list[Component]]) -> list[list[bool]]:
        """For each group of capacitors in parallel, returns a list of booleans, that tells if each capacitor is
        inverted in relation to the first.

        For a capacitor to be considered inverted, the nodes in the netlist for two capacitors must be the same ones,
        but inverted. For example, for:
        C1 1 2 C1
        C2 2 1 C2
        C3 1 2 C3
        Assuming the first capacitor is C1, the list would be [False, True, False], since only the second capacitor have
        its nodes swapped.

        Args:
            capacitors_groups (list[list[Component]]): A list of groups of capacitors in parallel

        Returns:
            list[list[bool]]: A list of groups of directions
        """
        directions = []
        for capacitors in capacitors_groups:
            reference_nodes = capacitors[0].nodes
            directions.append([(capacitor.nodes != reference_nodes) for capacitor in capacitors])
        return directions

    capacitors_for_each_nodes = find_capacitors_for_each_nodes(circuit)
    capacitors_for_each_nodes = remove_non_parallel_capacitors(capacitors_for_each_nodes)
    capacitors_groups = sorted_components(capacitors_for_each_nodes.values())  # Returns a list
    directions_groups = get_directions_relative_to_first(capacitors_groups)
    equivalent_capacitors = equivalent_components(capacitors_groups, directions_groups)
    circuit = remove_originals(circuit, equivalent_capacitors)
    return circuit


def find_equivalent_inductors(circuit: list[Component]) -> list[EquivalentComponent | Component]:
    """Finds all the inductors that are in series in a circuit, and condenses them to a single equivalent inductor.

    Args:
        circuit (list[Component]): List of the original components.

    Returns:
        list[Component | EquivalentComponent]: List of the components, with the inductors in series turned into a
        single inductor.
    """

    def find_adjacent_component_and_node(node: str, circuit: list[Component]) -> tuple[Component, str]:
        """Finds a component that is connected to a certain node, and the other node this component is connected to.

        Args:
            node (str): The node to find the component connected to
            circuit (list[Component]): List of components

        Returns:
            tuple[Component, str]: The component connect to the node, and the other node for the component
        """
        for component in circuit:
            if node in component.nodes:
                nodes = component.nodes
                other_node = nodes[1] if nodes[0] == node else nodes[0]
                return component, other_node

    def series_inductors_branch(
        node: str, external_nodes: list[str], circuit: list[Component]
    ) -> tuple[list[Component], list[Component], list[bool]]:
        """Starting from a certain external node, find a branch (sequence of components that starts and ends in an
        external node), and get the sequence of inductors in it, if any.

        Args:
            node (str): The starting external node
            external_nodes (list[str]): List of external nodes
            circuit (list[Component]): List of components for the circuit

        Returns:
            tuple[list[Component], list[Component], list[bool]]: A tuple containing the list of components in the
            branch, the list of inductors in this branch, and the list of directions of each inductor, in relationship
            to the first.
        """
        circuit = circuit.copy()

        branch = []
        inductors = []
        directions = []
        while True:
            component, adjacent_node = find_adjacent_component_and_node(node, circuit)
            # The directions tells us if the component is placed "along" the branch
            direction = adjacent_node == component.nodes[1]

            branch.append(component)
            if component.type == "L":
                inductors.append(component)
                directions.append(direction)

            # Removes the passed through component (so the next node doesn't become the same as the last one)
            circuit.remove(component)

            if adjacent_node in external_nodes:
                break
            node = adjacent_node

        # The elements of series_directions are True if their directions are opposite to the first inductor. Since the
        # first inductor is always in the same direction as itself, it should always be False. Since it is possible that
        # the first inductor direction is True, due to the way that the while loop in this function works (only the
        # first element in the branch is always False, and it might not be the inductor), the next lines of code is
        # necessary to ensure that the first one is always False Also, all the following inductors directions should be
        # reversed in that case, to keep the direction order.
        if directions and directions[0]:
            directions = [not i for i in directions]

        return branch, inductors, directions

    def series_inductors(circuit: list[Component]) -> tuple[list[list[Component]], list[list[bool]]]:
        """Finds groups of inductors in parallel, and their directions related to the first.

        Args:
            circuit (list[Component]): List of components for the circuit.

        Returns:
            tuple[list[list[Component]], list[list[bool]]]: Groups of inductors in parallel, and their directions
            related to the first.
        """
        node_list = flatten(component.nodes for component in circuit)
        # External nodes: Nodes with three or more connections (beginnings of branches), or just one node ("terminals")
        external_nodes = [i for i in Counter(node_list) if Counter(node_list)[i] != 2]

        # If there isn't a single external node, the first node is arbitrarily set as the external node
        if not external_nodes:
            external_nodes.append(node_list[0])

        inductor_groups = []
        directions = []
        for node in external_nodes:
            while any(node in component.nodes for component in circuit):
                branch, inductors_in_series, series_directions = series_inductors_branch(node, external_nodes, circuit)
                circuit = [i for i in circuit if i not in branch]
                if len(inductors_in_series) > 1:
                    inductor_groups.append(inductors_in_series)
                    directions.append(series_directions)
        return inductor_groups, directions

    inductors_in_series_groups, directions_groups = series_inductors(circuit)
    for inductors_in_series, directions in zip(inductors_in_series_groups, directions_groups):
        # For this loop, the first inductor is turned into an equivalent component, and all the others are turned into shorts
        circuit.remove(inductors_in_series[0])
        for inductor in inductors_in_series[1:]:
            circuit.remove(inductor)
            inductor = deepcopy(inductor)
            inductor.type = "short"
            inductor.voltage = 0
            inductor.current = sp.Symbol(f"_I{inductor.name}")
            circuit.append(inductor)

        equivalent_inductance = sum(i.value for i in inductors_in_series)
        equivalent_inductor = EquivalentComponent(inductors_in_series, directions, equivalent_inductance)
        circuit.append(equivalent_inductor)
    return circuit


def condense_circuit(circuit: list[Component]) -> list[Component | EquivalentComponent]:
    """Replaces every group of capacitors in parallel and inductors in series with an equivalent component.

    Args:
        circuit (list[Component]): List of every component for the circuit

    Returns:
        list[Component | EquivalentComponent]: List of components for the circuit, with capacitors in parallel and
        inductors in series replaced with their equivalent counterparts
    """
    circuit = find_equivalent_capacitors(circuit)
    circuit = find_equivalent_inductors(circuit)

    return circuit


def expand_circuit(circuit: list[Component | EquivalentComponent]) -> list[Component]:
    """Replaces every equivalent component in the circuit with their original counterparts.

    Args:
        circuit (list[Component  |  EquivalentComponent]): List of components, with some equivalent components still.

    Returns:
        list[Component]: List of components, with all the original components already in place.
    """

    def expand_component(equivalent_component: EquivalentComponent) -> list[Component]:
        """Given an equivalent component, returns its original components.

        Also, calculates the voltages and currents for each one of the original components, based on the values for the
        equivalent component.

        Args:
            equivalent_component (EquivalentComponent): The equivalent component

        Returns:
            list[Component]: List of the original components.
        """
        originals = []
        for component, inverted_flag in zip(equivalent_component.originals, equivalent_component.inverted_flags):
            if equivalent_component.type == "L":
                component.current = equivalent_component.current
                component.voltage = equivalent_component.voltage * component.value / equivalent_component.value
            elif equivalent_component.type == "C":
                component.voltage = equivalent_component.voltage
                component.current = equivalent_component.current * component.value / equivalent_component.value

            if inverted_flag:
                component.voltage *= -1
                component.current *= -1

            originals.append(component)

        return originals

    circuit = [i for i in circuit if i.type != "short"]
    equivalent_comps = [component for component in circuit if isinstance(component, EquivalentComponent)]
    for component in equivalent_comps:
        originals = expand_component(component)

        circuit.remove(component)
        circuit.extend(originals)

    return circuit
