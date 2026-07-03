\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{doc}[2026/07/03 Course doc template by fedemelo]

\LoadClass[11pt,letterpaper]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage[spanish]{babel}
\RequirePackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{enumitem}
\RequirePackage{fancyhdr}
\RequirePackage{helvet}
\RequirePackage[T1]{fontenc}
\RequirePackage{setspace}
\RequirePackage{ragged2e}
\RequirePackage{titlesec}
\RequirePackage{course-config}

\renewcommand{\familydefault}{\sfdefault}

\titlespacing*{\section}{0pt}{1.2em}{0.5em}
\titlespacing*{\subsection}{0pt}{1em}{0.3em}

\definecolor{docgray}{RGB}{128, 128, 128}

\newcommand{\professor}[1]{\def\@professor{#1}}
\newcommand{\@professor}{}

\newcommand{\makedocheader}{
    \pagestyle{plain}

    \begin{minipage}[T]{0.25\textwidth}
        \includegraphics[width=\textwidth]{inge-uniandes.png}
    \end{minipage}%
    \hfill
    \begin{minipage}[T]{0.45\textwidth}
        \centering
        \textbf{\department}\\[0.5em]
        \textcolor{docgray}{\@course}
    \end{minipage}%
    \hfill
    \begin{minipage}[T]{0.25\textwidth}
        \raggedleft
        \includegraphics[width=\textwidth]{abet.png}
    \end{minipage}

    \flushright
    \@date

    \vspace{0.2cm}
    \centering

    \textbf{\Large\@title}

    \vspace{0.2cm}
    \flushleft

    Profesor: \@professor

    \vspace{0.4cm}
}

\setlist[itemize]{
    leftmargin=20pt,
    itemsep=6pt,
    parsep=0pt,
    topsep=3pt,
    partopsep=0pt,
    label=\textbullet
}

\setlist[enumerate]{
    leftmargin=20pt,
    itemsep=6pt,
    parsep=0pt,
    topsep=3pt,
    partopsep=0pt
}

\setlength{\parindent}{0pt}
\setlength{\parskip}{6pt plus 2pt minus 1pt}

\endinput
