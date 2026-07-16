"""Tests for the card header/footer sub-directives and the legacy separators.

These exercise the parser-portable ``card-header``/``card-footer`` directive
syntax, the deprecated ``^^^``/``+++`` separator fallback (gated on
``sd_card_legacy_separators``), and prove the two produce identical doctrees.
"""

from docutils import nodes
import pytest

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


def _rst_builder(sphinx_builder, **conf):
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"], **conf})
    return builder


def _cards(doctree):
    return list(doctree.findall(lambda n: is_component(n, "card")))


# ---------------------------------------------------------------------------
# Doctree identity: legacy separators vs. header/footer directives
# ---------------------------------------------------------------------------

IDENTITY_RST = """
Heading
=======

.. card:: Card Title

   .. card-header::

      Header *emph*

   Card content

   .. card-footer::

      Footer

.. card:: Card Title

   Header *emph*
   ^^^
   Card content
   +++
   Footer
"""

IDENTITY_MYST = """
# Heading

::::{card} Card Title

:::{card-header}
Header *emph*
:::

Card content

:::{card-footer}
Footer
:::
::::

:::{card} Card Title
Header *emph*
^^^
Card content
+++
Footer
:::
"""


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_new_and_legacy_identical(fmt, sphinx_builder):
    """The directive syntax and the legacy separators must produce an
    identical card doctree for equivalent input.
    """
    if fmt == "rst":
        builder = _rst_builder(sphinx_builder, suppress_warnings=["design.card_legacy"])
        builder.src_path.joinpath("index.rst").write_text(IDENTITY_RST, encoding="utf8")
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": ["myst_parser", "sphinx_design"],
                "myst_enable_extensions": ["colon_fence"],
                "suppress_warnings": ["design.card_legacy"],
            }
        )
        builder.src_path.joinpath("index.md").write_text(IDENTITY_MYST, encoding="utf8")
    builder.build()  # asserts no (unsuppressed) warnings
    cards = _cards(builder.get_doctree("index"))
    assert len(cards) == 2
    new, legacy = cards
    assert new.pformat() == legacy.pformat()


def test_grid_item_card_new_and_legacy_identical(sphinx_builder):
    """``grid-item-card`` gets the same treatment as ``card``."""
    builder = _rst_builder(sphinx_builder, suppress_warnings=["design.card_legacy"])
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. grid:: 2

   .. grid-item-card:: Title

      .. card-header::

         Header

      Body

      .. card-footer::

         Footer

   .. grid-item-card:: Title

      Header
      ^^^
      Body
      +++
      Footer
""",
        encoding="utf8",
    )
    builder.build()
    cards = _cards(builder.get_doctree("index"))
    assert len(cards) == 2
    assert cards[0].pformat() == cards[1].pformat()


# ---------------------------------------------------------------------------
# Legacy deprecation warning
# ---------------------------------------------------------------------------


def test_card_legacy_warns_once_per_document(sphinx_builder):
    """The legacy separators emit exactly one ``design.card_legacy`` warning
    per document, regardless of how many cards use them.
    """
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card::

   A
   ^^^
   B

.. card::

   C
   +++
   D
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    # exactly one deprecation notice, however many cards use the separators
    # (count the unique message body, since Sphinx may also append the subtype)
    assert builder.warnings.count("card header/footer separators are deprecated") == 1
    assert "[design.card_legacy]" in builder.warnings


def test_card_legacy_warning_suppressible(sphinx_builder):
    """The deprecation warning is suppressible via ``suppress_warnings``."""
    builder = _rst_builder(sphinx_builder, suppress_warnings=["design.card_legacy"])
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card::

   A
   ^^^
   B
   +++
   C
""",
        encoding="utf8",
    )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index")
    assert list(doctree.findall(lambda n: is_component(n, "card-header")))
    assert list(doctree.findall(lambda n: is_component(n, "card-footer")))


def test_card_legacy_disabled(sphinx_builder):
    """With the flag off, separators are ordinary rST and no slots are made."""
    builder = _rst_builder(sphinx_builder, sd_card_legacy_separators=False)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card::

   .. code-block:: text

      first
      +++
      second
""",
        encoding="utf8",
    )
    builder.build()  # no deprecation warning, no mis-split
    doctree = builder.get_doctree("index")
    # the killer regression: the ``+++`` inside the code-block survives intact
    literals = list(doctree.findall(nodes.literal_block))
    assert len(literals) == 1
    assert "+++" in literals[0].astext()
    assert not list(doctree.findall(lambda n: is_component(n, "card-footer")))
    assert "[design.card_legacy]" not in builder.warnings


# ---------------------------------------------------------------------------
# Directive-syntax behaviours
# ---------------------------------------------------------------------------


def test_card_header_footer_out_of_order(sphinx_builder):
    """A footer directive before the body still renders in the footer slot."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   .. card-footer::

      Footer

   Body

   .. card-header::

      Header
""",
        encoding="utf8",
    )
    builder.build()  # no warnings
    card = _cards(builder.get_doctree("index"))[0]
    # slots are assembled in header, body, footer order regardless of source
    kinds = [child.get("design_component") for child in card.children]
    assert kinds == ["card-header", "card-body", "card-footer"]


def test_card_header_only(sphinx_builder):
    """A card with only a header directive (no footer)."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   .. card-header::

      Just a header

   Body
""",
        encoding="utf8",
    )
    builder.build()  # no warnings
    card = _cards(builder.get_doctree("index"))[0]
    kinds = [child.get("design_component") for child in card.children]
    assert kinds == ["card-header", "card-body"]


def test_card_footer_only(sphinx_builder):
    """A card with only a footer directive (no header)."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   Body

   .. card-footer::

      Just a footer
