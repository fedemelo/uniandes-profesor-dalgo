---
name: run-autograder
description: Runs autograder/ against one homework's Brightspace submissions, checking the preconditions first and interpreting the grading + complexity-check output afterward. Use when asked to grade, run the autograder on, or check submissions for a homework.
---

Grades one homework's downloaded submissions in the Docker-sandboxed autograder under `autograder/`. Run from the repo root. `autograder/README.md` documents the full design — this skill is the operational checklist for actually running it.

## Step 0: preconditions

- Docker is running (`docker info`), and the sandbox image is built: `docker image inspect dalgo-autograder`. If missing, `docker build -t dalgo-autograder autograder/docker` (only needed once, or after `autograder/docker/Dockerfile` changes).
- `homework/N-nombre/tests/` has fixtures (`case_*.in`/`.out`) and `solucion_tarea_N.py` exists — if not, that's `generate-test-cases`' job, not this skill's.
- Exactly one zip sits in `autograder/submissions/N-nombre/`, downloaded by hand from Brightspace's assignment submissions page. If it's missing or there's more than one, stop and ask the user for it rather than guessing which to use.

## Step 1: if the tests were just regenerated, check the complexity-check seed

Skip this step unless `homework/N-nombre/tests/` changed in this session (e.g. via `generate-test-cases`, or a manual case renumbering).

`autograder/grader/scaling.py`'s `SCALERS` dict hardcodes a *seed filename* per homework (e.g. `"case_17.in"`) that the complexity check truncates down to smaller sizes. It does not reference cases by content or size, only by filename — so renumbering or regenerating a homework's test cases silently breaks it (it'll fail loudly at complexity-check time with "requested n=... exceeds seed case size ...", or worse, silently truncate a differently-shaped case).

If the homework has an entry in `SCALERS`, verify its seed filename still exists under `homework/N-nombre/tests/` and is large enough (its `n` must be $\geq$ the largest size in `scaling.DEFAULT_SIZES`, currently 100,000) and still matches the scaler function's expected per-case grammar (read the scaler, e.g. `truncate_array_case`, to see what it expects). Update the filename in `SCALERS` if the case it pointed to no longer exists or no longer fits.

## Step 2: run it

```
python3 -m autograder.grader.cli N-nombre
```

Useful flags: `--zip <path>` (skip auto-discovery), `--timeout <seconds>` (skip auto-calibration), `--workers <n>` (default 8), `--skip-complexity`. To re-run just the complexity check afterward (e.g. with a different `--sizes` schedule): `python3 -m autograder.grader.complexity_cli N-nombre`.

## Step 3: interpret and report

Report to the user, in order:

1. **Pass/fail summary** — who got full marks, who didn't, and how far short (e.g. `5/13` not just "failed"). Call out anyone with `no_code_file`, `unsupported_language`, `compile_error`, or `error` status by name — these need a human look, not just a low score.
2. **Complexity check**, if it ran (the homework needs a `SCALERS` entry — if it doesn't and the homework has a stated complexity requirement, say so rather than silently letting it be skipped). Anyone `flagged` is suspected of the wrong asymptotic complexity even though they may have passed correctness; say which ones and why (fell short of the reference's reached size, or exceeded the time threshold at the same size).
3. Where results landed: `autograder/results/N-nombre/<timestamp>.csv`/`.json` (+ `-complexity.csv` if it ran) and the `-meta.json` provenance files, for the record if a grade is disputed later.

Don't hand-interpret a submission's specific bug from the summary alone — if the user wants to know *why* someone failed, read that submission's per-case results from the saved `.json` (stdout/stderr/returncode per case) rather than guessing from the pass count.
