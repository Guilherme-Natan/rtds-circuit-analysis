.. _usage-cli:

Command line interface (CLI)
============================

You can analyze a circuit using the ``rtds-circuit-analysis`` command on the terminal. Some basic examples on how to use
this program are found in the :ref:`quickstart section <cli-overview>`.

All other relevant information can be found by running the ``rtds-circuit-analysis -h`` help command. Below is a copy of
this command's output. There are some :ref:`small caveats <cli-caveats>` you should keep in mind when writing the commands.
The rules for writing this are the same ones for writing the
:ref:`component values <component_values>`.

.. _cli-help:

----

.. argparse::
   :module: rtds_cli.create_parser
   :func: create_parser
   :prog: rtds-circuit-analysis

   -T --time-step
      The rules for writing the time step are the same ones for writing the :ref:`component values <component_values>`.

----

   
.. _cli-caveats:

Caveats
-------

- The options must always be written after the netlist file path, never before. So, ``rtds-circuit-analysis -v
  circuit.cir`` won't work, run ``rtds-circuit-analysis circuit.cir -v`` instead.
- Due to limitations of python's argparse library, you can't concatenate flags together in a single dash. So, things
  like ``rtds-circuit-analysis circuit.cir -ivn`` for printing all component currents, component voltages and node
  voltages won't work. Instead, write the flags separately, like ``rtds-circuit-analysis circuit.cir -i -v -n``.
- If you write multiple flags for the circuit, the information will be printed always in the same order (currents,
  component voltage, node voltage, continuous states, forward, backward and trapezoidal), **regardless** of the flags
  positions. So, ``rtds-circuit-analysis circuit.cir -n -i`` will print out the current first, even if ``-n`` was
  written before.
