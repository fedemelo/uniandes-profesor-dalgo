"""Generate unique exam variants from a question bank.

Given a question bank where each question slot can have multiple variant files,
this script generates N unique exams (one per student) that maximize diversity
in both question selection and ordering.

Output is a single .tex file containing all exams back-to-back, producing a
single PDF for easy printing.
"""

import argparse
import collections
import itertools
import math
import pathlib
import random
import re
import sys
import tomllib
from typing import NamedTuple

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from scripts.latex_gen import compile_tex, grid_directive_lines, require_config_keys


class QuestionSlot(NamedTuple):
    """A question directory with its available variant files."""

    name: str  # e.g., "q1"
    variants: list[str]  # paths relative to repo root, e.g., ["exams/exam-1/questions/q1/v1.tex"]


class ExamAssignment(NamedTuple):
    """A specific exam: which variant for each slot, in which order."""

    variant_indices: tuple[int, ...]  # which variant index per slot (in original q1..qN order)
    ordering: tuple[int, ...]  # permutation of slot indices defining question order


def load_course_config(course_path: pathlib.Path) -> dict:
    """Load the shared course configuration (semester, section, etc.)."""
    if not course_path.is_file():
        raise SystemExit(f"Error: Course config not found: {course_path}")

    with open(course_path, "rb") as f:
        config = tomllib.load(f)

    require_config_keys(config, {"course.semester": str, "course.section": int}, "course config")

    return config["course"]


def load_config(path: str) -> dict:
    """Load and validate a TOML exam configuration file."""
    config_path = pathlib.Path(path)
    if not config_path.is_file():
        raise SystemExit(f"Error: Config file not found: {config_path}")

    with open(config_path, "rb") as f:
        config = tomllib.load(f)

    required = {
        "exam.name": str,
        "exam.title": str,
        "exam.date": str,
        "exam.num_students": int,
        "exam.seed": int,
    }
    require_config_keys(config, required, "exam config")

    if config["exam"]["num_students"] < 1:
        raise SystemExit("Error: num_students must be >= 1")

    return config


def scan_question_bank(
    base: pathlib.Path, repo_root: pathlib.Path
) -> tuple[list[QuestionSlot], str | None]:
    """Scan an exam's question bank directory (exams/exam-N/questions/).

    Returns (slots, preamble_path) where preamble_path is None if no preamble.tex exists.
    """
    if not base.is_dir():
        raise SystemExit(f"Error: Question bank directory not found: {base}")

    preamble = base / "preamble.tex"
    preamble_path = str(preamble.relative_to(repo_root)) if preamble.is_file() else None

    slots = []
    for entry in sorted(base.iterdir()):
        if entry.is_dir() and entry.name.startswith("q"):
            variants = sorted(
                str(f.relative_to(repo_root))
                for f in entry.iterdir()
                if f.suffix == ".tex" and f.name.startswith("v")
            )
            if not variants:
                raise SystemExit(f"Error: No variant files (v*.tex) found in {entry}")
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

    # Follow \input to shared file
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
    """Validate that variant scores are consistent and total is exactly 50."""
    question_scores: list[int] = []

    for slot in slots:
        variant_scores = [
            _extract_score(v, repo_root) for v in slot.variants
        ]

        if len(set(variant_scores)) > 1:
            details = ", ".join(
                f"{pathlib.Path(v).name}={s}" for v, s in zip(slot.variants, variant_scores)
            )
            raise SystemExit(
                f"Error: All variants of {slot.name} must have the same score. "
                f"Found: {details}. "
                "Mixed exams cannot contain different point values for the same question."
            )

        question_scores.append(variant_scores[0])

    total = sum(question_scores)
    if total != 50:
        breakdown = ", ".join(
            f"{s.name}={sc}" for s, sc in zip(slots, question_scores)
        )
        raise SystemExit(
            f"Error: The total exam score must be exactly 50 décimas. "
            f"Got {total} ({breakdown})."
        )


