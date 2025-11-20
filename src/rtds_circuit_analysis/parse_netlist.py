"""Functions related to extracting and parsing data from a netlist"""

import re

import sympy as sp

from rtds_circuit_analysis.utils import error_message


class Component:
    """Represents a component in a circuit. Mostly for internal use, although you can use it to extract the voltage and
    current directly from a component.

    Attributes:
        name (str): The name of the component.
        type (str): What type the component is ("V" for voltage sources, "R" for resistors, etc)
        nodes (tuple[str]): The two nodes the component is connected to, in order
        value (sympy.Rational | sympy.Symbol): The value for the component (Volts for voltage sources, Ohms for
          resistors, etc)
        current: The current calculated for the component
        voltage: The voltage calculated for the component
    """

    def __init__(self, name: str, nodes: tuple[str], value: sp.Rational | sp.Symbol):
        self.name = name
        self.type = name[0]
        self.nodes = nodes
        # Strings beginning with "_" are the unknowns for the equations
        match self.type:
            case "V":
                self.value = self.voltage = value
                self.current = sp.Symbol(f"_I{self.name}")
            case "I":
                self.value = self.current = value
                self.voltage = sp.Symbol(f"_V{self.name}")
            case "C":
                self.voltage = sp.Symbol(f"V{self.name}")
                self.current = sp.Symbol(f"_I{self.name}")
                self.value = value
            case "L":
                self.current = sp.Symbol(f"I{self.name}")
                self.voltage = sp.Symbol(f"_V{self.name}")
                self.value = value
            case "R":
                self.voltage = None
                self.current = sp.Symbol(f"_I{self.name}")
                self.value = value

    def __str__(self):
        if self.type == "short":
            return f"Short, that connect the nodes {self.nodes[0]} and {self.nodes[1]}"

        component_type_table = dict(
            zip("VICLR", ("Voltage Source", "Current Source", "Capacitor", "Inductor", "Resistor"))
        )
        return (
            f"{component_type_table[self.type]} {self.name}, connected to the nodes "
            f"{self.nodes[0]} and {self.nodes[1]}, with value of {self.value}"
        )

    def __repr__(self):
        if self.type == "short":
            return f"Component(Short (originally {self.name}), {self.nodes})"
        return f"Component({self.name}, {self.nodes}, {self.value})"


def parse_value(value: str) -> sp.Expr:
    """Parse the value as a number, symbol, or expression.

    It follows the following logic:
        - Integers and decimal numbers become Sympy Rationals
        - Words that begin with letters become Sympy Symbols
        - Words that begin with numbers (but have letters in it) become a product of the number (as a Sympy
          Integer/Rational), and a Sympy Symbol (example: 2R1 -> 2 * R1)
        - Numbers with SI prefixes are converted accordingly (example: 1K -> 1000)

    Args:
        value (str): The unparsed value.

    Returns:
        sp.Expr: The parsed value, generically a Sympy Expression.
    """
    # If it begins with a letter, returns it as a Sympy Symbol
    if value[0].isalpha():
        return sp.Symbol(value)

    # Splits the value between the number part, and the rest (including SI prefix)
    match = re.search(r"[\d\.\-+eE]+", value)
    value_number_part = match.group(0)
    value_rest = value[match.end(0) :]
    if value_number_part == "-":
        value_number_part = "-1"

    # Convert SI prefix to number, if it is present
    si_prefix_exp_table = dict(zip("pnμumkKMGT", (-12, -9, -6, -6, -3, 3, 3, 6, 9, 12)))
    si_multiplier = sp.Integer(1)
    if value_rest and value_number_part != "-1" and value_rest[0] in si_prefix_exp_table:
        si_exp = sp.Rational(si_prefix_exp_table[value_rest[0]])
        si_multiplier = sp.Rational(10**si_exp)
        value_rest = value_rest[1:]

    if not value_rest:
        return sp.Rational(value_number_part) * si_multiplier
    return sp.Rational(value_number_part) * si_multiplier * sp.Symbol(value_rest)


def get_lines(file_name: str) -> list[str]:
    """Reads the netlist file, and saves each relevant line in a list.

    This function ignores the following lines:
    - Lines beginning with *
    - Empty lines

    Args:
        file_name (str): Netlist file path.

    Returns:
        list[str]: List of relevant lines.
    """
    with open(file_name, "r", encoding="utf-8") as f:
        spice_file = f.readlines()
        lines = []
        for line in spice_file:
            line = line.strip()
            if not line or line[0] == "*":  # Removes comments and empty lines
                continue
            lines.append(line)
        return lines


def separate_line(line: str, num: int) -> tuple[str]:
    """Separates the line in words, and check if they match a predetermined value. If they don't, show an error message
    and quit the program.

    Args:
        line (str): The line to separate
        num (int): The number of words the line should be separated in.

    Returns:
        tuple[str]: The words for the line
    """
    words = re.split(r"\s+", line)
    if len(words) != num:
        error_message(f"Line '{line}' was supposed to have {num} words, got {len(words)} instead.")
    return words


def parse_components(lines: list[str], time_step: None | str) -> tuple[list[Component], bool]:
    """Turn the lines into component objects.

    Args:
        lines (list[str]): Lines from the .cir file.

    Returns:
        tuple[list[Component], bool]: List of Component objects, and possibly the time step for the circuit (if there is
        a .STEP line in the netlist)
    """
    components = []
    possible_time_step = None
    for line in lines:
        if len(line) >= 5 and line[:5].upper() == ".STEP":
            _, possible_time_step = separate_line(line, 2)
            continue
        name, node1, node2, value = separate_line(line, 4)
        name, node1, node2 = map(lambda x: x.upper(), (name, node1, node2))
        component = Component(name, (node1, node2), parse_value(value))
        components.append(component)

    if time_step:
        time_step = parse_value(time_step)
    if possible_time_step:
        time_step = parse_value(possible_time_step)

    return components, time_step
