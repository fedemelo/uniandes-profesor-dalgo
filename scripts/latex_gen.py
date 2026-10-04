"""Shared helpers for the TOML-driven LaTeX generators (exams/generate.py,
pre-parcial/generate.py): config-key validation, the answer-space grid
directives used by both, and two-pass pdflatex compilation with
minted/shell-escape support.
"""

import os
import pathlib
import shutil
import subprocess

# How a question slot's answer space is laid out on paper, driven by a
# `grid` config table keyed by slot name (e.g. `q1 = "own_page"`), used by
# both exams/generate.py and exams/generate_pre_parcial.py:
#   "own_page": force a page break, fill that whole new page with a grid, then
#               break again --- for a question whose statement already nearly
#               fills a page, so the grid needs a dedicated page of its own.
#   "blank":    just force a page break, no grid --- for a question whose
#               answer is short prose/trace, not code, so it only needs
#               whatever blank space is left on its own page.
#   "inline":   fill the remaining space on the *same* page with a grid, no
#               forced break --- for a question whose statement is short
#               enough that statement + grid both fit on one page.
# A slot omitted from the config gets no forced break or grid, flowing
# straight into the next question.
GRID_DIRECTIVES = {
    "own_page": [r"\newpage", r"\programmingGrid", r"\newpage"],
    "blank": [r"\newpage"],
    "inline": [r"\programmingGrid"],
}


def grid_directive_lines(slot_name: str, directive: str) -> list[str]:
    """Return the .tex lines for a slot's grid directive, validating it's known."""
    if directive not in GRID_DIRECTIVES:
        raise SystemExit(
            f"Error: Unknown grid directive '{directive}' for {slot_name}. "
            f"Expected one of: {', '.join(GRID_DIRECTIVES)}."
        )
    return GRID_DIRECTIVES[directive]


def require_config_keys(config: dict, required: dict[str, type], context: str) -> None:
    """Validate that each dotted key in `required` is present in `config` with the right type."""
    for dotted_key, expected_type in required.items():
        parts = dotted_key.split(".")
        val = config
        for part in parts:
            if not isinstance(val, dict) or part not in val:
                raise SystemExit(f"Error: Missing required {context} key: {dotted_key}")
            val = val[part]
        if not isinstance(val, expected_type):
            raise SystemExit(
                f"Error: {context} key {dotted_key} must be {expected_type.__name__}, "
                f"got {type(val).__name__}"
            )


def compile_tex(tex_path: pathlib.Path, repo_root: pathlib.Path) -> None:
    """Compile a .tex file to PDF with pdflatex, two passes (minted/Pygments needs the first
    pass to generate its output before the second pass can read it), then clean up aux files.
    """
    pdflatex = shutil.which("pdflatex")
    if pdflatex is None:
        raise SystemExit("Error: pdflatex not found in PATH")

    output_dir = tex_path.parent
    packages_dir = repo_root / "packages"
    texinputs = f"{packages_dir}:{repo_root}:{os.environ.get('TEXINPUTS', '')}"
    env = {**os.environ, "TEXINPUTS": texinputs}

    cmd = [
        pdflatex,
        "-shell-escape",
        "-interaction=nonstopmode",
        tex_path.name,
    ]

    for pass_num in (1, 2):
        print(f"Compiling {tex_path.name} (pass {pass_num}/2)...", end=" ", flush=True)
        result = subprocess.run(cmd, cwd=str(output_dir), env=env, capture_output=True)

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")

        if result.returncode != 0 and pass_num == 2:
            print("FAILED")
            log_path = output_dir / (tex_path.stem + ".compile.log")
            with open(log_path, "w") as f:
                f.write(stdout)
                f.write("\n--- STDERR ---\n")
                f.write(stderr)
            raise SystemExit(f"Compilation failed. See {log_path} for details.")

        print("OK")

    for ext in ("aux", "log", "out"):
        for f in output_dir.glob(f"*.{ext}"):
            f.unlink()
    minted_dir = output_dir / f"_minted-{tex_path.stem}"
    if minted_dir.is_dir():
        shutil.rmtree(minted_dir)
