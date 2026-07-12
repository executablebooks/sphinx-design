from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from docutils import nodes
import pytest

from sphinx_design._compat import findall
from sphinx_design.icons import get_material_icon_data, get_octicon_data
from sphinx_design.shared import is_component
from sphinx_design.tabs import sd_tab_input


def test_octicons(file_regression):
    """Test the available octicon names.

    This is intended to provide a diff of the octicons available,
    when the octicons are updated, to check if we are removing any
    (and hence breaking back-compatibility).
    """
    data = get_octicon_data()
    content = ""
    for octicon in sorted(data):
        content += f"{octicon}: {','.join(data[octicon]['heights'])}\n"
    file_regression.check(content)


@pytest.mark.parametrize("style", ["regular", "outlined", "round", "sharp", "twotone"])
def test_material(style, file_regression):
    """Test the available material icons names.

    This is intended to provide a diff of the octicons available,
    when the octicons are updated, to check if we are removing any
    (and hence breaking back-compatibility).
    """
    data = get_material_icon_data(style)
    content = ""
    for name in sorted(data):
        content += f"{name}: {','.join(data[name]['heights'])}\n"
    file_regression.check(content)


def test_tab_set_with_invalid_children(
    sphinx_builder, file_regression, normalize_doctree_xml
):
    """Test that tab-set with invalid children does not crash.

    This reproduces the issue from https://github.com/executablebooks/sphinx-design/issues/243
    where a ValueError was raised when a tab-set contained non-tab-item children.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Tab Test document
=================

.. tab-set::

   .. tab-item:: A

      A content

   foo

   .. tab-item:: B

      B content
""",
        encoding="utf8",
    )
    # Build should not crash, but should produce a warning
    builder.build(assert_pass=False)
    assert "All children of a 'tab-set' should be 'tab-item'" in builder.warnings

    # Valid tab items should still be processed
    doctree = builder.get_doctree("index", post_transforms=True)
    doctree.attributes.pop("translation_progress", None)
    file_regression.check(
        normalize_doctree_xml(doctree.pformat()),
        basename="test_tab_set_with_invalid_children",
        extension=".xml",
        encoding="utf8",
    )


GRID_WITH_COMMENT = {
    "rst": """
Test
====

.. grid:: 2

   .. a comment

   .. grid-item::

      A

   .. grid-item::

      B
""",
    "myst": """
# Test

`````{grid} 2

% a comment

```{grid-item}
A
```

```{grid-item}
B
```
`````
""",
}


@pytest.mark.parametrize("fmt", ["rst", "myst"])
def test_grid_with_comment(fmt, sphinx_builder):
    """A comment between grid-items should not trigger a warning.

    See https://github.com/executablebooks/sphinx-design/issues/86
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            GRID_WITH_COMMENT["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            GRID_WITH_COMMENT["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index")
    grid_items = list(findall(doctree)(lambda node: is_component(node, "grid-item")))
    assert len(grid_items) == 2


CARD_CAROUSEL_WITH_COMMENT = {
    "rst": """
Test
====

.. card-carousel:: 2

   .. a comment

   .. card:: Card A

      content A

   .. card:: Card B

      content B
""",
    "myst": """
# Test

