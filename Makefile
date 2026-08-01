# Add `packages` directory to `TEXINPUTS` env var so pdftex can find custom packages
# Directory is relative, so it looks for a packages/ directory 
# within the directory where the tex file being compiled is located.
TEXINPUTS := ./packages/:$(TEXINPUTS)
export TEXINPUTS

TEX=pdflatex -shell-escape

.PHONY: policies consejos math-docs latex-intro grupos course-docs \
	home1 home2 home3 home4 home5 home6 home7 homeworks \
	sol1 sol2 sol3 sol4 sol5 sol6 sol7 soluciones

policies:
	$(TEX) -output-directory=course-docs/policies course-docs/policies/policies.tex

grupos:
	$(TEX) -output-directory=course-docs/grupos course-docs/grupos/grupos.tex

consejos:
	$(TEX) -output-directory=announcements announcements/consejos.tex

math-docs:
	$(TEX) -output-directory=course-docs/math-docs course-docs/math-docs/math-docs.tex
	biber course-docs/math-docs/math-docs
	$(TEX) -output-directory=course-docs/math-docs course-docs/math-docs/math-docs.tex
	$(TEX) -output-directory=course-docs/math-docs course-docs/math-docs/math-docs.tex

latex-intro:
	$(TEX) -output-directory=course-docs/latex-intro course-docs/latex-intro/latex-intro.tex
	biber course-docs/latex-intro/latex-intro
	$(TEX) -output-directory=course-docs/latex-intro course-docs/latex-intro/latex-intro.tex
	$(TEX) -output-directory=course-docs/latex-intro course-docs/latex-intro/latex-intro.tex

course-docs: policies consejos math-docs latex-intro grupos

home1:
	$(TEX) -output-directory=homework/1-recursion-y-dividir-y-conquistar homework/1-recursion-y-dividir-y-conquistar/1-recursion-y-dividir-y-conquistar.tex

home2:
	$(TEX) -output-directory=homework/2-programacion-dinamica-i homework/2-programacion-dinamica-i/2-programacion-dinamica-i.tex

home3:
	$(TEX) -output-directory=homework/3-programacion-dinamica-ii homework/3-programacion-dinamica-ii/3-programacion-dinamica-ii.tex

home4:
	$(TEX) -output-directory=homework/4-grafos homework/4-grafos/4-grafos.tex

home5:
	$(TEX) -output-directory=homework/5-intratabilidad homework/5-intratabilidad/5-intratabilidad.tex

home6:
	$(TEX) -output-directory=homework/6-algoritmos-aproximados homework/6-algoritmos-aproximados/6-algoritmos-aproximados.tex

home7:
	$(TEX) -output-directory=homework/7-algoritmos-aleatorios homework/7-algoritmos-aleatorios/7-algoritmos-aleatorios.tex

homeworks: home1 home2 home3 home4 home5 home6 home7

sol1:
	$(TEX) -output-directory=homework/1-recursion-y-dividir-y-conquistar homework/1-recursion-y-dividir-y-conquistar/1-recursion-y-dividir-y-conquistar-solucion.tex

sol2:
	$(TEX) -output-directory=homework/2-programacion-dinamica-i homework/2-programacion-dinamica-i/2-programacion-dinamica-i-solucion.tex

sol3:
	$(TEX) -output-directory=homework/3-programacion-dinamica-ii homework/3-programacion-dinamica-ii/3-programacion-dinamica-ii-solucion.tex

sol4:
	$(TEX) -output-directory=homework/4-grafos homework/4-grafos/4-grafos-solucion.tex

sol5:
	$(TEX) -output-directory=homework/5-intratabilidad homework/5-intratabilidad/5-intratabilidad-solucion.tex

sol6:
	$(TEX) -output-directory=homework/6-algoritmos-aproximados homework/6-algoritmos-aproximados/6-algoritmos-aproximados-solucion.tex

sol7:
	$(TEX) -output-directory=homework/7-algoritmos-aleatorios homework/7-algoritmos-aleatorios/7-algoritmos-aleatorios-solucion.tex

soluciones: sol1 sol2 sol3 sol4 sol5 sol6 sol7

clean:  # Remove all temporary files
	find . \
	\( \
		-name "*.aux" -o \
		-name "*.bcf" -o \
		-name "*.log" -o \
		-name "*.out" -o \
		-name "*.toc" -o \
		-name "*.pyg" -o \
		-name "*.bak0" -o \
		-name "*.bbl" -o \
		-name "*.blg" -o \
		-name "*.glg" -o \
		-name "*.glo" -o \
		-name "*.gls" -o \
		-name "*.ist" -o \
		-name "*.fdb_latexmk" -o \
		-name "*.fls" -o \
		-name "*.gz" -o \
		-name "*.lof" -o \
		-name "*.lot" -o \
		-name "*.run.xml" -o \
		-name "*.listing" \
	\) \
	-exec rm {} +

clean-all: clean  # Remove all temporary files and the generated pdf
	find . -name "*.pdf" -exec rm {} +