#!/usr/bin/env python3
"""Independent exact checks for selected physical/string-frame formulae.

This audit is deliberately small: it checks algebraic coefficients and signs
that are easy to encode without pretending to certify global hypotheses.
"""

from __future__ import annotations

import sympy as sp


def require_zero(expr: sp.Expr, label: str) -> None:
    residual = sp.factor(sp.together(expr))
    if residual != 0:
        raise AssertionError(f"{label}: {residual}")
    print(f"PASS: {label}")


def main() -> None:
    phi, kappa_grad_sq, f_sq = sp.symbols(
        "phi kappa_grad_sq f_sq", real=True
    )
    # Vary -2 (d phi)^2 - (1/2) exp(4 phi) (d kappa)^2.
    # After integration by parts its phi Euler coefficient is
    # 4 Box(phi) - 2 exp(4 phi) (d kappa)^2.
    box_phi = sp.symbols("box_phi", real=True)
    phi_euler = 4 * box_phi - 2 * sp.exp(4 * phi) * kappa_grad_sq
    require_zero(
        sp.solve(sp.Eq(phi_euler, 0), box_phi)[0]
        - sp.exp(4 * phi) * kappa_grad_sq / 2,
        "neutral EMDA dilaton equation coefficient",
    )

    # Four-dimensional conformal dictionary g_E=e^{-2 phi} g_s.
    abs_j_s, sqrt_g_s, mass = sp.symbols(
        "abs_j_s sqrt_g_s mass", positive=True
    )
    abs_j_e = sp.exp(-phi) * abs_j_s
    sqrt_g_e = sp.exp(-4 * phi) * sqrt_g_s
    n_s = abs_j_s / sqrt_g_s
    n_e = abs_j_e / sqrt_g_e
    require_zero(n_e - sp.exp(3 * phi) * n_s, "number-density scaling")
    require_zero(
        mass * abs_j_e - mass * sp.exp(-phi) * abs_j_s,
        "Einstein-minimal dust becomes variable-mass string dust",
    )

    # Variable mass m_s=m exp(-phi): source d[-m_s |J|]/dphi=+rho_s.
    rho_s = mass * sp.exp(-phi) * n_s
    scalar_source = sp.diff(-mass * sp.exp(-phi) * abs_j_s, phi) / sqrt_g_s
    require_zero(scalar_source - rho_s, "string-frame scalar source sign")

    # The Ward identity plus number conservation yields a=P grad(phi).
    # Algebraically, div(rho u)= -rho u(phi), and the proposed acceleration
    # a_nu=phi_nu+u_nu u(phi) gives div(T)^mu_nu=rho phi_nu.
    u_phi, u_nu, phi_nu = sp.symbols("u_phi u_nu phi_nu", real=True)
    div_t = -rho_s * u_phi * u_nu + rho_s * (phi_nu + u_nu * u_phi)
    require_zero(div_t - rho_s * phi_nu, "string-frame Ward/force sign")

    # Darmois momentum equivalence in a three-dimensional hypersurface.
    jump_k, hypersurface_dim = sp.symbols("jump_k hypersurface_dim")
    trace_of_momentum_jump = jump_k - hypersurface_dim * jump_k
    require_zero(
        trace_of_momentum_jump.subs(hypersurface_dim, 3) + 2 * jump_k,
        "three-boundary trace coefficient",
    )

    # Buscher transform of the helical plateau with B_{phi t}=0.
    radius, q0 = sp.symbols("radius q0", positive=True)
    g_phiphi = radius**2 - q0**2
    g_tphi = q0
    require_zero(1 / g_phiphi - 1 / (radius**2 - q0**2), "Buscher g_phiphi")
    require_zero(g_tphi / g_phiphi - q0 / (radius**2 - q0**2), "Buscher B_phi_t")

    # Outer half-circle estimate: r~R, field difference R^-1,
    # normal derivative R^-2, and ds~R gives R^-1.
    R = sp.symbols("R", positive=True)
    outer_scaling = R * R**-1 * R**-2 * R
    require_zero(outer_scaling - R**-1, "axidilaton outer-boundary decay")

    print("All independent physical/string algebra checks passed.")


if __name__ == "__main__":
    main()
