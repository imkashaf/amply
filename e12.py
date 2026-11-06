
"""
Amply - Deterministic E12/E24 Component Calculator

Provides reliable standard component selection and RC filter calculations.
"""

import argparse
import math

E12 = [
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
    3.3, 3.9, 4.7, 5.6, 6.8, 8.2
]

E24 = [
    1.0, 1.1, 1.2, 1.3, 1.5, 1.6,
    1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
    3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
    5.6, 6.2, 6.8, 7.5, 8.2, 9.1
]

SERIES = {
    "E12": E12,
    "E24": E24
}


def validate_positive(value, name="value"):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number.")

    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a finite positive number.")


def snap(value, series="E12"):
    """
    Snap a theoretical component value to the nearest
    standard E12 or E24 value.

    Returns:
        (standard_value, error_percent)
    """

    validate_positive(value)

    series = series.upper()

    if series not in SERIES:
        raise ValueError("Series must be E12 or E24.")

    base = SERIES[series]

    decade = math.floor(math.log10(value))
    mantissa = value / (10 ** decade)

    candidates = base + [10.0]

    nearest = min(
        candidates,
        key=lambda x: abs(math.log10(x) - math.log10(mantissa))
    )

    standard_value = nearest * (10 ** decade)

    error_percent = (
        (standard_value - value) / value
    ) * 100

    return standard_value, error_percent


def fmt_resistance(value):
    validate_positive(value)

    if value >= 1e6:
        return f"{value / 1e6:g} MΩ"

    if value >= 1e3:
        return f"{value / 1e3:g} kΩ"

    return f"{value:g} Ω"


def fmt_capacitance(value):
    validate_positive(value)

    if value >= 1e-3:
        return f"{value / 1e-3:g} mF"

    if value >= 1e-6:
        return f"{value / 1e-6:g} µF"

    if value >= 1e-9:
        return f"{value / 1e-9:g} nF"

    return f"{value / 1e-12:g} pF"


def fmt_frequency(value):
    validate_positive(value)

    if value >= 1e9:
        return f"{value / 1e9:g} GHz"

    if value >= 1e6:
        return f"{value / 1e6:g} MHz"

    if value >= 1e3:
        return f"{value / 1e3:g} kHz"

    return f"{value:g} Hz"


def rc_cutoff(resistance, capacitance):
    """
    Calculate the cutoff frequency of a first-order RC filter.

    fc = 1 / (2πRC)
    """

    validate_positive(resistance, "Resistance")
    validate_positive(capacitance, "Capacitance")

    return 1 / (
        2 * math.pi * resistance * capacitance
    )


def design_rc_filter(fc_target, c_pick=100e-9, series="E12"):
    """
    Design a first-order RC filter using standard components.

    Selects a standard capacitor, calculates ideal resistance,
    snaps resistance to the selected E-series, and recalculates
    the actual cutoff frequency.
    """

    validate_positive(fc_target, "Target frequency")
    validate_positive(c_pick, "Capacitance")

    series = series.upper()

    if series not in SERIES:
        raise ValueError("Series must be E12 or E24.")

    c_std, c_error = snap(c_pick, series)

    r_ideal = 1 / (
        2 * math.pi * fc_target * c_std
    )

    r_std, r_error = snap(r_ideal, series)

    fc_actual = rc_cutoff(r_std, c_std)

    frequency_error = (
        (fc_actual - fc_target) / fc_target
    ) * 100

    return {
        "R_ideal": r_ideal,
        "R_std": r_std,
        "C_ideal": c_pick,
        "C_std": c_std,
        "R_error_pct": r_error,
        "C_error_pct": c_error,
        "fc_target": fc_target,
        "fc_actual": fc_actual,
        "fc_error_pct": frequency_error,
        "text": (
            f"RC Filter Design ({series})\n"
            f"Capacitor: {fmt_capacitance(c_std)}\n"
            f"Ideal resistance: {fmt_resistance(r_ideal)}\n"
            f"Selected resistance: {fmt_resistance(r_std)}\n"
            f"Target cutoff: {fmt_frequency(fc_target)}\n"
            f"Actual cutoff: {fmt_frequency(fc_actual)}\n"
            f"Frequency error: {frequency_error:+.2f}%"
        )
    }


def main():
    parser = argparse.ArgumentParser(
        description="Amply E12/E24 Component Calculator"
    )

    parser.add_argument(
        "value",
        type=float,
        help="Theoretical component value"
    )

    parser.add_argument(
        "--series",
        default="E12",
        choices=["E12", "E24", "e12", "e24"],
        help="Standard component series"
    )

    args = parser.parse_args()

    try:
        standard, error = snap(args.value, args.series)

        print(f"Input: {args.value:g}")
        print(f"Standard value: {standard:g}")
        print(f"Series: {args.series.upper()}")
        print(f"Error: {error:+.2f}%")

    except (ValueError, TypeError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
