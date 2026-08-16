from __future__ import annotations

import hashlib
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from . import report, sandbox


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(cmd: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=10, text=True)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def _docker_image_id(repo_root: Path) -> str | None:
    return _run(["docker", "image", "inspect", sandbox.IMAGE, "--format", "{{.Id}}"], cwd=repo_root)


def _git_info(repo_root: Path) -> dict:
    commit = _run(["git", "rev-parse", "HEAD"], cwd=repo_root)
    status = _run(["git", "status", "--porcelain"], cwd=repo_root)
    return {
        "commit": commit,
        "dirty": bool(status) if status is not None else None,
    }


def collect(*, repo_root: Path, homework: str, export_zip: Path, params: dict) -> dict:
    """Everything needed to answer 'why did this student's submission get this result' later:
    which zip was graded, which autograder code ran it, and what grading parameters were used.
    """
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "homework": homework,
        "export_zip": {
            "name": export_zip.name,
            "sha256": _sha256(export_zip),
        },
        "autograder_git_commit": _git_info(repo_root),
        "docker_image": {
            "tag": sandbox.IMAGE,
            "id": _docker_image_id(repo_root),
        },
        "params": params,
    }


def save(
    *,
    repo_root: Path,
    homework: str,
    export_zip: Path,
    params: dict,
    results_dir: Path,
    stamp: str,
    suffix: str = "",
) -> Path:
    meta = collect(repo_root=repo_root, homework=homework, export_zip=export_zip, params=params)
    return report.save_meta(meta, homework, results_dir, stamp, suffix=suffix)
