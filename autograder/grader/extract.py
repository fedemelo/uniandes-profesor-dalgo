from __future__ import annotations

import re
from pathlib import Path

from .languages import REGISTRY
from .safe_zip import MAX_UNCOMPRESSED_BYTES, UnsafeZipError, safe_extractall
from .submission import Submission

# Brightspace export folder name, e.g.:
# "34561-465221 - Juan Diego Acuña - 14 de agosto de 2026 2334"
_FOLDER_RE = re.compile(r"^(?P<student_id>\d+)-(?P<course_id>\d+) - (?P<name>.+) - (?P<timestamp>.+)$")

_CODE_EXTENSIONS = {ext for language in REGISTRY for ext in language.extensions}
_MAX_NESTED_ZIP_DEPTH = 3
# Per-submission cap on bytes extracted from *all* nested zips combined -- safe_extractall bounds
# each individual zip, but a folder with many small sibling zips could otherwise still multiply
# past that per-zip cap.
_MAX_NESTED_TOTAL_BYTES = MAX_UNCOMPRESSED_BYTES

_SPANISH_MONTHS = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12,
}
_TIMESTAMP_RE = re.compile(r"(\d{1,2}) de (\w+) de (\d{4}) (\d{3,4})")


def _timestamp_key(timestamp: str) -> tuple[int, int, int, int]:
    """Best-effort sort key for '15 de agosto de 2026 1300'-style Brightspace timestamps."""
    match = _TIMESTAMP_RE.match(timestamp)
    if not match:
        return (0, 0, 0, 0)
    day, month_name, year, hhmm = match.groups()
    month = _SPANISH_MONTHS.get(month_name.lower(), 0)
    return (int(year), month, int(day), int(hhmm))


def _unzip_nested_archives(
    folder: Path, notes: list[str], depth: int = 0, budget: list[int] | None = None
) -> None:
    if budget is None:
        budget = [0]  # bytes extracted so far from nested zips, shared across the whole recursion
    if depth >= _MAX_NESTED_ZIP_DEPTH:
        if any(folder.glob("*.zip")):
            notes.append(f"stopped unzipping nested archives: exceeded max nesting depth of {_MAX_NESTED_ZIP_DEPTH}")
        return
    for archive in list(folder.glob("*.zip")):
        if budget[0] > _MAX_NESTED_TOTAL_BYTES:
            notes.append(
                f"stopped unzipping nested archives: combined total exceeds "
                f"{_MAX_NESTED_TOTAL_BYTES // (1024 * 1024)} MB cap"
            )
            return
        target = folder / archive.stem
        target.mkdir(exist_ok=True)
        try:
            budget[0] += safe_extractall(archive, target)
        except UnsafeZipError as exc:
            notes.append(f"rejected nested archive {archive.relative_to(folder)}: {exc}")
            continue
        if budget[0] > _MAX_NESTED_TOTAL_BYTES:
            notes.append(
                f"stopped unzipping nested archives: combined total exceeds "
                f"{_MAX_NESTED_TOTAL_BYTES // (1024 * 1024)} MB cap"
            )
            return
        _unzip_nested_archives(target, notes, depth + 1, budget)


def _find_code_file(folder: Path, notes: list[str]) -> Path | None:
    _unzip_nested_archives(folder, notes)
    # Zips built on macOS carry a __MACOSX/._<name> AppleDouble stub per file, sharing the real
    # file's extension -- exclude those or one can get picked over the student's actual code.
    candidates = sorted(
        p
        for p in folder.rglob("*")
        if p.suffix in _CODE_EXTENSIONS and p.is_file() and not p.name.startswith("._")
    )
    if not candidates:
        return None
    if len(candidates) > 1:
        notes.append(
            "multiple candidate code files found, picked "
            f"{candidates[0].relative_to(folder)}: {[str(c.relative_to(folder)) for c in candidates]}"
        )
    return candidates[0]


def load_submissions(export_zip: Path, extract_root: Path) -> list[Submission]:
    """Extract a raw Brightspace assignment-download zip and locate each student's code file."""
    extract_root.mkdir(parents=True, exist_ok=True)
    safe_extractall(export_zip, extract_root)

    by_student: dict[str, Submission] = {}
    for entry in sorted(extract_root.iterdir()):
        if not entry.is_dir():
            continue  # skip index.html and the like
        match = _FOLDER_RE.match(entry.name)
        if not match:
            print(f"! skipping {entry.name!r}: doesn't match the expected Brightspace folder name")
            continue

        notes: list[str] = []
        code_file = _find_code_file(entry, notes)
        if code_file is None:
            notes.append("no code file found")

        submission = Submission(
            student_id=match["student_id"],
            name=match["name"],
            timestamp=match["timestamp"],
            folder=entry,
            code_file=code_file,
            notes=notes,
        )

        existing = by_student.get(submission.student_id)
        if existing is None or _timestamp_key(submission.timestamp) >= _timestamp_key(existing.timestamp):
            by_student[submission.student_id] = submission

    return sorted(by_student.values(), key=lambda s: s.name)
