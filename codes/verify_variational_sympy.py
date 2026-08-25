#!/usr/bin/env python3
"""Independent exact checks for the variational/multisymplectic section.

Run with

    python3 verify_variational_sympy.py

The script uses only exact SymPy algebra. It writes no files and performs no
floating-point tests. Every PASS line names a manuscript identity.
"""

from __future__ import annotations

import sympy as sp


CHECKS = 0


def canonical(expr: sp.Expr) -> sp.Expr:
    """Return a robust exact normal form for the rational/log expressions."""
    return sp.factor(sp.cancel(sp.together(sp.expand(expr))))


def check_zero(name: str, expr: sp.Expr) -> None:
    global CHECKS
    residual = canonical(expr)
    if residual != 0:
        raise AssertionError(f"FAIL: {name}\nResidual: {residual}")
    CHECKS += 1
    print(f"PASS: {name}")


def check_equal(name: str, lhs: sp.Expr, rhs: sp.Expr) -> None:
    check_zero(name, lhs - rhs)


def main() -> None:
    r, z = sp.symbols("r z", positive=True)
    ell = sp.symbols("ell", real=True)
    eta_star = sp.symbols("eta_star", positive=True)

    # ------------------------------------------------------------------
    # 1. The point transformation, pulled-back action, and fold.
    # ------------------------------------------------------------------
    eta, eta_r, eta_z = sp.symbols("eta eta_r eta_z", positive=True)
    phi = 2 * eta + ell * r**2 * sp.log(eta / eta_star) - ell * eta**2 / 2
    A = sp.diff(phi, eta)
    B = sp.diff(phi, r)
    F_r = B + A * eta_r
    F_z = A * eta_z
    L_eta = (F_r**2 + F_z**2) / (2 * r)

    check_equal("Phi_eta=A", sp.diff(phi, eta), A)
    check_equal("Phi_r at fixed eta=B", sp.diff(phi, r), B)

    pi_r = sp.diff(L_eta, eta_r)
    pi_z = sp.diff(L_eta, eta_z)
    check_equal("eta polymomentum pi^r=A F_r/r", pi_r, A * F_r / r)
    check_equal("eta polymomentum pi^z=A F_z/r", pi_z, A * F_z / r)

    hessian = sp.hessian(L_eta, (eta_r, eta_z))
    check_equal("velocity Hessian rr=A^2/r", hessian[0, 0], A**2 / r)
    check_equal("velocity Hessian rz=0", hessian[0, 1], sp.S.Zero)
    check_equal("velocity Hessian zz=A^2/r", hessian[1, 1], A**2 / r)
    check_equal("velocity Hessian determinant=A^4/r^2", hessian.det(), A**4 / r**2)

    v = sp.symbols("v", positive=True)
    x_fold = -2 * v / (1 - v**2)
    A_v = canonical(A.subs(eta, r * v))
    check_zero("fold equals lower density root", A_v.subs(ell, x_fold / r))
    phi_etaeta = sp.diff(phi, eta, 2)
    check_equal(
        "fold second derivative",
        phi_etaeta.subs(eta, r * v),
        -ell * (1 + 1 / v**2),
    )

    # Functional Euler--Lagrange chain rule, checked with actual functions.
    eta_fun = sp.Function("eta")(r, z)
    phi_fun = (
        2 * eta_fun
        + ell * r**2 * sp.log(eta_fun / eta_star)
        - ell * eta_fun**2 / 2
    )
    A_fun = sp.diff(phi_fun, eta_fun)
    L_fun = (sp.diff(phi_fun, r) ** 2 + sp.diff(phi_fun, z) ** 2) / (2 * r)
    EL_eta = (
        sp.diff(L_fun, eta_fun)
        - sp.diff(sp.diff(L_fun, sp.diff(eta_fun, r)), r)
        - sp.diff(sp.diff(L_fun, sp.diff(eta_fun, z)), z)
    )
    L_op_phi = sp.diff(phi_fun, r, 2) - sp.diff(phi_fun, r) / r + sp.diff(phi_fun, z, 2)
    check_equal("Euler--Lagrange chain rule", EL_eta, -A_fun * L_op_phi / r)

    # The exact VFE identity L(Phi(r,r v))=r E[v].
    vf = sp.Function("v")(r, z)
    eta_v = r * vf
    phi_v = 2 * eta_v + ell * r**2 * sp.log(eta_v / eta_star) - ell * eta_v**2 / 2
    E_v = (
        (2 + ell * r * (1 / vf - vf)) * (sp.diff(vf, r, 2) + sp.diff(vf, z, 2))
        + (2 / r + 3 * ell * (1 / vf - vf)) * sp.diff(vf, r)
        - ell * r * (1 / vf**2 + 1) * (sp.diff(vf, r) ** 2 + sp.diff(vf, z) ** 2)
        + 2 * ell / r
        - 2 * vf / r**2
    )
    L_phi_v = sp.diff(phi_v, r, 2) - sp.diff(phi_v, r) / r + sp.diff(phi_v, z, 2)
    check_equal("auxiliary identity L(Phi)=r E[v]", L_phi_v, r * E_v)

    # ------------------------------------------------------------------
    # 2. Legendre transform and Poincare--Cartan pullback.
    # ------------------------------------------------------------------
    Pi_r, Pi_z = sp.symbols("Pi_r Pi_z")
    eta_r_inverse = r * Pi_r / A**2 - B / A
    eta_z_inverse = r * Pi_z / A**2
    H_eta = canonical(
        Pi_r * eta_r_inverse
        + Pi_z * eta_z_inverse
        - L_eta.subs({eta_r: eta_r_inverse, eta_z: eta_z_inverse})
    )
    H_eta_expected = r * (Pi_r**2 + Pi_z**2) / (2 * A**2) - B * Pi_r / A
    check_equal("eta De Donder--Weyl Hamiltonian", H_eta, H_eta_expected)

    # Coefficients of d eta^dz, d eta^dr, and dr^dz after pulling back
    # Theta_F. This is deliberately component based and independent of a
    # differential-form package.
    p_r = Pi_r / A
    p_z = Pi_z / A
    H_F = r * (p_r**2 + p_z**2) / 2
    pullback_coeffs = (p_r * A, -p_z * A, p_r * B - H_F)
    eta_coeffs = (Pi_r, -Pi_z, -H_eta_expected)
    for label, lhs, rhs in zip(
        ("deta^dz", "deta^dr", "dr^dz"), pullback_coeffs, eta_coeffs
    ):
        check_equal(f"Poincare--Cartan pullback coefficient {label}", lhs, rhs)

    # Fixed-boundary symplectic pullback:
    # dF=A d eta, pi=A p, hence d eta^d pi=A d eta^d p=dF^d p.
    A_eta = sp.diff(A, eta)
    p, deta_1, deta_2, dp_1, dp_2 = sp.symbols(
        "p deta_1 deta_2 dp_1 dp_2"
    )
    dF_1, dF_2 = A * deta_1, A * deta_2
    dpi_1 = A * dp_1 + p * A_eta * deta_1
    dpi_2 = A * dp_2 + p * A_eta * deta_2
    F_boundary_form = dF_1 * dp_2 - dF_2 * dp_1
    eta_boundary_form = deta_1 * dpi_2 - deta_2 * dpi_1
    check_equal(
        "fixed-boundary symplectic trace pullback",
        F_boundary_form,
        eta_boundary_form,
    )

    # ------------------------------------------------------------------
    # 3. Multisymplectic, Noether, stress, and dilation identities.
    # ------------------------------------------------------------------
    f = sp.Function("f")(r, z)
    g = sp.Function("g")(r, z)

    def Lop(u: sp.Expr) -> sp.Expr:
        return sp.diff(u, r, 2) - sp.diff(u, r) / r + sp.diff(u, z, 2)

    omega_r = (f * sp.diff(g, r) - g * sp.diff(f, r)) / r
    omega_z = (f * sp.diff(g, z) - g * sp.diff(f, z)) / r
    check_equal(
        "off-shell multisymplectic form formula",
        sp.diff(omega_r, r) + sp.diff(omega_z, z),
        (f * Lop(g) - g * Lop(f)) / r,
    )

    F = sp.Function("F")(r, z)
    Fr, Fz = sp.diff(F, r), sp.diff(F, z)
    LF = Lop(F)
    Jzr = Fr * Fz / r
    Jzz = (Fz**2 - Fr**2) / (2 * r)
    check_equal(
        "z-Noether divergence off shell",
        sp.diff(Jzr, r) + sp.diff(Jzz, z),
        Fz * LF / r,
    )

    grad2 = Fr**2 + Fz**2
    Trr = (Fr**2 - Fz**2) / (2 * r)
    Trz = Fr * Fz / r
    Tzz = (Fz**2 - Fr**2) / (2 * r)
    check_equal(
        "radial stress divergence off shell",
        sp.diff(Trr, r) + sp.diff(Trz, z),
        Fr * LF / r + grad2 / (2 * r**2),
    )
    check_equal(
        "vertical stress divergence off shell",
        sp.diff(Trz, r) + sp.diff(Tzz, z),
        Fz * LF / r,
    )

    D_r = r * Trr + z * Trz - F * Fr / (2 * r)
    D_z = r * Trz + z * Tzz - F * Fz / (2 * r)
    check_equal(
        "improved dilation divergence off shell",
        sp.diff(D_r, r) + sp.diff(D_z, z),
        (r * Fr + z * Fz - F / 2) * LF / r,
    )
    check_equal(
        "Pohozaev local divergence off shell",
        sp.diff(r * Trr + z * Trz, r) + sp.diff(r * Trz + z * Tzz, z),
        grad2 / (2 * r) + (r * Fr + z * Fz) * LF / r,
    )

    # The z-slice Hamilton equations imply the auxiliary PDE.
    pi = sp.Function("pi")(r, z)
    hamilton_residual = (r * sp.diff(pi, z) + sp.diff(F, r, 2) - Fr / r).subs(
        sp.diff(pi, z), -sp.diff(Fr / r, r)
    )
    check_zero("z-Hamilton equations imply L(F)=0", hamilton_residual)

    # The cocycle density obeys a boundary-flux law.
    cocycle_density = (f * sp.diff(g, z) - g * sp.diff(f, z)) / r
    cocycle_balance = sp.diff(cocycle_density, z) + sp.diff(omega_r, r)
    substitutions = {
        sp.diff(f, z, 2): -sp.diff(f, r, 2) + sp.diff(f, r) / r,
        sp.diff(g, z, 2): -sp.diff(g, r, 2) + sp.diff(g, r) / r,
    }
    check_zero("solution cocycle endpoint balance", cocycle_balance.xreplace(substitutions))

    # ------------------------------------------------------------------
    # 4. Exact modes and the Ernst reduced action.
    # ------------------------------------------------------------------
    k = sp.symbols("k", positive=True)
    exact_modes = {
        "constant mode": sp.S.One,
        "quadratic mode": r**2,
        "Bessel--Hadamard mode": r * sp.besselj(1, k * r) * sp.cosh(k * z),
    }
    for name, mode in exact_modes.items():
        check_zero(name, sp.simplify(sp.expand_func(Lop(mode)).doit()))

    reflected_q = r * sp.besselj(1, k * r)
    check_zero(
        "reflected-layer radial Bessel equation",
        sp.simplify(
            sp.expand_func(
                sp.diff(reflected_q, r, 2)
                - sp.diff(reflected_q, r) / r
                + k**2 * reflected_q
            )
        ).doit(),
    )
    jump_normal_derivative = -k * reflected_q - k * reflected_q
    check_equal(
        "reflected-layer delta coefficient",
        jump_normal_derivative,
        -2 * k * r * sp.besselj(1, k * r),
    )

    ernst_f = sp.Function("ernst_f")(r, z)
    chi = sp.Function("chi")(r, z)
    ernst_L = r * (
        sp.diff(ernst_f, r) ** 2
        + sp.diff(ernst_f, z) ** 2
        + sp.diff(chi, r) ** 2
        + sp.diff(chi, z) ** 2
    ) / (2 * ernst_f**2)
    EL_f = (
        sp.diff(ernst_L, ernst_f)
        - sp.diff(sp.diff(ernst_L, sp.diff(ernst_f, r)), r)
        - sp.diff(sp.diff(ernst_L, sp.diff(ernst_f, z)), z)
    )
    EL_chi = (
        sp.diff(ernst_L, chi)
        - sp.diff(sp.diff(ernst_L, sp.diff(chi, r)), r)
        - sp.diff(sp.diff(ernst_L, sp.diff(chi, z)), z)
    )
    axis_lap_f = sp.diff(ernst_f, r, 2) + sp.diff(ernst_f, r) / r + sp.diff(ernst_f, z, 2)
    axis_lap_chi = sp.diff(chi, r, 2) + sp.diff(chi, r) / r + sp.diff(chi, z, 2)
    ernst_f_eq = ernst_f * axis_lap_f - (
        sp.diff(ernst_f, r) ** 2
        + sp.diff(ernst_f, z) ** 2
        - sp.diff(chi, r) ** 2
        - sp.diff(chi, z) ** 2
    )
    ernst_chi_eq = ernst_f * axis_lap_chi - 2 * (
        sp.diff(ernst_f, r) * sp.diff(chi, r)
        + sp.diff(ernst_f, z) * sp.diff(chi, z)
    )
    check_equal("Ernst f Euler--Lagrange equation", EL_f, -r * ernst_f_eq / ernst_f**3)
    check_equal("Ernst chi Euler--Lagrange equation", EL_chi, -r * ernst_chi_eq / ernst_f**3)

    print(f"All {CHECKS} exact SymPy checks passed.")


if __name__ == "__main__":
    main()
