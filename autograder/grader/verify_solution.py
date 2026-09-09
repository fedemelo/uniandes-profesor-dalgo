from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import calibrate, languages, report, sandbox
from .grade import grade_all
from .submission import Submission
from .testcases import TestCase


def load_test_cases(tests_dir: Path) -> list[TestCase]:
    cases = []
    for in_file in sorted(tests_dir.glob("case_*.in")):
        out_file = in_file.with_suffix(".out")
        cases.append(
            TestCase(name=in_file.stem, input_bytes=in_file.read_bytes(), expected_bytes=out_file.read_bytes())
        )
    return cases


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Sandbox-grade a single reference/candidate solution against a tests/ "
        "directory of case_*.in/.out fixtures -- not tied to homework/'s Brightspace-submission "
        "layout, for spot-checking a solution (e.g. a project's) directly."
    )
    parser.add_argument("solution", type=Path, help="path to the solution source file (.py/.java/.c)")
    parser.add_argument("tests_dir", type=Path, help="directory containing case_*.in/.out fixtures")
    parser.add_argument("--timeout", type=float, default=None, help="per-case timeout in seconds; omit to auto-calibrate")
    args = parser.parse_args()

    if not args.solution.is_file():
        sys.exit(f"No such file: {args.solution}")
    if not args.tests_dir.is_dir():
        sys.exit(f"No such directory: {args.tests_dir}")

    test_cases = load_test_cases(args.tests_dir)
    if not test_cases:
        sys.exit(f"No case_*.in/.out fixtures found under {args.tests_dir}")

    language = languages.detect(args.solution)
    if language is None:
        sys.exit(f"Unsupported file extension: {args.solution.suffix}")

    sandbox.warm_up()

    timeout = args.timeout
    if timeout is None:
        if not isinstance(language, languages.Python):
            sys.exit("--timeout is required for non-Python solutions (auto-calibration only supports Python)")
        print("Calibrating timeout from the solution itself...")
        timeout = calibrate.calibrate_timeout(args.solution, test_cases)
        print(f"Using timeout={timeout:.2f}s ({calibrate.SAFETY_FACTOR:.0f}x the slowest case)\n")

    submission = Submission(
        student_id="candidate", name=args.solution.stem, timestamp="", folder=args.solution.parent, code_file=args.solution
    )

    print(f"Grading {args.solution} against {len(test_cases)} test cases...\n")
    results = grade_all([submission], test_cases, timeout=timeout, max_workers=1)
    report.print_summary(results)

    result = results[0]
    if result.status != "graded":
        sys.exit(1)
    failed = [c for c in result.cases if not c.passed]
    if not failed:
        print("\nAll cases passed.")
        return

    print(f"\n{len(failed)} case(s) failed:")
    for case in failed:
        reason = "timed out" if case.timed_out else f"returncode={case.returncode}, output mismatch"
        print(f"  {case.name}: {reason} ({case.elapsed:.2f}s)")
    sys.exit(1)


if __name__ == "__main__":
    main()
