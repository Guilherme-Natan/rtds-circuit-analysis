import sys
from os.path import basename, splitext
from textwrap import indent
from typing import TYPE_CHECKING

import sympy as sp

if TYPE_CHECKING:
    from argparse import Namespace

    from rtds_circuit_analysis import Circuit


def indent1(string: str) -> str:
    """Indent string one time

    Args:
        string (str): The unindented string

    Returns:
        str: The string, indented one time
    """
    return indent(string, 4 * " ")


def get_equations(circuit: "Circuit", args: "Namespace") -> dict[str, sp.Eq]:
    """Get the equations for the circuit, accordingly to the chosen method

    Args:
        circuit (Circuit): The circuit object.
        args (Namespace): The command line arguments

    Returns:
        dict[str, sp.Eq]: The dict that relates each component to its sympy equation.
    """
    # Get expression for the method chosen
    if args.forward:
        expressions = circuit.forward
    elif args.backward:
        expressions = circuit.backward
    else:
        expressions = circuit.trapezoidal

    # Generate the equations
    equations = expressions.copy()
    for component, expression in expressions.items():
        # Generates the left hand side for the equation
        lhs = component
        match lhs[0]:
            case "C":
                lhs = "V" + lhs
            case "L":
                lhs = "I" + lhs
        lhs += "_{n}"
        lhs = sp.Symbol(lhs)

        # Stores the equation in the dictionary
        equations[component] = sp.Eq(lhs, expression)

    return equations


def get_parameters(equations: dict[str, sp.Eq]) -> list[str]:
    """The parameter for the circuit, that is, the values for the resistors, capacitors and inductors that are literal,
    instead of numeric.

    Args:
        equations (dict[str, sp.Eq]): Dict that relates each component to its equation.

    Returns:
        list[str]: List of parameters, where the values for resistors comes first, then inductors, and finally
        capacitors.
    """
    # Get list of parameters from the equations (resistor, capacitor and inductors literal values)
    parameters = set()
    for equation in equations.values():
        symbols = equation.free_symbols
        parameters.update(str(symbol) for symbol in symbols if str(symbol)[0] in ("R", "C", "L"))
    parameters = list(parameters)

    # Sorts the list, r first, then l, then c
    priority_rlc = {"R": 0, "L": 1, "C": 2}
    parameters.sort(key=lambda symbol: (priority_rlc[symbol[0]], symbol))

    return parameters


def get_cpp_headers(fixed: str, point: str) -> str:
    """Layout the required information at the start of every vitis cpp file.

    Args:
        fixed (str): Number of bits the fixed point representation should have.
        point (str): Number of bits behind the point the fixed point representation should have (including the sign).

    Returns:
        str: The cpp header
    """

    return (
        "#include <ap_fixed.h>\n"
        "#include <ap_int.h>\n"
        f"typedef ap_fixed<{fixed}, {point}, AP_TRN, AP_WRAP> data_t;\n"
        "typedef ap_uint<1> uint1_t;\n"
    )


def get_cpp_parameters(parameters: list[str]) -> str:
    """Transforms the list of parameters into a list of "#define"s in cpp, so the user can manually change it later.

    Args:
        parameters (list[str]): _description_

    Returns:
        str: _description_
    """

    max_whitespaces = 1 + max(len(parameter) for parameter in parameters)
    output = "\n"
    for parameter in parameters:
        whitespaces = " " * (max_whitespaces - len(parameter))
        output += f"#define {parameter}{whitespaces}data_t(CHANGEME)\n"

    return output