`````{card-carousel} 2

% a comment

````{card} Card A
content A
````

````{card} Card B
content B
````
`````
""",
}


@pytest.mark.parametrize("fmt", ["rst", "myst"])
def test_card_carousel_with_comment(fmt, sphinx_builder):
    """A comment between cards should not trigger a warning.

    See https://github.com/executablebooks/sphinx-design/issues/86
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            CARD_CAROUSEL_WITH_COMMENT["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            CARD_CAROUSEL_WITH_COMMENT["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index")
    cards = list(findall(doctree)(lambda node: is_component(node, "card")))
    assert len(cards) == 2


TAB_SET_WITH_COMMENT = {
    "rst": """
Test
====

.. tab-set::

   .. a comment

   .. tab-item:: A

      A content

   .. tab-item:: B

      B content
""",
    "myst": """
# Test

````{tab-set}

% a comment

```{tab-item} A
A content
```

```{tab-item} B
B content
```
````
""",
}


@pytest.mark.parametrize("fmt", ["rst", "myst"])
def test_tab_set_with_comment(fmt, sphinx_builder):
    """A comment between tab-items should not trigger a warning.

    See https://github.com/executablebooks/sphinx-design/issues/86
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            TAB_SET_WITH_COMMENT["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            TAB_SET_WITH_COMMENT["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    # both tabs should still render in the HTML output
    doctree = builder.get_doctree("index", post_transforms=True)
    inputs = list(findall(doctree)(sd_tab_input))
    assert len(inputs) == 2
    assert inputs[0]["checked"] is True


TAB_SET_WITH_TARGET = {
    "rst": """
Test
====

.. tab-set::

   .. _my-target:

   .. tab-item:: A

      A content

See :ref:`target link <my-target>`.
""",
    "myst": """
# Test

````{tab-set}

(my-target)=

```{tab-item} A
A content
```
````

See {ref}`target link <my-target>`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", "myst"])
def test_tab_set_with_target(fmt, sphinx_builder):
    """A hyperlink target before a tab-item should be preserved,
    so that references to it still resolve, and should not trigger a warning.

    See https://github.com/executablebooks/sphinx-design/issues/86
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            TAB_SET_WITH_TARGET["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            TAB_SET_WITH_TARGET["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    # the target survives both the directive and HTML transform rebuilds,
    # placed at the front of the tab-set
    targets = list(findall(doctree)(nodes.target))
    assert len(targets) == 1
    assert is_component(targets[0].parent, "tab-set")
    assert targets[0].parent.children[0] is targets[0]
    # the tab still renders and is selected by default
    inputs = list(findall(doctree)(sd_tab_input))
    assert len(inputs) == 1
    assert inputs[0]["checked"] is True
    # the reference resolves to the target
    references = list(findall(doctree)(nodes.reference))
    assert len(references) == 1
    assert references[0]["refid"] == "my-target"


def test_tab_set_with_paragraph_warns(sphinx_builder):
    """A bare paragraph directly inside a tab-set should still warn."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        """
Test
====

.. tab-set::

   .. tab-item:: A

      A content

   not a tab item
""",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert "All children of a 'tab-set' should be 'tab-item'" in builder.warnings
    assert "[design.tab]" in builder.warnings
I18N_INDEX_RST = """\
Heading

.. _target-section:

Target Section
==============

.. button-link:: https://example.com

    Click me now

.. button-ref:: target-section
    :ref-type: ref

    Go to target

See the :bdg-primary:`stable` badge.
"""


def test_button_i18n_gettext(sphinx_builder, file_regression):
    """Gettext extraction should target only the button text, not the directive.

    See https://github.com/executablebooks/sphinx-design/issues/96

    Known gap (visible in the regression file): ``button-ref`` text is absent
    from the ``.pot`` because the gettext builder extracts from the resolved
    doctree, and std-domain xref resolution flattens explicit-title content,
    discarding the translatable marker. Translation itself still works for
    both button types (see ``test_button_i18n_translated``), since the Locale
    transform runs before resolution.
    """
    builder = sphinx_builder("gettext", conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(I18N_INDEX_RST, encoding="utf8")
    builder.build()
    out = (builder.out_path / "index.pot").read_text(encoding="utf8")
    # strip the metadata header (contains a varying timestamp)
    out = out[out.find("#: ") :]
    file_regression.check(
        out, basename="test_button_i18n_gettext", extension=".pot", encoding="utf8"
    )


def test_button_i18n_translated(sphinx_builder):
    """Translated buttons must keep their classes, link and resolve refs.

    See https://github.com/executablebooks/sphinx-design/issues/44
    and https://github.com/executablebooks/sphinx-design/issues/263
    """
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "language": "de",
            "locale_dirs": ["locales"],
        }
    )
    builder.src_path.joinpath("index.rst").write_text(I18N_INDEX_RST, encoding="utf8")
    catalog = Catalog(locale="de", domain="index")
    catalog.add("Click me now", "Klick mich jetzt")
    catalog.add("Go to target", "Zum Ziel")
    mo_dir = builder.src_path / "locales" / "de" / "LC_MESSAGES"
    mo_dir.mkdir(parents=True)
    with (mo_dir / "index.mo").open("wb") as handle:
        write_mo(handle, catalog)

    builder.build()
    doctree = builder.get_doctree("index", post_transforms=True)
    references = list(doctree.findall(nodes.reference))

    external = [
        ref
        for ref in references
        if "sd-btn" in ref["classes"]
        and ref.get("refuri", "").startswith("https://example.com")
    ]
    assert len(external) == 1, [r.pformat() for r in references]
    assert external[0].astext() == "Klick mich jetzt"

    internal = [
        ref
        for ref in references
        if "sd-btn" in ref["classes"] and not ref.get("refuri", "").startswith("http")
    ]
    assert len(internal) == 1, [r.pformat() for r in references]
    assert internal[0].astext() == "Zum Ziel"

    badges = [
        node
        for node in doctree.findall(nodes.inline)
        if "sd-badge" in node.get("classes", [])
    ]
    assert len(badges) == 1
    assert badges[0].astext() == "stable"
