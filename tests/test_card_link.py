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
import sphinx

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


# ---------------------------------------------------------------------------
# link-new-tab tests
# ---------------------------------------------------------------------------

# Sphinx's HTML writer renders a reference's ``rel`` attribute only from 7.4;
# ``target`` is rendered on every supported version.
# Browsers imply ``noopener`` for ``target="_blank"`` anyway.
RENDERS_REL = sphinx.version_info >= (7, 4)


def _stretched_link_tags(html):
    """Return the opening ``<a ...>`` tag of every card ``sd-stretched-link``."""
    return re.findall(r"<a [^>]*\bsd-stretched-link\b[^>]*>", html)


def _assert_opens_in_new_tab(html):
    """The card's only stretched link opens in a new tab."""
    tags = _stretched_link_tags(html)
    assert len(tags) == 1, tags
    assert 'target="_blank"' in tags[0], tags[0]
    if RENDERS_REL:
        assert 'rel="noreferrer noopener"' in tags[0], tags[0]
    else:
        assert "rel=" not in tags[0], tags[0]


NEW_TAB_URL_RST = """
Heading
=======

.. card:: New-tab URL card
    :link: https://example.com
    :link-new-tab:

    Card body
"""

NEW_TAB_URL_MYST = """
# Heading

:::{card} New-tab URL card
:link: https://example.com
:link-new-tab:

Card body
:::
"""


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_url_new_tab(fmt, sphinx_builder):
    """``link-new-tab`` adds ``target="_blank"`` and ``rel="noreferrer noopener"``
    to a URL card link.
    """
    builder = _build(sphinx_builder, fmt, NEW_TAB_URL_RST, NEW_TAB_URL_MYST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _stretched_link_hrefs(html) == ["https://example.com"]
    _assert_opens_in_new_tab(html)


NEW_TAB_REF_RST = """
Heading
=======

My Section
----------

Some content.

.. card:: New-tab internal card
    :link: my section
    :link-type: ref
    :link-new-tab:

    Card body
"""

NEW_TAB_REF_MYST = """
# Heading

## My Section

Some content.

:::{card} New-tab internal card
:link: my section
:link-type: ref
:link-new-tab:

Card body
:::
"""


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_ref_new_tab(fmt, sphinx_builder):
    """``link-new-tab`` also applies to internal cross-reference cards.

    ``pending_xref`` is resolved to ``nodes.reference`` before
    ``doctree-resolved`` fires, so the event handler can stamp the
    ``target`` and ``rel`` attributes onto the real anchor.
    """
    builder = _build(sphinx_builder, fmt, NEW_TAB_REF_RST, NEW_TAB_REF_MYST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _stretched_link_hrefs(html) == ["#my-section"]
    _assert_opens_in_new_tab(html)


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_doc_new_tab(fmt, sphinx_builder):
    """``link-new-tab`` applies to a ``link-type: doc`` card linking to another page."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        index = (
            "Heading\n=======\n\n"
            ".. toctree::\n\n    other\n\n"
            ".. card:: New-tab doc card\n"
            "    :link: other\n    :link-type: doc\n    :link-new-tab:\n\n"
            "    Card body\n"
        )
        builder.src_path.joinpath("index.rst").write_text(index, encoding="utf8")
        builder.src_path.joinpath("other.rst").write_text(
            "Other\n=====\n", encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        index = (
            "# Heading\n\n"
            "```{toctree}\nother\n```\n\n"
            ":::{card} New-tab doc card\n"
            ":link: other\n:link-type: doc\n:link-new-tab:\n\n"
            "Card body\n:::\n"
        )
        builder.src_path.joinpath("index.md").write_text(index, encoding="utf8")
        builder.src_path.joinpath("other.md").write_text("# Other\n", encoding="utf8")
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _stretched_link_hrefs(html) == ["other.html"]
    _assert_opens_in_new_tab(html)


NEW_TAB_GRID_RST = """
Heading
=======

.. grid:: 1

    .. grid-item-card:: New-tab grid card
        :link: https://example.com
        :link-new-tab:

        Grid card body
"""

NEW_TAB_GRID_MYST = """
# Heading

::::{grid} 1

:::{grid-item-card} New-tab grid card
:link: https://example.com
:link-new-tab:

Grid card body
:::

::::
"""


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_grid_item_card_new_tab(fmt, sphinx_builder):
    """``link-new-tab`` works on ``grid-item-card`` (synced ``option_spec``)."""
    builder = _build(sphinx_builder, fmt, NEW_TAB_GRID_RST, NEW_TAB_GRID_MYST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _stretched_link_hrefs(html) == ["https://example.com"]
    _assert_opens_in_new_tab(html)


NO_NEW_TAB_RST = """
Heading
=======

My Section
----------

.. card:: URL card
    :link: https://example.com

    Card body

.. card:: Internal card
    :link: my section
    :link-type: ref

    Card body
"""

NO_NEW_TAB_MYST = """
# Heading

## My Section

:::{card} URL card
:link: https://example.com

Card body
:::

:::{card} Internal card
:link: my section
:link-type: ref

Card body
:::
"""


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_link_without_new_tab(fmt, sphinx_builder):
    """Without ``link-new-tab``, card links keep opening in the same tab."""
    builder = _build(sphinx_builder, fmt, NO_NEW_TAB_RST, NO_NEW_TAB_MYST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _stretched_link_hrefs(html) == ["https://example.com", "#my-section"]
    for tag in _stretched_link_tags(html):
        assert "target=" not in tag, tag
        assert "rel=" not in tag, tag
