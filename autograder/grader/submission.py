from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Submission:
    student_id: str
    name: str
    timestamp: str
    folder: Path
    code_file: Path | None
    notes: list[str] = field(default_factory=list)
