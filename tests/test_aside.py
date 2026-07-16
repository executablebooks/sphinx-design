"""Tests for the ``aside`` component (see #97).

The RST/MyST doctree structure and classes are locked by the snippet
regression fixtures (``tests/test_snippets``); these tests additionally assert
the *rendered HTML* semantics: a native ``<aside>`` element, the
``aria-labelledby`` wiring, cross-reference behaviour and the documented
trailing-float workaround.
"""

import re

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
    """An aside renders as a semantic ``<aside>``, labelled by its title."""
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
    builder.build()  # asserts no warnings (the :ref: to the title must resolve)

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
    # a titled, :name:d aside is labelled by (and anchored on) its title
    assert asides[0]["aria_labelledby"] == "note-1"

    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert re.search(
        r'<aside aria-labelledby="note-1" '
        r'class="sd-aside sd-aside-right sd-aside-w-33 sd-mb-3">',
        html,
    )
    # a plain <div> carrying the component class would defeat the semantics
    assert '<div class="sd-aside ' not in html
    # the :name: target lands on the title, so the reference resolves and the
    # anchor (and the aria-labelledby referent) is present in the output
    assert '<p class="sd-aside-title rubric" id="note-1">' in html


def test_aside_titled_autolabels_with_stable_id(sphinx_builder):
    """A titled aside without ``:name:`` gets a deterministic title id + label.

    The id is numbered in document order (``sd-aside-title-<n>``), so it is
    stable across rebuilds with no randomness.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n.. aside:: Heads up\n\n   Content.\n", encoding="utf8"
    )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    (aside,) = doctree.findall(aside_main)
    assert aside["aria_labelledby"] == "sd-aside-title-0"
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'aria-labelledby="sd-aside-title-0"' in html
    assert '<p class="sd-aside-title rubric" id="sd-aside-title-0">' in html


def test_aside_untitled_is_unlabelled(sphinx_builder):
    """An untitled aside is left unlabelled (no invented aria-label)."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n.. aside::\n\n   Untitled content.\n", encoding="utf8"
    )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    (aside,) = doctree.findall(aside_main)
    assert "aria_labelledby" not in aside
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # no aria-* labelling on the aside element itself (the theme may use
    # aria-label elsewhere on the page, so scope the check to the <aside> tag)
    aside_tag = re.search(r"<aside\b[^>]*>", html).group(0)
    assert "aria-label" not in aside_tag


def test_aside_untitled_target_on_container(sphinx_builder):
    """Without a title the ``:name:`` target lands on the aside itself,
    and a reference with explicit text resolves without warning.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Title
=====

.. aside::
   :name: bare-aside

   Untitled aside content.

See :ref:`the note <bare-aside>`.
""",
        encoding="utf8",
    )
    builder.build()  # asserts no warnings (explicit link text is supplied)
    doctree = builder.get_doctree("index", post_transforms=True)
    (aside,) = doctree.findall(aside_main)
    assert "bare-aside" in aside["ids"]
    assert "aria_labelledby" not in aside
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert '<aside class="sd-aside sd-aside-right sd-aside-w-33 sd-mb-3" ' in html
    assert 'id="bare-aside"' in html
    # the explicit-text reference resolves to a working internal link
    assert 'href="#bare-aside"' in html
    assert ">the note</span></a>" in html


def test_aside_untitled_bare_ref_warns(sphinx_builder):
    """A bare ``:ref:`` to an untitled (captionless) named aside warns and
    renders without a link, per standard Sphinx captionless-target behaviour.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Title
=====

.. aside::
   :name: bare-aside

   Untitled aside content.

See :ref:`bare-aside`.
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "A title or caption not found: 'bare-aside'" in builder.warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # rendered as inert text, not a hyperlink
    assert '<span class="xref std std-ref">bare-aside</span>' in html
    assert 'href="#bare-aside"' not in html


def test_aside_trailing_clear_workaround(sphinx_builder):
    """The documented trailing-aside workaround emits a cleared block.

    A float is not contained by its section, so a trailing aside is followed by
    a ``div`` carrying ``sd-clear-both`` to push subsequent content below it.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Title
=====

.. aside:: Wrap-up
   :align: right

   The last content in this section.

.. div:: sd-clear-both
""",
        encoding="utf8",
    )
    builder.build()  # asserts no warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    aside_pos = html.index("</aside>")
    clear_pos = html.index('<div class="sd-clear-both')
    # the clearing div follows the aside in source order
    assert aside_pos < clear_pos


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
