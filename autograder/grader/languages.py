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
    _PUBLIC_CLASS_RE = re.compile(r"\bpublic\s+(?:(?:final|abstract|static|strictfp|sealed)\s+)*class\s+(\w+)")
    _CLASS_RE = re.compile(r"\bclass\s+(\w+)")
    _STRING_OR_CHAR_RE = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'')
    _COMMENT_RE = re.compile(r"/\*.*?\*/|//[^\n]*", re.DOTALL)

    def stage(self, source: Path, workdir: Path) -> Staged:
        text = source.read_text(encoding="utf-8", errors="replace")
        # Strip string/char literals first so a comment marker inside one (e.g. "/* not a
        # comment */") isn't mistaken for a real comment; then strip comments so a leftover
        # commented-out `public class` declaration can't be matched instead of the real one.
        searchable = self._COMMENT_RE.sub(" ", self._STRING_OR_CHAR_RE.sub('""', text))
        # javac requires the file be named after the public class, which isn't necessarily the
        # first `class` in the file -- a helper class (e.g. a Node) may come before it.
        match = self._PUBLIC_CLASS_RE.search(searchable) or self._CLASS_RE.search(searchable)
        class_name = match.group(1) if match else "Main"
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
