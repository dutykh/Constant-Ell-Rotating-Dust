<!--
Constant-ell rotating-dust galaxy models, Part I: research-code package.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Research-code package

This directory contains the symbolic certificates, independent checks, and
figure generator for Part I of the constant-$\ell$ rotating-dust study. The
package is deliberately lightweight: the analytical proofs remain in the
manuscript, while the programs expose the algebraic reductions and validation
identities that materially support them.

## Tested environment

- Maple 2022.0 with `DEtools`, `DifferentialThomas`,
  `DifferentialGeometry`, `PDEtools`, and `Physics`;
- Python 3.14.4, SymPy 1.14.0, NumPy 2.3.5, and Matplotlib 3.10.7;
- TeX Live 2025, pdfTeX 1.40.28, REVTeX 4.2, and `latexmk` 4.87;
- `pdfinfo` from Poppler for page accounting.

Recent Python 3 versions should suffice. The scripts use no random input
except `verify_approx_flat_sharpness.py`, whose Monte Carlo comparison has a
fixed seed and supplements exact symbolic endpoint checks.

## Conventions and input/output

The calculations use spacetime signature $(-,+,+,+)$ and units $c=1$, with
$G_{\rm N}$ retained in the physical action and junction formulas. The
coordinates $t,r,z$ and the potential $\eta$ have dimensions of length;
$\phi$, $v$, $H$, and $\mu$ are dimensionless; $\Omega$ and $\ell$ have
dimensions of inverse length; and $x=r\ell$ is dimensionless. The axial
coordinate has period $2\pi$.

The certificate scripts require no external data or command-line input; each
encodes the displayed identities symbolically, prints `PASS` records, and
exits nonzero if a check fails. `generate_figures.py` writes three vector PDFs
and `density_phase_boundaries.csv` into `figures/`. It overwrites only those
named generated artifacts. `check_manuscript.py` takes the manuscript TeX and
BibTeX paths, with optional log and reference-audit paths, and emits a
fail-fast textual audit.

## Principal commands

Run these commands from the repository root:

```sh
make figures
make python-checks
make maple MAPLE=/opt/maple2022/bin/maple
make verify
make check-style
make rebuild
```

`make verify` runs the Python certificates and then the Maple certificates.
`make python-checks` alone is the right entry point in an environment without
Maple.

The ordinary `make` command builds the PDF and then removes the auxiliary
files, leaving the compiled manuscript alone in the working directory. Run
`make clean` to remove the auxiliary files while retaining an existing PDF, and
`make distclean` to remove the PDF as well. `make help` lists every target.

## File map

- `constant_ell_checks.mpl`: exact branch algebra inherited from and extended
  beyond the original calculation;
- `verify_variational.mpl`: Euler--Lagrange, polymomentum, stress, and current
  identities for the auxiliary weighted scalar action;
- `rifsimp_branches.mpl`: generic differential-elimination branch with its
  nonvanishing assumptions exposed;
- `thomas_certificates.mpl`: disjoint differential Thomas components,
  including the singular strata excluded by the generic branch;
- `verify_variational_sympy.py`: independent SymPy checks of the variational,
  density-fold, matching, distributional, and related exact identities;
- `verify_approx_flat_sharpness.py`: exact and fixed-seed checks of the sharp
  and refined approximately-flat annular-span estimates;
- `audit_core_symbolic.py`: independently re-derived algebra for the central
  density, trace, asymptotic, and matching proofs;
- `audit_physical_string_sympy.py`: independent sign and coefficient checks
  for the physical action, frame dictionary, Buscher illustration, and
  axidilaton boundary estimate;
- `generate_figures.py`: deterministic generator for all three vector PDF
  figures and the machine-readable density-boundary CSV;
- `check_manuscript.py`: fail-fast LaTeX house-style and build-log audit;
- `revision_tracker.py`: the authors' atomic claim--evidence register and
  page-accounting tool. It reads and atomically updates a `REVISION_STATE.json`
  drafting state, from which it regenerates a human-readable dashboard. That
  state belongs to the private drafting workspace and is not part of this
  repository, so the tracker has no target in the `Makefile`; the script is
  kept here because the manuscript's reproducibility appendix names it.

`FIGURES.md` gives the scientific interpretation, exact formulas, generation
command, placement, and visual-inspection record for the figures.
`README_MAPLE_CERTIFICATES.md` explains the Maple branch certificates and
their assumptions in more detail.

Every certificate prints the identities or branches it tests and exits
nonzero on failure. These computations are supporting evidence, not
substitutes for the primary proofs and their independent adversarial audits.
