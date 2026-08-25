#!/usr/bin/env python3
"""Independent symbolic checks for algebra used in the root-manuscript proofs.

This is an audit certificate, not a replacement for the analytic, geometric,
or global arguments. It deliberately re-derives the identities from primitive
definitions instead of importing the manuscript's verification routines.
"""

from __future__ import annotations

import sympy as sp


def require_zero(name: str, expression: sp.Expr) -> None:
    reduced = sp.factor(sp.together(expression))
    if reduced != 0:
        raise AssertionError(f"{name}: expected zero, obtained {reduced}")
    print(f"PASS {name}")


def main() -> None:
    r, v, ell = sp.symbols("r v ell", positive=True, finite=True)
    x = sp.symbols("x", real=True)

    # Constant-field residual and exact/truncated agreement.
    residual = 2 * ell / r - 2 * v / r**2
    require_zero("constant-field residual", residual - 2 * (ell * r - v) / r**2)

    # Density factor, roots, and stationary point.
    density = 4 * v**2 - 4 * v**3 * x - (1 - v**4) * x**2
    factored = (2 * v - (1 + v**2) * x) * (2 * v + (1 - v**2) * x)
    require_zero("density factorization", density - factored)
    x_minus = -2 * v / (1 - v**2)
    x_plus = 2 * v / (1 + v**2)
    require_zero("lower density root", density.subs(x, x_minus))
    require_zero("upper density root", density.subs(x, x_plus))
    x_star = -2 * v**3 / (1 - v**4)
    require_zero("density stationary point", sp.diff(density, x).subs(x, x_star))
    require_zero(
        "density maximum value",
        density.subs(x, x_star) - 4 * v**2 / (1 - v**4),
    )

    # Flat-trace transverse curvature follows from the exact VFE balance.
    A = 2 + ell * r * (1 / v - v)
    vzz = 2 * (v - ell * r) / (r**2 * A)
    require_zero("flat-trace VFE balance", A * vzz + 2 * ell / r - 2 * v / r**2)

    # Exact logarithmic equatorial identity, derived from the root VFE.
    s, q, Z, y = sp.symbols("s q Z y", real=True)
    ur = v * s / r
    urr = v * (q + s**2 - s) / r**2
    vz = sp.Integer(0)
    vzz_log = v * Z / r**2
    lap = urr + vzz_log
    grad2 = ur**2 + vz**2
    exact_vfe = (
        (2 + ell * r * (1 / v - v)) * lap
        + (2 / r + 3 * ell * (1 / v - v)) * ur
        - ell * r * (1 / v**2 + 1) * grad2
        + 2 * ell / r
        - 2 * v / r**2
    )
    logarithmic_identity = (
        (2 + y * (1 - v**2)) * (Z + q)
        + 2 * (1 - y * v**2) * s**2
        + 2 * y * (1 - v**2) * s
        + 2 * y
        - 2
    )
    require_zero(
        "exact logarithmic trace identity",
        (r**2 / v * exact_vfe).subs(ell, y * v / r) - logarithmic_identity,
    )

    # The factorization driving the nonpositive-ell span estimate.
    A_log = 2 + y * (1 - v**2)
    master_rhs = (
        2 * (1 - y)
        - 2 * (1 - y * v**2) * s**2
        - 2 * y * (1 - v**2) * s
    )
    sharp_factor = -y * (1 + s) * (3 - v**2 - (1 + v**2) * s)
    require_zero(
        "nonpositive-ell sharp factorization",
        master_rhs - A_log * (1 - s**2) - sharp_factor,
    )

    # Differentiate the positive-ell comparison bound and recover its
    # stationary equation.
    eps, alpha = sp.symbols("eps alpha", positive=True)
    K = eps * (3 - eps) * (1 - eps) / (1 + eps)
    B_alpha = (
        eps * (2 + alpha) / ((1 + eps) * (1 - eps - alpha))
        - sp.log(alpha) / (1 - eps)
    )
    stationary_numerator = sp.factor(
        sp.diff(B_alpha, alpha)
        * alpha
        * (1 - eps)
        * (1 - eps - alpha) ** 2
    )
    require_zero(
        "positive-ell optimizer equation",
        stationary_numerator
        + ((1 - eps - alpha) ** 2 - K * alpha),
    )

    # Israel trace algebra on a three-dimensional boundary.
    d1, d2, d3 = sp.symbols("d1 d2 d3", real=True)
    delta_trace = d1 + d2 + d3
    shell_diag = [-d1 + delta_trace, -d2 + delta_trace, -d3 + delta_trace]
    require_zero("Israel trace inversion", sum(shell_diag) - 2 * delta_trace)

    print("All independent root-manuscript symbolic checks passed.")


if __name__ == "__main__":
    main()
