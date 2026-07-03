# Add `packages` directory to `TEXINPUTS` env var so pdftex can find custom packages
# Directory is relative, so it looks for a packages/ directory 
# within the directory where the tex file being compiled is located.
TEXINPUTS := ./packages/:$(TEXINPUTS)
export TEXINPUTS

TEX=pdflatex -shell-escape

.PHONY: policies

policies:
	$(TEX) policies/policies.tex

clean:  # Remove all temporary files
	find . \
	\( \
		-name "*.aux" -o \
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