from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from autograder.grader import sandbox, scaling


def _fake_run(elapsed_by_input_len: dict[int, float], timeout_below: int | None = None):
    """Build a stand-in for sandbox.run: elapsed time depends only on stdin length, no Docker."""

    def run(workdir, cmd, *, stdin=b"", timeout=0.0):
        n = len(stdin)
        if timeout_below is not None and n >= timeout_below:
            return sandbox.RunResult(b"", b"", None, elapsed=timeout, timed_out=True)
        return sandbox.RunResult(b"ok", b"", 0, elapsed=elapsed_by_input_len[n], timed_out=False)

    return run


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_takes_the_min_over_repeats(self):
        inputs_by_size = {10: b"x" * 10}
        call_count = 0

        def run(workdir, cmd, *, stdin=b"", timeout=0.0):
            nonlocal call_count
            call_count += 1
            # First call looks slow (e.g. cold start); later calls are the true, faster time.
            elapsed = 5.0 if call_count == 1 else 0.1
            return sandbox.RunResult(b"ok", b"", 0, elapsed=elapsed, timed_out=False)

        with patch.object(sandbox, "run", side_effect=run):
            points = scaling.measure(["true"], self.workdir, inputs_by_size, timeout=10.0, repeats=3)

        self.assertEqual(points[0].elapsed, 0.1)

    def test_stops_at_the_first_size_that_times_out(self):
        inputs_by_size = {10: b"x" * 10, 20: b"x" * 20, 30: b"x" * 30}
        fake = _fake_run({10: 0.1, 20: 0.2, 30: 0.3}, timeout_below=20)

        with patch.object(sandbox, "run", side_effect=fake):
            points = scaling.measure(["true"], self.workdir, inputs_by_size, timeout=10.0, repeats=1)

        self.assertEqual([p.n for p in points], [10])


class TruncateArrayCaseTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_truncates_to_the_requested_size(self):
        seed = self.tmp / "seed.in"
        seed.write_text("1\n5\n1 2 3 4 5\n0 10\n")

        result = scaling.truncate_array_case(seed, 3)

        self.assertEqual(result, b"1\n3\n1 2 3\n0 10\n")

    def test_rejects_a_size_larger_than_the_seed(self):
        seed = self.tmp / "seed.in"
        seed.write_text("1\n5\n1 2 3 4 5\n0 10\n")

        with self.assertRaises(ValueError):
            scaling.truncate_array_case(seed, 10)


if __name__ == "__main__":
    unittest.main()
