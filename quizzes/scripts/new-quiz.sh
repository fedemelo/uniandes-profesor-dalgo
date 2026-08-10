#!/usr/bin/env bash
# Scaffolds a new quiz's file tree under quizzes/, per the architecture
# documented in quizzes/CLAUDE.md. Writes only skeleton .tex files (drivers,
# empty problema/solucion); no problem content.
#
# Usage: new-quiz.sh <N-slug> "<Nombre legible>"
#   e.g. new-quiz.sh 1-conteo-inversiones "Conteo de inversiones"

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <N-slug> \"<Nombre legible>\"" >&2
    exit 1
fi

dir_name=$1
nombre=$2

if [[ ! $dir_name =~ ^([0-9]+)-([a-z0-9-]+)$ ]]; then
    echo "Error: '$dir_name' must look like '<N>-<slug-kebab>', e.g. '1-conteo-inversiones'" >&2
    exit 1
fi

n=${BASH_REMATCH[1]}

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
quiz_dir="$repo_root/quizzes/$dir_name"

if [[ -e $quiz_dir ]]; then
    echo "Error: $quiz_dir already exists" >&2
    exit 1
fi

mkdir -p "$quiz_dir/tex/quiz" "$quiz_dir/tex/solucion"

cat > "$quiz_dir/tex/problema.tex" <<EOF
\\section{Problema}
EOF

: > "$quiz_dir/tex/solucion/solucion.tex"

cat > "$quiz_dir/tex/quiz/$dir_name.tex" <<EOF
% !TeX spellcheck = es_ANY
\\documentclass{doc}

\\usepackage{fmbdalgo}
\\usepackage{quiz}

\\title{Quiz $n: $nombre}
\\professor{Federico Melo Barrero}
\\presentationdate{TODO}

\\begin{document}
\\makedocheader
\\quizidentification
\\input{quizzes/$dir_name/tex/problema}
\\quizback

\\end{document}
EOF

cat > "$quiz_dir/tex/solucion/$dir_name-solucion.tex" <<EOF
% !TeX spellcheck = es_ANY
\\documentclass{doc}

\\usepackage{fmbdalgo}

\\title{Solución quiz $n: $nombre}
\\professor{Federico Melo Barrero}

\\begin{document}
\\makedocheader
\\soluciontrue
\\input{quizzes/$dir_name/tex/solucion/solucion}

\\end{document}
EOF

echo "Created $quiz_dir"
