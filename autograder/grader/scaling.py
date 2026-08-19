from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from . import sandbox

DEFAULT_SIZES = [1_000, 2_000, 4_000, 8_000, 16_000, 32_000, 64_000, 100_000]


def truncate_array_case(seed: Path, n: int) -> bytes:
    """Build a single-case input at size `n` by slicing `n` array values out of a larger seed
    case. Matches homework 2's per-case grammar: n / n-length array / two bound integers.
    """
    _, _, array_line, bounds = seed.read_text().splitlines()[:4]
    values = array_line.split()
    if n > len(values):
        raise ValueError(f"requested n={n} exceeds seed case size {len(values)}")
    return f"1\n{n}\n{' '.join(values[:n])}\n{bounds}\n".encode()


# Maps a homework slug to (seed case filename, size -> input-bytes scaler). Only homeworks with a
# stated complexity requirement need an entry here; add one by writing a scaler for that
# homework's per-case input grammar.
SCALERS: dict[str, tuple[str, Callable[[Path, int], bytes]]] = {
    "2-dividir-y-conquistar": ("case_12.in", truncate_array_case),
}


@dataclass(frozen=True)
class SizePoint:
    n: int
    elapsed: float


def measure(
    run_cmd: list[str], workdir: Path, inputs_by_size: dict[int, bytes], *, timeout: float, repeats: int
) -> list[SizePoint]:
    """Time `run_cmd` at each size, taking the min over `repeats` runs to denoise. Stops at the
    first size that times out or crashes, since larger sizes would only be slower or no more likely
    to succeed.
    """
    points = []
    for n in sorted(inputs_by_size):
        best: float | None = None
        for _ in range(repeats):
            result = sandbox.run(workdir, run_cmd, stdin=inputs_by_size[n], timeout=timeout)
            if result.timed_out or result.returncode != 0:
                best = None
                break
            best = result.elapsed if best is None else min(best, result.elapsed)
        if best is None:
            break
        points.append(SizePoint(n=n, elapsed=best))
    return points
