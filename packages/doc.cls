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
\RequirePackage{dirtytalk}
\RequirePackage{amssymb}  % Symbols and fonts. Includes amsfonts.
\RequirePackage{amsthm}  % Theorem setups with \theoremstyle, \proof and \qedsymbol.
\RequirePackage{mathtools}  % amsmath package extension with bug fixes. Includes amsmath, which includes amsbsy (\boldsymbol and fake boldface \pmb), amsopn (operator names with \DeclareMathOperator) and amstext (text in mathmode with \text).
\RequirePackage{forest}  % Draw trees

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

\newcommand{\dateout}[1]{\def\@dateout{#1}}
\def\@dateout{}

\newcommand{\duedate}[1]{\def\@duedate{#1}}
\def\@duedate{}

\newif\ifsolucion
\solucionfalse

\newcommand{\makedocheader}{
    \pagestyle{plain}

    \begin{minipage}[T]{0.25\textwidth}
        \includegraphics[width=0.84\textwidth]{inge-uniandes.pdf}
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
    \noindent
    \ifx\@professor\@empty\else
        {\scshape Profesor}: \@professor\par
    \fi
    \ifx\@dateout\@empty\else
        {\scshape Fecha de asignación}: \@dateout\par
    \fi
    \ifx\@duedate\@empty\else
        {\scshape Fecha máxima de entrega}: \@duedate\par
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
