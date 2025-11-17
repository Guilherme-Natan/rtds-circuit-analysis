# RTDS Circuit Analysis

RTDS Circuit Analysis is a Python software for solving electrical circuits, when given their [netlist](#netlist). It
accepts literal values for each component value (such as `Vin` for the voltage for a source), and output the solutions
as mathematical expressions/equations, based upon these literal values.

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
circuit. They will be formatted like `VIN IN 0 V`, where:
- The the first letter in the first word, `V` is the component type (V for voltage source, R for resistors, etc), and
  together with the other letters, `VIN`, make up the component name.
- The second and third words are the nodes the component is connected to. Their names are arbitrary, except for the node
  0, which will **always** be ground. It is also **always** necessary.
- The final word will be the value for the circuit. It can be a literal (such as in this case, `V`), a numeric value
  (like `10k`), or a combination of both (like `10VIN`).

For more info on how to write your netlists, check out [here](https://rtds-circuit-analysis.readthedocs.io/en/stable/netlists.html)

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

For more info on how to use the cli, check out [here](https://rtds-circuit-analysis.readthedocs.io/en/stable/cli.html)

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

For more info on how to use the library, check out [here](https://rtds-circuit-analysis.readthedocs.io/en/stable/library.html)

## Output Examples

Some examples of the full output for some circuits and their netlists:

### Voltage Divisor

#### Circuit

![rlc_circuit](https://raw.githubusercontent.com/Guilherme-Natan/rtds-circuit-analysis/refs/heads/main/docs/_static/voltage_1.png)

#### Netlist

```
V1 IN 0 10
R1 IN OUT 6k
R2 OUT 0 4k
```

#### Output

```
*** Currents ***

V1 --> 1/1000
R1 --> 1/1000
R2 --> 1/1000

*** Voltages (components) ***
R1 --> 6
R2 --> 4

*** Voltages (nodes) ***
IN --> 10
OUT --> 4

*** This circuit is stateless ***
```

### RLC Circuit

#### Circuit

![rlc_circuit](https://raw.githubusercontent.com/Guilherme-Natan/rtds-circuit-analysis/refs/heads/main/docs/_static/rlc_circuit.png)

#### Netlist

```
V1 1 0 10
R1 1 2 1k
L1 2 3 100m
C1 3 0 10u
.STEP 1e-3
```

#### Output

```
*** Currents ***
V1 --> IL1
R1 --> IL1
C1 --> IL1

*** Voltages (components) ***
R1 --> 1000*IL1
L1 --> -1000*IL1 - VC1 + 10

*** Voltages (nodes) ***
1 --> 10
3 --> VC1
2 --> 10 - 1000*IL1

*** State equations (continuous) ***        
dIL1/dt = -10000*IL1 - 10*VC1 + 100
dVC1/dt = 100000*IL1

*** State equations (forward) ***        
IL1_{n} = -9*IL1_{n-1} - VC1_{n-1}/100 + 1/10
VC1_{n} = 100*IL1_{n-1} + VC1_{n-1}

*** State equations (backward) ***        
IL1_{n} = IL1_{n-1}/12 - VC1_{n-1}/1200 + 1/120
VC1_{n} = 25*IL1_{n-1}/3 + 11*VC1_{n-1}/12 + 5/6

*** State equations (trapezoidal) ***        
IL1_{n} = -17*IL1_{n-1}/25 - VC1_{n-1}/625 + 2/125
VC1_{n} = 16*IL1_{n-1} + 23*VC1_{n-1}/25 + 4/5
```

For more info on how to interpret the solutions, check out
[here](https://rtds-circuit-analysis.readthedocs.io/en/stable/solutions.html)
