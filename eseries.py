"""Deterministic E12/E24 helpers for Amply.

The LLM should call these instead of doing the math itself.
"""
import math

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2]
E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]
SERIES = {"E12": E12, "E24": E24}


def snap(value: float, series: str = "E12") -> float:
    """Return the nearest standard value (ratio-wise) from the series."""
    if value <= 0:
        raise ValueError("value must be positive")
    decade = 10 ** math.floor(math.log10(value))
    base = SERIES[series] + [10.0]
    candidates = [b * decade for b in base] + [b * decade / 10 for b in base[-2:]]
    return min(candidates, key=lambda c: abs(math.log(c / value)))


def fmt(value: float, unit: str = "Ω") -> str:
    """Format with SI prefix, e.g. 4700 -> '4.7 kΩ'."""
    prefixes = [(1e9, "G"), (1e6, "M"), (1e3, "k"), (1, ""),
                (1e-3, "m"), (1e-6, "µ"), (1e-9, "n"), (1e-12, "p")]
    for scale, p in prefixes:
        if abs(value) >= scale * 0.9999:
            return f"{value / scale:.3g} {p}{unit}"
    return f"{value:.3g} {unit}"


def inverting_amp(gain: float, rin: float = 10_000, series: str = "E12") -> dict:
    """Inverting amp: Av = -Rf/Rin. Returns chosen parts and actual gain."""
    rin_s = snap(rin, series)
    rf_s = snap(abs(gain) * rin_s, series)
    return {"Rin": rin_s, "Rf": rf_s, "actual_gain": -rf_s / rin_s,
            "error_pct": ((rf_s / rin_s) - abs(gain)) / abs(gain) * 100}


def rc_lowpass(fc: float, r: float = 10_000, series: str = "E12") -> dict:
    """First-order RC filter: fc = 1/(2*pi*R*C). Pick R, solve and snap C."""
    r_s = snap(r, series)
    c_s = snap(1 / (2 * math.pi * r_s * fc), series)
    return {"R": r_s, "C": c_s, "actual_fc": 1 / (2 * math.pi * r_s * c_s)}


def voltage_divider(vin: float, vout: float, r_total: float = 10_000, series: str = "E12") -> dict:
    """Pick R1 (top) and R2 (bottom) from the series, both 1 kΩ-1 MΩ,
    minimising output error; ties go to the total closest to r_total."""
    vals = [b * d for d in (1e3, 1e4, 1e5) for b in SERIES[series]]
    best = min(
        ((abs(vin * r2 / (r1 + r2) - vout), abs(math.log((r1 + r2) / r_total)), r1, r2)
         for r1 in vals for r2 in vals),
        key=lambda t: (round(t[0], 6), t[1]),
    )
    _, _, r1, r2 = best
    return {"R1": r1, "R2": r2, "actual_vout": vin * r2 / (r1 + r2)}


if __name__ == "__main__":
    assert snap(4730) == 4700
    assert snap(18.2e-9) == 18e-9 or abs(snap(18.2e-9) - 18e-9) < 1e-12 or snap(18.2e-9) == 1.8e-8
    assert fmt(4700) == "4.7 kΩ"
    print(inverting_amp(-10))
    print(rc_lowpass(1000))
    print(voltage_divider(5, 3.3))
    print("ok")
