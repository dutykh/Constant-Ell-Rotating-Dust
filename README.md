<!--
Local realizability and global completion of constant-ell rotating dust.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Constant-ℓ Rotating Dust

Manuscript source, symbolic certificates, validation scripts, and figure
generators for the Batić–Dutykh study "Local realizability and global
completion of constant-ℓ rotating dust".

Stationary, axisymmetric rotating-dust spacetimes have been proposed as a
general-relativistic account of flat galactic rotation curves. This work asks
when a locally realizable equatorial rotation profile of the constant-ℓ
subclass can be completed to an isolated spacetime, and it separates the local
equations from regularity at the axis, positivity of the density, asymptotic
structure, junction conditions, and observational requirements. The geometry is
parametrized by a potential η(r, z) and a negative function H(η); the speed
measured by zero-angular-momentum observers (ZAMOs) is v = η/r, and the
departure from rigid rotation is encoded in ℓ(η) = H,η / H. The subclass of the
title is the one with ℓ(η) = ℓ₀ constant.

## Status

**Part I is complete** and is the whole of the present repository: the
manuscript (44 pages), three vector figures and two data tables with their
generators, and eight independent symbolic certificates in Maple and SymPy. The
principal theorems and their proofs are in the main text of the manuscript. Its
appendices carry the Runge approximation and metric reconstruction, further
axis arguments with an explicit flat trace, further radial-span estimates, the
comparison with the near-edge approximation, the junction formulas, the
nonlinear exterior hypotheses, and the spectroscopic formulation.

**Part II, the numerical companion, is in preparation.** It will address the
program of the numerical companion: closing the remaining sharp control
problem, constructing globally admissible backgrounds under the field equations
rather than by kinematic imposition, solving the interior and the stationary
vacuum exterior as one coupled free-boundary problem, establishing numerical
reliability and global regularity, determining dynamical stability, and
computing observables from the complete spacetime. Its code and data will be
added to this repository.

## Principal results

An exact point transformation reduces the velocity equation to a linear
elliptic equation. The transformation has a Whitney fold at the lower density
boundary, while positive density selects a regular inverse sheet on which the
reconstructed fields are real analytic. Flat equatorial rotation curves admit
local analytic realizations with positive density on admissible annuli. The
auxiliary elliptic Cauchy problem is nevertheless Hadamard unstable, so
analyticity does not give continuous dependence on smooth equatorial data.

Continuation of these local solutions is constrained in three ways. Under the
stated regularity and timelikeness hypotheses, a metric argument at a regular
axis forces `H′(0) = 0`, so a branch with constant `ℓ₀ ≠ 0` cannot reach the
axis. For reflection-symmetric solutions on annuli, nonnegative density and an
invariant transverse-concavity condition for the relative ZAMO rapidity bound
the radial span of exactly or approximately flat traces; the bounds are sharp
for nonpositive `ℓ₀` and, in the exactly flat limit, for positive `ℓ₀`. Along
an asymptotically flat equatorial end, a uniformly subluminal branch with
`ℓ₀ ≠ 0` has `r·v → q > 0`, and nonnegative density near the tail then forces
a locally flat vacuum region.

For a finite body, completion requires a vacuum exterior that realizes the full
Darmois matching data, and a zero-density surface is only a candidate boundary.
A toroidal body whose meridional section is a disk separated from the axis
imposes period conditions for globally single-valued exterior potentials,
although metric regularity permits a nonzero twist period fixed by the interior
matter-current flux. The gauge-fixed linearized Ernst equations about Minkowski
space give a compatibility condition on a fixed smooth bounded domain away from
the axis, expressed through a Dirichlet-to-Neumann map. It is a boundary test
within the linearized problem and not an existence theorem for a nonlinear
exterior. Finally, a spectroscopic prediction rests on the emitter-observer
frequency ratio, which depends on the emitter and observer motions and on the
connecting null rays in addition to the local ZAMO speed.

## Repository layout

