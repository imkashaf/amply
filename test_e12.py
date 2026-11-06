import math
import unittest
from e12 import snap, design_rc_filter, rc_cutoff, fmt_resistance, fmt_capacitance


class TestSnap(unittest.TestCase):
    def test_resistor_examples_from_readme(self):
        self.assertAlmostEqual(snap(4730)[0], 4700)      # 4.73k -> 4.7k
        self.assertEqual(snap(18.2e-9, "E12")[0], 1.8e-8)  # 18.2 nF -> 18 nF
        self.assertEqual(snap(18.2e-9, "E24")[0], 1.8e-8)

    def test_exact_values_unchanged(self):
        for v in (1.0, 2.2, 4.7, 8.2):
            self.assertAlmostEqual(snap(v)[0], v)
            self.assertAlmostEqual(snap(v * 1000)[0], v * 1000)

    def test_rounds_up_to_next_decade(self):
        self.assertEqual(snap(9.7)[0], 10.0)

    def test_error_sign(self):
        _, err = snap(4730)
        self.assertLess(err, 0)  # 4700 < 4730

    def test_invalid(self):
        with self.assertRaises(ValueError):
            snap(0)
        with self.assertRaises(ValueError):
            snap(-5)


class TestFilter(unittest.TestCase):
    def test_1khz_rc(self):
        d = design_rc_filter(1000, c_pick=100e-9)
        self.assertEqual(d["C_std"], 1e-7)
        self.assertAlmostEqual(d["R_std"], 1500)  # ideal ~1591 -> 1.5k
        self.assertAlmostEqual(d["fc_actual"], rc_cutoff(1500, 100e-9))
        self.assertLess(abs(d["fc_error_pct"]), 10)

    def test_formatting(self):
        self.assertEqual(fmt_resistance(4700), "4.7 kΩ")
        self.assertEqual(fmt_capacitance(1e-7), "100 nF")


if __name__ == "__main__":
    unittest.main()
