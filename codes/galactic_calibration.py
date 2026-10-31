#!/usr/bin/env python3
# Authors: Dr. Davide Batic (Mathematics Department, Khalifa University of
#          Science and Technology, Abu Dhabi, UAE)
#          Dr. Denys Dutykh (Mathematics Department, Khalifa University of
#          Science and Technology, Abu Dhabi, UAE)
"""Evaluate the exact radial-span bounds at representative galactic scales.

The analysis is written in dimensionless variables. This script supplies one
calibration, a characteristic stellar orbital speed v_c and a galactic radial
scale R_G with ell_0 R_G = a v_c, and evaluates three exact quantities at those
values: the density cutoff R_rho = 2 v_0 / (ell_0 (1 + v_0^2)) of an exactly
flat trace with speed v_0 = a v_c and positive ell_0, which equals
2 R_G / (1 + a^2 v_c^2); the supremum 2 / (1 + v_0^2) of the radial ratio
R_2 / R_1 for the same trace; and the logarithmic span bound 2 artanh(eps) for
nonpositive ell_0, with the radial ratio exp(2 artanh(eps)) that it implies.

The values are written to a machine-readable CSV in the figures directory.
"""

from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "figures" / "galactic_calibration.csv"

C_KM_S = 299792.458          # speed of light, km/s (exact, SI definition)
V_C_KM_S = 220.0             # characteristic stellar orbital speed, km/s
R_G_KPC = 10.0               # galactic radial scale, kpc
A_PARAM = 1.0                # the dimensionless parameter a, with ell_0 R_G = a v_c


def dimensionless_speed(v_km_s: float) -> float:
    """Return v/c for a speed given in km/s."""
    return v_km_s / C_KM_S


def exact_density_cutoff(a: float, v_c: float, r_g: float) -> float:
    """Return R_rho = 2 R_G / (1 + a^2 v_c^2) for ell_0 R_G = v_0 = a v_c."""
    return 2.0 * r_g / (1.0 + (a * v_c) ** 2)


def cutoff_relative_deficit(a: float, v_c: float) -> float:
    """Fractional shortfall of R_rho below the low-velocity value 2 R_G."""
    return 1.0 - 1.0 / (1.0 + (a * v_c) ** 2)


def span_bound_nonpositive_ell(eps: float) -> float:
    """Logarithmic span bound 2 artanh(eps) for nonpositive ell_0."""
    return 2.0 * math.atanh(eps)


def radius_ratio(log_span: float) -> float:
    """Convert a logarithmic span to the radial ratio R_2/R_1."""
    return math.exp(log_span)


def exact_flat_ratio_bound(v_0: float) -> float:
    """Supremum of R_2/R_1 for an exactly flat trace with positive ell_0: 2/(1+v_0^2)."""
    return 2.0 / (1.0 + v_0**2)


def epsilon_for_variation(factor: float, decades: float) -> float:
    """Value of eps for a trace varying by `factor` over `decades` decades."""
    return math.log(factor) / (decades * math.log(10.0))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    v_c = dimensionless_speed(V_C_KM_S)
    a_v = A_PARAM * v_c

    rows: list[dict[str, object]] = []

    def record(quantity: str, value: float, unit: str, note: str) -> None:
        rows.append({"quantity": quantity, "value": value, "unit": unit, "note": note})

    record("v_c", V_C_KM_S, "km/s", "characteristic stellar orbital speed")
    record("v_c_over_c", v_c, "1", "dimensionless characteristic speed")
    record("R_G", R_G_KPC, "kpc", "galactic radial scale")
    record("a", A_PARAM, "1", "dimensionless calibration parameter")
    record("ell_0_times_R_G", a_v, "1", "ell_0 R_G = a v_c, dimensionless")

    cutoff = exact_density_cutoff(A_PARAM, v_c, R_G_KPC)
    deficit = cutoff_relative_deficit(A_PARAM, v_c)
    record("R_rho_exact", cutoff, "kpc", "exact density-positivity cutoff")
    record("R_rho_exact_over_2RG", cutoff / (2.0 * R_G_KPC), "1", "ratio to 2 R_G")
    record("cutoff_relative_deficit", deficit, "1", "1 - R_rho_exact/(2 R_G)")

    for eps in (0.0, 0.01, 0.02, 0.05, 0.10):
        if eps == 0.0:
            lam, ratio = 0.0, 1.0
        else:
            lam = span_bound_nonpositive_ell(eps)
            ratio = radius_ratio(lam)
        record(f"Lambda_bound_eps_{eps:g}", lam, "1", "2 artanh(eps), nonpositive ell_0")
        record(f"ratio_bound_eps_{eps:g}", ratio, "1", "R_2/R_1 bound, nonpositive ell_0")

    record("exact_flat_ratio_bound", exact_flat_ratio_bound(a_v), "1",
           "2/(1+v_0^2), exactly flat, positive ell_0")
    record("eps_for_3pct_per_decade", epsilon_for_variation(1.03, 1.0), "1",
           "eps of a trace rising 3 percent per decade in radius")
    record("eps_for_5pct_per_decade", epsilon_for_variation(1.05, 1.0), "1",
           "eps of a trace rising 5 percent per decade in radius")

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["quantity", "value", "unit", "note"])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    width = max(len(str(r["quantity"])) for r in rows)
    for r in rows:
        value = r["value"]
        shown = f"{value:.6g}" if isinstance(value, float) else str(value)
        print(f"{str(r['quantity']):<{width}}  {shown:>12}  {r['unit']:<5}  {r['note']}")
    print(f"\nWrote {len(rows)} records to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
