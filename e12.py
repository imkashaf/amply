"""
e12.py - deterministic E-series snapping for Amply.

The LLM can propose theoretical values, but this module guarantees the final
numbers are real, standard E12/E24 parts and reports the resulting error.

Usage (CLI):
    python e12.py 4730            -> nearest E12 to 4.73 kOhm
    python e12.py 18.2e-9 --series E24
"""
import argparse
import math

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
SERIES = {"E12": E12, "E24": E24}


def snap(value, series="E12"):
    """Return (standard_value, error_percent) nearest to `value` (log-nearest)."""
    if value <= 0:
        raise ValueError("value must be positive")
    base = SERIES[series.upper()]
    decade = math.floor(math.log10(value))
    mantissa = value / 10 ** decade
    # include next decade's 1.0 so values like 9.7 snap up to 10.0
    candidates = base + [10.0]
    best = min(candidates, key=lambda c: abs(math.log10(c) - math.log10(mantissa)))
    snapped = round(best * 10 ** decade, 15)
    error = (snapped - value) / value * 100
    return snapped, error


def fmt_resistance(r):
    if r >= 1e6:
        return f"{r / 1e6:g} MΩ"
    if r >= 1e3:
        return f"{r / 1e3:g} kΩ"
    return f"{r:g} Ω"


def fmt_capacitance(c):
    if c >= 1e-6:
        return f"{c / 1e-6:g} µF"
    if c >= 1e-9:
        return f"{c / 1e-9:g} nF"
    return f"{c / 1e-12:g} pF"


def fmt_frequency(f):
    if f >= 1e6:
        return f"{f / 1e6:g} MHz"
    if f >= 1e3:
        return f"{f / 1e3:g} kHz"
    return f"{f:g} Hz"


def rc_cutoff(r, c):
    """fc = 1 / (2*pi*R*C)"""
    return 1 / (2 * math.pi * r * c)


def design_rc_filter(fc_target, c_pick=100e-9, series="E12"):
    """Pick a standard C, compute R for fc_target, snap R, report actual fc."""
    c_std, _ = snap(c_pick, series)
    r_ideal = 1 / (2 * math.pi * fc_target * c_std)
    r_std, r_err = snap(r_ideal, series)
    fc_actual = rc_cutoff(r_std, c_std)
    return {
        "R_ideal": r_ideal,
        "R_std": r_std,
        "C_std": c_std,
        "fc_target": fc_target,
        "fc_actual": fc_actual,
        "fc_error_pct": (fc_actual - fc_target) / fc_target * 100,
        "text": (
            f"C = {fmt_capacitance(c_std)} ({series}), "
            f"R ideal = {r_ideal:.1f} Ω → {fmt_resistance(r_std)} ({series}), "
            f"fc = {fmt_frequency(fc_actual)} "
            f"({(fc_actual - fc_target) / fc_target * 100:+.1f}% vs target)"
        ),
    }


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Snap a value to E12/E24")
    p.add_argument("value", type=float)
    p.add_argument("--series", default="E12", choices=["E12", "E24"])
    a = p.parse_args()
    v, e = snap(a.value, a.series)
    print(f"{a.value:g} → {v:g} ({a.series}), error {e:+.2f}%")
