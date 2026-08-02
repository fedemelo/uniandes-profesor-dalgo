# Add `packages` directory to `TEXINPUTS` env var so pdftex can find custom packages
# Directory is relative, so it looks for a packages/ directory 
# within the directory where the tex file being compiled is located.
TEXINPUTS := ./packages/:$(TEXINPUTS)
export TEXINPUTS

TEX=pdflatex -shell-escape

# Compiles $(2).tex in directory $(1), then renames the resulting PDF
# to match the document's \title, so no manual copy-and-rename is needed.
define compile
	$(TEX) -output-directory=$(1) $(1)/$(2).tex
	title=$$(sed -n 's/^\\title{\(.*\)}$$/\1/p' $(1)/$(2).tex | sed -e 's/\\LaTeX{}/LaTeX/g' -e 's/\\\\//g'); \
	mv "$(1)/$(2).pdf" "$(1)/$$title.pdf"
endef

# Same as compile, but resolves a bibliography (biber) first.
define biber_compile
	$(TEX) -output-directory=$(1) $(1)/$(2).tex
	biber $(1)/$(2)
	$(TEX) -output-directory=$(1) $(1)/$(2).tex
	$(call compile,$(1),$(2))
endef

# course-docs / announcements: target name -> directory holding its .tex
DOC_DIR_policies       := course-docs/policies
DOC_DIR_grupos         := course-docs/grupos
DOC_DIR_consejos       := announcements
DOC_DIR_math-docs      := course-docs/math-docs
DOC_DIR_latex-intro    := course-docs/latex-intro
DOC_DIR_entrada-salida := course-docs/entrada-salida

SIMPLE_DOCS := policies grupos consejos entrada-salida
BIBER_DOCS  := math-docs latex-intro

# homework/N-slug/ -> N, derived from each directory's numeric prefix
HOMEWORK_DIRS := $(sort $(shell find homework -mindepth 1 -maxdepth 1 -type d))
HOMEWORK_NUMS := $(foreach d,$(HOMEWORK_DIRS),$(word 1,$(subst -, ,$(notdir $(d)))))
$(foreach d,$(HOMEWORK_DIRS),$(eval HOMEWORK_DIR_$(word 1,$(subst -, ,$(notdir $(d)))) := $(d)))

# home1..homeN/sol1..solN are deliberately left out: listing them here
# would give each an empty explicit rule that shadows the home%/sol%
# pattern rules below, since they'd never gain a recipe of their own.
.PHONY: course-docs homeworks soluciones $(SIMPLE_DOCS) $(BIBER_DOCS)

$(SIMPLE_DOCS):
	$(call compile,$(DOC_DIR_$@),$@)

$(BIBER_DOCS):
	$(call biber_compile,$(DOC_DIR_$@),$@)

course-docs: $(SIMPLE_DOCS) $(BIBER_DOCS)

home%:
	$(call compile,$(HOMEWORK_DIR_$*),$(notdir $(HOMEWORK_DIR_$*)))

sol%:
	$(call compile,$(HOMEWORK_DIR_$*),$(notdir $(HOMEWORK_DIR_$*))-solucion)

homeworks: $(addprefix home,$(HOMEWORK_NUMS))

soluciones: $(addprefix sol,$(HOMEWORK_NUMS))

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