""",
        encoding="utf8",
    )
    builder.build()  # no warnings
    card = _cards(builder.get_doctree("index"))[0]
    kinds = [child.get("design_component") for child in card.children]
    assert kinds == ["card-body", "card-footer"]


def test_card_slot_class_option(sphinx_builder):
    """The sub-directives' ``:class:`` option, and the card's ``class-header`` /
    ``class-footer`` options, both land on the slot.
    """
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title
   :class-header: from-card

   .. card-header::
      :class: from-directive

      Header

   Body
""",
        encoding="utf8",
    )
    builder.build()  # no warnings
    card = _cards(builder.get_doctree("index"))[0]
    header = next(card.findall(lambda n: is_component(n, "card-header")))
    assert header["classes"] == ["sd-card-header", "from-card", "from-directive"]


def test_card_multiple_headers_warn_and_merge(sphinx_builder):
    """Multiple header directives warn and are merged into one slot."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   .. card-header::

      First

   .. card-header::

      Second

   Body
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "multiple 'card-header'" in builder.warnings
    assert "[design.card]" in builder.warnings
    card = _cards(builder.get_doctree("index"))[0]
    headers = list(card.findall(lambda n: is_component(n, "card-header")))
    assert len(headers) == 1
    assert "First" in headers[0].astext()
    assert "Second" in headers[0].astext()


def test_card_header_outside_card_warns(sphinx_builder):
    """A ``card-header`` outside a card warns (mirrors the tab-item check)."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card-header::

   orphan
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "parent of a 'card-header' should be a 'card'" in builder.warnings
    assert "[design.card]" in builder.warnings


def test_card_mixed_syntax_warns(sphinx_builder):
    """Using both separators and directives warns; directives win."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   .. card-header::

      Directive header

   Body
   +++
   Separator footer
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert (
        "mixes '^^^'/'+++' separators with card-header/card-footer" in builder.warnings
    )
    assert "sd_card_legacy_separators=False" in builder.warnings
    card = _cards(builder.get_doctree("index"))[0]
    headers = list(card.findall(lambda n: is_component(n, "card-header")))
    assert len(headers) == 1
    assert "Directive header" in headers[0].astext()


def test_card_directive_nested_in_legacy_chunk(sphinx_builder):
    """A card-header/card-footer directive nested inside a separator chunk is
    hoisted (warned + merged), leaving no doubled ``sd-card-*`` wrapper.
    """
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: footer directive in footer chunk

   Body
   +++
   .. card-footer::

      real footer

.. card:: header directive in header chunk

   .. card-header::

      real header

   ^^^
   Body two
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "mixes '^^^'/'+++' separators" in builder.warnings
    cards = _cards(builder.get_doctree("index"))
    assert len(cards) == 2
    # exactly one footer/header slot per card -- no slot-in-slot doubling
    footers = list(cards[0].findall(lambda n: is_component(n, "card-footer")))
    assert len(footers) == 1
    assert "real footer" in footers[0].astext()
    headers = list(cards[1].findall(lambda n: is_component(n, "card-header")))
    assert len(headers) == 1
    assert "real header" in headers[0].astext()


def test_card_empty_slot_directive_errors(sphinx_builder):
    """An empty card-header/card-footer directive errors (behaviour change vs
    an empty legacy chunk, which produced an empty slot).
    """
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title

   .. card-header::

   Body
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "Content block expected for the" in builder.warnings


def test_card_header_footer_options(sphinx_builder):
    """The inline ``:header:``/``:footer:`` options build the slots."""
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title
   :header: Inline **header**
   :footer: Inline footer

   Body
""",
        encoding="utf8",
    )
    builder.build()  # no warnings
    card = _cards(builder.get_doctree("index"))[0]
    header = next(card.findall(lambda n: is_component(n, "card-header")))
    footer = next(card.findall(lambda n: is_component(n, "card-footer")))
    assert "header" in header.astext()
    # inline markup is parsed (the emphasis produces a strong node)
    assert list(header.findall(nodes.strong))
    assert "Inline footer" in footer.astext()


def test_card_option_and_directive_conflict_warns(sphinx_builder):
    """A ``:header:`` option and a ``card-header`` directive conflict warns;
    the directive wins.
    """
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text(
        """
Heading
=======

.. card:: Title
   :header: Option header

   .. card-header::

      Directive header

   Body
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "':header:' option ignored" in builder.warnings
    card = _cards(builder.get_doctree("index"))[0]
    header = next(card.findall(lambda n: is_component(n, "card-header")))
    assert "Directive header" in header.astext()
    assert "Option header" not in header.astext()


def test_card_footer_line_attribution(sphinx_builder):
    """An error inside a card-footer reports the footer's line, not the card's.

    This is the payoff of the single-parse rework (killing the old
    ``TODO set proper lines``).
    """
    lines = [
        "Heading",
        "=======",
        "",
        ".. card:: Title",  # card starts on this line (index 3 -> line 4)
        "",
        "   Body",
        "",
        "   .. card-footer::",
        "",
        "      .. nonexistent-directive::",  # the error line
        "",
        "         boom",
        "",
    ]
    card_line = lines.index(".. card:: Title") + 1
    error_line = lines.index("      .. nonexistent-directive::") + 1
    builder = _rst_builder(sphinx_builder)
    builder.src_path.joinpath("index.rst").write_text("\n".join(lines), encoding="utf8")
    builder.build(assert_pass=False)
    assert "Unknown directive type" in builder.warnings
    assert f"index.rst:{error_line}:" in builder.warnings
    assert f"index.rst:{card_line}:" not in builder.warnings
