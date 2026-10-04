"""Generate the pre-parcial (mock exam) documents from a question bank.

Unlike exams/generate.py, there's no shuffling and no per-student variants:
each question slot has exactly one version per letter in `versions` (e.g. A
and B), and this script renders one full, static document per version —
version A gets every question's `vA.tex`, version B gets every question's
`vB.tex` — so students get two independent sets of practice problems.
"""

import argparse
import pathlib
import re
import sys
import tomllib
from typing import NamedTuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from scripts.latex_gen import compile_tex, grid_directive_lines, require_config_keys


class QuestionSlot(NamedTuple):
    """A question directory with one variant file per version letter."""

    name: str  # e.g., "q1"
    variants: dict[str, str]  # version letter -> path relative to repo root


def load_course_config(course_path: pathlib.Path) -> dict:
    """Load the course config shared with exams/ (semester, section)."""
    if not course_path.is_file():
        raise SystemExit(f"Error: Course config not found: {course_path}")

    with open(course_path, "rb") as f:
        config = tomllib.load(f)

    require_config_keys(config, {"course.semester": str, "course.section": int}, "course config")

    return config["course"]


def load_config(path: str) -> dict:
    """Load and validate a TOML pre-parcial configuration file."""
    config_path = pathlib.Path(path)
    if not config_path.is_file():
        raise SystemExit(f"Error: Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    required = {
        "pre_parcial.name": str,
        "pre_parcial.title": str,
        "pre_parcial.date": str,
        "pre_parcial.versions": list,
    }
    require_config_keys(config, required, "pre-parcial config")

    versions = config["pre_parcial"]["versions"]
    if len(versions) < 1 or any(not isinstance(v, str) for v in versions):
        raise SystemExit("Error: pre_parcial.versions must be a list of at least 1 version letter")

    return config


def scan_question_bank(
    base: pathlib.Path, repo_root: pathlib.Path, versions: list[str]
) -> tuple[list[QuestionSlot], str | None]:
    """Scan a pre-parcial's question bank directory (exams/pre-parcial-N/questions/).

    Returns (slots, preamble_path) where preamble_path is None if no preamble.tex exists.
    """
    if not base.is_dir():
        raise SystemExit(f"Error: Question bank directory not found: {base}")

    preamble = base / "preamble.tex"
    preamble_path = str(preamble.relative_to(repo_root)) if preamble.is_file() else None

    slots = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir() and entry.name.startswith("q"):
            variants = {}
            for version in versions:
                vfile = entry / f"v{version}.tex"
                if not vfile.is_file():
                    raise SystemExit(f"Error: Missing {vfile} for version {version}")
                variants[version] = str(vfile.relative_to(repo_root))
            slots.append(QuestionSlot(name=entry.name, variants=variants))

    if not slots:
        raise SystemExit(f"Error: No question directories (q*/) found in {base}")

    return slots, preamble_path


# Matches \question{N}, \gridquestion{N}, \namedgridquestion{N}
_SCORE_RE = re.compile(r"\\(?:named)?(?:grid)?question\{(\d+)\}")
_INPUT_RE = re.compile(r"\\input\{([^}]+)\}")


def _extract_score(variant_path: str, repo_root: pathlib.Path) -> int:
    """Extract the score (décimas) from a question variant .tex file.

    Follows one level of \\input if the variant delegates to a shared file.
    """
    full_path = repo_root / variant_path
    content = full_path.read_text(encoding="utf-8")

    match = _SCORE_RE.search(content)
    if match:
        return int(match.group(1))

    input_match = _INPUT_RE.search(content)
    if input_match:
        included = repo_root / (input_match.group(1) + ".tex")
        if included.is_file():
            included_content = included.read_text(encoding="utf-8")
            match = _SCORE_RE.search(included_content)
            if match:
                return int(match.group(1))

    raise SystemExit(
        f"Error: Could not extract score from {variant_path}. "
        "Expected \\question{{N}}, \\gridquestion{{N}}, or \\namedgridquestion{{N}}."
    )


