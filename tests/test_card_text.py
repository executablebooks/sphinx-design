"""Tests for how ``sd-card-text`` is stamped on card and dropdown paragraphs.

Covers two bugs:

- the dropdown HTML transform used to *replace* (rather than append to) the
  ``classes`` of every body paragraph, silently destroying user-authored
  classes;
- both cards and dropdowns used to stamp ``sd-card-text`` on *all* descendant
  paragraphs (via ``findall``), including paragraphs nested inside admonitions,
  lists, nested cards, etc., causing the spacing artefacts in
  https://github.com/executablebooks/sphinx-design/issues/40.

Both sites now stamp only *direct child* paragraphs, and always append.
"""

from collections.abc import Callable

from docutils import nodes
import pytest

from sphinx_design.shared import is_component

from .conftest import SphinxBuilder

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)


def _build(
    sphinx_builder: Callable[..., SphinxBuilder],
    fmt: str,
    rst: str,
    myst: str,
    myst_extensions: tuple[str, ...] = ("colon_fence",),
) -> SphinxBuilder:
    """Build ``rst`` or ``myst`` source depending on ``fmt``."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": ["myst_parser", "sphinx_design"],
                "myst_enable_extensions": list(myst_extensions),
            }
        )
        builder.src_path.joinpath("index.md").write_text(myst, encoding="utf8")
    builder.build()  # asserts no warnings
    return builder


def _direct_paragraphs(node: nodes.Element) -> list[nodes.paragraph]:
    """Return the direct child paragraphs of ``node``."""
    return [child for child in node.children if isinstance(child, nodes.paragraph)]


DROPDOWN_USER_CLASS = {
    "rst": """
Title
=====

.. dropdown:: My drop

   .. rst-class:: my-user-class

   A paragraph with a user class.
""",
    "myst": """
# Title

````{dropdown} My drop
{.my-user-class}
A paragraph with a user class.
````
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_dropdown_paragraph_keeps_user_class(
    fmt: str, sphinx_builder: Callable[..., SphinxBuilder]
):
    """A user class on a dropdown-body paragraph must survive the HTML transform,
    alongside ``sd-card-text`` (regression test for the class-wiping bug).
    """
    builder = _build(
        sphinx_builder,
        fmt,
        DROPDOWN_USER_CLASS["rst"],
        DROPDOWN_USER_CLASS["myst"],
        myst_extensions=("colon_fence", "attrs_block"),
    )
    doctree = builder.get_doctree("index", post_transforms=True)
    tagged = [
        para
        for para in doctree.findall(nodes.paragraph)
        if "my-user-class" in para.get("classes", [])
    ]
    assert len(tagged) == 1, [p.pformat() for p in doctree.findall(nodes.paragraph)]
    classes = tagged[0]["classes"]
    # the user class is preserved, and sd-card-text is appended (not a replacement)
    assert "my-user-class" in classes
    assert "sd-card-text" in classes


DROPDOWN_NESTED = {
    "rst": """
Title
=====

.. dropdown:: My drop

   Direct dropdown paragraph.

   .. note::

      Nested paragraph inside admonition.
""",
    "myst": """
# Title

::::{dropdown} My drop
Direct dropdown paragraph.

:::{note}
Nested paragraph inside admonition.
:::
::::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_dropdown_nested_paragraph_not_stamped(
    fmt: str, sphinx_builder: Callable[..., SphinxBuilder]
):
    """``sd-card-text`` is stamped on direct dropdown-body paragraphs only,
    not on paragraphs nested inside an admonition (regression test for #40).
    """
    builder = _build(
        sphinx_builder, fmt, DROPDOWN_NESTED["rst"], DROPDOWN_NESTED["myst"]
    )
    doctree = builder.get_doctree("index", post_transforms=True)
    body = next(doctree.findall(lambda n: is_component(n, "dropdown-body")))

    direct = _direct_paragraphs(body)
    assert len(direct) == 1
    assert "sd-card-text" in direct[0]["classes"]

    note = next(body.findall(nodes.note))
    nested = list(note.findall(nodes.paragraph))
    assert nested
    for para in nested:
        assert "sd-card-text" not in para.get("classes", [])


CARD_NESTED = {
    "rst": """
Title
=====

.. card:: My card

   Direct card paragraph.

   .. note::

      Nested paragraph inside admonition.
""",
    "myst": """
# Title

::::{card} My card
Direct card paragraph.

:::{note}
Nested paragraph inside admonition.
:::
::::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_card_nested_paragraph_not_stamped(
    fmt: str, sphinx_builder: Callable[..., SphinxBuilder]
):
    """``sd-card-text`` is stamped on direct card-body paragraphs only,
    not on paragraphs nested inside an admonition (regression test for #40).
    """
    builder = _build(sphinx_builder, fmt, CARD_NESTED["rst"], CARD_NESTED["myst"])
    doctree = builder.get_doctree("index", post_transforms=True)
    body = next(doctree.findall(lambda n: is_component(n, "card-body")))

    direct = _direct_paragraphs(body)
    assert len(direct) == 1
    assert "sd-card-text" in direct[0]["classes"]

    note = next(body.findall(nodes.note))
    nested = list(note.findall(nodes.paragraph))
    assert nested
    for para in nested:
        assert "sd-card-text" not in para.get("classes", [])


DROPDOWN_TWO_PARAS = {
    "rst": """
Title
=====

.. dropdown:: My drop

   First paragraph.

   Second paragraph.
""",
    "myst": """
# Title

::::{dropdown} My drop
First paragraph.

Second paragraph.
::::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_dropdown_two_paragraphs_identical(
    fmt: str, sphinx_builder: Callable[..., SphinxBuilder]
):
    """The #40 reproduction: two plain dropdown-body paragraphs should be
    stamped identically, so their spacing is consistent.
    """
    builder = _build(
        sphinx_builder, fmt, DROPDOWN_TWO_PARAS["rst"], DROPDOWN_TWO_PARAS["myst"]
    )
    doctree = builder.get_doctree("index", post_transforms=True)
    body = next(doctree.findall(lambda n: is_component(n, "dropdown-body")))

    direct = _direct_paragraphs(body)
    assert len(direct) == 2
    assert direct[0]["classes"] == direct[1]["classes"] == ["sd-card-text"]


GRID_ITEM_CARD_NESTED = {
    "rst": """
Title
=====

.. grid:: 1

   .. grid-item-card:: My card

      Direct card paragraph.

      .. note::

         Nested paragraph inside admonition.
""",
    "myst": """
# Title

:::::{grid} 1

::::{grid-item-card} My card
Direct card paragraph.

:::{note}
Nested paragraph inside admonition.
:::
::::
:::::
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_grid_item_card_nested_paragraph_not_stamped(
    fmt: str, sphinx_builder: Callable[..., SphinxBuilder]
):
    """``grid-item-card`` delegates to the card builder, so it must show the
    same behaviour: direct body paragraphs stamped, nested ones not (#40).
    """
    builder = _build(
        sphinx_builder,
        fmt,
        GRID_ITEM_CARD_NESTED["rst"],
        GRID_ITEM_CARD_NESTED["myst"],
    )
    doctree = builder.get_doctree("index", post_transforms=True)
    body = next(doctree.findall(lambda n: is_component(n, "card-body")))

    direct = _direct_paragraphs(body)
    assert len(direct) == 1
    assert "sd-card-text" in direct[0]["classes"]

    note = next(body.findall(nodes.note))
    nested = list(note.findall(nodes.paragraph))
    assert nested
    for para in nested:
        assert "sd-card-text" not in para.get("classes", [])
