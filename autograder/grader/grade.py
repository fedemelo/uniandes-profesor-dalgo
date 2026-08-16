from __future__ import annotations

import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path

from . import languages, sandbox
from .submission import Submission
from .testcases import TestCase, normalize

COMPILE_TIMEOUT = 30.0


@dataclass(frozen=True)
class CaseResult:
    name: str
    passed: bool
    elapsed: float
    timed_out: bool
    returncode: int | None


@dataclass
class SubmissionResult:
    submission: Submission
    status: str  # "graded" | "unsupported_language" | "no_code_file" | "compile_error"
    language: str | None = None
    compile_stderr: str | None = None
    cases: list[CaseResult] = field(default_factory=list)

    @property
    def score(self) -> tuple[int, int]:
        return (sum(c.passed for c in self.cases), len(self.cases))


def grade_submission(submission: Submission, test_cases: list[TestCase], timeout: float) -> SubmissionResult:
    if submission.code_file is None:
        return SubmissionResult(submission, status="no_code_file")

    language = languages.detect(submission.code_file)
    if language is None:
        return SubmissionResult(submission, status="unsupported_language")

    with tempfile.TemporaryDirectory(prefix=f"dalgo-{submission.student_id}-") as tmp:
        workdir = Path(tmp)
        staged = language.stage(submission.code_file, workdir)

        if staged.compile_cmd:
            compile_result = sandbox.run(workdir, staged.compile_cmd, timeout=COMPILE_TIMEOUT)
            if compile_result.timed_out or compile_result.returncode != 0:
                return SubmissionResult(
                    submission,
                    status="compile_error",
                    language=type(language).__name__,
                    compile_stderr=compile_result.stderr.decode("utf-8", errors="replace"),
                )

        case_results = []
        for case in test_cases:
            result = sandbox.run(workdir, staged.run_cmd, stdin=case.input_bytes, timeout=timeout)
            passed = (
                not result.timed_out
                and result.returncode == 0
                and normalize(result.stdout) == normalize(case.expected_bytes)
            )
            case_results.append(
                CaseResult(
                    name=case.name,
                    passed=passed,
                    elapsed=result.elapsed,
                    timed_out=result.timed_out,
                    returncode=result.returncode,
                )
            )

        return SubmissionResult(
            submission, status="graded", language=type(language).__name__, cases=case_results
        )


def grade_all(
    submissions: list[Submission],
    test_cases: list[TestCase],
    *,
    timeout: float = 10.0,
    max_workers: int = 8,
) -> list[SubmissionResult]:
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(grade_submission, submission, test_cases, timeout): submission
            for submission in submissions
        }
        results = [future.result() for future in as_completed(futures)]

    return sorted(results, key=lambda r: r.submission.name)
