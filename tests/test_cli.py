import unittest
from contextlib import redirect_stdout
from io import StringIO

from sympy import Rational

from rtds_circuit_analysis.parse_netlist import parse_components
from rtds_cli.create_parser import create_parser as create_cli_parser
from rtds_vitis.create_parser import create_parser as create_vitis_parser


class TestTimeStepArguments(unittest.TestCase):

    def test_cli_time_step_overrides_netlist(self):
        for create_parser in (create_cli_parser, create_vitis_parser):
            for flag in ("-T", "--time-step"):
                with self.subTest(parser=create_parser.__module__, flag=flag):
                    args = create_parser().parse_args(["circuit.cir", flag, "1e-6"])
                    _, time_step = parse_components([".STEP 1e-3"], args.time_step)
                    self.assertEqual(time_step, Rational(1, 1000000))

    def test_netlist_time_step_used_without_argument(self):
        _, time_step = parse_components([".STEP 1e-3"], None)
        self.assertEqual(time_step, Rational(1, 1000))

    def test_time_step_unset_without_argument_or_directive(self):
        _, time_step = parse_components([], None)
        self.assertIsNone(time_step)


class TestVersionArguments(unittest.TestCase):

    def assert_version(self, create_parser, flag, command):
        output = StringIO()
        parser = create_parser()
        parser.prog = command
        with self.assertRaisesRegex(SystemExit, "0"):
            with redirect_stdout(output):
                parser.parse_args([flag])

        self.assertEqual(output.getvalue(), f"{command} 0.3.4\n")

    def test_circuit_analysis_version_arguments(self):
        for flag in ("-v", "--version"):
            with self.subTest(flag=flag):
                self.assert_version(
                    create_cli_parser,
                    flag,
                    "rtds-circuit-analysis",
                )

    def test_vitis_version_arguments(self):
        for flag in ("-v", "--version"):
            with self.subTest(flag=flag):
                self.assert_version(create_vitis_parser, flag, "rtds-vitis")


if __name__ == "__main__":
    unittest.main()
