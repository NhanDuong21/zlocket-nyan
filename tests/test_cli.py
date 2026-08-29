from __future__ import annotations

import io
import json
import socket
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

from zlocket.cli import main


class CliTests(unittest.TestCase):
    def test_json_output_is_machine_readable(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output):
            exit_code = main(["--accounts", "2", "--repeat", "4", "--json"])

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["environment"], "mock")
        self.assertEqual(payload["requests_attempted"], 8)

    def test_run_does_not_open_a_network_connection(self) -> None:
        output = io.StringIO()
        with patch.object(
            socket,
            "create_connection",
            side_effect=AssertionError("network access attempted"),
        ), redirect_stdout(output):
            exit_code = main(["--dry-run", "--accounts", "1", "--repeat", "1"])

        self.assertEqual(exit_code, 0)
        self.assertIn("No external network requests were sent", output.getvalue())


if __name__ == "__main__":
    unittest.main()