def get_inputs_and_states(equations: dict[str, sp.Eq]) -> tuple[list[str], list[str]]:
    """Gets the state variables, and the inputs, that will be used in the fpga simulation.

    Args:
        equations (dict[str, sp.Eq]): The state equations for the circuit.

    Returns:
        tuple[list[str], list[str]]: The state variable, and the inputs.
    """
    # Get states
    states = [f"V{component}" if component[0] == "C" else f"I{component}" for component in equations]
    states = sorted(states)

    # Get inputs
    inputs = set()
    for equation in equations.values():
        symbols = {str(symbol) for symbol in equation.free_symbols}
        # Remove parameters and states
        symbols = {symbol for symbol in symbols if (symbol[0] in ("V", "I")) and (symbol[:2] not in ("VC", "IL"))}
        inputs.update(symbols)

    # Remove _{n} and _{n-1} from the input names. This will also deduplicate those variables in case the method chosen
    # is the trapezoidal one (there would be one variable for _{n-1}, and another for _{n}).
    inputs_no_subscripts = set()
    for i in inputs:
        if i[-4:] == "_{n}":
            i = i[:-4]
        else:
            i = i[:-6]
        inputs_no_subscripts.add(i)

    inputs = sorted(list(inputs_no_subscripts))
    return inputs, states


def define_function(filepath: str, inputs: list[str], states: list[str]) -> str:
    """Defines the function used in by the Vitis Software for the RT Simulation.

    Args:
        filepath (str): The path for the netlist file
        inputs (list[str]): The inputs for the function
        states (list[str]): The states for the function

    Returns:
        str: The statement that defines the function
    """

    # Takes only the basename (without extension) for the name for the function
    name = splitext(basename(filepath))[0]

    # Write the inputs as parameters for the function
    parsed_inputs = ""
    for i in inputs:
        parsed_inputs += f" data_t {i},"

    # Write the inputs as parameters for the function
    parsed_states = ""
    for s in states:
        parsed_states += f" data_t *{s},"

    return f"\nvoid {name}(uint1_t sinc,{parsed_inputs}{parsed_states})" + "{\n"


def define_states(states: list[str]) -> str:
    """Declares the states that will be used by Vitis.

    Args:
        states (list[str]): The states to be used.

    Returns:
        str: The declaration of the states.
    """
    code = "\n"
    for state in states:
        code += f"static data_t {state}_old = 0;\n"
        code += f"static data_t {state}_new = 0;\n"
    return code


def define_inputs(inputs):
    """Declares the "old" (n-1) inputs that will be used by Vitis. Only necessary for the forward and trapezoidal
    method.

    Args:
        inputs (list[str]): The inputs to be used.

    Returns:
        str: The declaration of the "old" inputs.
    """
    code = "\n"
    for i in inputs:
        code += f"static data_t {i}_old = 0;\n"
    return code


def pass_states_new_old(states: list[str]) -> str:
    """Sets the old calculated states

    Args:
        states (list[str]): List of states

    Returns:
        str: Code the sets the old calculated states
    """
    code = "\n"
    for state in states:
        code += f"{state}_old = {state}_new;\n"
    return code


def pass_inputs_new_old(inputs):
    """Pass the current inputs to the old ones, to be used in the next iteration. Only necessary for the forward and
    trapezoidal method.

    Args:
        inputs (list[str]): The inputs to be used.

    Returns:
        str: The code that sets the "old" inputs.
    """
    code = "\n"
    for i in inputs:
        code += f"{i}_old = {i};\n"
    return code


def python_cpp_table(variables: list[str], is_input=False) -> dict[sp.Symbol, sp.Symbol]:
    """Creates a table that relates the name of each symbol in python's sympy, to how it should be called in cpp.

    Args:
        variables (list[str]): Symbols to add to the table
        is_input (bool, optional): If the symbols are inputs. Defaults to False.

    Returns:
        dict[sp.Symbol, sp.Symbol]: The table that relates python and cpp symbols.
    """

    table = {}
    if is_input:
        new_appendix = ""
    else:
        new_appendix = "_new"

    sym = sp.Symbol
    for variable in variables:
        table[sym(variable + "_{n-1}")] = sym(variable + "_old")
        table[sym(variable + "_{n}")] = sym(variable + new_appendix)

    return table


