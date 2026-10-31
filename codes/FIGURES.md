<!--
Local realizability and global completion of constant-ell rotating dust:
mechanism figures.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Mechanism figures

The script `generate_figures.py` creates three vector figures that illustrate
the density, topology, and completion mechanisms of the constant-ℓ analysis. It
also writes the sampled exact boundary curves for the density diagram to
`figures/density_phase_boundaries.csv`. The PDFs contain no raster layers and do
not require an external LaTeX installation.

## Regeneration

From the repository root, run

```sh
make figures
```

which runs

```sh
MPLCONFIGDIR=/tmp/constant-ell-matplotlib SOURCE_DATE_EPOCH=1787616000 \
    python3 codes/generate_figures.py
```

and then regenerates the calibration table documented in `codes/README.md`.
The explicit cache directory is optional on systems with a writable default
Matplotlib configuration directory. Pinning `SOURCE_DATE_EPOCH` suppresses the
wall-clock creation date that Matplotlib would otherwise stamp into each PDF,
so a rerun reproduces the committed files byte for byte. The only Python
dependencies are NumPy and Matplotlib. The figures were generated and inspected
with Python 3.14.4, NumPy 2.3.5, and Matplotlib 3.10.7. No random numbers or
external data enter the calculation. Other Matplotlib releases may lay the text
out with slightly different glyph metrics, so their output need not agree byte
for byte with the committed files.

All three PDFs are exactly 7.0 inches wide and are intended for a REVTeX
`figure*` at `\textwidth`:

| Output | Natural size | Scientific purpose |
|---|---:|---|
| `figures/density_admissibility_phase.pdf` | 7.0 by 3.75 inches | Shows the exact density roots, admissible strip, fold, and the kinematics of increasing radius at fixed sign of ℓ. |
| `figures/viability_gate_flow.pdf` | 7.0 by 4.45 inches | Separates local equations, density, domain topology, outer completion, and observables into necessary logical gates. |
| `figures/toroidal_period_obstructions.pdf` | 7.0 by 3.95 inches | Relates an off-axis meridional disk to a solid-torus body and displays the three period obstructions. |

Colours follow the colour-vision-deficiency-safe Okabe–Ito palette. Line
style, hatching, border style, and labels redundantly encode every scientific
distinction. The three PDFs were rasterized at 130 dpi, corresponding to
ordinary full-page reading scale, and inspected in both colour and grayscale
on 2026-10-31. The inspection found no clipped labels, overlaps, ambiguous
arrows, illegible text, or distinctions that disappear in grayscale.

## Equations and limitations encoded

The density figure uses only the exact identities

```text
x₋(v) = −2v / (1 − v²),      x₊(v) = 2v / (1 + v²),      x = rℓ,
```

and shades `x₋(v) ⩽ x ⩽ x₊(v)`. The lower root is the fold `A = 0`. The two
fixed-sign curves are deliberately labelled representative: they show how
`x = rℓ` can move as `r` increases, but they are not claimed to solve the
velocity-field equation.

The flow figure treats every solid arrow as a necessary gate along the branch
chosen at the domain-topology split. Dashed links are conditional or
interpretive. In particular, the auxiliary weighted action and
multisymplectic geometry describe the reduced velocity-field equation; they
are not the physical Einstein–Hilbert–Brown-dust action. Passing the gates
does not construct an isolated global galaxy.

The topology figure assumes the hypotheses of the toroidal-body theorem:
one embedded meridional disk, a regular free axial action over that disk, and
closed reconstruction forms on the exterior orbit surface. With one generator
`γ`, exactness is equivalent to vanishing of the displayed period. The
meridional quadrature period is

```text
Pμ := ∮_γ αμ.
```

Even when `Pζ = Pχ = 0`, existence of single-valued potentials does not prove
that `(ϖ, ζ)` is a global Weyl chart; noncriticality, injectivity, and
properness remain separate.

## Relation to the manuscript

The manuscript does not reproduce these figures; they accompany it as
supplementary illustrations. Each file is pure vector output sized for a REVTeX
`figure*` at `\textwidth`, so any of them can be inserted without rescaling. A
caption should carry the interpretive caveats stated above: the representative
radial paths in the density diagram are not solutions of the velocity-field
equation; the dashed links in the gate flow are conditional, and its auxiliary
variational sidecar is explicitly distinct from the physical
Einstein–Hilbert–Brown-dust action; and the vanishing of the first two periods
still does not make `(ϖ, ζ)` a global Weyl chart.
