"""Tests for the ``card`` / ``grid-item-card`` ``:link:`` option.

Covers #110 for the card path (the follow-up to the ``button-ref`` fix in
#281): a ``:link:`` reference target that contains whitespace -- e.g. the
labels ``sphinx.ext.autosectionlabel`` generates from section titles -- must be
preserved (and, for ``link-type: ref``, lowercased to match the ``:ref:``
role), rather than having all its whitespace stripped by ``directives.uri``.

The bug affected both the ``card`` directive (``cards.py``) and the
``grid-item-card`` directive (``grids.py``), which has its own ``option_spec``
that previously also ran ``:link:`` through ``directives.uri`` before delegating
to ``CardDirective.create_card``.
"""

import re

from docutils.parsers.rst import directives
import pytest

from sphinx_design.cards import CardDirective

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

# guard MyST variants so the ``py311-no-myst`` environment still passes
MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)


def _build(sphinx_builder, fmt, rst, myst, *, assert_pass=True):
    """Build a single-document project written in ``rst`` or ``myst``.

    ``sphinx.ext.autosectionlabel`` is enabled so that section titles become
    (multi-word) reference labels -- exactly the #110 reproduction.
    """
    if fmt == "rst":
        builder = sphinx_builder(
            conf_kwargs={"extensions": ["sphinx_design", "sphinx.ext.autosectionlabel"]}
        )
        builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": [
                    "myst_parser",
                    "sphinx_design",
                    "sphinx.ext.autosectionlabel",
                ],
                "myst_enable_extensions": ["colon_fence"],
            }
        )
        builder.src_path.joinpath("index.md").write_text(myst, encoding="utf8")
    builder.build(assert_pass=assert_pass)
    return builder


def _stretched_link_hrefs(html):
    """Return the ``href`` of every card ``sd-stretched-link`` anchor.

    This isolates the card's own link from unrelated anchors (e.g. the section
    heading's permalink), which also point at ``#my-section-name``.
    """
    return re.findall(r'<a [^>]*\bsd-stretched-link\b[^>]*href="([^"]*)"', html)


def test_get_link_target_normalisation():
    """``get_link_target`` normalises a raw ``:link:`` value per ``link-type``.

    ``url`` strips *all* whitespace (byte-identical to the previous
    ``directives.uri`` behaviour); ``ref`` collapses internal whitespace *and*
    lowercases (matching Sphinx's ``XRefRole(lowercase=True)`` ``:ref:`` role);
    ``doc``/``any`` collapse whitespace but preserve case.
    """
    # url: identical to directives.uri (all whitespace removed)
    assert CardDirective.get_link_target(
        "https://example.com/a b", "url"
    ) == directives.uri("https://example.com/a b")
    assert (
        CardDirective.get_link_target("my article section", "url") == "myarticlesection"
    )
    # ref: whitespace collapsed to single spaces, then lowercased
    assert CardDirective.get_link_target("My   Article\n Section", "ref") == (
        "my article section"
    )
    assert CardDirective.get_link_target("  Spaced-Label  ", "ref") == "spaced-label"
    # doc / any: whitespace collapsed, case preserved
    assert CardDirective.get_link_target("My   Doc\n Name", "doc") == "My Doc Name"
    assert CardDirective.get_link_target("My   Any\n Target", "any") == "My Any Target"


CARD_MULTIWORD = {
    "rst": """
Heading
=======

My Section Name
---------------

Some content.

.. card:: A card title
    :link: my section name
    :link-type: ref

    Card body
""",
    "myst": """
# Heading

## My Section Name

Some content.

:::{card} A card title
:link: my section name
:link-type: ref

Card body
:::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_ref_multiword_target(fmt, sphinx_builder):
    """A ``card`` ``:link:`` to a multi-word ref label resolves (#110)."""
    builder = _build(sphinx_builder, fmt, CARD_MULTIWORD["rst"], CARD_MULTIWORD["myst"])
    # a clean build (no ``undefined label`` warning) already proves it resolved
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert "#my-section-name" in _stretched_link_hrefs(html)


GRID_MULTIWORD = {
    "rst": """
Heading
=======

My Section Name
---------------

Some content.

.. grid:: 1

    .. grid-item-card:: A grid card
        :link: my section name
        :link-type: ref

        Grid card body
""",
    "myst": """
# Heading

## My Section Name

Some content.

::::{grid} 1

:::{grid-item-card} A grid card
:link: my section name
:link-type: ref

Grid card body
:::

::::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_grid_item_card_ref_multiword_target(fmt, sphinx_builder):
    """A ``grid-item-card`` ``:link:`` to a multi-word ref label resolves.

    This is the exact #110 reproduction; ``grid-item-card`` has its own
    ``option_spec``, so it needs the same fix as ``card``.
    """
    builder = _build(sphinx_builder, fmt, GRID_MULTIWORD["rst"], GRID_MULTIWORD["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert "#my-section-name" in _stretched_link_hrefs(html)


TITLECASE_RST = """
Heading
=======

My Section Name
---------------

Some content.

.. card:: A card title
    :link: My Section Name
    :link-type: ref

    Card body
"""


def test_card_ref_titlecase_target(sphinx_builder):
    """A Title-Case ``ref`` target resolves like ``:ref:`` (lowercase parity).

    Sphinx stores std-domain labels lowercased and ``:ref:`` lowercases its
    target, so the verbatim heading text can be pasted as ``:link:``.
    """
    builder = _build(sphinx_builder, "rst", TITLECASE_RST, "")
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert "#my-section-name" in _stretched_link_hrefs(html)


URL_RST = """
Heading
=======

.. card:: A card title
    :link: https://example.com/a b
    :link-type: url

    Card body

.. card:: Another card
    :link: https://example.com/plain

    Body
"""


def test_card_link_url_whitespace_unchanged(sphinx_builder):
    """``link-type: url`` behaviour is byte-identical to before the fix.

    ``directives.uri`` removed all whitespace from URLs; the default
    (``link-type: url``) path must keep doing exactly that.
    """
    builder = _build(sphinx_builder, "rst", URL_RST, "")
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    hrefs = _stretched_link_hrefs(html)
    assert hrefs == [
        directives.uri("https://example.com/a b"),
        "https://example.com/plain",
    ]
    assert hrefs[0] == "https://example.com/ab"


UNRESOLVED_RST = """
Heading
=======

.. card:: A card title
    :link: No Such Label
    :link-type: ref

    Card body
"""


def test_card_ref_unresolved_warns(sphinx_builder):
    """An unresolved ``ref`` ``:link:`` warns and still builds (no crash).

    The (normalised, lowercased) target appears in a standard missing-reference
    warning; the card body still renders, unlinked.
    """
    builder = _build(sphinx_builder, "rst", UNRESOLVED_RST, "", assert_pass=False)
    # the collapsed + lowercased target is what is looked up (and reported)
    assert "undefined label: 'no such label'" in builder.warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # build completed and the content survives, just without a resolved link
    assert "Card body" in html
    assert _stretched_link_hrefs(html) == []
