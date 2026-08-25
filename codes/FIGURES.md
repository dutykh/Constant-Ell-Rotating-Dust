# Mechanism figures

`generate_figures.py` creates the three vector figures used to clarify the
paper's principal mechanisms. It also writes the sampled exact boundary
curves for the density diagram to `figures/density_phase_boundaries.csv`.
The PDFs contain no raster layers and do not require an external LaTeX
installation.

## Regeneration

From the `revised` directory, run

```sh
MPLCONFIGDIR=/tmp/constant-ell-matplotlib python3 codes/generate_figures.py
```

The explicit cache directory is optional on systems with a writable default
Matplotlib configuration directory. The only Python dependencies are NumPy
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

## Recommended manuscript insertions and captions

### Density-admissibility phase diagram

Insert immediately after the remark following
Theorem~`\ref{thm:density-whitney-fold}` and before the automatic-analyticity
subsection.

```tex
\begin{figure*}[t]
  \includegraphics[width=\textwidth]{figures/density_admissibility_phase.pdf}
  \caption{Exact density-admissibility diagram in the variables
  $0<v\leqslant0.8$ and $x=r\ell$. At a regular noncritical point, the
  hatched strip $x_-(v)\leqslant x\leqslant x_+(v)$ is equivalent to
  $\rho\geqslant0$. The lower boundary is simultaneously $A=0$, the
  Whitney fold of the point-linearising map, whereas the upper boundary is
  an ordinary zero of the algebraic density factor. The dash-dotted and
  dotted curves illustrate only the kinematics of $x=r\ell$ for fixed-sign
  $\ell$ as $r$ increases; they are not solutions of the VFE. Thus the
  diagram selects a local inverse sheet but does not establish a global
  spacetime.}
  \label{fig:density-admissibility-phase}
\end{figure*}
```

### Local-to-global viability gates

Insert after the proof of Theorem~`\ref{thm:main-viability}` and before the
next section.

```tex
\begin{figure*}[t]
  \includegraphics[width=\textwidth]{figures/viability_gate_flow.pdf}
  \caption{Logical architecture of the constant-$\ell$ viability problem.
  Solid arrows are necessary gates along the chosen domain branch, while
  dashed links are conditional. A regular axis blocks nonzero constant
  $\ell$; an axis-avoiding core still requires either a controlled
  asymptotic continuation or complete finite-boundary and exterior data
  before observable predictions can be assigned. Passing any gate is not a
  sufficiency theorem. The purple sidecar records auxiliary variational and
  multisymplectic structure of the VFE and is explicitly distinct from the
  physical Einstein--Hilbert--Brown-dust action.}
  \label{fig:viability-gate-flow}
\end{figure*}
```

### Toroidal topology and period obstructions

Insert immediately after the proof of
Theorem~`\ref{thm:toroidal-body-periods}` and before the paragraph beginning
“The theorem repairs an important logical point”.

```tex
\begin{figure*}[t]
  \includegraphics[width=\textwidth]{figures/toroidal_period_obstructions.pdf}
  \caption{Topology and periods for one compact axis-avoiding body. Its
  meridional disk $B$ revolves to
  $\Omega_{\mathrm{mat}}\simeq D^2\times S^1$, while the exterior orbit
  surface $Q^+$ has one homology generator $\gamma$. Under the local
  closedness equations, $P_\zeta=0$, $P_\chi=0$, and $P_\mu=0$ are exactly
  the single-valuedness tests for $\zeta$, $\chi$, and $\mu$, respectively.
  The first two period tests still do not make $(\varpi,\zeta)$ a global Weyl
  chart: noncriticality, injectivity, and properness must be checked
  separately.}
  \label{fig:toroidal-period-obstructions}
\end{figure*}
```
