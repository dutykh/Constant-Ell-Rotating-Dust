#!/usr/bin/env python3
"""Generate the manuscript's three mechanism figures as vector PDFs.

The script deliberately avoids ``text.usetex`` so that figure regeneration
does not depend on a particular TeX installation.  Mathematical labels use
Matplotlib's built-in STIX mathtext renderer.  All geometry and numerical
curves are deterministic.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Ellipse, FancyArrowPatch, FancyBboxPatch, PathPatch, Polygon
from matplotlib.path import Path as MplPath


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT_DIR = SCRIPT_DIR.parent / "figures"

# Okabe--Ito colours, paired with line styles, hatching, and explicit labels so
# that no scientific distinction depends on colour alone.
BLUE = "#0072B2"
ORANGE = "#E69F00"
GREEN = "#009E73"
VERMILION = "#D55E00"
PURPLE = "#CC79A7"
SKY = "#56B4E9"
INK = "#202124"
MID_GREY = "#6B7075"
LIGHT_GREY = "#F1F2F3"
WHITE = "#FFFFFF"


def configure_matplotlib() -> None:
    """Set compact journal-style defaults with editable TrueType text."""

    mpl.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["DejaVu Serif", "STIXGeneral", "Times New Roman"],
            "mathtext.fontset": "stix",
            "font.size": 8.0,
            "axes.labelsize": 8.5,
            "axes.titlesize": 9.0,
            "xtick.labelsize": 7.5,
            "ytick.labelsize": 7.5,
            "legend.fontsize": 7.2,
            "axes.linewidth": 0.7,
            "lines.linewidth": 1.35,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "savefig.facecolor": WHITE,
            "figure.facecolor": WHITE,
        }
    )


def save_pdf(fig: mpl.figure.Figure, path: Path, title: str, subject: str) -> None:
    """Save a fixed-size vector PDF with minimal scholarly metadata."""

    fig.savefig(
        path,
        format="pdf",
        dpi=300,
        metadata={
            "Title": title,
            "Author": "D. Bertacca and D. Dutykh",
            "Subject": subject,
            "Creator": "codes/generate_figures.py",
        },
    )
    plt.close(fig)


def add_arrow_along_curve(
    ax: mpl.axes.Axes,
    x: np.ndarray,
    y: np.ndarray,
    start_fraction: float,
    colour: str,
) -> None:
    """Place an arrowhead on a plotted parametric curve."""

    index = int(start_fraction * (len(x) - 2))
    arrow = FancyArrowPatch(
        (x[index], y[index]),
        (x[index + 1], y[index + 1]),
        arrowstyle="-|>",
        mutation_scale=9,
        linewidth=1.2,
        color=colour,
        shrinkA=0,
        shrinkB=0,
        zorder=7,
    )
    ax.add_patch(arrow)


def density_phase_figure(output_dir: Path) -> None:
    """Plot the exact density interval and representative radial paths."""

    v = np.linspace(0.035, 0.80, 600)
    x_minus = -2.0 * v / (1.0 - v**2)
    x_plus = 2.0 * v / (1.0 + v**2)
    density_at_minus = 4.0 * v**2 - 4.0 * v**3 * x_minus - (1.0 - v**4) * x_minus**2
    density_at_plus = 4.0 * v**2 - 4.0 * v**3 * x_plus - (1.0 - v**4) * x_plus**2
    fold_jacobian = 2.0 + x_minus * (1.0 / v - v)
    if not (
        np.all(x_minus < 0.0)
        and np.all(x_plus > 0.0)
        and np.allclose(density_at_minus, 0.0, rtol=0.0, atol=2.0e-14)
        and np.allclose(density_at_plus, 0.0, rtol=0.0, atol=2.0e-14)
        and np.allclose(fold_jacobian, 0.0, rtol=0.0, atol=2.0e-14)
    ):
        raise RuntimeError("density-boundary identity check failed")

    data_path = output_dir / "density_phase_boundaries.csv"
    with data_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(["v", "x_minus", "x_plus"])
        writer.writerows(zip(v, x_minus, x_plus, strict=True))

    fig, ax = plt.subplots(figsize=(7.0, 3.75))
    fig.subplots_adjust(left=0.095, right=0.985, bottom=0.16, top=0.93)

    ymin, ymax = -4.75, 1.18
    ax.fill_between(
        v,
        x_minus,
        x_plus,
        facecolor=SKY,
        alpha=0.20,
        edgecolor="none",
        zorder=1,
    )
    ax.fill_between(
        v,
        x_minus,
        x_plus,
        facecolor="none",
        edgecolor=BLUE,
        hatch="////",
        linewidth=0.0,
        alpha=0.24,
        zorder=2,
    )
    lower_line, = ax.plot(
        v,
        x_minus,
        color=VERMILION,
        linewidth=1.8,
        label=r"$x_-(v)=-2v/(1-v^2)$: $A=0$ (fold)",
        zorder=5,
    )
    upper_line, = ax.plot(
        v,
        x_plus,
        color=INK,
        linestyle="--",
        linewidth=1.55,
        label=r"$x_+(v)=2v/(1+v^2)$: ordinary density root",
        zorder=5,
    )

    # These curves encode only x=r ell with fixed sign while r increases;
    # their mild v-variation is illustrative and is not asserted to solve
    # the velocity-field equation.
    tau = np.linspace(0.0, 1.0, 180)
    v_pos = 0.31 + 0.13 * tau + 0.012 * np.sin(np.pi * tau)
    x_pos = 0.09 + 1.02 * tau
    v_neg = 0.64 - 0.10 * tau + 0.012 * np.sin(np.pi * tau)
    x_neg = -0.22 - 2.75 * tau
    if not (np.all(np.diff(x_pos) > 0.0) and np.all(np.diff(x_neg) < 0.0)):
        raise RuntimeError("fixed-sign radial path lost monotonicity in x=r*ell")
    positive_line, = ax.plot(
        v_pos,
        x_pos,
        color=ORANGE,
        linestyle="-.",
        linewidth=1.75,
        label=r"representative $\ell>0$ path ($r$ increasing)",
        zorder=6,
    )
    negative_line, = ax.plot(
        v_neg,
        x_neg,
        color=PURPLE,
        linestyle=":",
        linewidth=2.1,
        label=r"representative $\ell<0$ path ($r$ increasing)",
        zorder=6,
    )
    add_arrow_along_curve(ax, v_pos, x_pos, 0.55, ORANGE)
    add_arrow_along_curve(ax, v_neg, x_neg, 0.57, PURPLE)

    ax.axhline(0.0, color=MID_GREY, linewidth=0.65, zorder=0)
    ax.text(
        0.47,
        -0.47,
        r"admissible algebraic factor: $\mathcal{N}_v(x)\geqslant0$",
        ha="center",
        va="center",
        color=INK,
        bbox={"boxstyle": "round,pad=0.24", "facecolor": WHITE, "edgecolor": BLUE, "linewidth": 0.7},
        zorder=8,
    )
    ax.text(0.70, 0.88, r"$\mathcal{N}_v(x)<0$", ha="center", color=MID_GREY)
    ax.text(0.69, -4.25, r"$\mathcal{N}_v(x)<0$", ha="center", color=MID_GREY)
    ax.annotate(
        "orientation-preserving\ninverse sheet",
        xy=(0.57, -1.44),
        xytext=(0.34, -2.55),
        ha="center",
        va="center",
        fontsize=7.4,
        arrowprops={"arrowstyle": "->", "color": BLUE, "linewidth": 0.8},
        color=INK,
    )

    ax.set_xlim(0.0, 0.82)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel(r"subluminal speed $v$")
    ax.set_ylabel(r"$x=r\ell$")
    ax.set_xticks(np.arange(0.0, 0.81, 0.1))
    ax.set_yticks(np.arange(-4.0, 1.1, 1.0))
    ax.grid(True, color="#D8DADD", linewidth=0.45, linestyle=(0, (1.5, 2.5)), zorder=0)
    ax.spines[["top", "right"]].set_visible(False)

    handles = [lower_line, upper_line, positive_line, negative_line]
    ax.legend(
        handles=handles,
        loc="lower left",
        frameon=True,
        framealpha=0.96,
        edgecolor="#B8BBC0",
        ncol=2,
        columnspacing=1.2,
        handlelength=3.0,
        borderpad=0.55,
    )

    save_pdf(
        fig,
        output_dir / "density_admissibility_phase.pdf",
        "Density-admissibility phase diagram",
        "Exact roots, admissible region, density fold, and schematic fixed-sign radial paths.",
    )


def rounded_box(
    ax: mpl.axes.Axes,
    xy: tuple[float, float],
    width: float,
    height: float,
    text: str,
    *,
    face: str = WHITE,
    edge: str = INK,
    linestyle: str = "-",
    fontsize: float = 7.5,
    linewidth: float = 1.0,
    zorder: int = 3,
) -> FancyBboxPatch:
    """Add a normalized-coordinate flowchart box and centred text."""

    patch = FancyBboxPatch(
        xy,
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.015",
        transform=ax.transAxes,
        facecolor=face,
        edgecolor=edge,
        linewidth=linewidth,
        linestyle=linestyle,
        zorder=zorder,
    )
    ax.add_patch(patch)
    ax.text(
        xy[0] + width / 2,
        xy[1] + height / 2,
        text,
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=fontsize,
        color=INK,
        linespacing=1.2,
        zorder=zorder + 1,
    )
    return patch


def axes_arrow(
    ax: mpl.axes.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    colour: str = INK,
    linestyle: str = "-",
    mutation_scale: float = 9.0,
    connectionstyle: str = "arc3",
    zorder: int = 2,
) -> None:
    """Add a flow arrow in normalized axes coordinates."""

    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            transform=ax.transAxes,
            arrowstyle="-|>",
            mutation_scale=mutation_scale,
            linewidth=1.0,
            linestyle=linestyle,
            color=colour,
            connectionstyle=connectionstyle,
            shrinkA=2,
            shrinkB=2,
            zorder=zorder,
        )
    )


def viability_flow_figure(output_dir: Path) -> None:
    """Draw the local-to-global chain of necessary viability gates."""

    fig, ax = plt.subplots(figsize=(7.0, 4.45))
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.055, top=0.965)
    ax.set_axis_off()

    rounded_box(
        ax,
        (0.045, 0.765),
        0.205,
        0.135,
        r"Exact constant-$\ell$ VFE" + "\n" + "field-equation gate",
        face="#EAF4FA",
        edge=BLUE,
    )
    rounded_box(
        ax,
        (0.315, 0.765),
        0.215,
        0.135,
        "Density interval and fold" + "\n" + r"$\mathcal{N}_v\geqslant0$; $x_-\!: A=0$",
        face="#EDF7F3",
        edge=GREEN,
    )

    branch = Polygon(
        [[0.655, 0.83], [0.73, 0.92], [0.805, 0.83], [0.73, 0.74]],
        closed=True,
        transform=ax.transAxes,
        facecolor="#FFF6DD",
        edgecolor=ORANGE,
        linewidth=1.1,
        zorder=3,
    )
    ax.add_patch(branch)
    ax.text(
        0.73,
        0.83,
        "Does the domain\nmeet the axis?",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=7.4,
        color=INK,
        zorder=4,
    )

    axes_arrow(ax, (0.25, 0.832), (0.315, 0.832), colour=INK)
    axes_arrow(ax, (0.53, 0.832), (0.653, 0.832), colour=INK)
    ax.text(0.282, 0.852, "necessary", transform=ax.transAxes, ha="center", fontsize=6.5, color=MID_GREY)
    ax.text(0.59, 0.852, "necessary", transform=ax.transAxes, ha="center", fontsize=6.5, color=MID_GREY)

    rounded_box(
        ax,
        (0.425, 0.505),
        0.225,
        0.135,
        "Axis-connected branch\nregular-axis jet test",
        face="#FFF0EC",
        edge=VERMILION,
    )
    rounded_box(
        ax,
        (0.73, 0.505),
        0.24,
        0.135,
        "Axis-avoiding branch\nlocal or semi-global core",
        face="#EEF3FA",
        edge=BLUE,
    )
    axes_arrow(ax, (0.70, 0.755), (0.54, 0.64), colour=VERMILION)
    axes_arrow(ax, (0.765, 0.755), (0.85, 0.64), colour=BLUE)
    ax.text(0.61, 0.68, "yes", transform=ax.transAxes, fontsize=6.8, color=VERMILION)
    ax.text(0.81, 0.68, "no", transform=ax.transAxes, fontsize=6.8, color=BLUE)

    rounded_box(
        ax,
        (0.405, 0.285),
        0.255,
        0.115,
        r"$H'(0)=0$; nonzero constant $\ell$" + "\n" + "blocked at a regular axis",
        face=WHITE,
        edge=VERMILION,
        linestyle="--",
        fontsize=7.2,
    )
    axes_arrow(ax, (0.537, 0.505), (0.537, 0.40), colour=VERMILION)

    rounded_box(
        ax,
        (0.455, 0.105),
        0.225,
        0.145,
        "Continue to infinity\nasymptotic locking and\neventual-vacuum tests",
        face="#F4F6F7",
        edge=MID_GREY,
        fontsize=7.2,
    )
    rounded_box(
        ax,
        (0.72, 0.105),
        0.25,
        0.145,
        "Terminate at finite radius\nDarmois data, topology periods,\nand exterior Ernst compatibility",
        face="#F4F6F7",
        edge=MID_GREY,
        fontsize=7.0,
    )
    axes_arrow(
        ax,
        (0.77, 0.505),
        (0.65, 0.25),
        colour=BLUE,
        connectionstyle="arc3,rad=-0.05",
    )
    axes_arrow(
        ax,
        (0.90, 0.505),
        (0.845, 0.25),
        colour=BLUE,
        connectionstyle="arc3,rad=-0.04",
    )

    rounded_box(
        ax,
        (0.045, 0.455),
        0.31,
        0.17,
        "Auxiliary weighted action, Noether currents,\nand multisymplectic geometry\n\nDiagnostic structure of the VFE;\nnot the Einstein--Hilbert--dust action",
        face="#F8F0F7",
        edge=PURPLE,
        linestyle="--",
        fontsize=7.0,
    )
    axes_arrow(
        ax,
        (0.20, 0.625),
        (0.15, 0.765),
        colour=PURPLE,
        linestyle="--",
        connectionstyle="arc3,rad=-0.15",
    )
    axes_arrow(
        ax,
        (0.355, 0.555),
        (0.422, 0.765),
        colour=PURPLE,
        linestyle="--",
        connectionstyle="arc3,rad=0.14",
    )

    rounded_box(
        ax,
        (0.045, 0.105),
        0.31,
        0.145,
        "Observer maps and predictions\nonly after a viable metric and\nobserver congruence are fixed",
        face="#FFF7E6",
        edge=ORANGE,
        fontsize=7.3,
    )
    axes_arrow(
        ax,
        (0.455, 0.175),
        (0.355, 0.175),
        colour=ORANGE,
        linestyle="--",
    )
    axes_arrow(
        ax,
        (0.72, 0.145),
        (0.355, 0.145),
        colour=ORANGE,
        linestyle="--",
        connectionstyle="arc3,rad=-0.07",
    )

    ax.text(
        0.50,
        0.036,
        "Solid arrows are necessary gates along the chosen branch; dashed links are conditional.\n"
        "No path by itself constructs a global isolated galaxy.",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=7.0,
        fontweight="semibold",
        color=INK,
        linespacing=1.15,
    )

    save_pdf(
        fig,
        output_dir / "viability_gate_flow.pdf",
        "Local-to-global viability gates",
        "Necessary gates, branch alternatives, non-implications, and the auxiliary variational sidecar.",
    )


def torus_path(center: tuple[float, float], outer: tuple[float, float], inner: tuple[float, float]) -> MplPath:
    """Create an elliptical annulus path for a schematic solid torus."""

    cx, cy = center
    outer_w, outer_h = outer
    inner_w, inner_h = inner
    theta_outer = np.linspace(0.0, 2.0 * np.pi, 181)
    theta_inner = np.linspace(2.0 * np.pi, 0.0, 181)
    outer_vertices = np.column_stack(
        [cx + 0.5 * outer_w * np.cos(theta_outer), cy + 0.5 * outer_h * np.sin(theta_outer)]
    )
    inner_vertices = np.column_stack(
        [cx + 0.5 * inner_w * np.cos(theta_inner), cy + 0.5 * inner_h * np.sin(theta_inner)]
    )
    vertices = np.vstack([outer_vertices, inner_vertices])
    codes = np.full(len(vertices), MplPath.LINETO, dtype=np.uint8)
    codes[0] = MplPath.MOVETO
    codes[len(outer_vertices)] = MplPath.MOVETO
    return MplPath(vertices, codes)


def topology_period_figure(output_dir: Path) -> None:
    """Draw the orbit-space topology, revolution, and period tests."""

    fig, ax = plt.subplots(figsize=(7.0, 3.95))
    fig.subplots_adjust(left=0.015, right=0.985, bottom=0.055, top=0.96)
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_axis_off()

    # Panel (a): meridional orbit half-plane and a disk separated from the axis.
    ax.text(0.18, 0.945, "(a) Meridional orbit surface", ha="center", va="center", fontsize=8.4, fontweight="semibold")
    ax.plot([0.055, 0.055], [0.20, 0.88], color=INK, linewidth=1.7)
    ax.plot([0.055, 0.335], [0.20, 0.20], color=INK, linewidth=0.8)
    ax.text(0.034, 0.55, "regular axis $r=0$", rotation=90, ha="center", va="center", fontsize=7.0)
    ax.text(0.325, 0.17, "$r$", ha="center", va="center")
    ax.text(0.038, 0.87, "$z$", ha="center", va="center")
    body = Ellipse((0.205, 0.535), 0.105, 0.205, facecolor="#F7D8D0", edgecolor=VERMILION, linewidth=1.2, hatch="///")
    ax.add_patch(body)
    ax.text(0.205, 0.535, "$B$", ha="center", va="center", fontsize=9.0, fontweight="semibold")
    ax.text(0.10, 0.30, "$Q^+$", ha="center", va="center", fontsize=9.0, color=BLUE)
    gamma_theta = np.linspace(0.20 * np.pi, 2.20 * np.pi, 220)
    gamma_x = 0.205 + 0.078 * np.cos(gamma_theta)
    gamma_y = 0.535 + 0.148 * np.sin(gamma_theta)
    ax.plot(gamma_x, gamma_y, color=BLUE, linewidth=1.5)
    arrow_index = 105
    ax.add_patch(
        FancyArrowPatch(
            (gamma_x[arrow_index], gamma_y[arrow_index]),
            (gamma_x[arrow_index + 4], gamma_y[arrow_index + 4]),
            arrowstyle="-|>",
            mutation_scale=9,
            color=BLUE,
            linewidth=1.3,
        )
    )
    ax.annotate(
        r"$\gamma$ generates $H_1(Q^+;\mathbb{Z})$",
        xy=(0.276, 0.62),
        xytext=(0.185, 0.79),
        ha="center",
        va="center",
        fontsize=7.0,
        arrowprops={"arrowstyle": "->", "linewidth": 0.7, "color": BLUE},
    )

    # Panel (b): revolution of B about the axial orbit gives a solid torus.
    ax.text(0.505, 0.945, "(b) Axial revolution", ha="center", va="center", fontsize=8.4, fontweight="semibold")
    axes_arrow(ax, (0.345, 0.59), (0.405, 0.59), colour=MID_GREY, mutation_scale=10)
    ax.text(0.375, 0.625, "$U(1)$", ha="center", va="bottom", fontsize=7.0, color=MID_GREY)

    torus = PathPatch(
        torus_path((0.505, 0.58), (0.245, 0.215), (0.105, 0.078)),
        facecolor="#DDECF6",
        edgecolor=BLUE,
        linewidth=1.25,
    )
    ax.add_patch(torus)
    # Meridional contours make the ring interpretation legible in grayscale.
    ax.add_patch(Ellipse((0.438, 0.58), 0.038, 0.185, fill=False, edgecolor=MID_GREY, linewidth=0.65, linestyle="--"))
    ax.add_patch(Ellipse((0.572, 0.58), 0.038, 0.185, fill=False, edgecolor=MID_GREY, linewidth=0.65, linestyle="--"))
    ax.plot([0.385, 0.625], [0.58, 0.58], color=BLUE, linewidth=0.55, alpha=0.7)
    ax.text(0.505, 0.39, r"$\Omega_{\mathrm{mat}}\simeq D^2\!\times S^1$", ha="center", va="center", fontsize=8.0)
    ax.text(0.505, 0.33, r"$\partial\Omega_{\mathrm{mat}}\simeq T^2$", ha="center", va="center", fontsize=7.6)
    ax.text(0.505, 0.755, "off-axis body", ha="center", va="center", fontsize=7.0, color=VERMILION)

    # Panel (c): period tests for the three locally reconstructed potentials.
    ax.text(0.79, 0.945, "(c) Global period tests", ha="center", va="center", fontsize=8.4, fontweight="semibold")
    rounded_box(
        ax,
        (0.655, 0.705),
        0.31,
        0.135,
        r"$P_{\zeta}=\oint_{\gamma} *_q d\varpi$"
        + "\n"
        + r"$P_{\zeta}=0\ \Longleftrightarrow$ global conjugate $\zeta$",
        face="#EEF5FA",
        edge=BLUE,
        fontsize=7.0,
    )
    rounded_box(
        ax,
        (0.655, 0.505),
        0.31,
        0.135,
        r"$P_{\chi}=\oint_{\gamma}\omega_k$"
        + "\n"
        + r"$P_{\chi}=0\ \Longleftrightarrow$ global twist $\chi$",
        face="#F0F8F4",
        edge=GREEN,
        fontsize=7.0,
    )
    rounded_box(
        ax,
        (0.655, 0.305),
        0.31,
        0.135,
        r"$P_{\mu}=\oint_{\gamma}\alpha_{\mu}$"
        + "\n"
        + r"$P_{\mu}=0\ \Longleftrightarrow$ single-valued $\mu$",
        face="#FFF7E6",
        edge=ORANGE,
        fontsize=7.0,
    )
    ax.text(
        0.81,
        0.18,
        "Vanishing periods give exactness.\nThey do not guarantee a global Weyl chart:\nnoncriticality, injectivity, and properness remain.",
        ha="center",
        va="center",
        fontsize=7.1,
        color=INK,
        bbox={"boxstyle": "round,pad=0.28", "facecolor": WHITE, "edgecolor": MID_GREY, "linewidth": 0.75, "linestyle": "--"},
    )

    save_pdf(
        fig,
        output_dir / "toroidal_period_obstructions.pdf",
        "Toroidal topology and period obstructions",
        "Off-axis matter topology and the periods required for single-valued reconstructed potentials.",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="output directory (default: revised/figures relative to this script)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    configure_matplotlib()
    density_phase_figure(output_dir)
    viability_flow_figure(output_dir)
    topology_period_figure(output_dir)
    print(f"Wrote vector figures and source data to {output_dir}")


if __name__ == "__main__":
    main()
