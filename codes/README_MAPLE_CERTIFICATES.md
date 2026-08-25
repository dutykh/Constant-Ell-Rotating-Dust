<!--
Constant-ell rotating-dust galaxy models, Part I: Maple certificates.

Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
         Dr. Denys Dutykh (Mathematics Department, Khalifa University of
         Science and Technology, Abu Dhabi, UAE)
-->

# Maple differential-algebra certificates

These scripts provide a proportionate, machine-checkable audit of the local differential-algebra statements used in Part I. They were tested with Maple 2022.0 on 2026-08-25.

From the repository root, the complete Maple layer is run with

```sh
make maple MAPLE=/opt/maple2022/bin/maple
```

which executes all four certificates in order:

```sh
maple -q constant_ell_checks.mpl
maple -q verify_variational.mpl
maple -q rifsimp_branches.mpl
maple -q thomas_certificates.mpl
```

The two branch certificates documented here can also be run on their own from
`codes/`.

Each script exits with a Maple error if any deterministic assertion fails. A successful run ends with an `All ... passed.` line. Maple's command-line kernel starts a local `mserver`; a restricted container may therefore need permission to create a local socket even though these scripts use no network resource.

## Encoded system

The auxiliary logarithm is replaced by a field (y), producing the polynomial differential system

```text
F - 2 eta - ell r^2 y + (ell/2) eta^2 = 0,
eta y_r - eta_r = 0,
eta y_z - eta_z = 0,
r(F_rr + F_zz) - F_r = 0.
```

The relevant fold polynomial is

```text
A_eta = 2 eta + ell r^2 - ell eta^2 = eta partial_eta Phi_ell.
```

Thus the logarithmic chart requires `eta<>0`, and the regular sheet additionally requires `A_eta<>0`. In the direct velocity formulation the rational VFE is multiplied by `r^2 v^2` only after recording `r<>0` and `v<>0`; its principal fold polynomial is `A_v=2v+ell r(1-v^2)=v A`.

## What the scripts certify

`rifsimp_branches.mpl` runs the regular and fold systems separately. It verifies that the regular output retains `eta<>0` and `A_eta<>0`, recovers the nonlinear VFE from the auxiliary polynomial system, keeps the `ell=0` branch explicit, proves the constant-field incompatibility at first prolongation, and displays the spurious `v=0` closure created by clearing the rational denominator. It also independently verifies the meridional quadrature identity

```text
partial_z M_r - partial_r M_z
    = eta_z A L(F)/(4r).
```

`thomas_certificates.mpl` represents the constant parameter by a field `L(r,z)` with `L_r=L_z=0`, preventing Maple from assuming `ell<>0`. The complete Thomas decomposition of the auxiliary polynomial closure has four disjoint components:

1. one nonzero-`ell`, `eta<>0`, `A_eta<>0` regular component;
2. one explicit `ell=0`, `eta<>0` regular component;
3. two `eta=0` polynomial-closure components.

The `eta=0` components are not solutions in the original logarithmic chart. The fold restriction `eta<>0`, `A_eta=0` has no solution whose image remains in the fold on a two-dimensional open patch. This does not prohibit a codimension-one fold crossing with the additional even-contact compatibility required by the local normal form.

The generic Thomas component also records `1+r^2 L^2<>0`. This separant is automatic for real `r` and `L`; it remains visible because the algebraic decomposition does not impose an ordered real coefficient field.

For the constant-field system, the complete cleared closure consists of the two cases `v=0, ell=0` and `v=0, ell<>0`. Imposing the physical inequation `v<>0` makes the system inconsistent on both the regular and fold branches. The scripts expose the exact compatibility chain

```text
P_const = 2 v^2 (ell r - v),
partial_r(ell r-v) = ell
```

under `v_r=0` and constant `ell`, hence `ell=0` and then `v=0`.

The symbol check verifies that the coefficients of `v_rr` and `v_zz` are both `r^2 v A_v`, while the mixed coefficient vanishes. Consequently, on the physical regular sheet the scalar symbol has rank one and kernel dimension two; at the fold its rank is zero and the kernel dimension jumps to three.

## Scope and limitations

The axis `r=0` is a singular codimension-one locus of the chosen independent-coordinate chart, not a two-dimensional differential component. It is recorded as an excluded base stratum rather than treated as an open PDE solution. Positivity, smooth axis extension, global existence, asymptotic admissibility, and matching are not consequences of these local differential-ideal calculations.
