<!--
Constant-ell rotating-dust galaxy models, Part I: mechanism figures.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Mechanism figures

`generate_figures.py` creates the three vector figures used to clarify the
paper's principal mechanisms. It also writes the sampled exact boundary
curves for the density diagram to `figures/density_phase_boundaries.csv`.
The PDFs contain no raster layers and do not require an external LaTeX
installation.

## Regeneration

From the repository root, run

```sh
make figures
```

which is equivalent to

```sh
MPLCONFIGDIR=/tmp/constant-ell-matplotlib SOURCE_DATE_EPOCH=1787616000 \
    python3 codes/generate_figures.py
```

The explicit cache directory is optional on systems with a writable default
Matplotlib configuration directory. Pinning `SOURCE_DATE_EPOCH` suppresses the
wall-clock creation date that Matplotlib would otherwise stamp into each PDF,
so a rerun reproduces the committed files byte for byte. The only Python dependencies are NumPy
and Matplotlib. The figures were generated and inspected with Python 3.14.4,
NumPy 2.3.5, and Matplotlib 3.10.7. No random numbers or external data enter
the calculation.

All three PDFs are exactly 7.0 inches wide and are intended for a REVTeX
`figure*` at `\textwidth`:

| Output | Natural size | Scientific purpose |
|---|---:|---|
| `figures/density_admissibility_phase.pdf` | 7.0 by 3.75 inches | Shows the exact density roots, admissible strip, fold, and the kinematics of increasing radius at fixed sign of $\ell$. |
| `figures/viability_gate_flow.pdf` | 7.0 by 4.45 inches | Separates local equations, density, domain topology, outer completion, and observables into necessary logical gates. |
| `figures/toroidal_period_obstructions.pdf` | 7.0 by 3.95 inches | Relates an off-axis meridional disk to a solid-torus body and displays the three period obstructions. |

Colours follow the colour-vision-deficiency-safe Okabe--Ito palette. Line
style, hatching, border style, and labels redundantly encode every scientific
distinction. The three PDFs were rasterized at 130 dpi, corresponding to
ordinary full-page reading scale, and inspected in both colour and grayscale
on 2026-08-25. The final inspection found no clipped labels, overlaps,
ambiguous arrows, illegible text, or distinctions that disappear in
grayscale.

## Equations and limitations encoded

The density figure uses only the exact identities

$$
x_-(v)=-\frac{2v}{1-v^2},\qquad
x_+(v)=\frac{2v}{1+v^2},\qquad x=r\ell,
$$

and shades $x_-\leqslant x\leqslant x_+$. The lower root is the fold
$A=0$. The two fixed-sign curves are deliberately labelled representative:
they show how $x=r\ell$ can move as $r$ increases, but they are not claimed
to solve the velocity-field equation.

The flow figure treats every solid arrow as a necessary gate along the branch
chosen at the domain-topology split. Dashed links are conditional or
interpretive. In particular, the auxiliary weighted action and
multisymplectic geometry describe the reduced velocity-field equation; they
are not the physical Einstein--Hilbert--Brown-dust action. Passing the gates
does not construct an isolated global galaxy.

The topology figure assumes the hypotheses of the toroidal-body theorem:
one embedded meridional disk, a regular free axial action over that disk, and
closed reconstruction forms on the exterior orbit surface. With one generator
$\gamma$, exactness is equivalent to vanishing of the displayed period. We
write

$$
P_\mu:=\oint_\gamma\alpha_\mu
$$

for the meridional quadrature period. Even when $P_\zeta=P_\chi=0$, existence
of single-valued potentials does not prove that $(\varpi,\zeta)$ is a global
Weyl chart; noncriticality, injectivity, and properness remain separate.

## Placement in the manuscript

Each figure is set as a REVTeX `figure*` at `\textwidth`.

| Figure | Label | Location |
|---|---|---|
| `density_admissibility_phase.pdf` | `fig:density-admissibility-phase` | `sections/analytic_global_structure.tex`, after the remark following the density-fold theorem |
| `viability_gate_flow.pdf` | `fig:viability-gate-flow` | `DB-DD-ConstantEll-RotatingDust-PartI.tex`, after the proof of the main viability theorem |
| `toroidal_period_obstructions.pdf` | `fig:toroidal-period-obstructions` | `sections/topology_exterior.tex`, after the proof of the toroidal-body period theorem |

The captions carry the interpretive caveats stated above: the representative
radial paths in the density diagram are not solutions of the VFE; the dashed
links in the gate flow are conditional, and its auxiliary variational sidecar is
explicitly distinct from the physical Einstein--Hilbert--Brown-dust action; and
the vanishing of the first two periods still does not make $(\varpi,\zeta)$ a
global Weyl chart.
