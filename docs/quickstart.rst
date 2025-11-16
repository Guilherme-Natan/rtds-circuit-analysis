Quick Start
===========

.. _create-netlist:

Create your netlist
-------------------

Before actually using this program, you will need to write the circuit you want to analise as a *netlist*.
This software uses a netlist style similar to SPICE programs, where each line corresponds to each component in the
circuit. They will be formatted like ``VIN IN 0 V``, where:

- The the first letter in the first word, ``V`` is the component type (V for voltage source, R for resistors, etc), and
  together with the other letters, ``VIN``, make up the component name. More on :ref:`here <component_names>`.
- The second and third words are the nodes the component is connected to. Their names are arbitrary, except for the node
  0, which will **always** be ground. It is also **always** necessary. More on :ref:`here <nodes>`.
- The final word will be the value for the circuit. It can be a literal (such as in this case, ``V``), a numeric value
  (like ``10k``), or a combination of both (like ``10VIN``). More on :ref:`here <component_values>`.

For example, here is a RLC circuit, and its netlist:

.. grid:: 2
    :gutter: 2

    .. grid-item::

        .. image:: _static/rlc_circuit.png
            :alt: RLC Circuit

    .. grid-item::
        :child-align: center

        .. parsed-literal::

            **V1 1 0 10
            R1 1 2 1k
            L1 2 3 100m
            C1 3 0 10u**

While simple, there are some caveats when writing the netlist for a circuit. You can read the full documentation on
netlists for this software :ref:`here <netlist-docs>`.

Usage
-----

After creating the netlist, store it into a ``netlist.cir``, and choose how you intent on using this software:

.. _cli-overview:

Command Line Interface
++++++++++++++++++++++

The basic usage for the CLI software is in the form:

.. code-block:: bash
   
    rtds-circuit-analysis netlist.cir


This will print all the solutions for the circuit (node voltages, currents, states, etc). You can use flags to filter
the output. For example, to show only the currents for each component, you can run:

.. code-block:: bash

    rtds-circuit-analysis netlist.cir -i


You can filter it even more, by giving the components/node names to the flags as parameters. So, if you want the voltage
and current for the resistor R1 only, you can run:

.. code-block:: bash

    rtds-circuit-analysis netlist.cir -v R1 -i R1

To take a look at every flag available, run the help command:

.. code-block:: bash

    rtds-circuit-analysis -h

For a more in depth explanation on how to use the command line interface, click :ref:`here <usage-cli>`.

Library
+++++++

To solve the circuit, you need to import the ``Circuit`` class, and pass the netlist as a parameter, creating a
``circuit`` object.

.. code-block:: python

    from rtds_circuit_analysis import Circuit

    circuit = Circuit("netlist.cir")

This ``circuit`` object will have all circuit solutions stored as attributes. So, for example, to find the voltage at
node "2", you can use:

.. code-block:: python

    circuit.node_voltages["2"]


You can also use the ``print`` methods to print the solutions for the circuit in a formatted manner, similar to the
:ref:`CLI <cli-overview>`. For example, to print the voltages for the components R1 and R2, you can run:

.. code-block:: python

    circuit.print_component_voltages("R1", "R2")


For a more in depth explanation on how to use the python library, click :ref:`here <usage-lib>`.

Output Examples
---------------

Some examples of the full output for some circuits and their netlists:

Voltage Divisor
+++++++++++++++

.. grid:: 2
    :gutter: 2

    .. grid-item::
        :child-align: center

        .. image:: _static/voltage_1.png
            :alt: Voltage Divisor

    .. grid-item::
        :child-align: center

        .. rubric:: Netlist:
            
        .. parsed-literal::

            **V1 IN 0 10
            R1 IN OUT 6k
            R2 OUT 0 4k**

        .. rubric:: Output:

        .. parsed-literal::

            **\*\*\* Currents \*\*\*
            V1 --> 1/1000
            R1 --> 1/1000
            R2 --> 1/1000**

            **\*\*\* Voltages (components) \*\*\*
            R1 --> 6
            R2 --> 4**

            **\*\*\* Voltages (nodes) \*\*\*
            IN --> 10
            OUT --> 4**

            **\*\*\* This circuit is stateless \*\*\***

RLC Circuit
+++++++++++

.. grid:: 2
    :gutter: 2

    .. grid-item::
        :child-align: center

        .. image:: _static/rlc_circuit.png
            :alt: RLC Circuit

    .. grid-item::
        :child-align: center

        .. rubric:: Netlist:
            
        .. parsed-literal::

            **V1 1 0 10
            R1 1 2 1k
            L1 2 3 100m
            C1 3 0 10u
            .STEP 1e-3**


        .. rubric:: Output:

        .. parsed-literal::

            **\*\*\* Currents \*\*\*
            V1 --> IL1
            R1 --> IL1
            C1 --> IL1**

            **\*\*\* Voltages (components) \*\*\*
            R1 --> 1000*IL1
            L1 --> -1000*IL1 - VC1 + 10**

            **\*\*\* Voltages (nodes) \*\*\*
            1 --> 10
            3 --> VC1
            2 --> 10 - 1000*IL1**

            **\*\*\* State equations (continuous) \*\*\*        
            dIL1/dt = -10000*IL1 - 10*VC1 + 100
            dVC1/dt = 100000*IL1**

            **\*\*\* State equations (forward) \*\*\*        
            IL1_{n} = -9*IL1_{n-1} - VC1_{n-1}/100 + 1/10
            VC1_{n} = 100*IL1_{n-1} + VC1_{n-1}**

            **\*\*\* State equations (backward) \*\*\*        
            IL1_{n} = IL1_{n-1}/12 - VC1_{n-1}/1200 + 1/120
            VC1_{n} = 25*IL1_{n-1}/3 + 11*VC1_{n-1}/12 + 5/6**

            **\*\*\* State equations (trapezoidal) \*\*\*        
            IL1_{n} = -17*IL1_{n-1}/25 - VC1_{n-1}/625 + 2/125
            VC1_{n} = 16*IL1_{n-1} + 23*VC1_{n-1}/25 + 4/5**

