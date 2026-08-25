#!/usr/bin/env python3
"""Symbolic and randomized checks for the approximate-flatness sharpness audit."""

from __future__ import annotations

import random

import sympy as sp


def require_zero(expr: sp.Expr, name: str) -> None:
    simplified = sp.factor(sp.together(expr))
    if simplified != 0:
        raise AssertionError(f"{name}: nonzero residual {simplified}")


def drift(u: sp.Expr, y: sp.Expr, s: sp.Expr) -> sp.Expr:
    return 2 * (1 + s) * ((1 - s) - y * (1 - u**2 * s)) / (
        2 + y * (1 - u**2)
    )


def symbolic_checks() -> None:
    u, y, s, q, r, ell = sp.symbols(
        "u y s q r ell", positive=True, finite=True
    )
    g = drift(u, y, s)
    acoef = 2 + y * (1 - u**2)

    unfactored = (
        2 * (1 - y)
        - 2 * (1 - y * u**2) * s**2
        - 2 * y * (1 - u**2) * s
    )
    factored = 2 * (1 + s) * ((1 - s) - y * (1 - u**2 * s))
    require_zero(unfactored - factored, "master numerator factorization")
    require_zero(g - factored / acoef, "control drift")

    x = sp.symbols("x", nonnegative=True)
    gx = 2 * (1 + s) * ((1 - s) - y * (1 - x * s)) / (2 + y * (1 - x))
    dy_expected = 2 * (1 + s) * (s * x + s + x - 3) / (
        2 + y * (1 - x)
    ) ** 2
    dx_expected = 2 * y * (1 + s) * ((1 + s) - y * (1 - s)) / (
        2 + y * (1 - x)
    ) ** 2
    require_zero(sp.diff(gx, y) - dy_expected, "drift y derivative")
    require_zero(sp.diff(gx, x) - dx_expected, "drift x derivative")

    ds_numerator = 2 * s * (x * y - 1) + y * (x - 1)
    require_zero(
        sp.diff(gx, s)
        - 2 * ds_numerator / (2 + y * (1 - x)),
        "drift s derivative",
    )

    eps, alpha, m = sp.symbols("eps alpha m", positive=True)
    c0 = 2 * (1 + eps) * (1 - eps - alpha) / (2 + alpha)
    cplus = (
        2
        * (1 + eps)
        * (1 - eps - alpha * (1 - m**2 * eps))
        / (2 + alpha * (1 - m**2))
    )
    cminus_one = (1 - eps**2) * (1 - alpha)
    cplus_difference = (
        2
        * alpha
        * m**2
        * (1 + eps)
        * (1 + eps - alpha * (1 - eps))
        / ((2 + alpha) * (2 + alpha * (1 - m**2)))
    )
    cminus_one_difference = (
        alpha
        * (1 + eps)
        * (1 + eps - alpha * (1 - eps))
        / (2 + alpha)
    )
    require_zero(cplus - c0 - cplus_difference, "cplus strict gap")
    require_zero(
        cminus_one - c0 - cminus_one_difference,
        "cminus x=1 strict gap",
    )

    # Convexity of the auxiliary trace in X=r^2.
    phi = (
        2 * r * u
        + ell * r**2 * sp.log(r * u)
        - sp.Rational(1, 2) * ell * r**2 * u**2
    )

    def dt(expr: sp.Expr) -> sp.Expr:
        return sp.simplify(
            sp.diff(expr, r) * r
            + sp.diff(expr, u) * s * u
            + sp.diff(expr, s) * q
        )

    phi_x = dt(phi) / (2 * r**2)
    phi_xx = sp.factor(dt(phi_x) / (2 * r**2))
    y_sub = ell * r / u
    a_sub = 2 + y_sub * (1 - u**2)
    g_sub = drift(u, y_sub, s)
    require_zero(
        phi_xx - u * a_sub * (q - g_sub) / (4 * r**3),
        "auxiliary convexity identity",
    )

    # The rigid extremal and its harmonic auxiliary datum.
    tau, amp, r0 = sp.symbols("tau amp r0", positive=True)
    s_ext = sp.tanh(tau)
    require_zero(sp.diff(s_ext, tau) - (1 - s_ext**2), "rigid slope ODE")
    rr = sp.symbols("rr", positive=True)
    eta = amp * (rr**2 / r0 + r0) / 2
    require_zero(sp.diff(eta, rr, 2) - sp.diff(eta, rr) / rr, "radial harmonicity")


def numeric_checks(samples: int = 5000) -> None:
    rng = random.Random(20260825)
    for _ in range(samples):
        eps = rng.uniform(1.0e-4, 0.95)
        alpha = rng.uniform(1.0e-5, (1 - eps) * (1 - 1.0e-6))
        m = rng.uniform(1.0e-4, 0.999)

        c0 = 2 * (1 + eps) * (1 - eps - alpha) / (2 + alpha)
        cplus = (
            2
            * (1 + eps)
            * (1 - eps - alpha * (1 - m * m * eps))
            / (2 + alpha * (1 - m * m))
        )
        if alpha <= (1 - eps) / (1 + eps):
            cminus = (
                2
                * (1 - eps)
                * (1 + eps - alpha * (1 + m * m * eps))
                / (2 + alpha * (1 - m * m))
            )
        else:
            cminus = (1 - eps * eps) * (1 - alpha)
        cstar = min(cplus, cminus)
        if not cstar > c0 > 0:
            raise AssertionError(
                f"strict comparison failed: eps={eps}, alpha={alpha}, m={m}"
            )

        # Random state in the small-y rectangle must obey G >= cstar.
        state_y = rng.uniform(1.0e-10, alpha)
        state_u = rng.uniform(m, 1 - 1.0e-10)
        state_s = rng.uniform(-eps, eps)
        gval = float(drift(state_u, state_y, state_s))
        if gval + 2.0e-12 < cstar:
            raise AssertionError(
                "rectangular drift lower bound failed: "
                f"G={gval}, cstar={cstar}, state={(state_u, state_y, state_s)}"
            )


def main() -> None:
    symbolic_checks()
    numeric_checks()
    print("PASS: symbolic identities and 5000 randomized control comparisons")


if __name__ == "__main__":
    main()
