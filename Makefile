# Constant-ell rotating-dust galaxy models, Part I:
# local realizability, sharp constraints, and global-completion obstructions.
#
# Build and verification driver for the manuscript, its supplementary
# material, and the accompanying research-code package.
#
# Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
#          Science and Technology, Abu Dhabi, UAE)
#          Dr. Denys Dutykh (Mathematics Department, Khalifa University of
#          Science and Technology, Abu Dhabi, UAE)
#
# Quick start:
#   make          compile both PDFs and remove the auxiliary files
#   make verify   run the SymPy and Maple certificates
#   make help     list every available target

SHELL := /bin/bash

# ---------------------------------------------------------------------------
# Manuscript, supplement, and generated artifacts
# ---------------------------------------------------------------------------

JOB  := DB-DD-ConstantEll-RotatingDust-PartI
SUPP := $(JOB)-Supplement

TEX := $(JOB).tex
BIB := $(JOB).bib
PDF := $(JOB).pdf
LOG := $(JOB).log

# The supplement carries its own embedded reference list and compiles
# independently of the manuscript and of the bibliography database.
SUPPTEX := $(SUPP).tex
SUPPPDF := $(SUPP).pdf

PDFS := $(PDF) $(SUPPPDF)

FIGURES := figures/density_admissibility_phase.pdf \
	   figures/toroidal_period_obstructions.pdf \
	   figures/viability_gate_flow.pdf
FIGDATA := figures/density_phase_boundaries.csv

# Auxiliary files that latexmk does not remove on its own.
AUXEXTRA := $(JOB).bbl $(JOB)Notes.bib $(SUPP).bbl $(SUPP)Notes.bib

# ---------------------------------------------------------------------------
# External tools; override on the command line when they live elsewhere, e.g.
#   make maple MAPLE=/opt/maple2022/bin/maple
# ---------------------------------------------------------------------------

PYTHON  ?= python3
LATEXMK ?= latexmk
MAPLE   ?= maple

LATEXMKFLAGS ?= -pdf -interaction=nonstopmode -halt-on-error -file-line-error

# Matplotlib requires a writable configuration directory, which is not always
# available on shared or containerised systems, and stamps a creation date into
# every PDF it writes. Pinning SOURCE_DATE_EPOCH to the figure inspection date
# keeps regenerated figures byte-identical to the committed ones.
MPLCONFIGDIR      ?= /tmp/constant-ell-matplotlib
SOURCE_DATE_EPOCH ?= 1787616000

FIGENV := MPLCONFIGDIR=$(MPLCONFIGDIR) SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH)

.PHONY: all build rebuild manuscript supplement figures python-checks maple \
	verify check-style clean distclean help

.DEFAULT_GOAL := all
.DELETE_ON_ERROR:

# ---------------------------------------------------------------------------
# Manuscript and supplement
# ---------------------------------------------------------------------------

# A successful compilation leaves the two PDFs alone in the working directory:
# the auxiliary files are removed as soon as latexmk reports success. They
# survive a failed run, where they are needed for diagnosis.
all: $(PDFS)
	@$(MAKE) --no-print-directory clean

build: all

manuscript: $(PDF)

supplement: $(SUPPPDF)

$(PDF): $(TEX) $(BIB)
	$(LATEXMK) $(LATEXMKFLAGS) $(TEX)

$(SUPPPDF): $(SUPPTEX)
	$(LATEXMK) $(LATEXMKFLAGS) $(SUPPTEX)

rebuild: distclean
	$(MAKE) all

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

# A single run of the generator produces all four artifacts, so they share one
# grouped rule; the figures are rebuilt only when the generator changes or an
# artifact is missing.
$(FIGURES) $(FIGDATA) &: codes/generate_figures.py
	$(FIGENV) $(PYTHON) codes/generate_figures.py

# Unconditional regeneration on request.
figures:
	$(FIGENV) $(PYTHON) codes/generate_figures.py

# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

verify: python-checks maple

python-checks:
	$(PYTHON) codes/check_manuscript.py $(TEX) $(BIB)
	$(PYTHON) codes/verify_variational_sympy.py
	$(PYTHON) codes/verify_approx_flat_sharpness.py
	$(PYTHON) codes/audit_core_symbolic.py
	$(PYTHON) codes/audit_physical_string_sympy.py

maple:
	@command -v $(MAPLE) >/dev/null 2>&1 || { \
	  echo 'Maple was not found on the search path. Set MAPLE explicitly:'; \
	  echo '  make maple MAPLE=/opt/maple2022/bin/maple'; \
	  exit 1; }
	cd codes && $(MAPLE) -q constant_ell_checks.mpl
	cd codes && $(MAPLE) -q verify_variational.mpl
	cd codes && $(MAPLE) -q rifsimp_branches.mpl
	cd codes && $(MAPLE) -q thomas_certificates.mpl

# House-style and build-log audit of the manuscript. The build log is not kept
# between builds, so this target recompiles unconditionally, audits, and cleans
# up again.
check-style:
	$(LATEXMK) -g $(LATEXMKFLAGS) $(TEX)
	$(PYTHON) codes/check_manuscript.py --log $(LOG) $(TEX) $(BIB)
	@$(MAKE) --no-print-directory clean

# ---------------------------------------------------------------------------
# Housekeeping
# ---------------------------------------------------------------------------

# Remove the auxiliary files and retain the compiled PDFs.
clean:
	@$(LATEXMK) -c $(TEX) >/dev/null
	@$(LATEXMK) -c $(SUPPTEX) >/dev/null
	@$(RM) $(AUXEXTRA)

# Remove the auxiliary files and the compiled PDFs.
distclean:
	@$(LATEXMK) -C $(TEX) >/dev/null
	@$(LATEXMK) -C $(SUPPTEX) >/dev/null
	@$(RM) $(AUXEXTRA)

help:
	@echo 'Targets for $(JOB):'
	@echo
	@echo '  all, build     compile both PDFs, then remove the auxiliary files (default)'
	@echo '  manuscript     compile $(PDF) alone'
	@echo '  supplement     compile $(SUPPPDF) alone'
	@echo '  rebuild        discard every build artifact and compile afresh'
	@echo '  figures        regenerate the three vector figures and the CSV'
	@echo '  python-checks  run the manuscript audit and the SymPy certificates'
	@echo '  maple          run the four Maple differential-algebra certificates'
	@echo '  verify         python-checks followed by maple'
	@echo '  check-style    recompile, audit house style and the build log, clean up'
	@echo '  clean          remove the auxiliary files, keep the PDFs'
	@echo '  distclean      remove the auxiliary files and the PDFs'
	@echo '  help           show this list'
	@echo
	@echo 'Tool overrides: PYTHON, LATEXMK, MAPLE, LATEXMKFLAGS, MPLCONFIGDIR,'
	@echo 'SOURCE_DATE_EPOCH.'
