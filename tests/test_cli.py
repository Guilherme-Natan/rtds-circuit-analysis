import unittest
from contextlib import redirect_stdout
from io import StringIO

from rtds_cli.create_parser import create_parser as create_cli_parser
from rtds_vitis.create_parser import create_parser as create_vitis_parser


class TestVersionArguments(unittest.TestCase):

    def assert_version(self, create_parser, flag, command):
        output = StringIO()
        parser = create_parser()
        parser.prog = command
        with self.assertRaisesRegex(SystemExit, "0"):
            with redirect_stdout(output):
                parser.parse_args([flag])

        self.assertEqual(output.getvalue(), f"{command} 0.3.2\n")

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
