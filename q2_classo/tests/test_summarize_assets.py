"""Guard against the summarize visualizer shipping blank plot panes.

Every ``offline.plot(...)`` call in ``_summarize/_visualizer.py`` was commented
out while the jinja2 templates still referenced 16 ``<iframe src="./*.html">``
files, so every plot pane in the .qzv rendered blank -- with no Python error to
notice. This is a static check (no solve required, runs in milliseconds) that
the .html filenames the templates ask for and the .html filenames the visualizer
source writes are the same set. It compares literals only -- it does not prove
that any particular writer is reached at runtime.

It also catches case mismatches: the code used to write ``StabSel-tree.html``
while the template asked for ``stabsel-tree.html``, which silently breaks on any
case-sensitive filesystem.
"""

import pathlib
import re
import unittest

_SUMMARIZE = pathlib.Path(__file__).resolve().parents[1] / "_summarize"
_VISUALIZER = _SUMMARIZE / "_visualizer.py"
_ASSETS = _SUMMARIZE / "assets"


def _iframe_targets() -> set:
    targets = set()
    for template in _ASSETS.glob("*.html"):
        targets |= set(
            re.findall(r'src="\./([^"]+\.html)"', template.read_text())
        )
    return targets


def _written_filenames() -> set:
    src = _VISUALIZER.read_text()
    # Literals written straight into the output directory ...
    written = set(
        re.findall(
            r'os\.path\.join\((?:output_dir|directory),\s*"([^"]+\.html)"', src
        )
    )
    # ... plus the literals handed to the plot_* helpers as name/name1/name2,
    # which those helpers join with `directory`.
    written |= set(re.findall(r'^\s*"([a-z][a-z0-9-]*\.html)",\s*$', src, re.M))
    return written


class TestSummarizeAssets(unittest.TestCase):
    def test_every_iframe_has_a_writer(self):
        missing = sorted(_iframe_targets() - _written_filenames())
        self.assertEqual(
            missing,
            [],
            f"templates reference files nothing writes (blank panes): {missing}",
        )

    def test_no_orphan_writers(self):
        orphans = sorted(_written_filenames() - _iframe_targets())
        self.assertEqual(
            orphans,
            [],
            f"visualizer writes files no template displays: {orphans}",
        )

    def test_plots_are_actually_written(self):
        """The regression itself: no commented-out plot calls left behind."""
        src = _VISUALIZER.read_text()
        self.assertNotIn(
            "# offline.plot(",
            src,
            "commented-out offline.plot call found -- plot panes will be blank",
        )
        self.assertIn("write_html(", src)

    def test_plotly_js_is_not_fetched_from_a_cdn(self):
        """A .qzv must render offline and inside `qiime tools view`."""
        src = _VISUALIZER.read_text()
        for match in re.findall(r'include_plotlyjs=(["\'])(\w+)\1', src):
            self.assertNotEqual(
                match[1], "cdn", "include_plotlyjs='cdn' breaks offline viewing"
            )


if __name__ == "__main__":
    unittest.main()
