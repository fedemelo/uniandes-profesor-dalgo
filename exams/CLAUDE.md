# Exam architecture

Ported from the Introducción a la Programación course's exam generator, which
had to shuffle many question variants per student. This course doesn't need
that — one question per point, no variants — but the scaffolding is kept as
is so a future exam can add variants/shuffling without a rewrite.

```
exams/
  config/
    course.toml         (shared: semester, section)
  exam-N/
    config.toml           (name, title, date, num_students, seed, optional prerequisites)
    questions/
      preamble.tex          (optional: extra \usepackage lines for this exam)
      q1/
        v1.tex               (question content; v2.tex etc. for variants, unused for now)
      q2/
        v1.tex
      ...
    output/
      N-exams.tex           (generated)
      N-exams.pdf           (generated)
    past-exam-N/           (reference material: the actual exam N from a prior semester)
  pre-parcial-N/           (see "Pre-parciales" below)
```

`generate.py exams/exam-N/config.toml` scans `exams/exam-N/questions/q*/`,
reads each slot's variant(s), and renders `num_students` exams back-to-back
into one `.tex`/`.pdf` (one exam per student when shuffling variants/ordering;
with a single variant per question and `num_students = 1`, it just renders
that one exam). Each question file must end in `\question{décimas}{...}` (or
delegate via `\input` to a file that does) — `generate.py` reads the score
from there and requires every exam's décimas to sum to exactly 50.

Question files use the `exam` document class (`packages/exam.cls`): wrap each
question in `\begin{halfpage}...\end{halfpage}` (keeps two questions per page)
and write it as `\question{décimas}{enunciado}`.

## Building

`make examN` — e.g. `make exam1` runs `exams/exam-1/config.toml` through
`generate.py --compile`, writing to `exams/exam-1/output/`.

Or run `generate.py` directly for more control (`--dry-run` to preview
assignments without writing files, `--output-dir` to override the output
location).

## Pre-parciales

A pre-parcial is a mock exam handed out as practice material, not a graded
exam. It reuses the exam's look and feel (`packages/exam.cls`, same header,
integrity block, instructions) but its generator (`generate_pre_parcial.py`)
is much simpler than the real exam's: no per-student shuffling, no
prerequisites, no score-sum requirement — because nothing here is randomized
or graded.

Each question slot carries exactly one variant per version letter (e.g. `A`
and `B`, configurable), and `generate_pre_parcial.py` renders one full,
static document per version: version A is every question's `vA.tex`
back-to-back, version B is every question's `vB.tex`. So question 1 shows up
as "1A" in one document and "1B" in the other — different problems on the
same topic, not shuffled variants of one problem like in the real exam.

```
exams/pre-parcial-N/
  config.toml            (name, title, date, versions = ["A", "B", ...])
  questions/
    preamble.tex           (optional: extra \usepackage lines for this pre-parcial)
    q1/
      vA.tex                 (question content, version A)
      vB.tex                 (question content, version B)
    q2/
      vA.tex
      vB.tex
    ...
  output/
    N-pre-parcial-A.tex               (generated)
    Ejemplo A de examen N -- YYYY-S.pdf
    N-pre-parcial-B.tex               (generated)
    Ejemplo B de examen N -- YYYY-S.pdf
```

The `.tex` files keep the plain `N-pre-parcial-<version>` name, but each
compiled PDF is renamed to its document title — `Ejemplo <version> de examen
N -- <semester>` (a pre-parcial is practice for the exam of the same number,
so its title names that exam, not itself) — the same way `title`/`\title`
drive the renamed output elsewhere in this repo (homework, quizzes).

The shared course config (`exams/config/course.toml`) is reused as-is rather
than duplicated per pre-parcial. Score consistency is still checked (a
question's A and B versions must carry the same décimas), but unlike exams
there's no requirement that the total add up to 50 — this document isn't
graded.

`make preparcialN` — e.g. `make preparcial1` runs
`exams/pre-parcial-1/config.toml` through `generate_pre_parcial.py --compile`,
writing every version's document to `exams/pre-parcial-1/output/`. Versions
missing their question files simply aren't buildable yet — list only the
versions with content in `config.toml`'s `versions` key (e.g. `["A"]` while
version B is still being written), and add the rest once they exist.

Each question also gets a blank answer space after it, laid out per
`[pre_parcial.grid]` in `config.toml` (keyed by slot name, e.g. `q1 = "..."`),
using `packages/programming-grid.sty`'s auto-sizing grid (already pulled in by
`exam.cls`). Three directives, chosen per question by how much space its
answer needs and how much room its statement already takes on the page:
- `"own_page"`: break to a fresh page, fill that whole page with a grid, break
  again — for a statement that already nearly fills its own page, so the grid
  needs a dedicated page.
- `"blank"`: just break to a fresh page, no grid — for a short prose/trace
  answer that only needs whatever blank space is left, not a code grid.
- `"inline"`: fill the rest of the *current* page with a grid, no forced
  break — for a short statement, so statement and grid share one page.

Omitting a slot from `[pre_parcial.grid]` leaves it with no forced break or
grid, flowing straight into the next question.

## Shared code

Compilation (`compile_tex`) and TOML key validation (`require_config_keys`)
are shared between `generate.py` and `generate_pre_parcial.py` via
`scripts/latex_gen.py` (repo root), rather than duplicated.
