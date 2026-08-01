# Homework architecture

Each homework lives in `homework/N-nombre-kebab/` (N = 1-7) and contains:

- `N-nombre-kebab.tex` — assignment driver (statement only)
- `N-nombre-kebab-solucion.tex` — solution driver (statement + solution)
- `problemas.tex` — the single ordered list of `\input`s for that homework's problems, `\input` by both drivers
- `problemas/M-nombre-problema/enunciado.tex` — problem M's statement
- `problemas/M-nombre-problema/solucion.tex` — problem M's solution

`problemas.tex` is the only place the problem list/order is written. Each entry looks like:

```latex
\input{homework/N-nombre-kebab/problemas/M-nombre-problema/enunciado}
\ifsolucion
    \input{homework/N-nombre-kebab/problemas/M-nombre-problema/solucion}
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

Create `problemas/M-nombre-problema/enunciado.tex` and `solucion.tex`, then append the two-line `\input`/`\ifsolucion` pair above to that homework's `problemas.tex`.