```
DB-DD-ConstantEll-RotatingDust-PartI.tex   manuscript source (REVTeX 4.2)
references.bib                             bibliography, 90 records
DB-DD-ConstantEll-RotatingDust-PartI.pdf   compiled manuscript, 44 pages
Makefile                                   build and verification driver
figures/                                   three vector PDFs and two data tables
codes/                                     certificates, generators, audits
LICENSE                                    GNU LGPL v2.1
```

The manuscript is a single-file source that draws its reference list from the
bibliography database.

## Building the manuscript

Requirements: a TeX Live installation with REVTeX 4.2, `latexmk`, and GNU Make
4.3 or newer (grouped targets are used).

```sh
make
```

This compiles the manuscript and then removes every auxiliary file, leaving the
PDF alone in the working directory. Auxiliary files survive a *failed* run,
where they are needed for diagnosis.

| Target | Effect |
|---|---|
| `make`, `make build` | compile the manuscript, then remove the auxiliary files |
| `make manuscript` | compile the manuscript PDF alone |
| `make rebuild` | discard every build artifact and compile afresh |
| `make figures` | regenerate the three vector figures and the two CSV tables |
| `make python-checks` | the four SymPy certificates |
| `make maple` | the four Maple differential-algebra certificates |
| `make verify` | `python-checks` followed by `maple` |
| `make check-style` | recompile, audit the source and the build log, clean up |
| `make clean` | remove the auxiliary files, keep the PDF |
| `make distclean` | remove the auxiliary files and the PDF |
| `make help` | list the targets |

Tool locations are overridable: `PYTHON`, `LATEXMK`, `MAPLE`, `LATEXMKFLAGS`,
`MPLCONFIGDIR`, `SOURCE_DATE_EPOCH`.

## Reproducing the symbolic certificates

```sh
make verify
```

Maple is not usually on the search path, so pass its location explicitly:

```sh
make maple MAPLE=/opt/maple2022/bin/maple
```

Use `make python-checks` alone in an environment without Maple. Every
certificate prints the identities or branches it tests, ends with a
`All ... passed.` line, and exits nonzero on the first failed assertion. The
suite has eight independent layers:

| Script | Certifies |
|---|---|
| `codes/constant_ell_checks.mpl` | the eleven exact reductions: exact-minus-retained identity, both constant-field residuals, Killing-block determinant, density factorization and roots, point-linearization, logarithmic trace, fold factorization, optimizer equation |
| `codes/verify_variational.mpl` | Euler–Lagrange, polymomentum, stress, and current identities of the auxiliary weighted scalar action |
| `codes/rifsimp_branches.mpl` | the generic differential-elimination branch with every nonvanishing assumption exposed, plus the exact Frobenius identity for the μ quadrature |
| `codes/thomas_certificates.mpl` | a disjoint four-component differential Thomas decomposition, the first-prolongation constant-field incompatibility, and the symbol-rank jump |
| `codes/verify_variational_sympy.py` | 32 exact SymPy checks of the variational, density-fold, matching, distributional, and reduced Ernst identities |
| `codes/verify_approx_flat_sharpness.py` | exact control drift and comparison differences, plus 5000 seeded admissible state comparisons |
| `codes/audit_core_symbolic.py` | independently rederived central-density, trace, asymptotic, and matching algebra |
| `codes/audit_physical_string_sympy.py` | signs and coefficients of the physical action, frame dictionary, Buscher illustration, and axidilaton boundary estimate |

The suite is retained in full. Two of its scripts, `codes/verify_variational.mpl`
and `codes/audit_physical_string_sympy.py`, certify the auxiliary variational
algebra and the physical action and frame dictionary; the analysis they support
is not part of the present manuscript.

The audit script `codes/check_manuscript.py`, run by `make check-style`, is
independent of the certificates. It audits citation keys, duplicate labels, PDF
metadata, house-style inequalities and delimiters, and build-log diagnostics,
and reports each typographic finding in the source. It takes the manuscript
source and the bibliography database as its two arguments.

The file `codes/README_MAPLE_CERTIFICATES.md` documents the encoded differential
system, the branch assumptions, and the scope of the Maple decompositions. The
file `codes/README.md` gives the full file map and conventions.

