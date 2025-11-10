"""Functions related to converting differential equations to difference equations"""

from dataclasses import dataclass
from typing import Callable

import sympy as sp


@dataclass
class DifferenceEquations:
    """Class to store the difference equations for the circuit, in their implicit form."""

    forward: list[sp.Eq]
    backward: list[sp.Eq]
    trapezoidal: list[sp.Eq]


@dataclass
class DifferenceSolution:
    """The solutions for each difference method."""

    forward: dict[str, sp.Eq]
    backward: dict[str, sp.Eq]
    trapezoidal: dict[str, sp.Eq]


@dataclass
class Symbols:
    """Symbols that correspond to values that vary with time within a circuit. In their differential form, and in their
    equivalent difference form.
    """

    continuous: list[sp.Expr]
    discrete_equivalent: list[sp.Expr]


def forward(continuous_symbols: sp.Symbol) -> list[sp.Symbol]:
    """Transform a symbol in continuous form to its difference form, using the forward method.

    Args:
        continuous_symbols (sp.Symbol): Symbol in continuous form.

    Returns:
        list[sp.Symbol]: Symbol in difference form.
    """

    return sp.Symbol(str(continuous_symbols) + "_{n-1}")


def backward(continuous_symbols: sp.Symbol) -> list[sp.Symbol]:
    """Transform a symbol in continuous form to its difference form, using the backward method.

    Args:
        continuous_symbols (sp.Symbol): Symbol in continuous form.

    Returns:
        list[sp.Symbol]: Symbol in difference form.
    """
    return sp.Symbol(str(continuous_symbols) + "_{n}")


def trapezoidal(continuous_symbols: sp.Symbol) -> list[sp.Expr]:
    """Transform a symbol in continuous form to its difference form, using the trapezoidal method.

    Args:
        continuous_symbols (sp.Symbol): Symbol in continuous form.

    Returns:
        list[sp.Expr]: Expression in difference form.
    """
    return (forward(continuous_symbols) + backward(continuous_symbols)) / 2


def convert_to(
    discrete_method: Callable, variable: str, continuous_expression: sp.Expr, time_step: str | None
) -> sp.Eq:
    """Convert a state equation in differential form, to its respective difference form.

    Args:
        discrete_method (Callable): The method to use for the transform.
        variable (str): The variable related to the component's equation, in differential form.
        continuous_expression (sp.Expr): The variable's expression, in continuous form, related to the "right hand side"
        of the state equation.
        time_step (str | None): The time step for the circuit. If it is None, the expressions will receive the
        time step as a "Ts" sympy symbol.

    Returns:
        sp.Eq: The state equation in difference form.
    """
    # Get the symbols for the expression
    symbols = Symbols(list(continuous_expression.free_symbols), [])

    # Keep only the symbols that vary with time (voltages and currents, symbols that begin with V or I)
    symbols_filtered = []
    for symbol in symbols.continuous:
        if str(symbol)[0] in ("V", "I"):
            symbols_filtered.append(symbol)
    symbols.continuous = symbols_filtered

    # Finds the equivalent form of each continuous symbol for the discrete method used
    for symbol in symbols.continuous:
        symbols.discrete_equivalent.append(discrete_method(symbol))

    # Substitutes the discrete symbols in the continuous expression
    discrete_expression = continuous_expression
    for symbol_continuous, symbol_discrete in zip(symbols.continuous, symbols.discrete_equivalent):
        discrete_expression = discrete_expression.subs(symbol_continuous, symbol_discrete)

    # Returns the equation
    new_value, old_value = sp.Symbol(variable + "_{n}"), sp.Symbol(variable + "_{n-1}")
    if not time_step:
        time_step = sp.Symbol("Ts")
    else:
        time_step = sp.Rational(time_step)
    return sp.Eq(new_value, old_value + time_step * discrete_expression)


