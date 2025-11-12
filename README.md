# RTDS Circuit Analysis

RTDS Circuit Analysis is a Python software for solving electrical circuits, when given their [netlist](#netlist).

## Installation

If you plan on using the [command line interface](#command-line-interface) for this software, you can use
[pipx](https://github.com/pypa/pipx) for this:

```bash
pipx install rtds-circuit-analysis
```

If you want to use the [library](#library), however, you might prefer using [pip](https://pip.pypa.io/en/stable/) for the installation:
```bash
pip install rtds-circuit-analysis
```

## Netlist

Before actually [using](#usage) this program, you will need to write the circuit you want to analise as a *netlist*.
This software uses a netlist style similar to SPICE programs, where each line corresponds to each component in the
circuit. They will be formatted like `Vin in 0 V`, where:
- The the first letter in the first word, `V` is the component type (V for voltage source, R for resistors, etc), and
  together with the other letters, `Vin`, make up the component name.
- The second and third words are the nodes the component is connected to. Their names are arbitrary, except for the node
  0, which will **always** be ground. It is also **always** necessary.
- The final word will be the value for the circuit. It can be a literal (such as in this case, `V`), a numeric value
  (like `10k`), or a combination of both (like `10Vin`).

<!-- TODO: Link to the sphinx section about netlists here -->

For example, here is a basic RLC circuit...

![rlc_circuit](https://raw.githubusercontent.com/Guilherme-Natan/rtds-circuit-analysis/refs/heads/main/docs/_static/rlc_circuit.png)

... and its netlist representation:
```
V1 1 0 10
R1 1 2 1k
L1 2 3 100m
C1 3 0 10u
```

## Usage

After creating the netlist, store it into a `netlist.cir`, and choose how you intent on using this software:

### Command Line Interface

The basic usage for the CLI software is in the form:

```bash
rtds-circuit-analysis netlist.cir
```

This will print all the solutions for the circuit (node voltages, currents, states, etc). You can use flags to filter
the output. For example, to show only the currents for each component, you can run:

```bash
rtds-circuit-analysis netlist.cir -i
```

You can filter it even more, by giving the components/node names to the flags as parameters. So, if you want the voltage
and current for the resistor R1 only, you can run:

```bash
rtds-circuit-analysis netlist.cir -v R1 -i R1
```

To take a look at every flag available, run the help command:

```bash
rtds-circuit-analysis -h
```

<!-- TODO: Link the section about the cli in the sphinx docs here -->

### Library

To solve the circuit, you need to import the `Circuit` class, and pass the netlist as a parameter, creating a `circuit`
object.

```python
from rtds_circuit_analysis import Circuit

circuit = Circuit("netlist.cir")
```

This `circuit` object will have all circuit solutions stored as attributes. So, for example, to find the voltage at node
"2", you can use:

```python
circuit.node_voltages["2"]
```

You can also use the `print` methods to print the solutions for the circuit in a formatted manner, similar to the
[CLI](#command-line-interface). For example, to print the voltages for the components R1 and R2, you can run:

```python
circuit.print_component_voltages("R1", "R2")
```

<!-- TODO: Link the section about the library in the sphinx docs here -->
