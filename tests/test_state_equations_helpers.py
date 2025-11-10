"""Helper functions for test_meq"""

# pylint: disable=no-member
import unittest
from dataclasses import dataclass

from rtds_circuit_analysis import Circuit


@dataclass
class _CorrectValues:
    states: dict = None
    node_voltages: dict = None
    currents: dict = None
    component_voltages: dict = None


class _AssertResults(unittest.TestCase):
    """Functions for asserting that the results of the main program are correct"""

    def _assert_all_results_equal(self, function_name, correct_values):
        """Asserts that all the results for a given circuit are correct"""
        file_name = f"tests/test_files/{function_name[5:]}.cir"

        try:
            calculated_values = Circuit(file_name)
        except FileNotFoundError:
            self.fail(f"Could not access file: {file_name}")

        self._assert_results_equal(calculated_values.states, correct_values.states, "state equations")
        self._assert_results_equal(calculated_values.node_voltages, correct_values.node_voltages, "node voltages")
        self._assert_results_equal(
            calculated_values.component_voltages, correct_values.component_voltages, "component voltages"
        )
        self._assert_results_equal(calculated_values.currents, correct_values.currents, "component currents")

    def _assert_results_equal(self, test, correct, results_group):
        self.assertTrue(
            len(test) == len(correct),
            msg=f"""
  Different number of elements between the test and calculated values for {results_group}

  Calculated values:   {test} ({len(test)} values)

  Correct values:      {correct} ({len(correct)} values)
                """,
        )
        for key in test:
            self.assertTrue(
                test[key].equals(correct[key]),
                msg=f"""
  Value not matching for {results_group}: '{key}'.

  Calculated value =  {test[key]}

  Correct value =     {correct[key]}
                """,
            )
