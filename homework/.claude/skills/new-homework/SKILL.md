---
name: new-homework
description: Scaffolds a new homework problem end-to-end — statement, I/O contract, deliverables, and solution — following homework/CLAUDE.md's architecture. Use when asked to create, add, or draft a new homework/tarea.
---

Two steps, run from the repo root. homework/CLAUDE.md documents the file layout and conventions this skill produces — read it first if it isn't already in context.

## Step 0: scaffold

If the homework directory doesn't exist yet, get the week number, slug, and display name from the user (e.g. `6-ruta-optima`, "Ruta óptima"), then run:

    homework/scripts/new-homework.sh <N-slug> "<Nombre legible>"

This creates the full `tex/` skeleton (both drivers, empty `problema`/`entrada-salida`/`entregables`/`solucion`) per homework/CLAUDE.md's layout. It leaves `\dateout`/`\duedate` as `TODO` in the assignment driver — fill those in once the user gives real dates, or ask for them now.

## Step 1: statement + I/O

The user gives a rough, high-level description of the problem — a draft, not a finished spec. From it, write only:

- `tex/problema.tex` — the polished statement.
- `tex/tarea/entrada-salida.tex` — the Entrada/Salida contract (state only what's specific to this problem; never repeat the stdin/stdout convention itself, per homework/CLAUDE.md) plus one example with at least three worked cases (input + expected output). The example should be as small as possible while still illustrating the problem's key points, and the cases should cover edge conditions (empty input, single-element input, etc.) and any other interesting scenarios.

You can use /homework/1-recursion/tex/problema.tex and /homework/1-recursion/tex/tarea/entrada-salida.tex as examples of how to structure the statement and I/O contract.

Do not write `entregables.tex` yet, unless the user's draft already specifies deliverables. Build with `make hwN` and show the assignment PDF. This step is the one most likely to need back-and-forth — a vague draft rarely survives becoming a precise, unambiguous statement on the first pass, so iterate with the user before moving on.

Once the statement and examples are confirmed, ask the user for the deliverables (entregables): what's expected beyond the standard-I/O implementation baseline, if anything, and how points split across items.

## Step 2: entregables + solution

With the deliverables in hand, write:

- `tex/tarea/entregables.tex` — the numbered/lettered deliverable list with points (sub-items' points must sum to their parent item's).
    - You can use homework/1-recursion/tex/tarea/entregables.tex as an example of how deliverables should be structured.
- `tex/solucion/solucion.tex` — the solution, mirroring `entregables.tex`'s numbering item-for-item, as succinct as possible: no restated problem, no restated I/O, just the answers.
    - You can use homework/1-recursion/tex/solucion/solucion.tex as an example of how solutions should be structured.
- `solucion_tarea_N.py` — the reference implementation (stdin/stdout, per the baseline). Run it against the worked examples from Step 1 to confirm it actually produces the expected output before presenting it.

Build with `make hwN` and show both PDFs.

## Step 3: Committing the Homework

Once everything is said and done, and everything is tested, commit the new homework directory to the repo, **without committing the solutions**. Treat the solutions as a secret, the user must commit the solutions themselves, so they can choose at which point in time they are visible to the students (the repository is public).
