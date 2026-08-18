from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from autograder.grader import grade, sandbox, testcases
from autograder.grader.submission import Submission
from autograder.grader.testcases import TestCase


def _run_result(*, stdout=b"", stderr=b"", returncode=0, elapsed=0.1, timed_out=False):
    return sandbox.RunResult(
        stdout=stdout, stderr=stderr, returncode=returncode, elapsed=elapsed, timed_out=timed_out
    )


class GradeSubmissionTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.cases = [TestCase(name="case_1", input_bytes=b"2 3\n", expected_bytes=b"5\n")]

    def _submission(self, filename: str | None, content: str = "print(1)\n") -> Submission:
        code_file = None
        if filename is not None:
            code_file = self.tmp / filename
            code_file.write_text(content)
        return Submission(student_id="1", name="Someone", timestamp="", folder=self.tmp, code_file=code_file)

    def test_no_code_file(self):
        result = grade.grade_submission(self._submission(None), self.cases, timeout=5.0)

        self.assertEqual(result.status, "no_code_file")
        self.assertEqual(result.cases, [])

    def test_unsupported_language(self):
        result = grade.grade_submission(self._submission("sol.tex", "not code"), self.cases, timeout=5.0)

        self.assertEqual(result.status, "unsupported_language")

    def test_compile_error_on_nonzero_returncode(self):
        submission = self._submission("sol.c", "int main() { return 0; }\n")
        with patch.object(sandbox, "run", return_value=_run_result(returncode=1, stderr=b"boom")):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertEqual(result.status, "compile_error")
        self.assertEqual(result.compile_stderr, "boom")

    def test_compile_error_on_timeout(self):
        submission = self._submission("sol.c", "int main() { return 0; }\n")
        with patch.object(sandbox, "run", return_value=_run_result(timed_out=True, returncode=None)):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertEqual(result.status, "compile_error")

    def test_case_passes_when_output_matches(self):
        submission = self._submission("sol.py")
        with patch.object(sandbox, "run", return_value=_run_result(stdout=b"5\n")):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertEqual(result.status, "graded")
        self.assertEqual(result.score, (1, 1))
        self.assertTrue(result.cases[0].passed)

    def test_case_fails_when_output_differs(self):
        submission = self._submission("sol.py")
        with patch.object(sandbox, "run", return_value=_run_result(stdout=b"6\n")):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertEqual(result.score, (0, 1))
        self.assertFalse(result.cases[0].passed)

    def test_case_fails_on_timeout_even_with_matching_stdout(self):
        submission = self._submission("sol.py")
        with patch.object(sandbox, "run", return_value=_run_result(stdout=b"5\n", timed_out=True, returncode=None)):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertFalse(result.cases[0].passed)
        self.assertTrue(result.cases[0].timed_out)

    def test_case_fails_on_nonzero_returncode_even_with_matching_stdout(self):
        submission = self._submission("sol.py")
        with patch.object(sandbox, "run", return_value=_run_result(stdout=b"5\n", returncode=1)):
            result = grade.grade_submission(submission, self.cases, timeout=5.0)

        self.assertFalse(result.cases[0].passed)


class NormalizeTests(unittest.TestCase):
    def test_ignores_trailing_whitespace_per_line(self):
        self.assertEqual(testcases.normalize(b"5 \n6\t\n"), testcases.normalize(b"5\n6\n"))

    def test_ignores_trailing_blank_lines(self):
        self.assertEqual(testcases.normalize(b"5\n6\n\n\n"), testcases.normalize(b"5\n6\n"))

    def test_distinguishes_actually_different_output(self):
        self.assertNotEqual(testcases.normalize(b"5\n6\n"), testcases.normalize(b"5\n7\n"))


if __name__ == "__main__":
    unittest.main()
