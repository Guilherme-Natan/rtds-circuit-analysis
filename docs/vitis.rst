Vitis HLS Code Generation
=========================

If you want to implement the generated difference equations in a FPGA, to perform a real time simulation, you might
want to use `Vitis HLS
<https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vitis/vitis-hls.html>`_. With this software, you can
write the code for the real time simulation in C++, instead of Verilog or VHDL.

The ``rtds-vitis`` cli utility provides a way to automatically create the .cpp file necessary for Vithis HLS to perform
the implementation. Like the :ref:`rtds-circuit-analysis <usage-cli>` cli utility, it takes a netlist as an input. Some
things to keep in mind when writing the netlist for this software:

- The literal values of the voltage/current sources in the netlist will be considered the inputs for the FPGA
- The state variables (capacitor voltages and inductor currents) will be the outputs for the FPGA
- Any literal value for passive components in the netlist will create a "CHANGEME" entry in the cpp code, that you
  manually need to change to the numeric value for the components (using exponential notation, e.g. "5.7e3"), before
  actually synthesizing the code with Vitis HLS.
- The "top function" name will be the name for the netlist's file, without the extension (example: The top function
  name for ``rlc_circuit.cir`` will be ``rlc_circuit``)
      - The "top function" is the function you will want to choose when creating the Vitis HLS project
        
.. admonition:: Saving to a file
   :class: tip

   This utility prints the output directly to the terminal. If you want to save the output to a file, use can use the
   ">" output redirect operator. 
   
   For example:

   .. code-block::

      rtds-vitis circuit.cir -T 1e-6 -F 32 -P 8 -f > circuit.cpp
   
   With the ``> circuit.cpp`` at the end of the command, the output will be saved to the "circuit.cpp" file.

   
All other relevant information can be found by running the ``rtds-vitis -h`` help command. Below is a copy of this
command's output.

----

.. argparse::
   :module: rtds_vitis.create_parser
   :func: create_parser
   :prog: rtds-vitis

   -T --time-step
      The rules for writing the time step are the same ones for writing the :ref:`component values <component_values>`.
