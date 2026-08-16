---
name: generate-test-cases
description: Builds a homework's grading test suite (handcrafted edge cases plus oracle-generated random cases) from its finished statement and reference solution. Use when asked to generate, build, or create test cases for a homework.
---

Builds `homework/N-nombre/tests/` for one homework: a set of stdin/stdout fixture pairs suitable for automated grading. Run from the repo root.

## Step 0: preconditions

This skill only works on a *finished* homework. Before doing anything else, verify all three exist for the target `N-nombre`:

- `tex/problema.tex` and `tex/tarea/entrada-salida.tex` — a real statement and I/O contract, not scaffolding placeholders.
- `tex/solucion/solucion.tex` (and ideally the built "Solución ..." PDF) — the answer key.
- `solucion_tarea_N.py` (or equivalent) — a working reference implementation that reads stdin and writes stdout per the stated convention.

If any of these is missing, empty, or still a TODO placeholder, **stop immediately and report exactly what's missing** to the user. Do not draft a statement, write a solution, or otherwise fill the gap yourself — that's the `new-homework` skill's job, on a separate request.

Do not evaluate, test, or second-guess the correctness of the statement, the solution writeup, or the reference implementation. Treat all three as ground truth. Your job is only to read them for understanding, and to trust the reference implementation's stdout as the correct expected output for whatever you feed it.

## Step 1: understand the problem

Read `tex/problema.tex` and `tex/tarea/entrada-salida.tex` to extract:

- The exact input/output format (this homework's part of the shared stdin/stdout convention).
- Every stated constraint and its bounds (e.g. `1 ≤ n ≤ 10^5`, value ranges, guarantees like "at least one valid sequence exists").
- The algorithmic technique the homework targets (recursion, divide-and-conquer, etc.) — this tells you which failure modes are worth probing on purpose.

## Step 2: handcraft edge and boundary cases

Write these by hand, thinking like a problem-setter, not a fuzzer:

- Boundary values of every constrained parameter: smallest allowed, largest allowed, and values just inside/outside guarantees stated in the problem.
- Degenerate structures: empty input where legal, single-element input, all-equal elements, already-sorted / reverse-sorted, all-zero, all-negative, all-positive.
- Failure modes specific to the technique being tested: e.g. overflow-adjacent values for arithmetic problems, patterns known to break naive (non-divide-and-conquer) implementations of the technique, cases where a greedy or off-by-one shortcut would produce a plausible-but-wrong answer.
- The worked example(s) already published in `entrada-salida.tex` — include them too, as a sanity baseline.

Each handcrafted case should target one thing; keep them small enough to reason about by hand.

## Step 3: generate randomized cases

Write a small generator script, `tests/generate.py`, parameterized by size and value range, and use it to produce additional cases biased toward:

- Small `n`, many of them — for broad structural coverage.
- Maximum `n` per the stated constraints — for performance/stress testing.

Do not sample uniformly over the whole input space as the only strategy — bias generation toward the boundary/degenerate shapes from Step 2 rather than treating volume alone as coverage.

## Step 4: produce expected outputs

Run every case (handcrafted and generated) through the reference implementation via stdin/stdout, exactly as a grader would invoke it. Its stdout is the expected output — do not inspect it for plausibility or recompute it by hand.

## Step 5: save fixtures

Write each case as a pair under `homework/N-nombre/tests/`:

```
tests/
  generate.py
  case_01.in
  case_01.out
  case_02.in
  case_02.out
  ...
```

Number them in the order written across Steps 2–3 (handcrafted cases first, then generated ones). Keep `generate.py` reproducible — re-running it (or re-running it with adjusted parameters) should be enough to regenerate or extend the random batch later, without redoing Step 3 from scratch.

## Step 6: report

Summarize what was produced: how many cases, and one line per handcrafted case naming what it targets (skip this per-case listing for the generated batch — just state the count and size range). This is for the user to sanity-check coverage before trusting the suite for grading.

## Step 7: committing

The `.out` files are produced by the reference solution and the `.in`/`.out` pairing together can hint at the intended algorithm, so treat the fixtures the same as solutions: do not commit them yourself. Leave that to the user, per the same reasoning in `new-homework`'s Step 3.

`generate.py` is different — it only produces inputs, not answers, so it doesn't leak the algorithm. It's fine to commit alongside the fixtures once the user commits those, but still let the user make that call rather than committing it unprompted.
