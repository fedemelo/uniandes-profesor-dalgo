# Uniandes profesor: Dalgo

Exámenes, quizzes, tareas y anuncios que escribí como profesor del curso ISIS-2112: Diseño de Algoritmos de la Universidad de los Andes, desde agosto de 2026.

## Docs

| | Build all | Build one |
|---|---|---|
| `course-docs/` | `make course-docs` |`make <doc>` (docs: `policies`, `grupos`, `math-docs`, `latex-intro`, `std-input-output`) | 
| `homework/` | `make hws` | `make hw1` |
| `quizzes/` | `make qzs` | `make qz1` |
| `announcements/` | — | `make path/to/file.md` | 

Docs, homeworks, and quizzes are LaTeX, built off the shared `packages/` styles/classes.

Announcements aren't built — they're plain Markdown, and `make path/to/file.md` renders one to HTML on the clipboard as rich text, ready to paste into a Brightspace announcement.