def validate_prerequisites(
    prerequisites: dict, slots: list[QuestionSlot]
) -> dict[int, set[int]]:
    """Validate prerequisite config and convert question names to slot indices.

    Uses Kahn's algorithm to detect cycles in the dependency graph.
    Returns a mapping from slot index to set of prerequisite slot indices.
    """
    slot_name_to_idx = {s.name: i for i, s in enumerate(slots)}
    slot_names = set(slot_name_to_idx)

    prereq_indices: dict[int, set[int]] = {}

    for question, deps in prerequisites.items():
        if question not in slot_names:
            raise SystemExit(f"Error: prerequisite key '{question}' not found in question bank")
        if not isinstance(deps, list):
            raise SystemExit(f"Error: prerequisites for '{question}' must be a list, got {type(deps).__name__}")
        for dep in deps:
            if not isinstance(dep, str):
                raise SystemExit(f"Error: prerequisite values must be strings, got {type(dep).__name__}")
            if dep not in slot_names:
                raise SystemExit(f"Error: prerequisite '{dep}' for '{question}' not found in question bank")
            if dep == question:
                raise SystemExit(f"Error: '{question}' cannot be a prerequisite of itself")

        q_idx = slot_name_to_idx[question]
        prereq_indices[q_idx] = {slot_name_to_idx[d] for d in deps}

    # Cycle detection via Kahn's algorithm (topological sort)
    in_degree: dict[int, int] = collections.defaultdict(int)
    adjacency: dict[int, list[int]] = collections.defaultdict(list)
    all_nodes: set[int] = set()

    for q_idx, dep_indices in prereq_indices.items():
        all_nodes.add(q_idx)
        for dep_idx in dep_indices:
            all_nodes.add(dep_idx)
            adjacency[dep_idx].append(q_idx)
            in_degree[q_idx] += 1

    queue = collections.deque(n for n in all_nodes if in_degree[n] == 0)
    sorted_count = 0

    while queue:
        node = queue.popleft()
        sorted_count += 1
        for neighbor in adjacency[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if sorted_count != len(all_nodes):
        raise SystemExit("Error: prerequisite graph contains a cycle")

    return prereq_indices


def is_valid_ordering(ordering: tuple[int, ...], prerequisites: dict[int, set[int]]) -> bool:
    """Check whether an ordering respects all prerequisite constraints."""
    position = {slot_idx: pos for pos, slot_idx in enumerate(ordering)}
    return all(
        all(position[dep] < position[q] for dep in deps)
        for q, deps in prerequisites.items()
    )


def distance(a: ExamAssignment, b: ExamAssignment, num_questions: int) -> int:
    """Compute weighted distance between two exam assignments.

    Variant differences are weighted by num_questions, making question content
    differences much more significant than ordering differences.
    """
    variant_diff = sum(1 for va, vb in zip(a.variant_indices, b.variant_indices) if va != vb)
    order_diff = sum(1 for oa, ob in zip(a.ordering, b.ordering) if oa != ob)
    return variant_diff * num_questions + order_diff


def generate_exam_assignments(
    slots: list[QuestionSlot],
    num_students: int,
    seed: int,
    prerequisites: dict[int, set[int]] | None = None,
) -> list[ExamAssignment]:
    """Generate num_students maximally diverse exam assignments.

    Uses farthest-first traversal (greedy maximin dispersion) to select exams
    that are spread as far apart as possible in the (variant, ordering) space.
    If num_students exceeds how many unique exams the question bank supports,
    the maximally-diverse set is cycled to fill the remaining slots (so exams
    repeat, but each repeat is still spread out among distinct classmates).
    Only orderings that respect prerequisite constraints are considered.
    """
    if prerequisites is None:
        prerequisites = {}
    num_questions = len(slots)
    variants_per_slot = [len(s.variants) for s in slots]

    # Enumerate the full exam space (only orderings that respect prerequisites)
    variant_combos = list(itertools.product(*(range(v) for v in variants_per_slot)))
    orderings = [
        o for o in itertools.permutations(range(num_questions))
        if is_valid_ordering(o, prerequisites)
    ]

    total_space = len(variant_combos) * len(orderings)

    if total_space < num_students:
        print(
            f"Warning: Only {total_space:,} unique exams possible "
            f"({len(variant_combos):,} variant combos x {len(orderings):,} orderings), "
            f"but {num_students} requested. Reusing exams from the maximally-diverse "
            f"set to fill the rest."
        )

    all_exams = [
        ExamAssignment(variant_indices=vc, ordering=o)
        for vc in variant_combos
        for o in orderings
    ]

    # Farthest-first traversal for maximum diversity
    rng = random.Random(seed)
    first_idx = rng.randrange(len(all_exams))

    selected_indices = [first_idx]
    # min_dist[i] = minimum distance from exam i to any already-selected exam
    # -1 means already selected
    min_dist = [distance(all_exams[first_idx], all_exams[i], num_questions) for i in range(len(all_exams))]
    min_dist[first_idx] = -1

    unique_count = min(num_students, total_space)
    for _ in range(unique_count - 1):
        best_idx = max(range(len(all_exams)), key=lambda i: min_dist[i])
        selected_indices.append(best_idx)

        # Update min distances
        new_exam = all_exams[best_idx]
        for i in range(len(all_exams)):
            if min_dist[i] >= 0:
                d = distance(new_exam, all_exams[i], num_questions)
                if d < min_dist[i]:
                    min_dist[i] = d
        min_dist[best_idx] = -1

    # More students than unique exams exist: cycle back through the
    # maximally-diverse set already selected to fill the remaining slots.
    for i in range(num_students - unique_count):
        selected_indices.append(selected_indices[i % unique_count])

    return [all_exams[i] for i in selected_indices]


def format_exam_id(index: int, total: int) -> str:
    """Format exam ID with zero-padding based on total count."""
    width = max(3, len(str(total)))
    return str(index + 1).zfill(width)


def exam_title_line(title: str, exam_id: str, semester: str) -> str:
    return f"\\title{{{title} {exam_id} -- {semester}}}"


def render_all_exams_tex(
    assignments: list[ExamAssignment],
    config: dict,
    course_cfg: dict,
    slots: list[QuestionSlot],
    preamble_path: str | None,
) -> str:
    """Render a single .tex file containing all exams back-to-back."""
    exam_cfg = config["exam"]
    grid_cfg = exam_cfg.get("grid", {})
    semester = course_cfg["semester"]
    num_students = exam_cfg["num_students"]
    lines = [r"\documentclass{exam}"]

    if preamble_path is not None:
        lines.append(f"\\input{{{preamble_path}}}")

    lines.append("")
    lines.append(exam_title_line(exam_cfg["title"], format_exam_id(0, num_students), semester))
    lines.append(f"\\examdate{{{exam_cfg['date']}}}")
    lines.append("")
    lines.append(r"\begin{document}")

    for i, assignment in enumerate(assignments):
        exam_id = format_exam_id(i, num_students)

        lines.append("")
        lines.append(f"% ===== Exam {exam_id} =====")

        if i > 0:
            lines.append(r"\cleartoeven")
            lines.append(r"\setcounter{questioncounter}{0}")
            lines.append(r"\setcounter{page}{1}")
            lines.append(exam_title_line(exam_cfg["title"], exam_id, semester))

        lines.append(r"\makeexamheader")
        lines.append("")

        for slot_idx in assignment.ordering:
            slot = slots[slot_idx]
            variant_idx = assignment.variant_indices[slot_idx]
            variant_path = slot.variants[variant_idx]
            lines.append(f"\\input{{{variant_path}}}")

            directive = grid_cfg.get(slot.name)
            if directive is not None:
                lines.extend(grid_directive_lines(slot.name, directive))

    lines.append("")
    lines.append(r"\cleartoeven")

    lines.append(f"\\attendancesheet{{{exam_cfg['title']}}}{{{course_cfg['section']}}}")

    lines.append("")
    lines.append(r"\end{document}")
    lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate unique exam variants from a question bank."
    )
    parser.add_argument("config", help="Path to TOML config file")
    parser.add_argument("--compile", action="store_true", help="Compile .tex to PDF")
    parser.add_argument("--output-dir", help="Override output directory")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview assignments without writing files"
    )
    args = parser.parse_args()

    repo_root = pathlib.Path(__file__).resolve().parent.parent

    config = load_config(args.config)
    exam_cfg = config["exam"]
    exam_dir = pathlib.Path(args.config).resolve().parent
    course_cfg = load_course_config(repo_root / "exams" / "config" / "course.toml")

    questions_dir = exam_dir / "questions"
    slots, preamble_path = scan_question_bank(questions_dir, repo_root)
    validate_scores(slots, repo_root)

    num_students = exam_cfg["num_students"]
    seed = exam_cfg["seed"]

    prereq_cfg = config.get("prerequisites", {})
    prereq_indices = validate_prerequisites(prereq_cfg, slots)

    # Report question bank summary
    print(f"Exam: {exam_cfg['title']} -- {course_cfg['semester']}")
    print(f"Questions: {len(slots)}")
    for slot in slots:
        print(f"  {slot.name}: {len(slot.variants)} variant(s)")
    if prereq_indices:
        print("Prerequisites:")
        for q_idx, dep_indices in prereq_indices.items():
            deps = ", ".join(slots[d].name for d in dep_indices)
            print(f"  {slots[q_idx].name} requires: {deps}")

    variants_per_slot = [len(s.variants) for s in slots]
    num_valid_orderings = sum(
        1 for o in itertools.permutations(range(len(slots)))
        if is_valid_ordering(o, prereq_indices)
    )
    total_space = math.prod(variants_per_slot) * num_valid_orderings
    print(f"Total unique exams possible: {total_space:,}")
    print(f"Generating {num_students} exams (seed={seed})...")

    assignments = generate_exam_assignments(slots, num_students, seed, prereq_indices)

    if args.output_dir:
        output_dir = pathlib.Path(args.output_dir)
    else:
        output_dir = exam_dir / "output"

    if args.dry_run:
        for i, assignment in enumerate(assignments):
            exam_id = format_exam_id(i, num_students)
            print(f"\nexam {exam_id}:")
            for slot_idx in assignment.ordering:
                slot = slots[slot_idx]
                vi = assignment.variant_indices[slot_idx]
                print(f"  {slot.name}/{pathlib.Path(slot.variants[vi]).name}")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    tex_content = render_all_exams_tex(assignments, config, course_cfg, slots, preamble_path)
    tex_filename = f"{exam_cfg['name']}-exams.tex"
    tex_path = output_dir / tex_filename
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(tex_content)
    print(f"Written: {tex_path}")

    if args.compile:
        compile_tex(tex_path, repo_root)

    print(f"\nDone. Output in {output_dir}/")


if __name__ == "__main__":
    main()
