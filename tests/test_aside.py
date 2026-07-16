"""Tests for the ``aside`` component (see #97).

The RST/MyST doctree structure and classes are locked by the snippet
regression fixtures (``tests/test_snippets``); these tests additionally assert
the *rendered HTML* is a semantic ``<aside>`` element and that a ``:name:``
reference resolves to the aside title.
"""

import pytest

from sphinx_design.aside import aside_main
from sphinx_design.shared import is_component

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)

ASIDE_SRC = {
    "rst": """
Title
=====

.. aside:: My aside
   :name: note-1
   :align: right
   :width: 33%

   Wrapped content.

Body text that wraps around the floated aside.

See :ref:`note-1`.
""",
    "myst": """
# Title

:::{aside} My aside
:name: note-1
:align: right
:width: 33%

Wrapped content.
:::

Body text that wraps around the floated aside.

See {ref}`note-1`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_aside_renders_semantic_element(fmt, sphinx_builder):
    """An aside must render as a semantic ``<aside>`` element in HTML."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            ASIDE_SRC["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            ASIDE_SRC["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings (the :ref: must also resolve)

    # the HTML-only post-transform swaps the container for an aside_main node
    doctree = builder.get_doctree("index", post_transforms=True)
    asides = list(doctree.findall(aside_main))
    assert len(asides) == 1
    assert asides[0]["classes"] == [
        "sd-aside",
        "sd-aside-right",
        "sd-aside-w-33",
        "sd-mb-3",
    ]

    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert '<aside class="sd-aside sd-aside-right sd-aside-w-33 sd-mb-3">' in html
    # a plain <div> carrying the component class would defeat the semantics
    assert '<div class="sd-aside ' not in html
    # the :name: target lands on the title, so the reference resolves and the
    # anchor is present in the output
    assert 'id="note-1"' in html


def test_aside_untitled_target_on_container(sphinx_builder):
    """Without a title the ``:name:`` target lands on the aside itself."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Title
=====

.. aside::
   :name: bare-aside

   Untitled aside content.

See :ref:`bare-aside <bare-aside>`.
""",
        encoding="utf8",
    )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    asides = list(doctree.findall(aside_main))
    assert len(asides) == 1
    assert "bare-aside" in asides[0]["ids"]
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'id="bare-aside"' in html


def test_aside_non_html_degrades_to_container(sphinx_builder):
    """For non-HTML builders the aside stays a plain (div) container.

    The ``AsideHtmlTransform`` is HTML-only, so a text/latex build keeps the
    ``design_component="aside"`` container and never sees an ``aside_main``
    node (which only has HTML visitors).
    """
    builder = sphinx_builder("text", conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        ".. aside:: My aside\n\n   Content.\n", encoding="utf8"
    )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    assert not list(doctree.findall(aside_main))
    assert len(list(doctree.findall(lambda n: is_component(n, "aside")))) == 1
