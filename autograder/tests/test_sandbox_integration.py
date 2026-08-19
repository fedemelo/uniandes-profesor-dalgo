from __future__ import annotations

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from autograder.grader import sandbox


def _docker_ready() -> bool:
    if shutil.which("docker") is None:
        return False
    try:
        subprocess.run(["docker", "info"], capture_output=True, timeout=5, check=True)
        subprocess.run(["docker", "image", "inspect", sandbox.IMAGE], capture_output=True, timeout=5, check=True)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return True


@unittest.skipUnless(
    _docker_ready(), f"Docker not running or {sandbox.IMAGE!r} image not built (docker build -t {sandbox.IMAGE} autograder/docker)"
)
class SandboxIntegrationTests(unittest.TestCase):
    """Runs real containers against tiny synthetic snippets -- never real student data."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.workdir = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def test_runs_python_and_captures_stdout(self):
        (self.workdir / "main.py").write_text("print(sum(int(x) for x in input().split()))")

        result = sandbox.run(self.workdir, ["python3", "main.py"], stdin=b"2 3 4", timeout=10.0)

        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), b"9")

    def test_timeout_actually_kills_the_container(self):
        (self.workdir / "main.py").write_text("import time\ntime.sleep(30)\nprint('should not print')")

        result = sandbox.run(self.workdir, ["python3", "main.py"], timeout=1.0)

        self.assertTrue(result.timed_out)
        # If the kill didn't work, the client wait would drag out closer to 30s.
        self.assertLess(result.elapsed, 5.0)

    def test_network_is_disabled(self):
        (self.workdir / "main.py").write_text(
            "import socket\n"
            "s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n"
            "s.settimeout(3)\n"
            "try:\n"
            "    s.connect(('8.8.8.8', 53))\n"
            "    print('connected')\n"
            "except OSError:\n"
            "    print('blocked')\n"
        )

        result = sandbox.run(self.workdir, ["python3", "main.py"], timeout=10.0)

        self.assertEqual(result.stdout.strip(), b"blocked")

    def test_compiles_and_runs_c(self):
        (self.workdir / "main.c").write_text(
            "#include <stdio.h>\nint main(){int a,b;scanf(\"%d %d\",&a,&b);printf(\"%d\\n\",a+b);return 0;}"
        )

        compile_result = sandbox.run(self.workdir, ["gcc", "-O2", "-o", "main", "main.c"], timeout=30.0)
        self.assertEqual(compile_result.returncode, 0, compile_result.stderr)

        run_result = sandbox.run(self.workdir, ["./main"], stdin=b"2 3", timeout=10.0)
        self.assertEqual(run_result.stdout.strip(), b"5")

    def test_runaway_output_is_capped_instead_of_buffered_forever(self):
        (self.workdir / "main.py").write_text("while True:\n    print('x' * 1000)\n")

        result = sandbox.run(self.workdir, ["python3", "main.py"], timeout=15.0)

        self.assertTrue(result.timed_out)
        self.assertLessEqual(len(result.stdout), sandbox._MAX_OUTPUT_BYTES + 65536)
        # If the cap didn't cut it short, this would run for the full 15s timeout instead.
        self.assertLess(result.elapsed, 10.0)

    def test_large_stdin_interleaved_with_output_does_not_deadlock(self):
        # Reads and prints line-by-line rather than all at once, so a large enough input can fill
        # the stdout pipe while we're still writing stdin -- the scenario the concurrent
        # stdin-write/stdout-read threads in sandbox.run guard against.
        (self.workdir / "main.py").write_text(
            "import sys\n"
            "for line in sys.stdin:\n"
            "    sys.stdout.write(line)\n"
        )
        stdin = ("line %d\n" % i for i in range(200_000))
        payload = "".join(stdin).encode()

        result = sandbox.run(self.workdir, ["python3", "main.py"], stdin=payload, timeout=30.0)

        self.assertFalse(result.timed_out)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout, payload)

    def test_compiles_and_runs_java(self):
        (self.workdir / "Solution.java").write_text(
            "import java.util.Scanner;\n"
            "public class Solution {\n"
            "  public static void main(String[] args) {\n"
            "    Scanner sc = new Scanner(System.in);\n"
            "    System.out.println(sc.nextInt() + sc.nextInt());\n"
            "  }\n"
            "}\n"
        )

        compile_result = sandbox.run(self.workdir, ["javac", "Solution.java"], timeout=30.0)
        self.assertEqual(compile_result.returncode, 0, compile_result.stderr)

        run_result = sandbox.run(self.workdir, ["java", "Solution"], stdin=b"2 3", timeout=10.0)
        self.assertEqual(run_result.stdout.strip(), b"5")


if __name__ == "__main__":
    unittest.main()
