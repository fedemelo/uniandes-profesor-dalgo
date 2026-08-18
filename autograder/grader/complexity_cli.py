from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from . import complexity, extract, provenance, report, sandbox
from .cli import AUTOGRADER_ROOT, REPO_ROOT, find_export_zip
from .safe_zip import UnsafeZipError


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Standalone complexity check for one homework's submissions -- normally this "
        "runs automatically as part of `cli.py`; use this to re-run it alone, e.g. with different "
        "--sizes, without re-grading correctness."
    )
    parser.add_argument("homework", help="homework slug, e.g. 2-dividir-y-conquistar")
    parser.add_argument("--zip", type=Path, default=None, help="path to the Brightspace export zip")
    parser.add_argument(
        "--sizes", type=int, nargs="+", default=None, help="override the default geometric size schedule"
    )
    args = parser.parse_args()

    if not complexity.is_supported(args.homework):
        sys.exit(
            f"No input scaler registered for {args.homework!r} in scaling.py — "
            "complexity checking isn't wired up for this homework yet."
        )

    homework_dir = REPO_ROOT / "homework" / args.homework
    export_zip = args.zip or find_export_zip(args.homework)

    work_dir = AUTOGRADER_ROOT / "work" / f"{args.homework}-complexity"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    try:
        submissions = extract.load_submissions(export_zip, work_dir)
    except UnsafeZipError as exc:
        sys.exit(f"Rejected {export_zip}: {exc}")
    if not submissions:
        sys.exit(f"No submission folders recognized in {export_zip}.")

    sandbox.warm_up()  # avoid mistaking Docker's one-off cold-start cost for a slow case/submission

    print(f"Checking {len(submissions)} submissions...")
    check = complexity.run(args.homework, homework_dir, submissions, sizes=args.sizes)
    complexity.print_check(check)

    stamp = report.timestamp()
    results_dir = AUTOGRADER_ROOT / "results"
    csv_file = report.save_complexity_csv(check, args.homework, results_dir, stamp)
    meta_file = provenance.save(
        repo_root=REPO_ROOT,
        homework=args.homework,
        export_zip=export_zip,
        params=complexity.params(check),
        results_dir=results_dir,
        stamp=stamp,
        suffix="-complexity",
    )
    print(f"\nSaved: {csv_file}")
    print(f"Saved: {meta_file}")


if __name__ == "__main__":
    main()
