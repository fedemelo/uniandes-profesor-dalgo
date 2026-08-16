from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from . import sandbox
from .testcases import TestCase

SAFETY_FACTOR = 20.0
MIN_TIMEOUT = 2.0
_CALIBRATION_TIMEOUT = 60.0  # generous ceiling while measuring the (trusted) reference itself


def calibrate_timeout(reference_solution: Path, test_cases: list[TestCase]) -> float:
    """Time the reference solution on every case and derive a tight per-case grading timeout.

    A flat 10s timeout is enormous for an O(n log n) solution at the stated max n — it also
    happily lets a mis-implemented O(n^2) solution slip through undetected. Basing the timeout on
    how long the *correct* algorithm actually takes, with a safety margin for language/hardware
    variance, catches wrong-complexity submissions instead.
    """
    with tempfile.TemporaryDirectory(prefix="dalgo-calibrate-") as tmp:
        workdir = Path(tmp)
        shutil.copy(reference_solution, workdir / "main.py")
        run_cmd = ["python3", "main.py"]

        max_elapsed = 0.0
        for case in test_cases:
            result = sandbox.run(workdir, run_cmd, stdin=case.input_bytes, timeout=_CALIBRATION_TIMEOUT)
            if result.timed_out:
                raise RuntimeError(f"reference solution timed out on {case.name} during calibration")
            max_elapsed = max(max_elapsed, result.elapsed)

    return max(max_elapsed * SAFETY_FACTOR, MIN_TIMEOUT)
