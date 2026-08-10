# Add `packages` directory to `TEXINPUTS` env var so pdftex can find custom packages
# Directory is relative, so it looks for a packages/ directory 
# within the directory where the tex file being compiled is located.
TEXINPUTS := ./packages/:$(TEXINPUTS)
export TEXINPUTS

TEX=pdflatex -shell-escape

# Compiles $(3).tex, found in source directory $(1), into output directory
# $(2), then renames the resulting PDF to match the document's \title, so
# no manual copy-and-rename is needed. $(1) and $(2) may be the same dir.
define compile
	$(TEX) -output-directory=$(2) $(1)/$(3).tex
	title=$$(sed -n 's/^\\title{\(.*\)}$$/\1/p' $(1)/$(3).tex | sed -e 's/\\LaTeX{}/LaTeX/g' -e 's/\\\\//g' -e 's/: / - /g'); \
	mv "$(2)/$(3).pdf" "$(2)/$$title.pdf"
endef

# Same as compile, but resolves a bibliography (biber) first.
define biber_compile
	$(TEX) -output-directory=$(2) $(1)/$(3).tex
	biber $(2)/$(3)
	$(TEX) -output-directory=$(2) $(1)/$(3).tex
	$(call compile,$(1),$(2),$(3))
endef

# course-docs / announcements: target name -> directory holding its .tex
DOC_DIR_policies         := course-docs/policies
DOC_DIR_grupos           := course-docs/grupos
DOC_DIR_consejos         := announcements
DOC_DIR_math-docs        := course-docs/math-docs
DOC_DIR_latex-intro      := course-docs/latex-intro
DOC_DIR_std-input-output := course-docs/std-input-output

SIMPLE_DOCS := policies grupos consejos std-input-output
BIBER_DOCS  := math-docs latex-intro

# homework/N-slug/ -> N, derived from each directory's numeric prefix
HOMEWORK_DIRS := $(sort $(shell find homework -mindepth 1 -maxdepth 1 -type d))
HOMEWORK_NUMS := $(foreach d,$(HOMEWORK_DIRS),$(word 1,$(subst -, ,$(notdir $(d)))))
$(foreach d,$(HOMEWORK_DIRS),$(eval HOMEWORK_DIR_$(word 1,$(subst -, ,$(notdir $(d)))) := $(d)))

# quizzes/N-slug/ -> N, derived from each directory's numeric prefix
QUIZ_DIRS := $(sort $(shell find quizzes -mindepth 1 -maxdepth 1 -type d 2>/dev/null))
QUIZ_NUMS := $(foreach d,$(QUIZ_DIRS),$(word 1,$(subst -, ,$(notdir $(d)))))
$(foreach d,$(QUIZ_DIRS),$(eval QUIZ_DIR_$(word 1,$(subst -, ,$(notdir $(d)))) := $(d)))

# hw1..hwN and quiz1..quizN are deliberately left out: listing them here
# would give each an empty explicit rule that shadows the hw%/quiz%
# pattern rules below, since they'd never gain a recipe of their own.
.PHONY: course-docs all-hw all-quizzes $(SIMPLE_DOCS) $(BIBER_DOCS)

$(SIMPLE_DOCS):
	$(call compile,$(DOC_DIR_$@),$(DOC_DIR_$@),$@)

$(BIBER_DOCS):
	$(call biber_compile,$(DOC_DIR_$@),$(DOC_DIR_$@),$@)

course-docs: $(SIMPLE_DOCS) $(BIBER_DOCS)

# Homeworks migrated to the tex/tarea + tex/solucion layout keep their
# driver there; PDFs still land at the homework's root regardless. Those
# not yet migrated fall back to the flat layout (driver at the root too).
homework_tarea_src   = $(if $(wildcard $(1)/tex/tarea),$(1)/tex/tarea,$(1))
homework_solucion_src = $(if $(wildcard $(1)/tex/solucion),$(1)/tex/solucion,$(1))

hw%:
	$(call compile,$(call homework_tarea_src,$(HOMEWORK_DIR_$*)),$(HOMEWORK_DIR_$*),$(notdir $(HOMEWORK_DIR_$*)))
	$(call compile,$(call homework_solucion_src,$(HOMEWORK_DIR_$*)),$(HOMEWORK_DIR_$*),$(notdir $(HOMEWORK_DIR_$*))-solucion)

all-hw:
	$(foreach n,$(HOMEWORK_NUMS),$(MAKE) hw$(n);)

quiz%:
	$(call compile,$(QUIZ_DIR_$*)/tex/quiz,$(QUIZ_DIR_$*),$(notdir $(QUIZ_DIR_$*)))
	$(call compile,$(QUIZ_DIR_$*)/tex/solucion,$(QUIZ_DIR_$*),$(notdir $(QUIZ_DIR_$*))-solucion)

all-quizzes:
	$(foreach n,$(QUIZ_NUMS),$(MAKE) quiz$(n);)

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