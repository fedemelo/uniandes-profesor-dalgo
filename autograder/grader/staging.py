from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from . import sandbox
from .languages import Language, Staged

COMPILE_TIMEOUT = 30.0


@dataclass(frozen=True)
class CompileFailure:
    stderr: str


def stage_and_compile(language: Language, source: Path, workdir: Path) -> Staged | CompileFailure:
    """Stage a submission's code into `workdir` and compile it if the language needs it.

    Shared by grading and the complexity check so compile-error handling can't drift between them.
    """
    staged = language.stage(source, workdir)
    if staged.compile_cmd:
        compile_result = sandbox.run(workdir, staged.compile_cmd, timeout=COMPILE_TIMEOUT)
        if compile_result.timed_out or compile_result.returncode != 0:
            return CompileFailure(stderr=compile_result.stderr.decode("utf-8", errors="replace"))
    return staged
