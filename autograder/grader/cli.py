from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import calibrate, complexity, extract, provenance, reference, report, sandbox, testcases
from .grade import grade_all
from .safe_zip import UnsafeZipError

REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOGRADER_ROOT = REPO_ROOT / "autograder"


def find_export_zip(homework: str) -> Path:
    submissions_dir = AUTOGRADER_ROOT / "submissions" / homework
    zips = sorted(submissions_dir.glob("*.zip"))
    if not zips:
        sys.exit(
            f"No zip found in {submissions_dir}. Download the assignment submissions from "
            "Brightspace as a zip and drop it there, or pass --zip explicitly."
        )
    if len(zips) > 1:
        sys.exit(
            f"Multiple zips found in {submissions_dir}: {[z.name for z in zips]}. "
            "Keep only one, or pass --zip explicitly."
        )
    return zips[0]


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade a homework's Brightspace submissions in a Docker sandbox.")
    parser.add_argument("homework", help="homework slug, e.g. 2-dividir-y-conquistar")
    parser.add_argument("--zip", type=Path, default=None, help="path to the Brightspace export zip")
    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="per-test-case timeout in seconds; omit to auto-calibrate from the reference solution",
    )
    parser.add_argument("--workers", type=int, default=8, help="max concurrent submissions being graded")
    parser.add_argument(
        "--skip-complexity",
        action="store_true",
        help="skip the complexity check that otherwise runs automatically after grading",
    )
    args = parser.parse_args()

    homework_dir = REPO_ROOT / "homework" / args.homework
    if not homework_dir.is_dir():
        sys.exit(f"No such homework: {homework_dir}")

    test_cases = testcases.load(homework_dir)
    if not test_cases:
        sys.exit(f"No test cases found under {homework_dir / 'tests'}. Generate them first.")

    export_zip = args.zip or find_export_zip(args.homework)

    sandbox.warm_up()  # avoid mistaking Docker's one-off cold-start cost for a slow case/submission

    timeout = args.timeout
    if timeout is None:
        print("Calibrating timeout from the reference solution...")
        timeout = calibrate.calibrate_timeout(reference.solution_path(homework_dir), test_cases)
        print(f"Using timeout={timeout:.2f}s ({calibrate.SAFETY_FACTOR:.0f}x the reference's slowest case)\n")

    work_dir = AUTOGRADER_ROOT / "work" / args.homework
    if work_dir.exists():
        shutil.rmtree(work_dir)
    try:
        submissions = extract.load_submissions(export_zip, work_dir)
    except UnsafeZipError as exc:
        sys.exit(f"Rejected {export_zip}: {exc}")
    if not submissions:
        sys.exit(f"No submission folders recognized in {export_zip}.")

    print(f"Grading {len(submissions)} submissions against {len(test_cases)} test cases...\n")
    results = grade_all(submissions, test_cases, timeout=timeout, max_workers=args.workers)

    report.print_summary(results)
    stamp = report.timestamp()
    results_dir = AUTOGRADER_ROOT / "results"
    csv_file = report.save_summary_csv(results, args.homework, results_dir, stamp)
    json_file = report.save_json(results, args.homework, results_dir, stamp)
    meta_file = provenance.save(
        repo_root=REPO_ROOT,
        homework=args.homework,
        export_zip=export_zip,
        params={"timeout": timeout, "workers": args.workers},
        results_dir=results_dir,
        stamp=stamp,
    )
    print(f"\nSaved: {csv_file}")
    print(f"Saved: {json_file}")
    print(f"Saved: {meta_file}")

    if args.skip_complexity:
        return
    if not complexity.is_supported(args.homework):
        print(f"\n(No complexity scaler registered for {args.homework!r} -- skipping that check.)")
        return

    print(f"\nRunning complexity check for {len(submissions)} submissions...")
    check = complexity.run(args.homework, homework_dir, submissions)
    complexity.print_check(check)
    complexity_csv = report.save_complexity_csv(check, args.homework, results_dir, stamp)
    complexity_meta_file = provenance.save(
        repo_root=REPO_ROOT,
        homework=args.homework,
        export_zip=export_zip,
        params=complexity.params(check),
        results_dir=results_dir,
        stamp=stamp,
        suffix="-complexity",
    )
    print(f"\nSaved: {complexity_csv}")
    print(f"Saved: {complexity_meta_file}")


if __name__ == "__main__":
    main()
