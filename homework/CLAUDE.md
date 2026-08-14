# Homework architecture

Each `homework/N-nombre-kebab/` holds one problem, split as:

```
homework/N-nombre-kebab/
  Tarea semana N - Nombre.pdf            (built)
  Solución tarea semana N - Nombre.pdf   (built)
  solucion_tarea_N.py                    (reference implementation)
  tex/
    problema.tex                         (statement)
    tarea/
      N-nombre-kebab.tex                 (assignment driver)
      entrada-salida.tex
      entregables.tex
    solucion/
      N-nombre-kebab-solucion.tex        (solution driver)
      solucion.tex
```

The assignment driver `\input`s `tex/problema`, then `tex/tarea/entrada-salida` and `tex/tarea/entregables`. The solution driver `\input`s only `tex/solucion/solucion` (after `\soluciontrue`) — just the answers, numbered to match `entregables.tex`'s items. Points on sub-items must sum to their parent item's points.

Both drivers set `\title`/`\professor`; only the assignment driver sets `\dateout`/`\duedate`. Titles: `Tarea semana N: Nombre` / `Solución tarea semana N: Nombre` (N = release week, not sequential — gaps are fine). Write the colon normally; the Makefile rewrites `": "` to `" - "` in the output filename (Bloque Neón rejects colons in filenames).

## Building

- `make hwN` — assignment + solution PDF for homework N
- `make hws` — every homework

`hw%` uses `tex/tarea/`/`tex/solucion/` as driver source dirs when present, else falls back to the homework root. PDFs always land at the homework root regardless.