def validate_scores(slots: list[QuestionSlot], repo_root: pathlib.Path) -> None:
    """Validate that every version of a question carries the same score.

    Unlike exams/generate.py, the total isn't required to sum to 50: the
    pre-parcial isn't graded, so there's no fixed point budget to hit.
    """
    for slot in slots:
        scores = {v: _extract_score(p, repo_root) for v, p in slot.variants.items()}
        if len(set(scores.values())) > 1:
            details = ", ".join(f"{v}={s}" for v, s in scores.items())
            raise SystemExit(
                f"Error: All versions of {slot.name} must have the same score. "
                f"Found: {details}. "
                "Version A and B should be equally-weighted practice for the same question."
            )


def version_title(pp_cfg: dict, course_cfg: dict, version: str) -> str:
    """The document title for one version, e.g. 'Ejemplo A de examen 1 -- 2026-20'.

    A pre-parcial is practice for the exam of the same number (pre-parcial 1
    for examen 1, etc.), so its title names that exam rather than itself —
    this is also used verbatim as the output PDF's filename.
    """
    return f"Ejemplo {version} de examen {pp_cfg['name']} -- {course_cfg['semester']}"


def render_version_tex(
    config: dict,
    course_cfg: dict,
    slots: list[QuestionSlot],
    version: str,
    preamble_path: str | None,
) -> str:
    """Render a single .tex file for one version (e.g. A or B) of the pre-parcial."""
    pp_cfg = config["pre_parcial"]
    grid_cfg = pp_cfg.get("grid", {})
    lines = [r"\documentclass{exam}"]

    if preamble_path is not None:
        lines.append(f"\\input{{{preamble_path}}}")

    lines.append("")
    lines.append(f"\\title{{{version_title(pp_cfg, course_cfg, version)}}}")
    lines.append(f"\\examdate{{{pp_cfg['date']}}}")
    lines.append("")
    lines.append(r"\begin{document}")
    lines.append(r"\makeexamheader")
    lines.append("")

    for slot in slots:
        lines.append(f"\\input{{{slot.variants[version]}}}")

        directive = grid_cfg.get(slot.name)
        if directive is not None:
            lines.extend(grid_directive_lines(slot.name, directive))

    lines.append("")
    lines.append(r"\end{document}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the pre-parcial (mock exam) documents from a question bank."
    )
    parser.add_argument("config", help="Path to TOML config file")
    parser.add_argument("--compile", action="store_true", help="Compile .tex to PDF")
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview the question bank without writing files"
    )
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parent.parent

    config = load_config(args.config)
    pp_cfg = config["pre_parcial"]
    pre_parcial_dir = pathlib.Path(args.config).resolve().parent
    course_cfg = load_course_config(repo_root / "exams" / "config" / "course.toml")

    versions = pp_cfg["versions"]
    questions_dir = pre_parcial_dir / "questions"
    slots, preamble_path = scan_question_bank(questions_dir, repo_root, versions)
    validate_scores(slots, repo_root)

    print(f"Pre-parcial: {pp_cfg['title']} -- {course_cfg['semester']}")
    print(f"Questions: {len(slots)}")
    for slot in slots:
        print(f"  {slot.name}: versions {', '.join(sorted(slot.variants))}")

    if args.dry_run:
        return

    if args.output_dir:
        output_dir = pathlib.Path(args.output_dir)
    else:
        output_dir = pre_parcial_dir / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    for version in versions:
        tex_content = render_version_tex(config, course_cfg, slots, version, preamble_path)
        tex_filename = f"{pp_cfg['name']}-pre-parcial-{version}.tex"
        tex_path = output_dir / tex_filename
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(tex_content)
        print(f"Written: {tex_path}")

        if args.compile:
            compile_tex(tex_path, repo_root)
            pdf_path = tex_path.with_suffix(".pdf")
            renamed_path = output_dir / f"{version_title(pp_cfg, course_cfg, version)}.pdf"
            pdf_path.rename(renamed_path)
            print(f"Renamed: {renamed_path}")

    print(f"\nDone. Output in {output_dir}/")


if __name__ == "__main__":
    main()
