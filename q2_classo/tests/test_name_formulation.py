"""Tests for the formulation-label helper in the summarize visualizer.

The concomitant formulation has no user-facing tuning parameter for sigma, so
its label must not advertise an ``e = ...`` value (see review by C. Müller).
"""
import os
import tempfile
import unittest

from q2_classo._summarize._visualizer import name_formulation


class TestNameFormulation(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.out = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _label(self, **overrides):
        dictio = {
            "classification": False,
            "concomitant": False,
            "huber": False,
            "rho": 1.345,
            "rho_classification": 0.0,
        }
        dictio.update(overrides)
        return name_formulation(dictio, self.out)

    def test_r3_concomitant_has_no_e(self):
        label = self._label(concomitant=True, huber=False)
        self.assertEqual(label, "R3 (concomitant)")
        self.assertNotIn("e =", label)

    def test_r4_concomitant_huber_has_no_e(self):
        label = self._label(concomitant=True, huber=True)
        self.assertNotIn("e =", label)
        self.assertIn("rho", label)

    def test_r1_and_r2_unchanged(self):
        self.assertEqual(self._label(), "R1 (classic lasso formulation)")
        self.assertIn("R2", self._label(huber=True))


if __name__ == "__main__":
    unittest.main()
