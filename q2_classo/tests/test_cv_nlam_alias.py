"""Tests for the cv_nlam / cv__nlam deprecation shim.

The cross-validation lambda-count parameter was originally spelled ``cv__nlam``
with a double underscore, which QIIME 2 renders on the command line as
``--p-cv--nlam``. It is now ``cv_nlam``; the old spelling still works but warns.
"""

import unittest
import warnings

from q2_classo._func import _resolve_cv_nlam


class TestResolveCvNlam(unittest.TestCase):
    def test_default_passes_through(self):
        self.assertEqual(_resolve_cv_nlam(100, None), 100)

    def test_new_spelling_only(self):
        self.assertEqual(_resolve_cv_nlam(50, None), 50)

    def test_deprecated_spelling_is_honoured_and_warns(self):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            self.assertEqual(_resolve_cv_nlam(100, 120), 120)
        self.assertEqual(len(caught), 1)
        self.assertIs(caught[0].category, DeprecationWarning)
        self.assertIn("cv_nlam", str(caught[0].message))

    def test_both_spellings_agreeing_is_accepted(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", DeprecationWarning)
            self.assertEqual(_resolve_cv_nlam(120, 120), 120)

    def test_both_spellings_conflicting_raises(self):
        with self.assertRaises(ValueError):
            _resolve_cv_nlam(50, 120)


if __name__ == "__main__":
    unittest.main()
