import os
from typing import TYPE_CHECKING

from rtds_circuit_analysis.diference_equations import differential_to_difference
from rtds_circuit_analysis.format_output import format_output
from rtds_circuit_analysis.parse_data import parse_data
from rtds_circuit_analysis.parse_netlist import get_lines, parse_components
from rtds_circuit_analysis.solve_circuit import solve_circuit

if TYPE_CHECKING:
    import sympy

    from rtds_circuit_analysis.parse_data import Component


class Circuit:
    """Class that represents a circuit and all its data.

    Args:
        netlist (str): The netlist for the circuit. It can be either the path for a file containing the netlist, or the
          netlist itself directly as a string.
        time_step (str, optional): Value for the time step, used in the difference state equations. It is recommended to
          pass it in exponential form (ex.: ``"2.5e-6"``) **Needs to be a string**, passing it as a float may cause
          issues. Defaults to None.

    Attributes:
        components (list[Component]): List of components for the circuit.
        currents (dict[str, sympy.Expr]): Dictionary that relates each component name to its currents. Does not include
          trivial components, which are current sources and inductors.
        component_voltages (dict[str, sympy.Expr]): Dictionary that relates each component name to its voltages. Does
          not include trivial components, which are voltage sources and capacitors.
        node_voltages (dict[str, sympy.Expr]): Dictionary that relates each node name to its voltages.
        states (dict[str, sympy.Expr]): Dictionary that relates each energy storage component to its continuous state
          equation. **It only includes the right hand side of the equation!**
        forward (dict[str, sympy.Expr]): Dictionary that relates each energy storage component to its discrete state
          equation, using the forward method. **It only includes the right hand side of the equation, WITHOUT THE
          V_{n-1} / I_{n-1} ADDED TO IT!**
        backward (dict[str, sympy.Expr]): Dictionary that relates each energy storage component to its discrete state
          equation, using the backward method. **It only includes the right hand side of the equation, WITHOUT THE
          V_{n-1} / I_{n-1} ADDED TO IT!**
        trapezoidal (dict[str, sympy.Expr]): Dictionary that relates each energy storage component to its discrete state
          equation, using the trapezoidal method. **It only includes the right hand side of the equation, WITHOUT THE
          V_{n-1} / I_{n-1} ADDED TO IT!**
        time_step (sympy.Rational | None): The time step for the circuit.
    """

    def __init__(self, netlist: str, time_step: str | None = None):
        if os.path.exists(netlist):
            netlist = get_lines(netlist)
        else:
            netlist = netlist.strip().split("\n")

        self.components, time_step = parse_components(netlist, time_step)

        self.time_step = time_step

        parse_data(self.components)

        (
            self.components,
            self.currents,
            self.component_voltages,
            self.node_voltages,
            self.states,
        ) = solve_circuit(self.components)

        if self.states:
            self.forward, self.backward, self.trapezoidal = differential_to_difference(self.states, time_step)
        else:
            self.forward = self.backward = self.trapezoidal = None

    def _formatted_components(self):
        return f'*** Components for the circuit ***\n{"\n".join(str(component) for component in self.components)}\n'

    def _formatted_currents(self, components=None):
        return f"*** Currents ***\n{format_output(self.currents, components)}"

    def _formatted_component_voltages(self, components=None):
        return f"*** Voltages (components) ***\n{format_output(self.component_voltages, components)}"

    def _formatted_node_voltages(self, nodes=None):
        return f"*** Voltages (nodes) ***\n{format_output(self.node_voltages, nodes)}"

    def _formatted_states(self, components=None):
        return f"*** State equations (continuous) ***\
        \n{format_output(self.states, components, is_state=True, lhs_is_derivative=True)}"

    def _formatted_forward(self, components=None):
        return f"*** State equations (forward) ***\
        \n{format_output(self.forward, components, is_state=True, is_discrete=True)}"

    def _formatted_backward(self, components=None):
        return f"*** State equations (backward) ***\
        \n{format_output(self.backward, components, is_state=True, is_discrete=True)}"

    def _formatted_trapezoidal(self, components=None):
        return f"*** State equations (trapezoidal) ***\
        \n{format_output(self.trapezoidal, components, is_state=True, is_discrete=True)}"

    def print_components(self):
        """Print all components for the circuit"""
        print(self._formatted_components)

    def print_currents(self, *components: "Component"):
        """Prints the current for the given components (excluding inductors and current sources, which are obvious). If
        no components are given, prints the currents for *every* component.

        Args:
            *components: List of components to get the current for. If empty, prints the currents for every component.
        """
        print(self._formatted_currents(components))

    def print_component_voltages(self, *components: "Component"):
        """Prints the voltage for the given components (excluding capacitors and voltage sources, which are obvious). If
        no components are given, prints the voltages for *every* component.

        Args:
            *components: List of components to get the voltages for. If empty, prints the voltage for every component.
        """
        print(self._formatted_component_voltages(components))

    def print_node_voltages(self, *nodes: str):
        """Prints the voltage for each node. If no nodes are given, prints the voltages for every node.

        Args:
            *nodes: List of nodes to get the voltages for. If empty, prints the voltage for every node.
        """
        print(self._formatted_node_voltages(nodes))

    def print_states(self, *components: "Component"):
        """Prints the state equations for the system (continuous).

        Args:
            *components: List of components to get the state equations for. If empty, prints all the state equations for the circuit.
        """
        print(self._formatted_states(components))

    def print_forward(self, *components: "Component"):
        """Prints the state equations for the system (forward).

        Args:
            *components: List of components to get the state equations for. If empty, prints all the state equations for the circuit.
        """
        print(self._formatted_forward(components))

    def print_backward(self, *components: "Component"):
        """Prints the state equations for the system (backward).

        Args:
            *components: List of components to get the state equations for. If empty, prints all the state equations for the circuit.
        """
        print(self._formatted_backward(components))

    def print_trapezoidal(self, *components: "Component"):
        """Prints the state equations for the system (trapezoidal).

        Args:
            *components: List of components to get the state equations for. If empty, prints all the state equations for the circuit.
        """
        print(self._formatted_trapezoidal(components))

    def print_all(self):
        """Prints all the info related to the `circuit` object."""
        self.print_currents()
        self.print_component_voltages()
        self.print_node_voltages()
        if self.states:
            self.print_states()
            self.print_forward()
            self.print_backward()
            self.print_trapezoidal()
        else:
            print("*** This circuit is stateless ***")
            print("")

    def __str__(self):
        return f"""{self._formatted_components()}
{self._formatted_currents()}
{self._formatted_component_voltages()}
{self._formatted_node_voltages()}
{self._formatted_states()}
{self._formatted_forward()}
{self._formatted_backward()}
{self._formatted_trapezoidal()}"""

    def __repr__(self):
        return f"""Circuit(
components={str(self.components)},
node_voltages={self.node_voltages},
currents={self.currents},
component_voltages={self.component_voltages},
states={self.states}
forward={self.forward}
backward={self.backward}
trapezoidal={self.trapezoidal}
)
"""
