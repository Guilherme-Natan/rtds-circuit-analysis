"""Test for some basic circuits"""

import inspect

import sympy as sp

from tests.test_state_equations_helpers import _AssertResults, _CorrectValues

# pylint: disable=missing-function-docstring
# pylint: disable=too-many-public-methods
# pylint: disable=invalid-name
# pylint: disable=too-many-locals


class TestResistiveCircuits(_AssertResults):
    """Tests for purely resistive circuits"""

    def test_voltage_source(self):
        Vin, R1 = sp.symbols("Vin R1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Vin,
        }
        correct_values.component_voltages = {
            "R1": Vin,
        }
        correct_values.currents = {
            "VIN": Vin / R1,
            "R1": Vin / R1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_current_source(self):
        Iin, R1 = sp.symbols("Iin R1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Iin * R1,
        }
        correct_values.component_voltages = {
            "IIN": Iin * R1,
            "R1": Iin * R1,
        }
        correct_values.currents = {
            "R1": Iin,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_voltage_divider(self):
        Vin, R1, R2 = sp.symbols("Vin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Vin,
            "OUT": Vin * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": Vin * R1 / (R1 + R2),
            "R2": Vin * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "VIN": Vin / (R1 + R2),
            "R1": Vin / (R1 + R2),
            "R2": Vin / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_voltage_divider_var_1(self):
        # Inverted Voltage Source
        Vin, R1, R2 = sp.symbols("Vin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": -Vin,
            "OUT": -Vin * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": -Vin * R1 / (R1 + R2),
            "R2": -Vin * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "VIN": Vin / (R1 + R2),
            "R1": -Vin / (R1 + R2),
            "R2": -Vin / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_voltage_divider_var_2(self):
        # Inverted R1 Resistor
        Vin, R1, R2 = sp.symbols("Vin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Vin,
            "OUT": Vin * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": -Vin * R1 / (R1 + R2),
            "R2": Vin * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "VIN": Vin / (R1 + R2),
            "R1": -Vin / (R1 + R2),
            "R2": Vin / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_current_divider(self):
        Iin, R1, R2 = sp.symbols("Iin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": Iin * R1 * R2 / (R1 + R2),
            "R2": Iin * R1 * R2 / (R1 + R2),
            "IIN": Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "R1": Iin * R2 / (R1 + R2),
            "R2": Iin * R1 / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_current_divider_var_1(self):
        # Inverted Current Source
        Iin, R1, R2 = sp.symbols("Iin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": -Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": -Iin * R1 * R2 / (R1 + R2),
            "R2": -Iin * R1 * R2 / (R1 + R2),
            "IIN": Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "R1": -Iin * R2 / (R1 + R2),
            "R2": -Iin * R1 / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_current_divider_var_2(self):
        # Inverted R1 Resistor
        Iin, R1, R2 = sp.symbols("Iin R1 R2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.component_voltages = {
            "R1": -Iin * R1 * R2 / (R1 + R2),
            "R2": Iin * R1 * R2 / (R1 + R2),
            "IIN": Iin * R1 * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "R1": -Iin * R2 / (R1 + R2),
            "R2": Iin * R1 / (R1 + R2),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_parallel_voltage_source(self):
        Vin = sp.Symbol("Vin")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Vin,
            "OUT": Vin / 2,
        }
        correct_values.component_voltages = {
            "R1": Vin / 2,
            "R21": Vin / 2,
            "R22": Vin / 2,
        }
        correct_values.currents = {
            "VIN": Vin / 10000,
            "R1": Vin / 10000,
            "R21": Vin / 20000,
            "R22": Vin / 20000,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_parallel_current_source(self):

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": 10,
            "OUT": 5,
        }
        correct_values.component_voltages = {
            "R1": 5,
            "R21": 5,
            "R22": 5,
            "IIN": 10,
        }
        correct_values.currents = {
            "R1": sp.Rational("1e-3"),
            "R21": sp.Rational("0.5e-3"),
            "R22": sp.Rational("0.5e-3"),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_grounded_voltage_source(self):
        V1 = sp.Symbol("V1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": V1,
        }
        correct_values.component_voltages = {}
        correct_values.currents = {
            "V1": 0,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_grounded_voltage_source_resistors(self):
        V1 = sp.Symbol("V1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": V1,
            "2": V1,
            "3": V1,
        }
        correct_values.component_voltages = {
            "R1": 0,
            "R2": 0,
        }
        correct_values.currents = {
            "V1": 0,
            "R1": 0,
            "R2": 0,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_grounded_voltage_sources(self):
        V1, V2 = sp.symbols("V1 V2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": V1,
            "2": V1 + V2,
        }
        correct_values.component_voltages = {}
        correct_values.currents = {
            "V1": 0,
            "V2": 0,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_grounded_voltage_sources_resistors(self):
        V1, V2 = sp.symbols("V1 V2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": 0,
            "2": V1,
            "3": V1,
            "4": V1 + V2,
            "5": V1 + V2,
        }
        correct_values.component_voltages = {
            "R1": 0,
            "R2": 0,
            "R3": 0,
        }
        correct_values.currents = {
            "R1": 0,
            "V1": 0,
            "R2": 0,
            "V2": 0,
            "R3": 0,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    # Due to the way this script works, if you want to create a short circuited current source, you need to use a
    # 0 ohms resistor. The 2 following tests show this.

    def test_shorted_current_source(self):
        Iin = sp.symbols("Iin")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": 0,
        }
        correct_values.component_voltages = {
            "IIN": 0,
            "R0": 0,
        }
        correct_values.currents = {
            "R0": Iin,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_shorted_current_sources(self):
        I1, I2 = sp.symbols("I1, I2")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": 0,
        }
        correct_values.component_voltages = {
            "I1": 0,
            "I2": 0,
            "R0": 0,
        }
        correct_values.currents = {
            "R0": I1 + I2,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_current_sources_resistor(self):
        I1, I2, R1 = sp.symbols("I1, I2, R1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": R1 * (I1 + I2),
        }
        correct_values.component_voltages = {
            "I1": R1 * (I1 + I2),
            "I2": R1 * (I1 + I2),
            "R1": R1 * (I1 + I2),
        }
        correct_values.currents = {
            "R1": I1 + I2,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_voltage_and_current_sources_series(self):
        I1, V1, R1 = sp.symbols("I1, V1, R1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": V1,
            "2": R1 * I1,
        }
        correct_values.component_voltages = {
            "I1": R1 * I1 - V1,
            "R1": R1 * I1,
        }
        correct_values.currents = {
            "V1": I1,
            "R1": I1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_voltage_and_current_sources_parallel(self):
        I1, V1, R1 = sp.symbols("I1 V1 R1")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": V1,
        }
        correct_values.component_voltages = {
            "I1": V1,
            "R1": V1,
        }
        correct_values.currents = {
            "V1": V1 / R1 - I1,
            "R1": V1 / R1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_open_voltage_source(self):
        Vin, R1, R2, Va = sp.symbols("Vin R1 R2 Va")

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "IN": Vin,
            "OUT": Vin * R2 / (R1 + R2),
            "OPEN": Vin * R2 / (R1 + R2) + Va,
        }
        correct_values.component_voltages = {
            "R1": Vin * R1 / (R1 + R2),
            "R2": Vin * R2 / (R1 + R2),
        }
        correct_values.currents = {
            "VIN": Vin / (R1 + R2),
            "R1": Vin / (R1 + R2),
            "R2": Vin / (R1 + R2),
            "VOPEN": 0,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_multiple_voltage_sources(self):

        correct_values = _CorrectValues()
        correct_values.states = {}
        correct_values.node_voltages = {
            "1": -5,
            "2": 5,
            "3": 3,
            "4": -4,
        }
        correct_values.component_voltages = {
            "R1": -2,
            "R2": -3,
            "R3": -4,
        }
        correct_values.currents = {
            "V1": sp.Rational("2e-4"),
            "V2": sp.Rational("-2e-4"),
            "R1": sp.Rational("-2e-4"),
            "V3": sp.Rational("-1e-4"),
            "R2": sp.Rational("-6e-4"),
            "V4": sp.Rational("5e-4"),
            "R3": sp.Rational("-5e-4"),
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)


class TestStateEquations(_AssertResults):
    """Tests for circuits with energy storage elements"""

    def test_series_rlc(self):
        V, R, L, C = sp.symbols("V R L C")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - R * IL1 - VC1) / L,
            "C1": IL1 / C,
        }

        correct_values.node_voltages = {
            "1": V,
            "2": V - IL1 * R,
            "3": VC1,
        }
        correct_values.component_voltages = {
            "R1": IL1 * R,
            "L1": V - R * IL1 - VC1,
        }
        correct_values.currents = {
            "C1": IL1,
            "R1": IL1,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_parallel_rlc(self):
        I, R, L, C = sp.symbols("I R L C")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": VC1 / L,
            "C1": (I - IL1 - VC1 / R) / C,
        }

        correct_values.node_voltages = {
            "1": VC1,
        }
        correct_values.component_voltages = {
            "I1": VC1,
            "L1": VC1,
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": I - IL1 - VC1 / R,
            "R1": VC1 / R,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_state_equations_1(self):
        V, R, L, C = sp.symbols("V R L C")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - VC1) / L,
            "C1": (IL1 - VC1 / R) / C,
        }
        correct_values.node_voltages = {
            "1": V,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": V - VC1,
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": IL1 - VC1 / R,
            "R1": VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_state_equations_2(self):
        Vin, R1, L1, R2, L2, R3, L3, C1, C2 = sp.symbols("Vin R1 L1 R2 L2 R3 L3 C1 C2")
        IL1, IL2, IL3, VC1, VC2 = sp.symbols("IL1 IL2 IL3 VC1 VC2 ")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (Vin - R1 * IL1 - VC1) / L1,
            "L2": (VC1 - R2 * IL2 - VC2) / L2,
            "L3": (Vin - R3 * IL3 - VC2) / L3,
            "C1": (IL1 - IL2) / C1,
            "C2": (IL2 + IL3) / C2,
        }
        correct_values.node_voltages = {
            "1": Vin,
            "2": VC1,
            "3": VC2,
            "1_2": Vin - IL1 * R1,
            "2_3": VC1 - IL2 * R2,
            "1_3": Vin - IL3 * R3,
        }
        correct_values.component_voltages = {
            "R1": R1 * IL1,
            "R2": R2 * IL2,
            "R3": R3 * IL3,
            "L1": Vin - R1 * IL1 - VC1,
            "L2": VC1 - R2 * IL2 - VC2,
            "L3": Vin - R3 * IL3 - VC2,
        }
        correct_values.currents = {
            "R1": IL1,
            "R2": IL2,
            "R3": IL3,
            "C1": IL1 - IL2,
            "C2": IL2 + IL3,
            "VIN": IL1 + IL3,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_state_equations_3(self):
        Vin, R1, L1, R2, L2, C1, C2, RL = sp.symbols("Vin R1 L1 R2 L2 C1 C2 RL")
        IL1, IL2, VC1, VC2 = sp.symbols("IL1 IL2 VC1 VC2")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (Vin - R1 * IL1 - VC1) / L1,
            "L2": (VC1 - R2 * IL2 - VC2) / L2,
            "C1": (IL1 - IL2) / C1,
            "C2": (IL2 - VC2 / RL) / C2,
        }
        correct_values.node_voltages = {
            "1": Vin,
            "2": VC1,
            "3": VC2,
            "1_2": Vin - IL1 * R1,
            "2_3": VC1 - IL2 * R2,
        }
        correct_values.component_voltages = {
            "R1": R1 * IL1,
            "R2": R2 * IL2,
            "L1": Vin - R1 * IL1 - VC1,
            "L2": VC1 - R2 * IL2 - VC2,
            "RL": VC2,
        }
        correct_values.currents = {
            "R1": IL1,
            "R2": IL2,
            "C1": IL1 - IL2,
            "C2": IL2 - VC2 / RL,
            "VIN": IL1,
            "RL": VC2 / RL,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor(self):
        V, R, L1, L2, C1, C2 = sp.symbols("V R L1 L2 C1 C2")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - VC1) / (L1 + L2),
            "C1": (IL1 - VC1 / R) / (C1 + C2),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2": (V - VC1) * L2 / (L1 + L2) + VC1,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": (V - VC1) * L1 / (L1 + L2),
            "L2": (V - VC1) * L2 / (L1 + L2),
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": (IL1 - VC1 / R) * C1 / (C1 + C2),
            "C2": (IL1 - VC1 / R) * C2 / (C1 + C2),
            "R1": VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more(self):
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - VC1) / (L1 + L2 + L3 + L4),
            "C1": (IL1 - VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V - VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2B": (V - VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2C": (V - VC1) * L4 / (L1 + L2 + L3 + L4) + VC1,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": (V - VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": (V - VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": (V - VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": (V - VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": (IL1 - VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": (IL1 - VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": (IL1 - VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": (IL1 - VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more_order(self):
        # Same as the last one, but the order of the order of the inductors and capacitors in the .cir file is inverted. The circuit is exactly the
        # same as the last one, so the results should be the same as well
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - VC1) / (L1 + L2 + L3 + L4),
            "C1": (IL1 - VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V - VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2B": (V - VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2C": (V - VC1) * L4 / (L1 + L2 + L3 + L4) + VC1,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": (V - VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": (V - VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": (V - VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": (V - VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": (IL1 - VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": (IL1 - VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": (IL1 - VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": (IL1 - VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more_inverted(self):
        # Inductors 3 and 4, and capacitors 2 and 4 inverted
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V - VC1) / (L1 + L2 + L3 + L4),
            "C1": (IL1 - VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V - VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2B": (V - VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2C": (V - VC1) * L4 / (L1 + L2 + L3 + L4) + VC1,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": (V - VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": (V - VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": -(V - VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": -(V - VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": (IL1 - VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": -(IL1 - VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": (IL1 - VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": -(IL1 - VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more_inverted_2(self):
        # Inductors 1 and 4, and capacitors 2 and 4 inverted
        # Inverting inductor 1 will cause IL1 to invert as well
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": -(V - VC1) / (L1 + L2 + L3 + L4),
            "C1": (-IL1 - VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V - VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2B": (V - VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) + VC1,
            "1_2C": (V - VC1) * L4 / (L1 + L2 + L3 + L4) + VC1,
            "2": VC1,
        }
        correct_values.component_voltages = {
            "L1": -(V - VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": (V - VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": (V - VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": -(V - VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": VC1,
        }
        correct_values.currents = {
            "C1": (-IL1 - VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": -(-IL1 - VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": (-IL1 - VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": -(-IL1 - VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": VC1 / R,
            "V1": -IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more_inverted_3(self):
        # Inductors 3 and 4, and capacitors 1 and 4 inverted
        # Inverting capacitor 1 will cause VC1 to invert as well
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": (V + VC1) / (L1 + L2 + L3 + L4),
            "C1": -(IL1 + VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V + VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) - VC1,
            "1_2B": (V + VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) - VC1,
            "1_2C": (V + VC1) * L4 / (L1 + L2 + L3 + L4) - VC1,
            "2": -VC1,
        }
        correct_values.component_voltages = {
            "L1": (V + VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": (V + VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": -(V + VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": -(V + VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": -VC1,
        }
        correct_values.currents = {
            "C1": -(IL1 + VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": (IL1 + VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": (IL1 + VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": -(IL1 + VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": -VC1 / R,
            "V1": IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    def test_series_inductor_parallel_capacitor_more_inverted_4(self):
        # Inductors 1 and 2, and capacitors 1 and 3 inverted
        # Inverting capacitor 1 and indutor 1 will cause VC1 and IL1 to invert as well
        V, R, L1, L2, L3, L4, C1, C2, C3, C4 = sp.symbols("V R L1 L2 L3 L4 C1 C2 C3 C4")
        IL1, VC1 = sp.symbols("IL1 VC1")

        correct_values = _CorrectValues()
        correct_values.states = {
            "L1": -(V + VC1) / (L1 + L2 + L3 + L4),
            "C1": -(-IL1 + VC1 / R) / (C1 + C2 + C3 + C4),
        }
        correct_values.node_voltages = {
            "1": V,
            "1_2A": (V + VC1) * (L2 + L3 + L4) / (L1 + L2 + L3 + L4) - VC1,
            "1_2B": (V + VC1) * (L3 + L4) / (L1 + L2 + L3 + L4) - VC1,
            "1_2C": (V + VC1) * L4 / (L1 + L2 + L3 + L4) - VC1,
            "2": -VC1,
        }
        correct_values.component_voltages = {
            "L1": -(V + VC1) * L1 / (L1 + L2 + L3 + L4),
            "L2": -(V + VC1) * L2 / (L1 + L2 + L3 + L4),
            "L3": (V + VC1) * L3 / (L1 + L2 + L3 + L4),
            "L4": (V + VC1) * L4 / (L1 + L2 + L3 + L4),
            "R1": -VC1,
        }
        correct_values.currents = {
            "C1": -(-IL1 + VC1 / R) * C1 / (C1 + C2 + C3 + C4),
            "C2": (-IL1 + VC1 / R) * C2 / (C1 + C2 + C3 + C4),
            "C3": -(-IL1 + VC1 / R) * C3 / (C1 + C2 + C3 + C4),
            "C4": (-IL1 + VC1 / R) * C4 / (C1 + C2 + C3 + C4),
            "R1": -VC1 / R,
            "V1": -IL1,
        }
        self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)

    # This test takes too long (around 5 minutes). I will remove it then.
    # def test_series_inductor_parallel_capacitor_more_groups(self):
    #     # Multiple groups of series inductors and parallel capacitors
    #     Vin, R1, L1A, L1B, R2, L2A, L2B, R3, L3A, L3B, C1A, C1B, C2A, C2B = sp.symbols(
    #         "Vin R1 L1A L1B R2 L2A L2B R3 L3A L3B C1A C1B C2A C2B"
    #     )
    #     IL1A, IL2A, IL3A, VC1A, VC2A = sp.symbols("IL1A IL2A IL3A VC1A VC2A ")

    #     correct_values = _CorrectValues()
    #     correct_values.states = {
    #         "IL1A": (Vin - R1 * IL1A - VC1A) / (L1A + L1B),
    #         "IL2A": (VC1A - R2 * IL2A - VC2A) / (L2A + L2B),
    #         "IL3A": (Vin - R3 * IL3A - VC2A) / (L3A + L3B),
    #         "VC1A": (IL1A - IL2A) / (C1A + C1B),
    #         "VC2A": (IL2A + IL3A) / (C2A + C2B),
    #     }
    #     correct_values.node_voltages = {
    #         "1": Vin,
    #         "2": VC1A,
    #         "3": VC2A,
    #         # There are multiple ways to calculate these node voltages below, so it is possible for this test to fail
    #         # for one of these nodes, even with the output for the code being correct.
    #         "1_2A": Vin - IL1A * R1,
    #         "1_2B": Vin - IL1A * R1 - (Vin - R1 * IL1A - VC1A) * L1A / (L1A + L1B),
    #         "2_3A": VC1A - (VC1A - R2 * IL2A - VC2A) * L2A / (L2A + L2B),
    #         "2_3B": VC1A - (VC1A - R2 * IL2A - VC2A) * L2A / (L2A + L2B) - R2 * IL2A,
    #         "1_3A": Vin - (Vin - R3 * IL3A - VC2A) * L3A / (L3A + L3B),
    #         "1_3B": IL3A * R3 + VC2A,
    #     }
    #     correct_values.component_voltages = {
    #         "R1": R1 * IL1A,
    #         "R2": R2 * IL2A,
    #         "R3": R3 * IL3A,
    #         "L1A": (Vin - R1 * IL1A - VC1A) * L1A / (L1A + L1B),
    #         "L1B": (Vin - R1 * IL1A - VC1A) * L1B / (L1A + L1B),
    #         "L2A": (VC1A - R2 * IL2A - VC2A) * L2A / (L2A + L2B),
    #         "L2B": (VC1A - R2 * IL2A - VC2A) * L2B / (L2A + L2B),
    #         "L3A": (Vin - R3 * IL3A - VC2A) * L3A / (L3A + L3B),
    #         "L3B": (Vin - R3 * IL3A - VC2A) * L3B / (L3A + L3B),
    #     }
    #     correct_values.currents = {
    #         "R1": IL1A,
    #         "R2": IL2A,
    #         "R3": IL3A,
    #         "C1A": (IL1A - IL2A) * C1A / (C1A + C1B),
    #         "C1B": (IL1A - IL2A) * C1B / (C1A + C1B),
    #         "C2A": (IL2A + IL3A) * C2A / (C2A + C2B),
    #         "C2B": (IL2A + IL3A) * C2B / (C2A + C2B),
    #         "VIN": IL1A + IL3A,
    #     }
    #     self._assert_all_results_equal(inspect.currentframe().f_code.co_name, correct_values)
