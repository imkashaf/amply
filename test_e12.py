
import math
import unittest

from e12 import (
    snap,
    design_rc_filter,
    rc_cutoff,
    fmt_resistance,
    fmt_capacitance,
    fmt_frequency,
)


class TestSnap(unittest.TestCase):

    def test_e12_resistor_example(self):
        value, error = snap(4730, "E12")
        self.assertEqual(value, 4700)
        self.assertAlmostEqual(error, -0.63425, places=3)

    def test_e24_component_selection(self):
        value, _ = snap(18.2e-9, "E24")
        self.assertEqual(value, 18e-9)

    def test_exact_standard_values(self):
        for value in (1.0, 2.2, 4.7, 8.2):
            self.assertAlmostEqual(snap(value, "E12")[0], value)
            self.assertAlmostEqual(
                snap(value * 1000, "E12")[0],
                value * 1000
            )

    def test_rounds_to_next_decade(self):
        self.assertEqual(snap(9.7)[0], 10.0)

    def test_error_sign(self):
        _, error = snap(4730)
        self.assertLess(error, 0)

    def test_invalid_values(self):
        for value in (0, -5, float("inf"), float("-inf"), float("nan")):
            with self.assertRaises(ValueError):
                snap(value)

    def test_invalid_series(self):
        with self.assertRaises(ValueError):
            snap(1000, "E48")

    def test_non_numeric_input(self):
        with self.assertRaises(TypeError):
            snap("1000")


class TestRCFilter(unittest.TestCase):

    def test_1khz_rc_filter(self):
        result = design_rc_filter(1000, c_pick=100e-9)

        self.assertEqual(result["C_std"], 100e-9)
        self.assertAlmostEqual(result["R_std"], 1500)

        self.assertAlmostEqual(
            result["fc_actual"],
            rc_cutoff(1500, 100e-9)
        )

        self.assertLess(abs(result["fc_error_pct"]), 10)

    def test_rc_cutoff(self):
        result = rc_cutoff(1500, 100e-9)
        self.assertAlmostEqual(result, 1061.03295, places=3)

    def test_invalid_filter_inputs(self):
        for frequency in (0, -1000, float("inf"), float("nan")):
            with self.assertRaises(ValueError):
                design_rc_filter(frequency)

        for capacitance in (0, -1e-9, float("nan")):
            with self.assertRaises(ValueError):
                design_rc_filter(1000, capacitance)

    def test_invalid_filter_series(self):
        with self.assertRaises(ValueError):
            design_rc_filter(1000, series="E48")


class TestFormatting(unittest.TestCase):

    def test_resistance_formatting(self):
        self.assertEqual(fmt_resistance(4700), "4.7 kΩ")
        self.assertEqual(fmt_resistance(1000000), "1 MΩ")
        self.assertEqual(fmt_resistance(100), "100 Ω")

    def test_capacitance_formatting(self):
        self.assertEqual(fmt_capacitance(1e-7), "100 nF")
        self.assertEqual(fmt_capacitance(1e-6), "1 µF")
        self.assertEqual(fmt_capacitance(1e-3), "1 mF")

    def test_frequency_formatting(self):
        self.assertEqual(fmt_frequency(1000), "1 kHz")
        self.assertEqual(fmt_frequency(1000000), "1 MHz")
        self.assertEqual(fmt_frequency(50), "50 Hz")


if __name__ == "__main__":
    unittest.main()
