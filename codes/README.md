<!--
Local realizability and global completion of constant-ell rotating dust:
research-code package.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Research-code package

This directory contains the symbolic certificates, independent checks, figure
generator, and calibration table for the study "Local realizability and global
completion of constant-ℓ rotating dust". The package is deliberately
lightweight: the analytical proofs remain in the manuscript, while the programs
expose the algebraic reductions and validation identities that materially
support them.

## Tested environment

- Maple 2022.0 and 2022.1 with `DEtools`, `DifferentialThomas`,
  `DifferentialGeometry`, `PDEtools`, and `Physics`;
- Python 3.14.4, SymPy 1.14.0, NumPy 2.3.5, and Matplotlib 3.10.7;
- TeX Live 2025, pdfTeX 1.40.28, REVTeX 4.2, and `latexmk` 4.87;
- `pdfinfo` from Poppler for page accounting.

Recent Python 3 versions should suffice. The scripts use no random input
except `verify_approx_flat_sharpness.py`, whose Monte Carlo comparison has a
fixed seed and supplements exact symbolic endpoint checks.

## Conventions and input/output

The calculations use spacetime signature (−, +, +, +) and units c = 1, with
Newton's constant retained in the physical action and junction formulas. The
coordinates t, r, z and the potential η have dimensions of length; φ, v, H, and
μ are dimensionless; Ω and ℓ have dimensions of inverse length; and x = rℓ is
dimensionless. The axial coordinate has period 2π.

The certificate scripts require no external data or command-line input; each
encodes the displayed identities symbolically, prints `PASS` records, and
exits nonzero if a check fails. The figure generator `generate_figures.py`
writes three vector PDFs and `density_phase_boundaries.csv` into `figures/`,
and `galactic_calibration.py` writes `galactic_calibration.csv` there. Each
script overwrites only its own named artifacts.

## Principal commands

Run these commands from the repository root:

```sh
make figures
make python-checks
make maple MAPLE=/opt/maple2022/bin/maple
make verify
make rebuild
```

The command `make verify` runs the Python certificates and then the Maple
certificates. The command `make python-checks` alone is the right entry point
in an environment without Maple.

The ordinary `make` command builds the PDF and then removes the auxiliary
files, leaving the compiled manuscript alone in the working directory. Run
`make clean` to remove the auxiliary files while retaining an existing PDF, and
`make distclean` to remove the PDF as well. The command `make help` lists every
target.

## File map

- `constant_ell_checks.mpl`: exact branch algebra inherited from and extended
  beyond the original calculation;
- `verify_variational.mpl`: Euler–Lagrange, polymomentum, stress, and current
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
- `galactic_calibration.py`: exact radial-span bounds evaluated at one
  representative galactic calibration and written to
  `figures/galactic_calibration.csv`;
- `generate_figures.py`: deterministic generator for all three vector PDF
  figures and the machine-readable density-boundary CSV.

`FIGURES.md` gives the scientific interpretation, exact formulas, generation
command, relation to the manuscript, and visual-inspection record for the
figures. `README_MAPLE_CERTIFICATES.md` explains the Maple branch certificates
and their assumptions in more detail.

## Calibration table

The table `figures/galactic_calibration.csv` evaluates three exact results of
the manuscript at one representative galactic calibration: a stellar orbital
speed of 220 km/s and a radial scale of 10 kpc, with the dimensionless
parameter `a = 1` and `ℓ₀ R_G = a v_c`. The density cutoff of an exactly flat
trace with positive `ℓ₀` is `2 R_G / (1 + a² v_c²)`. The supremum of the radial
ratio `R₂ / R₁` for the same trace is `2 / (1 + v₀²)` with `v₀ = a v_c`. The
logarithmic span bound for nonpositive `ℓ₀` is `2 artanh(ε)`, which implies the
radial ratio `(1 + ε) / (1 − ε)`. At this calibration the cutoff differs from
the low-velocity value `2 R_G` by a relative amount of about `5.4 × 10⁻⁷`.

Every certificate prints the identities or branches it tests and exits
nonzero on failure. These computations are supporting evidence, not
substitutes for the proofs in the manuscript.
