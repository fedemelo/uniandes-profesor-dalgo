\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{doc}[2026/07/03 Course doc template by fedemelo]

\LoadClass[11pt,letterpaper]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage[spanish]{babel}
\RequirePackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}
\RequirePackage{xcolor}
\RequirePackage{amsmath}
\RequirePackage{graphicx}
\RequirePackage{enumitem}
\RequirePackage{fancyhdr}
\RequirePackage[scaled]{helvet}
\RequirePackage[T1]{fontenc}
\RequirePackage{setspace}
\RequirePackage{ragged2e}
\RequirePackage{csquotes}
\RequirePackage{titlesec}
\RequirePackage{microtype}
\RequirePackage{menukeys}
\RequirePackage{course-config}

\definecolor{docgray}{RGB}{128, 128, 128}

\RequirePackage[colorlinks=true, linkcolor=docgray, urlcolor=docgray, citecolor=docgray]{hyperref}

\renewcommand{\familydefault}{\sfdefault}

% Helvetica's small-caps face has generous built-in tracking; tighten it
\SetTracking{encoding=*, shape=sc}{-40}

\setcounter{secnumdepth}{0}

\titleformat{\section}{\normalfont\normalsize\bfseries\scshape}{}{0pt}{}
\titleformat{\subsection}{\normalfont\normalsize\bfseries\scshape}{}{0pt}{}

\titlespacing*{\section}{0pt}{1.2em}{0pt}
\titlespacing*{\subsection}{0pt}{1em}{0pt}

\newcommand{\professor}[1]{\def\@professor{#1}}
\def\@professor{}

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

    \vspace{0.2cm}
    \begin{center}
        \textbf{\scshape\@title}
    \end{center}

    \vspace{0.1cm}
    \ifx\@professor\@empty\else
        \noindent{\scshape Profesor}: \@professor
    \fi
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
