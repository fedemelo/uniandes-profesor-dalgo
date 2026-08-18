from __future__ import annotations

import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import languages, reference, scaling, staging
from .staging import CompileFailure
from .submission import Submission

RUN_TIMEOUT = 30.0
REPEATS = 2
SAFETY_FACTOR = 15.0  # vs. the reference solution's own time at the largest size it reaches
MIN_THRESHOLD = 1.0  # seconds; floor so a very fast reference doesn't make the threshold unrealistically tight


class NotSupported(Exception):
    """Raised when a homework has no scaler registered in scaling.SCALERS."""


@dataclass(frozen=True)
class SubmissionCheck:
    submission: Submission
    status: str  # "ok" | "flagged" | "no_code_file" | "unsupported_language" | "compile_error" | "no_points" | "error"
    points: list[scaling.SizePoint]
    error: str | None = None


@dataclass(frozen=True)
class Check:
    sizes: list[int]
    threshold: float
    reference_points: list[scaling.SizePoint]
    results: list[SubmissionCheck]


def is_supported(homework: str) -> bool:
    return homework in scaling.SCALERS


def run(
    homework: str, homework_dir: Path, submissions: list[Submission], *, sizes: list[int] | None = None
) -> Check:
    """Time the reference solution and every submission across a doubling size schedule, and flag
    submissions whose runtime at the largest size is far above the reference's -- the signal a
    flat correctness timeout can miss when a wrong-complexity solution still has good constants.
    """
    if not is_supported(homework):
        raise NotSupported(homework)
    seed_name, scaler = scaling.SCALERS[homework]
    sizes = sizes or scaling.DEFAULT_SIZES

    seed = homework_dir / "tests" / seed_name
    if not seed.is_file():
        raise FileNotFoundError(f"Seed case not found: {seed}")

    try:
        inputs_by_size = {n: scaler(seed, n) for n in sizes}
    except ValueError as exc:
        raise ValueError(f"can't build inputs for {homework!r} with sizes={sizes}: {exc}") from exc

    reference_points = _measure_reference(reference.solution_path(homework_dir), inputs_by_size)
    if not reference_points:
        raise RuntimeError("Reference solution didn't complete any size within the run timeout.")
    threshold = max(reference_points[-1].elapsed * SAFETY_FACTOR, MIN_THRESHOLD)
    # Compare against the size the reference itself reached, not the full requested schedule: if
    # RUN_TIMEOUT keeps even the reference from reaching the largest size, a submission matching
    # the reference's own performance shouldn't be flagged just for topping out at the same size.
    reference_max_size = reference_points[-1].n

    results = [_probe_submission_safe(s, inputs_by_size, reference_max_size, threshold) for s in submissions]
    return Check(sizes=sizes, threshold=threshold, reference_points=reference_points, results=results)


def params(check: Check) -> dict:
    """The grading parameters worth recording in a run's provenance metadata."""
    return {
        "sizes": check.sizes,
        "repeats": REPEATS,
        "run_timeout": RUN_TIMEOUT,
        "safety_factor": SAFETY_FACTOR,
        "threshold": check.threshold,
        "reference_n": check.reference_points[-1].n,
        "reference_elapsed": check.reference_points[-1].elapsed,
    }


def print_check(check: Check) -> None:
    print(
        f"Reference reached n={check.reference_points[-1].n} in {check.reference_points[-1].elapsed:.3f}s "
        f"-> flag threshold {check.threshold:.2f}s ({SAFETY_FACTOR:.0f}x)\n"
    )
    max_size = max(check.sizes)
    for result in check.results:
        if not result.points:
            print(f"{result.submission.name:35s} {result.status}")
            continue
        largest = result.points[-1]
        note = "" if largest.n == max_size else f" (only reached n={largest.n} within {RUN_TIMEOUT:.0f}s)"
        print(f"{result.submission.name:35s} {result.status}: n={largest.n} took {largest.elapsed:.3f}s{note}")
        sizes_reached = ", ".join(f"n={p.n}:{p.elapsed:.3f}s" for p in result.points)
        print(f"  {sizes_reached}")


def _measure_reference(reference_solution: Path, inputs_by_size: dict[int, bytes]) -> list[scaling.SizePoint]:
    with tempfile.TemporaryDirectory(prefix="dalgo-scale-reference-") as tmp:
        workdir = Path(tmp)
        shutil.copy(reference_solution, workdir / "main.py")
        return scaling.measure(["python3", "main.py"], workdir, inputs_by_size, timeout=RUN_TIMEOUT, repeats=REPEATS)


def _probe_submission_safe(
    submission: Submission, inputs_by_size: dict[int, bytes], reference_max_size: int, threshold: float
) -> SubmissionCheck:
    """Wraps _probe_submission so one submission raising can't abort the whole check and lose every
    other submission's results.
    """
    try:
        return _probe_submission(submission, inputs_by_size, reference_max_size, threshold)
    except Exception as exc:
        return SubmissionCheck(submission, "error", [], error=repr(exc))


def _probe_submission(
    submission: Submission, inputs_by_size: dict[int, bytes], reference_max_size: int, threshold: float
) -> SubmissionCheck:
    if submission.code_file is None:
        return SubmissionCheck(submission, "no_code_file", [])

    language = languages.detect(submission.code_file)
    if language is None:
        return SubmissionCheck(submission, "unsupported_language", [])

    with tempfile.TemporaryDirectory(prefix=f"dalgo-scale-{submission.student_id}-") as tmp:
        workdir = Path(tmp)
        staged = staging.stage_and_compile(language, submission.code_file, workdir)
        if isinstance(staged, CompileFailure):
            return SubmissionCheck(submission, "compile_error", [])

        points = scaling.measure(staged.run_cmd, workdir, inputs_by_size, timeout=RUN_TIMEOUT, repeats=REPEATS)

    if not points:
        return SubmissionCheck(submission, "no_points", points)

    largest = points[-1]
    flagged = largest.n < reference_max_size or largest.elapsed > threshold
    return SubmissionCheck(submission, "flagged" if flagged else "ok", points)
