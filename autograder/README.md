# Autograder

Grades homework code submissions (Python, Java, or C) against the test cases under
`homework/N-nombre/tests/`, running untrusted student code inside sandboxed, network-disabled
Docker containers.

Not covered here: Brightspace API integration (submissions are downloaded by hand for now),
grading the PDF portion of each deliverable (stays manual), and converting a pass count into an
actual point value in the gradebook (also manual).

Each homework's `entrada-salida.tex` requires a single file, stdin/stdout only. A Java submission
using a `package` declaration or split across multiple `.java` files won't compile/run here as a
result (it's staged and compiled standalone) — that's the student not following the stated
contract, treated as an earned failure rather than something the autograder works around.

## Setup

Build the sandbox image once (and again whenever `docker/Dockerfile` changes):

```
docker build -t dalgo-autograder autograder/docker
```

## Downloading submissions

In Brightspace, open the assignment's submissions and download all of them as a zip. The zip
contains a subfolder per student, each with the student's code file and PDF, sometimes zipped
again by the student themselves.

Drop that zip, unmodified, into:

```
autograder/submissions/<homework-slug>/
```

e.g. `autograder/submissions/2-dividir-y-conquistar/Tarea semana 2 ... .zip`. Exactly one zip
should live in that folder at a time.

## Grading

```
python3 -m autograder.grader.cli 2-dividir-y-conquistar
```

Run from the repo root. This extracts the zip into `autograder/work/` (scratch, wiped on every
run), locates each student's code file, detects its language, compiles it if needed, and runs
it against every `homework/2-dividir-y-conquistar/tests/case_*.in` fixture inside a fresh
container per run (`--rm`, `--network none`, memory/CPU/PID limits, no new privileges, dropped
capabilities). Submissions are graded concurrently (`--workers`, default 8); test cases within one
submission run sequentially.

The per-test-case timeout is auto-calibrated from the reference solution's own slowest case
(20x margin) unless `--timeout` is passed explicitly. A pass/fail summary prints to stdout;
`autograder/results/<homework-slug>/<timestamp>.csv` (gradebook-friendly summary),
`<timestamp>.json` (per-case pass/fail, elapsed time, return code), and `<timestamp>-meta.json`
(run provenance, see below) are all saved together.

Useful flags: `--timeout`, `--zip` (skip auto-discovery in `submissions/`), `--workers`.

### Complexity check

A correctness-only grading pass can't tell a genuinely `O(n log n)` solution from an `O(n^2)` one
that's just fast enough to sneak under the timeout at the stated max `n` (verified: a
deliberately-quadratic Python submission was flagged cleanly by this check even in a case where it
happened to also fail two correctness cases on timeout — the complexity check's diagnosis was
unambiguous where the raw pass count alone would have looked like "two wrong answers"). It times
both the reference solution and every submission across a doubling size schedule and flags anyone
whose time at the largest size is far above the reference's.

This runs **automatically** after every `cli.py` grading run, for any homework with an entry in
`scaling.SCALERS` (currently `2-dividir-y-conquistar` — see "Notes for extending" below to add
another), sharing that run's timestamp. Pass `--skip-complexity` to skip it. It saves
`<timestamp>-complexity.csv` and `<timestamp>-complexity-meta.json` alongside the grading output.

To re-run just the complexity check on its own (e.g. with a different `--sizes` schedule, without
re-grading correctness):

```
python3 -m autograder.grader.complexity_cli 2-dividir-y-conquistar
```

## Run provenance

Every grading or complexity run also saves a `*-meta.json`: which zip was graded (name + SHA-256),
which autograder git commit ran it (and whether the working tree was dirty), which Docker image ID
was used, and the grading parameters (timeout/threshold/sizes). If a student disputes a grade
later, this is what lets you reconstruct exactly what happened — the CSV/JSON results and their
meta file share the same timestamp.

## Testing

```
python3 -m unittest discover -s autograder/tests -t .
```

Most tests are pure Python (zip-bomb rejection, Brightspace folder/timestamp parsing, language
detection and staging, doubling-schedule input generation) — no Docker needed, safe to run
anywhere. `test_sandbox_integration.py` runs real containers against tiny synthetic snippets
(never real student data) to check the sandboxing guarantees that actually matter — timeout
actually kills the container, network is actually disabled, each language actually compiles and
runs. It auto-skips if Docker isn't running or the image isn't built.

## Notes for extending

- `grader/languages.py` is where Python/Java/C support lives — add a `Language` subclass and
  register it in `REGISTRY` to support another language.
- `grader/scaling.py`'s `SCALERS` dict is what wires a homework into the complexity check — add an
  entry mapping the homework slug to (seed test case filename, a function that builds a
  smaller-`n` input by scaling down that seed) to extend it to another homework.
- `submissions/`, `work/`, and `results/` are gitignored — they hold real student names and code,
  which shouldn't be committed.
