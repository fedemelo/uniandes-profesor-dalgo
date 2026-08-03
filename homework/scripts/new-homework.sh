#!/usr/bin/env bash
# Scaffolds a new homework's file tree under homework/, per the architecture
# documented in homework/CLAUDE.md. Writes only skeleton .tex files (drivers,
# empty problema/entrada-salida/entregables/solucion); no problem content.
#
# Usage: new-homework.sh <N-slug> "<Nombre legible>"
#   e.g. new-homework.sh 6-ruta-optima "Ruta óptima"

set -euo pipefail

if [[ $# -ne 2 ]]; then
    echo "Usage: $0 <N-slug> \"<Nombre legible>\"" >&2
    exit 1
fi

dir_name=$1
nombre=$2

if [[ ! $dir_name =~ ^([0-9]+)-([a-z0-9-]+)$ ]]; then
    echo "Error: '$dir_name' must look like '<N>-<slug-kebab>', e.g. '6-ruta-optima'" >&2
    exit 1
fi

n=${BASH_REMATCH[1]}

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
hw_dir="$repo_root/homework/$dir_name"

if [[ -e $hw_dir ]]; then
    echo "Error: $hw_dir already exists" >&2
    exit 1
fi

mkdir -p "$hw_dir/tex/tarea" "$hw_dir/tex/solucion"

cat > "$hw_dir/tex/problema.tex" <<EOF
\\section{Problema}
EOF

cat > "$hw_dir/tex/tarea/entrada-salida.tex" <<EOF
\\subsection{Entrada y salida}
EOF

cat > "$hw_dir/tex/tarea/entregables.tex" <<EOF
\\subsection{Entregables}
EOF

: > "$hw_dir/tex/solucion/solucion.tex"

cat > "$hw_dir/tex/tarea/$dir_name.tex" <<EOF
% !TeX spellcheck = es_ANY
\\documentclass{doc}

\\usepackage{fmbdalgo}

\\title{Tarea semana $n: $nombre}
\\professor{Federico Melo Barrero}
\\dateout{TODO}
\\duedate{TODO}

\\begin{document}
\\makedocheader
\\input{homework/$dir_name/tex/problema}
\\input{homework/$dir_name/tex/tarea/entrada-salida}
\\input{homework/$dir_name/tex/tarea/entregables}

\\end{document}
EOF

cat > "$hw_dir/tex/solucion/$dir_name-solucion.tex" <<EOF
% !TeX spellcheck = es_ANY
\\documentclass{doc}

\\usepackage{fmbdalgo}

\\title{Solución tarea semana $n: $nombre}
\\professor{Federico Melo Barrero}

\\begin{document}
\\makedocheader
\\soluciontrue
\\input{homework/$dir_name/tex/solucion/solucion}

\\end{document}
EOF

echo "Created $hw_dir"
