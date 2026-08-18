from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from autograder.grader import complexity, scaling
from autograder.grader.submission import Submission


class ProbeSubmissionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

        code_file = self.tmp / "sol.py"
        code_file.write_text("print('ok')\n")
        self.submission = Submission(
            student_id="1", name="Someone", timestamp="", folder=self.tmp, code_file=code_file
        )

    def _probe(self, points: list[scaling.SizePoint], *, reference_max_size: int, threshold: float):
        with patch.object(scaling, "measure", return_value=points):
            return complexity._probe_submission(self.submission, {}, reference_max_size, threshold)

    def test_not_flagged_when_it_reaches_further_than_the_reference(self):
        # e.g. a fast C/Java submission that outruns a reference solution that's always Python.
        points = [scaling.SizePoint(n=100_000, elapsed=0.5)]

        result = self._probe(points, reference_max_size=32_000, threshold=10.0)

        self.assertEqual(result.status, "ok")

    def test_flagged_when_it_falls_short_of_the_reference(self):
        points = [scaling.SizePoint(n=16_000, elapsed=0.5)]

        result = self._probe(points, reference_max_size=32_000, threshold=10.0)

        self.assertEqual(result.status, "flagged")

    def test_flagged_when_slower_than_threshold_even_at_the_same_size(self):
        points = [scaling.SizePoint(n=32_000, elapsed=20.0)]

        result = self._probe(points, reference_max_size=32_000, threshold=10.0)

        self.assertEqual(result.status, "flagged")


if __name__ == "__main__":
    unittest.main()
