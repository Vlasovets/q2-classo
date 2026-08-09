"""Registration smoke tests for the q2-classo plugin.

Importing ``plugin_setup`` is itself most of the value here: it exercises every
``register_function`` call (QIIME 2 raises TypeError for any parameter or
description key that does not match the function signature), every semantic type
registration, and all eight transformers. None of that is covered by the unit
tests, and none of it shows up until someone actually runs ``qiime classo``.
"""

import unittest

from q2_classo.plugin_setup import plugin


EXPECTED_METHODS = {
    "generate_data",
    "transform_features",
    "add_taxa",
    "add_covariates",
    "regress",
    "classify",
    "predict",
}

EXPECTED_VISUALIZERS = {"summarize"}


class TestPluginRegistration(unittest.TestCase):
    def test_plugin_name(self):
        self.assertEqual(plugin.name, "classo")

    def test_registered_methods(self):
        self.assertEqual(set(plugin.methods), EXPECTED_METHODS)

    def test_registered_visualizers(self):
        self.assertEqual(set(plugin.visualizers), EXPECTED_VISUALIZERS)

    def test_classify_is_not_registered_as_regress(self):
        """`classify` used to be registered with name="regress".

        The consequence was that `qiime classo --help` listed two actions both
        called "regress". Pin the fix.
        """
        self.assertEqual(plugin.methods["classify"].name, "classify")
        self.assertEqual(plugin.methods["regress"].name, "regress")

    def test_cv_nlam_and_deprecated_alias_both_registered(self):
        """`cv__nlam` (double underscore, --p-cv--nlam) is the legacy spelling.

        Both must stay registered: the new one so the CLI is sane, the old one so
        published tutorial commands and existing driver scripts keep working.
        """
        for action in ("regress", "classify"):
            params = plugin.methods[action].signature.parameters
            self.assertIn("cv_nlam", params, f"{action} is missing cv_nlam")
            self.assertIn(
                "cv__nlam", params, f"{action} dropped the deprecated cv__nlam alias"
            )


class TestTypeRegistration(unittest.TestCase):
    """Assert on the plugin object directly rather than via TestPluginBase.

    TestPluginBase.setUp resolves the plugin through the framework's registry by
    matching `self.package.split('.')[0]` against the plugin's registered
    `package` -- which here is "q2-classo" with a hyphen, so no dotted module
    path can ever match it. It also costs ~95s to load the whole registry.
    Reading `plugin.types` is equivalent for this assertion and instant.
    """

    def test_semantic_types_registered(self):
        registered = set(plugin.types)
        for name in ("CLASSOProblem", "ConstraintMatrix", "Weights"):
            self.assertIn(name, registered, f"semantic type {name} not registered")

    def test_formats_registered(self):
        formats = set(plugin.formats)
        for name in (
            "CLASSOProblemDirectoryFormat",
            "ConstraintDirectoryFormat",
            "WeightsDirectoryFormat",
        ):
            self.assertIn(name, formats, f"format {name} not registered")


if __name__ == "__main__":
    unittest.main()
