from __future__ import annotations

import csv
import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from .complexity import Check
from .grade import SubmissionResult


def print_summary(results: list[SubmissionResult]) -> None:
    for result in results:
        passed, total = result.score
        if result.status != "graded":
            print(f"{result.submission.name:35s} {result.status}")
        else:
            print(f"{result.submission.name:35s} {passed}/{total} ({result.language})")
        for note in result.submission.notes:
            print(f"  ! {note}")


def timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def save_meta(meta: dict, homework: str, results_dir: Path, stamp: str, *, suffix: str = "") -> Path:
    out_dir = results_dir / homework
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp}{suffix}-meta.json"
    out_file.write_text(json.dumps(meta, indent=2, ensure_ascii=False))
    return out_file


def save_summary_csv(results: list[SubmissionResult], homework: str, results_dir: Path, stamp: str) -> Path:
    out_dir = results_dir / homework
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp}.csv"

    with out_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["student_id", "name", "status", "language", "passed", "total", "notes"])
        for result in results:
            passed, total = result.score
            writer.writerow(
                [
                    result.submission.student_id,
                    result.submission.name,
                    result.status,
                    result.language or "",
                    passed,
                    total,
                    "; ".join(result.submission.notes),
                ]
            )

    return out_file


def save_json(results: list[SubmissionResult], homework: str, results_dir: Path, stamp: str) -> Path:
    out_dir = results_dir / homework
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp}.json"

    payload = []
    for result in results:
        entry = {
            "student_id": result.submission.student_id,
            "name": result.submission.name,
            "status": result.status,
            "language": result.language,
            "notes": result.submission.notes,
            "cases": [asdict(c) for c in result.cases],
        }
        if result.compile_stderr:
            entry["compile_stderr"] = result.compile_stderr
        if result.error:
            entry["error"] = result.error
        payload.append(entry)

    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return out_file


def save_complexity_csv(check: Check, homework: str, results_dir: Path, stamp: str) -> Path:
    out_dir = results_dir / homework
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{stamp}-complexity.csv"

    with out_file.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["student_id", "name", "status", "threshold_seconds", "largest_n", "largest_n_seconds", "points"]
        )
        for result in check.results:
            largest = result.points[-1] if result.points else None
            points_str = result.error or "; ".join(f"n={p.n}:{p.elapsed:.4f}s" for p in result.points)
            writer.writerow(
                [
                    result.submission.student_id,
                    result.submission.name,
                    result.status,
                    f"{check.threshold:.3f}",
                    largest.n if largest else "",
                    f"{largest.elapsed:.4f}" if largest else "",
                    points_str,
                ]
            )

    return out_file
