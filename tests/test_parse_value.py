import unittest

import sympy

from rtds_circuit_analysis.parse_netlist import parse_value


class TestValues(unittest.TestCase):

    def test_whole_numbers(self):
        numbers = ["0", "1", "10", "1983", "834875", "1000000", "999999999", "0800"]
        correct_numbers = [0, 1, 10, 1983, 834875, 1000000, 999999999, 800]
        for n, correct_n in zip(numbers, correct_numbers):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_negative_numbers(self):
        numbers = ["-0", "-1", "-10", "-1983", "-834875", "-1000000", "-0800"]
        correct_numbers = [-0, -1, -10, -1983, -834875, -1000000, -800]
        for n, correct_n in zip(numbers, correct_numbers):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_dot_numbers(self):
        numbers = ["0.0", "-0.0", "1.234", "1.20", "-1.5", "-85738.1958"]
        correct_numbers = [0, 0, 1.234, 1.2, -1.5, -85738.1958]
        for i in range(len(correct_numbers)):
            correct_numbers[i] = sympy.Rational(str(correct_numbers[i]))
        for n, correct_n in zip(numbers, correct_numbers):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_si_notation(self):
        numbers = [
            "0k",
            "0n",
            "10k",
            "5n",
            "-7u",
            "1.2k",
            "-1.7u",
            "0.3p",
            "857m",
        ]
        correct_numbers = [
            0,
            0,
            10000,
            0.000000005,
            -0.000007,
            1200,
            -0.0000017,
            0.0000000000003,
            0.857,
        ]
        for i in range(len(correct_numbers)):
            correct_numbers[i] = sympy.Rational(str(correct_numbers[i]))
        for n, correct_n in zip(numbers, correct_numbers):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_symbolic(self):
        symbols = ["R0", "I1", "V2", "aBc123", "-i"]
        correct_symbols = [
            sympy.Symbol("R0"),
            sympy.Symbol("I1"),
            sympy.Symbol("V2"),
            sympy.Symbol("aBc123"),
            sympy.Integer("-1") * sympy.Symbol("i"),
        ]
        for n, correct_n in zip(symbols, correct_symbols):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_symbol_and_number(self):
        expressions = ["0R", "-0R", "10R", "50V2", "-10I3", "-i", "2.2R4", "-5.7V5", "-nano", "-n"]
        correct_expressions = [
            0,
            0,
            sympy.Integer("10") * sympy.Symbol("R"),
            sympy.Integer("50") * sympy.Symbol("V2"),
            sympy.Integer("-10") * sympy.Symbol("I3"),
            sympy.Integer("-1") * sympy.Symbol("i"),
            sympy.Rational("2.2") * sympy.Symbol("R4"),
            sympy.Rational("-5.7") * sympy.Symbol("V5"),
            sympy.Rational("-1") * sympy.Symbol("nano"),
            sympy.Rational("-1") * sympy.Symbol("n"),
        ]
        for n, correct_n in zip(expressions, correct_expressions):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)

    def test_symbol_and_number_si(self):
        expressions = [
            "0kR",
            "-0nR",
            "10kR",
            "50mV2",
            "-10uI3",
            "2.2kR4",
            "-5.7pV5",
            "100nVin",
            "-100kRk",
            "10.2pp",
        ]
        correct_expressions = [
            0,
            0,
            sympy.Integer("10000") * sympy.Symbol("R"),
            sympy.Rational("0.05") * sympy.Symbol("V2"),
            sympy.Rational("-0.00001") * sympy.Symbol("I3"),
            sympy.Integer("2200") * sympy.Symbol("R4"),
            sympy.Rational("-0.0000000000057") * sympy.Symbol("V5"),
            sympy.Rational("0.0000001") * sympy.Symbol("Vin"),
            sympy.Rational("-100000") * sympy.Symbol("Rk"),
            sympy.Rational("0.0000000000102") * sympy.Symbol("p"),
        ]
        for n, correct_n in zip(expressions, correct_expressions):
            parsed_n = parse_value(n)
            self.assertEqual(parsed_n, correct_n)
