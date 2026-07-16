"""Accessibility-focused tests for the tabs component.

Covers:

* the ARIA wiring added for :issue:`30` — every tab ``label`` references the
  content panel it toggles via an ``aria-controls`` attribute pointing at a
  stable, unique id on the content container;
* the restored keyboard focus rings carried from :pr:`230`, whose styling
  lives in the compiled static stylesheet.
"""

from pathlib import Path
import re

import pytest

from sphinx_design.shared import is_component
from sphinx_design.tabs import sd_tab_label

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

# mirror the skip pattern used by the other test modules for MyST variants
MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)

COMPILED_CSS = (
    Path(__file__).parent.parent / "sphinx_design" / "static" / "sphinx-design.min.css"
)

# two tab-sets on one page, so we can check ids stay unique across sets
TWO_TAB_SETS = {
    "rst": """
Heading
=======

.. tab-set::

   .. tab-item:: A1

      A1 content

   .. tab-item:: B1

      B1 content

.. tab-set::

   .. tab-item:: A2

      A2 content

   .. tab-item:: B2

      B2 content
""",
    "myst": """
# Heading

::::{tab-set}
:::{tab-item} A1
A1 content
:::
:::{tab-item} B1
B1 content
:::
::::

::::{tab-set}
:::{tab-item} A2
A2 content
:::
:::{tab-item} B2
B2 content
:::
::::
""",
}


def _build_two_tab_sets(fmt, sphinx_builder):
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            TWO_TAB_SETS["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            TWO_TAB_SETS["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    return builder


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_tab_label_aria_controls_matches_content_id(fmt, sphinx_builder):
    """Each tab label's ``aria-controls`` equals the id of its content panel."""
    builder = _build_two_tab_sets(fmt, sphinx_builder)
    doctree = builder.get_doctree("index", post_transforms=True)

    tab_sets = list(doctree.findall(lambda n: is_component(n, "tab-set")))
    assert len(tab_sets) == 2

    checked = 0
    for tab_set in tab_sets:
        # the transform rebuilds each set as a flat sequence of
        # [input, label, content, input, label, content, ...], so a label is
        # immediately followed by the content container it controls
        kids = tab_set.children
        for i, node in enumerate(kids):
            if not isinstance(node, sd_tab_label):
                continue
            content = kids[i + 1]
            assert is_component(content, "tab-content")
            # the content id is prepended, so it is always ids[0]
            assert content["ids"], "content container should carry a stable id"
            assert node["aria_controls"] == content["ids"][0]
            assert node["aria_controls"].endswith("-content")
            checked += 1
    assert checked == 4

    # and the association survives into the rendered HTML
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    for label in doctree.findall(sd_tab_label):
        aria = label["aria_controls"]
        assert f'aria-controls="{aria}"' in html
        assert f'id="{aria}"' in html
    # the compiled stylesheet (carrying the focus rings) is linked from the page
    assert "sphinx-design.min.css" in html


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_tab_content_ids_unique_across_tab_sets(fmt, sphinx_builder):
    """Content ids (and their aria-controls references) are unique across sets."""
    builder = _build_two_tab_sets(fmt, sphinx_builder)
    doctree = builder.get_doctree("index", post_transforms=True)

    content_ids = [
        node["ids"][0]
        for node in doctree.findall(lambda n: is_component(n, "tab-content"))
    ]
    assert len(content_ids) == 4
    assert len(set(content_ids)) == 4  # every panel id is unique on the page

    aria = [label["aria_controls"] for label in doctree.findall(sd_tab_label)]
    assert sorted(aria) == sorted(content_ids)


def test_compiled_css_restores_focus_rings():
    """The compiled stylesheet restores keyboard focus rings (carried from #230).

    The CSS is a static asset, so we assert against the compiled file directly.
    """
    css = COMPILED_CSS.read_text(encoding="utf8")
    # minifier-agnostic view: selectors compare with all whitespace squeezed
    squeezed = re.sub(r"\s+", "", css)

    # focus-visible rings are present (buttons, coloured backgrounds, cards, ...)
    assert ":focus-visible" in css

    # tab labels: the ring is suppressed only for non-focus-visible (pointer)
    # focus, i.e. keyboard focus keeps a visible ring
    assert ".sd-tab-set>input:not(:focus-visible)+label" in squeezed

    # dropdown summary: the previous ``outline:none`` on focus (which killed the
    # keyboard ring) is gone, and an outline offset is applied instead
    assert "sd-summary-title:focus{outline:none}" not in squeezed
    assert "outline-offset:.25rem" in squeezed