## Figures and tables

```sh
make figures
```

All three PDFs are pure vector output, exactly 7.0 inches wide, and sized for a
REVTeX `figure*` at `\textwidth`. They accompany the manuscript, which does not
reproduce them. NumPy and Matplotlib are the only dependencies, and no random
numbers or external data enter the calculation.

| Output | Size | Purpose |
|---|---:|---|
| `figures/density_admissibility_phase.pdf` | 7.0 × 3.75 in | exact density roots, admissible strip, fold, and the kinematics of increasing radius at fixed sign of ℓ |
| `figures/viability_gate_flow.pdf` | 7.0 × 4.45 in | local equations, density, domain topology, outer completion, and observables as necessary logical gates |
| `figures/toroidal_period_obstructions.pdf` | 7.0 × 3.95 in | an off-axis meridional disk, the solid-torus body it sweeps, and the three period obstructions |

The table `figures/density_phase_boundaries.csv` holds the sampled exact
boundary curves of the density diagram. The table
`figures/galactic_calibration.csv` evaluates three exact results of the
manuscript, the density cutoff of an exactly flat trace with positive `ℓ₀`, the
supremum of its radial ratio, and the span bound for nonpositive `ℓ₀`, at one
representative galactic calibration of 220 km/s and 10 kpc; its definition is in
`codes/README.md`. Colours follow the colour-vision-deficiency-safe Okabe–Ito
palette, and line style, hatching, border style, and labels redundantly encode
every scientific distinction, so the figures survive grayscale reproduction.
Regeneration is byte-reproducible in the tested environment: the Makefile pins
`SOURCE_DATE_EPOCH` so that a rerun does not perturb the committed files. The
file `codes/FIGURES.md` records the exact formulas plotted, the relation of the
figures to the manuscript, and the visual-inspection record.

## Tested environment

- TeX Live 2025, pdfTeX 1.40.28, REVTeX 4.2, `latexmk` 4.87, GNU Make 4.4.1
- Python 3.14.4 with SymPy 1.14.0, NumPy 2.3.5, Matplotlib 3.10.7
- Maple 2022.0 and 2022.1 with `DEtools`, `DifferentialThomas`,
  `DifferentialGeometry`, `PDEtools`, and `Physics`
- `pdfinfo` from Poppler for page accounting

Recent Python 3 releases should suffice. Maple's command-line kernel starts a
local `mserver`, so a restricted container may need permission to create a
local socket; the scripts themselves make no network request.

## Conventions

Spacetime signature (−, +, +, +) and units c = 1, with Newton's constant retained
in the physical action and the junction formulas. The coordinates t, r, z and the
potential η have dimensions of length; φ, v, H, and μ are dimensionless; Ω and ℓ
have dimensions of inverse length; and x = rℓ is dimensionless. The axial
coordinate has period 2π.

## Scope and limitations

The certificates verify the encoded local algebra and differential ideals. They
do **not** certify axis regularity, global existence, positivity away from the
tested hypotheses, nonlinear vacuum matching, stability, or observational
viability. They are supporting evidence for the analytical proofs in the
manuscript, not substitutes for them. Passing every viability gate is not a
sufficiency theorem, and none of this constructs an isolated global galaxy.

## Citing this work

```bibtex
@unpublished{BaticDutykh2026ConstantEllPartI,
  author = {Bati\'c, Davide and Dutykh, Denys},
  title  = {Local realizability and global completion of
            constant-$\ell$ rotating dust},
  year   = {2026},
  note   = {Preprint},
}
```

## Authors

**Davide Batić**, Mathematics Department, Khalifa University of Science and
Technology, PO Box 127788, Abu Dhabi, United Arab Emirates.
<davide.batic@ku.ac.ae>

**Denys Dutykh**, Mathematics Department, Khalifa University of Science and
Technology, PO Box 127788, Abu Dhabi, United Arab Emirates.
<denys.dutykh@ku.ac.ae>

## License

Distributed under the GNU Lesser General Public License, version 2.1. See
[`LICENSE`](LICENSE) for the full text.
