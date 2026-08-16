from __future__ import annotations

import re
from pathlib import Path

_HOMEWORK_NUMBER_RE = re.compile(r"^(\d+)-")


def solution_path(homework_dir: Path) -> Path:
    match = _HOMEWORK_NUMBER_RE.match(homework_dir.name)
    if not match:
        raise ValueError(f"can't infer homework number from directory name {homework_dir.name!r}")
    path = homework_dir / f"solucion_tarea_{match.group(1)}.py"
    if not path.is_file():
        raise FileNotFoundError(f"no reference solution at {path}")
    return path
