from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TestCase:
    name: str
    input_bytes: bytes
    expected_bytes: bytes


def load(homework_dir: Path) -> list[TestCase]:
    cases = []
    for in_file in sorted((homework_dir / "tests").glob("case_*.in")):
        out_file = in_file.with_suffix(".out")
        cases.append(
            TestCase(
                name=in_file.stem,
                input_bytes=in_file.read_bytes(),
                expected_bytes=out_file.read_bytes(),
            )
        )
    return cases


def normalize(data: bytes) -> list[str]:
    text = data.decode("utf-8", errors="replace")
    return [line.rstrip() for line in text.strip("\n").splitlines()]
