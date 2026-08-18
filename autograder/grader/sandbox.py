from __future__ import annotations

import subprocess
import tempfile
import threading
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
    "--ulimit", "fsize=67108864",  # 64 MB per written file, so a runaway write loop can't fill host disk
    "--cap-drop", "ALL",
    "--security-opt", "no-new-privileges",
]

# Per-stream cap on what we'll buffer from a container's stdout/stderr, well above any legitimate
# homework output. `--memory` above only bounds the container's own cgroup -- it has no effect on
# the pipe buffer this process accumulates, so without this cap a submission with a runaway/
# accidental infinite print loop could grow this process's memory unbounded for the whole timeout.
_MAX_OUTPUT_BYTES = 10 * 1024 * 1024
_POLL_INTERVAL = 0.05


@dataclass(frozen=True)
class RunResult:
    stdout: bytes
    stderr: bytes
    returncode: int | None
    elapsed: float
    timed_out: bool
    output_capped: bool = False  # True when the kill was due to the output cap, not the deadline


def _read_capped(stream, cap: int, box: dict) -> None:
    """Read `stream` to EOF, keeping only the first `cap` bytes. Reading (and discarding) past the
    cap rather than stopping matters: once the container is killed for exceeding it, the still-
    running `docker run` client keeps trying to write further output into this pipe, and abandoning
    the read here would leave it blocked on that write forever, wedging `proc.wait()`.
    """
    chunks = []
    total = 0
    while True:
        chunk = stream.read(65536)
        if not chunk:
            break
        if total < cap:
            chunks.append(chunk)
            total += len(chunk)
            if total >= cap:
                box["exceeded"] = True
    box["data"] = b"".join(chunks)


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
    proc = subprocess.Popen(docker_cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def _feed_stdin() -> None:
        try:
            proc.stdin.write(stdin)
        except (BrokenPipeError, OSError):
            pass
        finally:
            try:
                proc.stdin.close()
            except OSError:
                pass

    stdout_box: dict = {}
    stderr_box: dict = {}
    # Draining stdin/stdout/stderr concurrently (rather than sequentially) avoids the classic pipe
    # deadlock: a submission that interleaves reading input with printing output can otherwise
    # block on a full stdout pipe while we're still writing stdin, and vice versa.
    threads = [
        threading.Thread(target=_feed_stdin),
        threading.Thread(target=_read_capped, args=(proc.stdout, _MAX_OUTPUT_BYTES, stdout_box)),
        threading.Thread(target=_read_capped, args=(proc.stderr, _MAX_OUTPUT_BYTES, stderr_box)),
    ]
    for thread in threads:
        thread.start()

    deadline = start + timeout
    timed_out = False
    while proc.poll() is None and not stdout_box.get("exceeded") and not stderr_box.get("exceeded"):
        if time.monotonic() >= deadline:
            timed_out = True
            break
        time.sleep(_POLL_INTERVAL)
    output_exceeded = bool(stdout_box.get("exceeded") or stderr_box.get("exceeded"))

    if timed_out or output_exceeded:
        # `--rm` cleans up the container on normal exit, but killing our client process here does
        # not stop the container itself — do that explicitly.
        subprocess.run(["docker", "kill", container_name], capture_output=True)
    proc.wait()
    for thread in threads:
        thread.join(timeout=5)
    proc.stdout.close()
    proc.stderr.close()

    killed = timed_out or output_exceeded
    return RunResult(
        stdout=stdout_box.get("data", b""),
        stderr=stderr_box.get("data", b""),
        returncode=None if killed else proc.returncode,
        elapsed=time.monotonic() - start,
        timed_out=killed,
        output_capped=output_exceeded,
    )


def warm_up() -> None:
    """Run one throwaway container so the *next* call's timing isn't skewed by Docker's one-off
    cold-start cost (image/overlay setup on the first `docker run` of a session can take seconds,
    dwarfing anything being measured).
    """
    with tempfile.TemporaryDirectory(prefix="dalgo-warmup-") as tmp:
        run(Path(tmp), ["true"], timeout=30.0)
