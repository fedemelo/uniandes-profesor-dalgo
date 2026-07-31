# Add `packages` directory to `TEXINPUTS` env var so pdftex can find custom packages
# Directory is relative, so it looks for a packages/ directory 
# within the directory where the tex file being compiled is located.
TEXINPUTS := ./packages/:$(TEXINPUTS)
export TEXINPUTS

TEX=pdflatex -shell-escape

.PHONY: policies consejos math-docs latex-intro grupos

policies:
	$(TEX) -output-directory=policies policies/policies.tex

grupos:
	$(TEX) -output-directory=grupos grupos/grupos.tex

consejos:
	$(TEX) -output-directory=announcements announcements/consejos.tex

math-docs:
	$(TEX) -output-directory=math-docs math-docs/math-docs.tex
	biber math-docs/math-docs
	$(TEX) -output-directory=math-docs math-docs/math-docs.tex
	$(TEX) -output-directory=math-docs math-docs/math-docs.tex

latex-intro:
	$(TEX) -output-directory=latex-intro latex-intro/latex-intro.tex
	biber latex-intro/latex-intro
	$(TEX) -output-directory=latex-intro latex-intro/latex-intro.tex
	$(TEX) -output-directory=latex-intro latex-intro/latex-intro.tex

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