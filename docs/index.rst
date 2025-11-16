.. RTDS Circuit Analysis documentation master file, created by
   sphinx-quickstart on Tue Nov 11 08:26:36 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

RTDS Circuit Analysis documentation
===================================

``rtds_circuit_analysis`` is a Python package for analyzing circuits described in SPICE-like netlists. It parses a
``.cir`` file, builds the corresponding system of equations, and provides symbolic and numeric tools to compute:

- Currents through components  
- Voltage drops  
- Node voltages  
- Continuous and discrete state equations  


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   netlists
   solutions
   cli
   library
