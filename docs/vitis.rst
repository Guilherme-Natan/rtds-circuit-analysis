Vitis HLS Code Generation
=========================

If you want to implement the generated difference equations in a FPGA, to perform a real time simulation, you might
want to use `Vitis HLS
<https://www.amd.com/en/products/software/adaptive-socs-and-fpgas/vitis/vitis-hls.html>`_. With this software, you can
write the code for the real time simulation in C++, instead of Verilog or VHDL.

The ``rtds-vitis`` cli utility provides a way to automatically create the .cpp file necessary for Vitis HLS to perform
the implementation. Like the :ref:`rtds-circuit-analysis <usage-cli>` cli utility, it takes a netlist as an input. Some
things to keep in mind when writing the netlist for this software:

- The literal values of the voltage/current sources in the netlist will be considered the inputs for the FPGA
- The state variables (capacitor voltages and inductor currents) will be the outputs for the FPGA
- Any literal value for passive components in the netlist will create a "CHANGEME" entry in the cpp code, that you
  manually need to change to the numeric value for the components (using exponential notation, e.g. "5.7e3"), before
  actually synthesizing the code with Vitis HLS.
- The "top function" name will contain the netlist file name and the discretization method. For example, the forward
  method for ``rlc_circuit.cir`` creates a function named ``rlc_circuit_forward``. The other possible suffixes are
  ``_backward`` and ``_trapezoidal``. This is the "top function" to select when creating the Vitis HLS project.
- The generated function advances the simulation on every call. It does not have ``sinc`` or ``aux_sinc`` parameters
  or synchronization logic.
- Generated C++ lines are limited to 80 characters whenever they can be split without breaking an identifier or
  literal.

Fixed-point representation
--------------------------

The ``-F`` option sets the total number of bits and defaults to 32. The ``-P`` option sets the number of bits after the
binary point and defaults to 28. Therefore, the default generated type is
``ap_fixed<32, 4, AP_TRN, AP_WRAP>``: Vitis receives the total width and the number of integer bits, calculated as
``F - P``.

Both options are optional. For example, ``-F 24 -P 16`` generates ``ap_fixed<24, 8, AP_TRN, AP_WRAP>``.
        
.. admonition:: Saving to a file
   :class: tip

   This utility prints the output directly to the terminal. If you want to save the output to a file, you can use the
   ">" output redirect operator. 
   
   For example:

   .. code-block::

      rtds-vitis circuit.cir -T 1e-6 -f > circuit_forward.cpp
   
   With ``> circuit_forward.cpp`` at the end of the command, the output will be saved to that file.

   
All other relevant information can be found by running the ``rtds-vitis -h`` help command. Below is a copy of this
command's output.

----

.. argparse::
   :module: rtds_vitis.create_parser
   :func: create_parser
   :prog: rtds-vitis

   -T --time-step
      The rules for writing the time step are the same ones for writing the :ref:`component values <component_values>`.
