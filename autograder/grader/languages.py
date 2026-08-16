from __future__ import annotations

import re
import shutil
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Staged:
    """A submission's code, already copied into a sandbox workdir, ready to run."""

    compile_cmd: list[str] | None
    run_cmd: list[str]


class Language(ABC):
    extensions: tuple[str, ...]

    @abstractmethod
    def stage(self, source: Path, workdir: Path) -> Staged: ...


class Python(Language):
    extensions = (".py",)

    def stage(self, source: Path, workdir: Path) -> Staged:
        shutil.copy(source, workdir / "main.py")
        return Staged(compile_cmd=None, run_cmd=["python3", "main.py"])


class C(Language):
    extensions = (".c",)

    def stage(self, source: Path, workdir: Path) -> Staged:
        shutil.copy(source, workdir / "main.c")
        return Staged(
            compile_cmd=["gcc", "-O2", "-o", "main", "main.c"],
            run_cmd=["./main"],
        )


class Java(Language):
    extensions = (".java",)
    _CLASS_RE = re.compile(r"\bpublic\s+class\s+(\w+)|\bclass\s+(\w+)")

    def stage(self, source: Path, workdir: Path) -> Staged:
        text = source.read_text(encoding="utf-8", errors="replace")
        match = self._CLASS_RE.search(text)
        class_name = next(g for g in (match.groups() if match else ()) if g) if match else "Main"
        shutil.copy(source, workdir / f"{class_name}.java")
        return Staged(
            compile_cmd=["javac", f"{class_name}.java"],
            run_cmd=["java", class_name],
        )


REGISTRY: tuple[Language, ...] = (Python(), C(), Java())


def detect(code_file: Path) -> Language | None:
    for language in REGISTRY:
        if code_file.suffix in language.extensions:
            return language
    return None
