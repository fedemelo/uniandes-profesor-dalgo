\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{exam}[2026/07/03 Course exam template by fedemelo]

\LoadClass[11pt,letterpaper]{article}

\RequirePackage[utf8]{inputenc}
\RequirePackage[spanish]{babel}
\RequirePackage[top=1in,bottom=1in,left=1in,right=1in]{geometry}
\RequirePackage{xcolor}
\RequirePackage{graphicx}
\RequirePackage{enumitem}
\RequirePackage{array}
\RequirePackage{tabularx}
\RequirePackage{amsmath}
\RequirePackage{amsfonts}
\RequirePackage{fancyhdr}
\RequirePackage{helvet}
\RequirePackage[T1]{fontenc}
\RequirePackage{setspace}
\RequirePackage{ragged2e}
\RequirePackage{tikz}
\RequirePackage{programming-grid}
\RequirePackage{attendance-sheet}
\RequirePackage{course-config}

\usepackage{minted}
\setminted[python]{
  fontsize=\small,
  tabsize=4,
  breaklines=true,
  autogobble,
  style=stata-light,  % Needed for no italics
}

% Override stata-light's red string color to black
% Macros are \PY@tok@XX (not \PYG@), loaded from the .pygstyle file
\AddToHook{begindocument/end}{%
  \makeatletter
  \@namedef{PY@tok@s}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@s1}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@s2}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sa}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sb}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sc}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@dl}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sd}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@se}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sh}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@si}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sx}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@sr}{\def\PY@tc##1{##1}}%
  \@namedef{PY@tok@ss}{\def\PY@tc##1{##1}}%
  \makeatother
}

\definecolor{examgray}{RGB}{128, 128, 128}
\newcommand{\examdate}[1]{\def\@examdate{#1}}

\renewcommand{\familydefault}{\sfdefault}

\newcommand{\makeexamheader}{
    \begin{minipage}[T]{0.25\textwidth}
        \includegraphics[width=\textwidth]{inge-uniandes.png}
    \end{minipage}%
    \hfill
    \begin{minipage}[T]{0.45\textwidth}
        \centering
        \textbf{\department}\\[0.5em]
        \textcolor{examgray}{\@course}
    \end{minipage}%
    \hfill
    \begin{minipage}[T]{0.25\textwidth}
        \raggedleft
        \includegraphics[width=\textwidth]{abet.png}
    \end{minipage}
    
    \flushright
    \@examdate

    \vspace{0.2cm}
    \centering

    \textbf{\@title}
    \flushleft

    \vspace{0.2cm}

    \instructions

    \vspace{0.2cm}

    \academicintegrity

    \newpage
    \pagestyle{plain}
}

\newcommand{\instructions}{
  \justifying

  Por favor, lea cuidadosamente las siguientes instrucciones:
  
  \begin{itemize}
      \item Para presentar el examen, debe entregar su carné estudiantil a cambio de este documento.
      \item El examen tiene una duración máxima de 80 minutos. Pasado ese tiempo, deberá entregar su examen y recibirá su carné estudiantil.
      \item Para abandonar el aula, debe entregar el examen, que se da por terminado, y recibir su carné estudiantil.
      \item El examen es individual. Está prohibida cualquier interacción con sus compañeros en tiempo de examen.
      \item No se permite el uso de dispositivos electrónicos (e.g., celulares, relojes inteligentes, agendas electrónicas, computadores, etc.) ni de materiales adicionales como libros, impresos u hojas distintas al examen. 
      \item En cada una de las preguntas abiertas, dejar la respuesta en blanco equivale automáticamente al 20\% del valor del punto. Al responder, renuncia a ese beneficio, mas puede obtener todo el valor del punto o puntos parciales ante una respuesta correcta o parcialmente correcta. Las respuestas incoherentes o esotéricas pueden generar penalizaciones negativas de hasta el valor total del punto.
      \item En preguntas que incluyen cuadrícula, use esta únicamente para escribir código de manera que quede claro en qué cuadro inicia cada instrucción. No escriba texto libre en la cuadrícula. Las respuestas ilegibles o inadecuadamente indentadas pueden ser calificadas como incorrectas. 
      \item Puede completar el examen con lápiz, pero únicamente se aceptarán reclamos sobre respuestas escritas en tinta indeleble.
      \item Si tiene dudas, levante su mano para solicitar la atención del profesor.
  \end{itemize}
}

\newcommand{\academicintegrity}{
  \raggedright
  \textbf{Compromiso de integridad}

  \justifying
  \noindent
  Al proporcionar sus datos a continuación, usted confirma su compromiso de completar este examen de acuerdo con las normas de integridad académica de la Universidad de los Andes, incluyendo acatar el Reglamento General de Estudiantes de Pregrado y todas las disposiciones relacionadas con evitar el fraude académico, establecidas en el Reglamento Disciplinario para Estudiantes de Pregrado.
  
  \raggedright
  \vspace*{0.4cm}

  Nombre: \rule{\dimexpr\linewidth-4.5em\relax}{0.4pt}

  \vspace*{0.5cm}

  Firma: \rule{\dimexpr\linewidth-3.5em\relax}{0.4pt}
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
\parindent=0pt

\newcounter{questioncounter}
\setcounter{questioncounter}{0}

\newcommand{\question}[2]{%
    \justifying
    \setlength{\parindent}{0pt}%
    \stepcounter{questioncounter}%
    \vspace{1em}%
    \noindent\textbf{Pregunta \arabic{questioncounter} (#1 décimas): }#2%
    \vspace{0.5em}%
    \par%
}

\newenvironment{halfpage}{%
    \noindent\begin{minipage}[t][0.45\textheight][t]{\textwidth}%
    \setlength{\parskip}{6pt plus 2pt minus 1pt}%
}{%
    \end{minipage}\par\medskip%
}

\newcommand{\cleartoeven}{%
  \clearpage
  \ifodd\c@page\else
    \null\thispagestyle{empty}\clearpage
  \fi
}

\endinput
