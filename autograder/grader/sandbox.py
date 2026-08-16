from __future__ import annotations

import subprocess
import tempfile
import time
import uuid
from dataclasses import dataclass
from pathlib import Path

IMAGE = "dalgo-autograder"

_DOCKER_HARDENING = [
    "--network", "none",
    "--memory", "256m",
    "--cpus", "1",
    "--pids-limit", "128",
    "--cap-drop", "ALL",
    "--security-opt", "no-new-privileges",
]


@dataclass(frozen=True)
class RunResult:
    stdout: bytes
    stderr: bytes
    returncode: int | None
    elapsed: float
    timed_out: bool


def run(workdir: Path, cmd: list[str], *, stdin: bytes = b"", timeout: float) -> RunResult:
    """Run `cmd` inside a throwaway, sandboxed container with `workdir` mounted at /work."""
    container_name = f"dalgo-autograder-{uuid.uuid4().hex[:12]}"
    docker_cmd = [
        "docker", "run", "--rm", "-i",
        "--name", container_name,
        *_DOCKER_HARDENING,
        "-v", f"{workdir}:/work",
        IMAGE,
        *cmd,
    ]
    start = time.monotonic()
    try:
        proc = subprocess.run(docker_cmd, input=stdin, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        # `--rm` cleans up the container on normal exit, but killing our client
        # process here does not stop the container itself — do that explicitly.
        subprocess.run(["docker", "kill", container_name], capture_output=True)
        return RunResult(
            stdout=exc.stdout or b"",
            stderr=exc.stderr or b"",
            returncode=None,
            elapsed=time.monotonic() - start,
            timed_out=True,
        )
    return RunResult(
        stdout=proc.stdout,
        stderr=proc.stderr,
        returncode=proc.returncode,
        elapsed=time.monotonic() - start,
        timed_out=False,
    )


def warm_up() -> None:
    """Run one throwaway container so the *next* call's timing isn't skewed by Docker's one-off
    cold-start cost (image/overlay setup on the first `docker run` of a session can take seconds,
    dwarfing anything being measured).
    """
    with tempfile.TemporaryDirectory(prefix="dalgo-warmup-") as tmp:
        run(Path(tmp), ["true"], timeout=30.0)