def keys_to_string(dictionary: dict) -> dict:
    """Transforms every key in a dictionary to a string.

    Args:
        dictionary (dict): Dictionary to transform

    Returns:
        dict: Dictionary, with its keys as strings.
    """
    return {str(k): v for k, v in dictionary.items()}


def variable_to_component(solutions: dict[str, sp.Expr]) -> dict[str, sp.Expr]:
    """Extracts the name of the capacitor/inductor from their voltage/current literal values. This is done by simply
    removing the first letter (V or I), and the last four character (_{n}) from the string.

    Args:
        solutions (dict[str, sp.Expr]): A dictionary, where the keys are the components state variables.

    Returns:
        dict[str, sp.Expr]: A dictionary, where the keys are the component names.
    """
    # By removing the first and 4 last letters from the variable name, the component is extracted
    return {variable[1:-4]: expression for variable, expression in solutions.items()}


def symbol_to_component(solutions: dict[sp.Symbol, sp.Expr]) -> dict[str, sp.Expr]:
    """Transforms the keys for the solutions dictionary from sympy symbols to the component names they relate to.

    Args:
        solutions (dict[sp.Symbol, sp.Expr]): The dictionary, where its keys are sympy symbols.

    Returns:
        dict[str, sp.Expr]: Dictionary, with keys related to the component names.
    """
    solutions = keys_to_string(solutions)
    return variable_to_component(solutions)


def convert_explicit(
    discrete_method: Callable,
    states_continuous: list[sp.Expr],
    to_solve_for: list[sp.Expr],
    time_step: str | None,
) -> dict[str, sp.Expr]:
    """Convert the state equations in continuous form into their (explicit) discrete form.

    Args:
        discrete_method (Callable): The method to use for the transform.
        states_continuous (list[sp.Expr]): The state equations for the circuit, in continuous form.
        to_solve_for (list[sp.Expr]):
        time_step (str | None): The time step for the circuit. If it is None, the expressions will receive the
        time step as a "Ts" sympy symbol.

    Returns:
        dict[str, sp.Expr]: The state equations for the chosen method
    """
    # Get the diference equations (implicit form)
    difference_equations = []
    for variable, state_expression in states_continuous.items():
        difference_equations.append(convert_to(discrete_method, variable, state_expression, time_step))

    # Turn them into their explicit form
    solutions = sp.solve(difference_equations, to_solve_for)

    # Turn the keys in the solutions dictionaries
    return symbol_to_component(solutions)


def differential_to_difference(
    states_continuous: list[sp.Expr], time_step: str | None = None
) -> tuple[dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr]]:
    """Transform the state equations in continuous form in the circuit, into their difference form, for the forward,
    backward and trapezoidal methods.

    Args:
        states_continuous (list[sp.Expr]): List of differential equations.
        time_step (str | None): The time step for the circuit. If it is None, the expressions will receive the
        time step as a "Ts" sympy symbol.


    Returns:
        tuple[dict[str, sp.Expr], dict[str, sp.Expr], dict[str, sp.Expr]]: State equations in differential form,
        for various methods.
    """
    # Turn the keys from the component name to the variable related to this component.
    states_continuous_variables = {}
    for component, expression in states_continuous.items():
        match component[0]:
            case "C":
                component = "V" + component
            case "L":
                component = "I" + component
        states_continuous_variables[component] = expression
    states_continuous = states_continuous_variables

    # Extract the symbols
    to_solve_for = []
    for variable in states_continuous:
        to_solve_for.append(sp.Symbol(variable + "_{n}"))

    # Get the difference equations for each method
    forward_solutions = convert_explicit(forward, states_continuous, to_solve_for, time_step)
    backward_solutions = convert_explicit(backward, states_continuous, to_solve_for, time_step)
    trapezoidal_solutions = convert_explicit(trapezoidal, states_continuous, to_solve_for, time_step)

    return forward_solutions, backward_solutions, trapezoidal_solutions
