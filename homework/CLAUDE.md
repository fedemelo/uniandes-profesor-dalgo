# Homework architecture

Each homework lives in `homework/N-nombre-kebab/` (N = 1-7) and contains:

- `N-nombre-kebab.tex` — assignment driver (statement only)
- `N-nombre-kebab-solucion.tex` — solution driver (statement + solution)
- `problemas.tex` — the single ordered list of `\input`s for that homework's problems, `\input` by both drivers
- `problemas/nombre-kebab/enunciado.tex` — one problem's statement
- `problemas/nombre-kebab/solucion.tex` — that problem's solution

Problem directories are named descriptively (kebab-case, no number prefix) — `problemas.tex` is the only place the problem order is written. Each entry looks like:

```latex
\input{homework/N-nombre-kebab/problemas/nombre-kebab/enunciado}
\ifsolucion
    \input{homework/N-nombre-kebab/problemas/nombre-kebab/solucion}
\fi
```

`\ifsolucion` is a boolean defined in `packages/doc.cls` (default false). The solution driver calls `\soluciontrue` before `\input{problemas}`; the assignment driver doesn't, so solution blocks are skipped there. Never fork `problemas.tex` or duplicate a problem's content between the two drivers — add the problem once under `problemas/` and both outputs pick it up.

Both drivers set `\title`, `\professor`, `\dateout`, `\duedate` (all from `doc.cls`) before `\makedocheader`.

## Building

- `make homeN` — assignment PDF only
- `make solN` — solution PDF only
- `make homeworks` — all 7 assignments
- `make soluciones` — all 7 solutions

## Adding a problem

Create `problemas/nombre-kebab/enunciado.tex` and `solucion.tex`, then append the two-line `\input`/`\ifsolucion` pair above to that homework's `problemas.tex`.

## What every problem requires

Every problem that asks for an implementation expects a classic algorithmic-judge submission: the program reads from standard input and writes to standard output — no function signatures, no file I/O. One program per problem, delivered as its own source file (never embedded in the statement or solution `.tex`).

This is the baseline for every problem's "qué se debe entregar" section. A problem may ask for additional deliverables on top of it (a proof, a complexity analysis, a written justification, etc.) — those are decided per problem and aren't part of this baseline.

### Input/output contract

Accepted languages: Python, Java, C++, JavaScript. Every problem statement's "Entrada"/"Salida" section should specify, precisely and unambiguously:

- **Entrada**: the first line gives the number of test cases; the format of each test case is defined by the problem.
- **Salida**: one line of output per test case, in the format the problem defines.

Each statement should also show how the grader invokes the solution, one line per accepted language, via shell redirection — never by passing the input as a command-line argument or opening files from within the program:

```
java Problema<Id> < entrada.in > salida.out
python problema<id>.py < entrada.in > salida.out
./problema<id> < entrada.in > salida.out     # C++, previously compiled
node problema<id>.js < entrada.in > salida.out
```

`<Id>`/`<id>` is the problem's identifier (e.g. `P0`), matched to the program's file/class name. Don't explain what `<`/`>` redirection means in the statement — that's covered once, for students, in `course-docs/entrada-salida` (built with `make entrada-salida`), which also has the worked Problema P0 example this convention is based on.