def format_equations(equations: list[sp.Eq], states: list[str], inputs: list[str]) -> str:
    """Format the sympy equations to the cpp file format.

    Args:
        equations (list[sp.Eq]): Equations to format.
        states (list[str]): States for the circuit.
        inputs (list[str]): Inputs for the circuit.

    Returns:
        str: Formatted equations.
    """
    states_table = python_cpp_table(states)
    inputs_table = python_cpp_table(inputs, is_input=True)
    subs_table = states_table | inputs_table

    code = "\n"
    for equation in equations.values():
        equation = equation.subs(subs_table)
        code += f"{equation.lhs} = {equation.rhs}\n"

    return code


def rt_simulation(equations: list[sp.Eq], states: list[str], inputs: list[str], is_backward: bool) -> str:
    """Writes the code that is mostly responsible to simulate the circuit.

    Args:
        equations (list[sp.Eq]): State equations for the circuit.
        states (list[str]): States for the circuit.
        inputs (list[str]): Inputs for the circuit.
        is_backward (bool): If the method chosen to convert the state equations to discrete form is the backward one.

    Returns:
        str: The code that simulates the circuit.
    """
    code = "\naux_sinc = sinc;\n"

    code += pass_states_new_old(states)

    code += format_equations(equations, states, inputs)

    if not is_backward:
        code += pass_inputs_new_old(inputs)
    return code


def if_else(rt_code: str) -> str:
    """Writes the "if else" that goes inside the main function

    Args:
        rt_code (str): The code that goes inside the "else"

    Returns:
        str: The completed "if else"
    """
    code = "\n"
    code += "if(aux_sinc == sinc){\n}\n"

    code += "else{\n"
    code += indent1(rt_code)
    code += "\n}\n"
    return code


def pass_states_new_out(states: list[str]) -> str:
    """Pass the new calculated states to the pointers (the FPGA outputs)

    Args:
        states (list[str]): List of states

    Returns:
        str: Code the passes the calculated states to the pointers
    """
    code = "\n"
    for state in states:
        code += f"*{state} = {state}_new;\n"
    return code


def main_function(equations: dict[str, sp.Eq], args: "Namespace") -> str:
    """Writes the main function to be used by Vitis HLS

    Args:
        equations (dict[str, sp.Eq]): The equations to add to the function
        args (Namespace): The arguments given for rtds-vitis

    Returns:
        str: The main function
    """

    inputs, states = get_inputs_and_states(equations)

    # Starts the main function
    def_fun = define_function(args.filepath, inputs, states)

    code = "\n"
    # Define the aux_sinc, for synchronizing the FPGA simulation
    code += "static uint1_t aux_sinc;" + "\n"

    # Define the states
    code += define_states(states)

    # Define the "n-1" input variables (not necessary in the backwards method)
    if not args.backward:
        code += define_inputs(inputs)

    # Writes the code that will actually perform the RT simulation
    rt_code = rt_simulation(equations, states, inputs, args.backward)
    code += if_else(rt_code)

    # Pass the states as outputs for the FPGA
    code += pass_states_new_out(states)

    # Adds the function declaration to the code, and idents everything
    code = f"{def_fun}{indent1(code)}"

    # Closes the main function
    code += "\n}"

    return code


def print_vitis_code(circuit: "Circuit", args: "Namespace"):
    """Prints the cpp vitis code, for implementing the circuit in an FPGA.

    Args:
        circuit (Circuit): The circuit's class
        args (Namespace): The arguments for the rtds-vitis command line code
    """

    # C headers
    code = get_cpp_headers(args.fixed, args.point)

    # Find the equations that generate the circuit, and its parameters
    equations = get_equations(circuit, args)
    parameters = get_parameters(equations)

    # Generate CHANGEME data_t entries when some component values are literals
    if parameters:
        code += get_cpp_parameters(parameters)

    # Write the main function
    code += main_function(equations, args)

    # Prints resulting code
    print(code)
    if parameters:
        print(
            "\n\033[33mWARNING: Components with literal values found. You'll need to replace all the "
            "'CHANGEME's in the cpp code with their respective numeric values\033[0m",
            file=sys.stderr,
        )
