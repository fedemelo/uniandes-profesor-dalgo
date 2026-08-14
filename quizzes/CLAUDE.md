# Quiz architecture

Each `quizzes/N-nombre-kebab/` holds one quiz, split as:

```
quizzes/N-nombre-kebab/
  Quiz N - Nombre.pdf            (built)
  Solución quiz N - Nombre.pdf   (built)
  tex/
    problema.tex                 (statement, self-contained: what's asked IS the deliverable)
    quiz/
      N-nombre-kebab.tex         (quiz driver)
    solucion/
      N-nombre-kebab-solucion.tex (solution driver)
      solucion.tex
```

Quizzes differ from `homework/` (see `homework/CLAUDE.md`) in several ways:

- No standard-input/standard-output convention — quizzes are graded on the design, not on an automated judge.
- No `entrada-salida.tex` and no `entregables.tex` — `problema.tex` states directly what the student must produce, structured as two items (exact point split may vary per quiz, but the shape is fixed since it's graded on-site by a human, not a judge):
  1. **(0 puntos)** Lluvia de ideas — prosa, diagramas o pseudocódigo, lo que ayude a pensar el algoritmo. Not collected/graded, just scratch space.
  2. La implementación en un lenguaje de programación real (Python, Java, C, C++, JavaScript o TypeScript), worth the most points — written on the back of the sheet, in the grid `\quizback` produces (see below).
- No reference `.py` implementation — quizzes are handwritten/on-site, not autograded.
- Quizzes are numbered sequentially on their own track (`N` = quiz number), independent of homework week numbers — never say "semana" in a quiz title.
- No `\dateout`/`\duedate` (nothing is assigned or turned in remotely) — instead `\presentationdate`, since quizzes are presented on-site in class.
- Every quiz driver `\usepackage{quiz}` and ends with `\quizback` (after `\input{tex/problema}`, before `\end{document}`): it starts a fresh page with a full-page code grid, so the sheet prints statement-front / grid-back. Add no content after `\quizback`.

The quiz driver `\input`s only `tex/problema`. The solution driver `\input`s only `tex/solucion/solucion` (after `\soluciontrue`) — just the answer, no restated problem. The solution mirrors `problema.tex`'s items (item 1 has no solution to give — it's ungraded scratch space); it doesn't need `\quizback` since it isn't printed double-sided for students.

Both drivers set `\title`/`\professor`; only the quiz driver sets `\presentationdate`. Titles: `Quiz N: Nombre` / `Solución quiz N: Nombre`. Write the colon normally; the Makefile rewrites `": "` to `" - "` in the output filename (Bloque Neón rejects colons in filenames).

## Building

- `make qzN` — quiz + solution PDF for quiz N
- `make qzs` — every quiz

PDFs land at the quiz's root regardless of driver location.
