import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from rtds_circuit_analysis import Circuit
from rtds_vitis.create_parser import create_parser
from rtds_vitis.vitis_code import (
    generate_vitis_code,
    get_cpp_headers,
    get_cpp_parameters,
)


class TestVitisParser(unittest.TestCase):

    def test_fixed_point_defaults(self):
        args = create_parser().parse_args(["circuit.cir", "-f"])

        self.assertEqual(args.fixed, 32)
        self.assertEqual(args.point, 28)

    def test_fixed_point_arguments_are_integers(self):
        args = create_parser().parse_args(
            ["circuit.cir", "-F", "24", "-P", "16", "-f"]
        )

        self.assertEqual(args.fixed, 24)
        self.assertEqual(args.point, 16)


class TestVitisCode(unittest.TestCase):

    @staticmethod
    def _generate(filepath, method, fixed=32, point=28):
        args = create_parser().parse_args(
            [
                filepath,
                "-T",
                "1e-6",
                "-F",
                str(fixed),
                "-P",
                str(point),
                method,
            ]
        )
        circuit = Circuit(filepath, args.time_step)
        return generate_vitis_code(circuit, args)

    def test_point_bits_are_converted_to_integer_bits(self):
        self.assertIn(
            "ap_fixed<32, 4, AP_TRN, AP_WRAP>",
            get_cpp_headers(32, 28),
        )
        self.assertIn(
            "ap_fixed<24, 8, AP_TRN, AP_WRAP>",
            get_cpp_headers(24, 16),
        )

    def test_forward_code_has_no_synchronization_interface(self):
        filepath = "tests/test_files/series_rlc.cir"
        args = create_parser().parse_args(
            [filepath, "-T", "1e-6", "-f"]
        )
        code = generate_vitis_code(
            Circuit(filepath, args.time_step),
            args,
        )

        self.assertIn("ap_fixed<32, 4, AP_TRN, AP_WRAP>", code)
        self.assertIn("void series_rlc_forward(", code)
        self.assertNotIn("sinc", code)
        self.assertNotIn("aux_sinc", code)
        self.assertNotIn("ap_int", code)
        self.assertNotIn("uint1_t", code)

    def test_literal_components_use_independent_fixed_point_type(self):
        for fixed, point in ((32, 28), (24, 16)):
            with self.subTest(fixed=fixed, point=point):
                code = self._generate(
                    "tests/test_files/series_rlc.cir", "-f", fixed, point,
                )
                self.assertIn(
                    "typedef ap_fixed<96, 32, AP_TRN, AP_WRAP> component_t;",
                    code,
                )
                for parameter in ("R", "L", "C"):
                    self.assertIn(
                        f"#define {parameter} component_t(CHANGEME)", code,
                    )
                self.assertNotIn("data_t(CHANGEME)", code)

    def test_long_component_macro_uses_wider_type(self):
        parameter = "R" + "x" * 70
        code = get_cpp_parameters([parameter])
        self.assertIn("    component_t(CHANGEME)\n", code)
        self.assertTrue(all(len(line) <= 80 for line in code.splitlines()))

    def test_numeric_components_do_not_declare_component_type(self):
        with TemporaryDirectory() as directory:
            filepath = Path(directory) / "numeric_rlc.cir"
            filepath.write_text(
                "V1 1 0 V\nR1 1 2 1000\nL1 2 3 1e-3\nC1 3 0 1e-6\n"
            )
            code = self._generate(str(filepath), "-f")
        self.assertNotIn("component_t", code)
        self.assertNotIn("CHANGEME", code)
        self.assertIn("typedef ap_fixed<32, 4, AP_TRN, AP_WRAP> data_t;", code)

    def test_function_name_contains_each_method(self):
        cases = (
            ("-f", "series_rlc_forward"),
            ("-b", "series_rlc_backward"),
            ("-t", "series_rlc_trapezoidal"),
        )

        for flag, function_name in cases:
            with self.subTest(flag=flag):
                code = self._generate(
                    "tests/test_files/series_rlc.cir",
                    flag,
                )
                self.assertIn(f"void {function_name}(", code)

    def test_generated_lines_do_not_exceed_80_characters(self):
        code = self._generate(
            "tests/test_files/state_equations_3.cir",
            "-t",
        )
        long_lines = [
            (number, len(line), line)
            for number, line in enumerate(code.splitlines(), start=1)
            if len(line) > 80
        ]

        self.assertEqual(long_lines, [])


if __name__ == "__main__":
    unittest.main()
