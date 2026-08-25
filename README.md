<!--
Constant-ell rotating-dust galaxy models, Part I:
local realizability, sharp constraints, and global-completion obstructions.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Constant-ℓ Rotating Dust

Manuscript source, symbolic certificates, validation scripts, and figure
generators for the Batić–Dutykh study of constant-ℓ rotating-dust galaxy
models.

Stationary, axisymmetric rotating-dust spacetimes have been proposed as a
general-relativistic account of flat galactic rotation curves. This work gives a
theorem-level analysis of the constant-ℓ subclass, separating local
realizability from regularity, positivity, asymptotic completion, junction, and
observational requirements. The geometry is parametrized by a potential
η(r, z) and a negative function H(η); the speed measured by zero-angular-momentum
observers (ZAMOs) is v = η/r, and the departure from rigid rotation is encoded in
ℓ(η) = H,η / H. The resulting hierarchy distinguishes proved identities, global
obstructions, conditional matching criteria, and questions reserved for the
numerical Part II.

## Status

**Part I is complete** (62 pages) and is the whole of the present repository:
manuscript source, five section files, three vector figures with their source
data, and eight independent symbolic certificates in Maple and SymPy.

**Part II, the numerical companion, is in preparation.** It will address the
program set out in the outlook of Part I: closing the remaining sharp control
problem, constructing globally admissible backgrounds under the field equations
rather than by kinematic imposition, solving the interior and the stationary
vacuum exterior as one coupled free-boundary problem, establishing numerical
reliability and global regularity, determining dynamical stability, and
computing observables from the complete spacetime. Its code and data will be
added to this repository.

## Principal results

- No nonzero constant ZAMO-speed field solves the exact velocity-field equation
  (VFE) on an open region, and none solves the retained-order truncation either;
  the constant-field ansatz fails already at first prolongation.
- Analytic exactly flat equatorial traces nevertheless exist locally away from
  the axis. Their continuation is controlled by a sharp density discriminant,
  by a Whitney fold of the point-linearising map, by axis regularity, and by
  quantitative span bounds.
- Density positivity at a regular noncritical point is exactly the strip
  x₋(v) ⩽ x ⩽ x₊(v) with x = rℓ, whose lower boundary is simultaneously the fold
  A = 0.
- Every solution on a regular sheet is automatically analytic, and plateaux
  propagate.
- Elliptic Cauchy continuation of the branch is exactly Hadamard unstable.
- Toroidal bodies carry global period obstructions: single-valuedness of the
  reconstruction potentials is equivalent to the vanishing of explicit
  meridional quadrature periods.
- The global regular-axis ℓ = 0 branch is Liouville rigid.
- The auxiliary equation possesses a weighted variational principle, a
  De Donder–Weyl multisymplectic formulation, Noether currents, and a Lagrangian
  boundary-data space. These structures degenerate precisely at the density fold
  and must **not** be identified with the physical Einstein–dust phase space.
- A zero-density surface is only a candidate boundary. Shell-free completion
  requires the complete Darmois data together with compatibility with a
  gauge-fixed exterior Ernst problem.
- The local ZAMO speed does not determine a spectroscopic rotation curve; the
  forward map to measured frequency shifts is formulated explicitly.

## Repository layout

```
DB-DD-ConstantEll-RotatingDust-PartI.tex   manuscript (REVTeX 4.2, PRA style)
DB-DD-ConstantEll-RotatingDust-PartI.bib   bibliography, 77 records
DB-DD-ConstantEll-RotatingDust-PartI.pdf   compiled manuscript, 62 pages
Makefile                                   build and verification driver
sections/                                  five \input section files
  analytic_global_structure.tex              fold geometry, analyticity, rigidity
  approx_flat_sharpness.tex                  state-constrained sharpness audit
  physical_variational_string.tex            covariant variation, EMDA, dualities
  topology_exterior.tex                      helical plateaux, periods, Ernst
  variational_multisymplectic.tex            weighted action, De Donder–Weyl
figures/                                   three vector PDFs and their source data
codes/                                     certificates, generators, audits
LICENSE                                    GNU LGPL v2.1
```

## Building the manuscript

Requirements: a TeX Live installation with REVTeX 4.2, `latexmk`, and GNU Make
4.3 or newer (grouped targets are used).

```sh
make
```

This compiles `DB-DD-ConstantEll-RotatingDust-PartI.pdf` and then removes every
auxiliary file, leaving the PDF alone in the working directory. Auxiliary files
survive a *failed* run, where they are needed for diagnosis.

| Target | Effect |
|---|---|
| `make`, `make build` | compile the PDF, then remove the auxiliary files |
| `make rebuild` | discard every build artifact and compile afresh |
| `make figures` | regenerate the three vector figures and the boundary CSV |
| `make python-checks` | manuscript audit and the four SymPy certificates |
| `make maple` | the four Maple differential-algebra certificates |
| `make verify` | `python-checks` followed by `maple` |
| `make check-style` | recompile, audit house style and the build log, clean up |
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

`codes/check_manuscript.py` additionally audits citation keys, duplicate labels,
PDF metadata, house-style inequalities and delimiters, and release-blocking
build-log diagnostics.

`codes/README_MAPLE_CERTIFICATES.md` documents the encoded differential system,
the branch assumptions, and the scope of the Maple decompositions.
`codes/README.md` gives the full file map and conventions.

## Figures

```sh
make figures
```

All three PDFs are pure vector output, exactly 7.0 inches wide, and intended for
a REVTeX `figure*` at `\textwidth`. NumPy and Matplotlib are the only
dependencies; no random numbers or external data enter the calculation.

| Output | Size | Purpose |
|---|---:|---|
| `figures/density_admissibility_phase.pdf` | 7.0 × 3.75 in | exact density roots, admissible strip, fold, and the kinematics of increasing radius at fixed sign of ℓ |
| `figures/viability_gate_flow.pdf` | 7.0 × 4.45 in | local equations, density, domain topology, outer completion, and observables as necessary logical gates |
| `figures/toroidal_period_obstructions.pdf` | 7.0 × 3.95 in | an off-axis meridional disk, the solid-torus body it sweeps, and the three period obstructions |

`figures/density_phase_boundaries.csv` holds the sampled exact boundary curves
of the density diagram. Colours follow the colour-vision-deficiency-safe
Okabe–Ito palette, and line style, hatching, border style, and labels redundantly
encode every scientific distinction, so the figures survive grayscale
reproduction. Regeneration is byte-reproducible: the Makefile pins
`SOURCE_DATE_EPOCH` so that a rerun does not perturb the committed files.
`codes/FIGURES.md` records the exact formulas plotted, the placement of each
figure, and the visual-inspection record.

## Tested environment

- TeX Live 2025, pdfTeX 1.40.28, REVTeX 4.2, `latexmk` 4.87, GNU Make 4.4.1
- Python 3.14.4 with SymPy 1.14.0, NumPy 2.3.5, Matplotlib 3.10.7
- Maple 2022.0 with `DEtools`, `DifferentialThomas`, `DifferentialGeometry`,
  `PDEtools`, and `Physics`
- `pdfinfo` from Poppler for page accounting

Recent Python 3 releases should suffice. Maple's command-line kernel starts a
local `mserver`, so a restricted container may need permission to create a local
socket; the scripts themselves make no network request.

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
  title  = {Constant-$\ell$ rotating-dust galaxy models, {P}art~{I}:
            local realizability, sharp constraints, and
            global-completion obstructions},
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
