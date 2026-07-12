import dataclasses as dc
import tomllib

from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from docutils import nodes
import pytest

from sphinx_design._compat import findall
from sphinx_design.config import SdConfig, get_sd_config
from sphinx_design.icons import get_material_icon_data, get_octicon_data
from sphinx_design.shared import is_component
from sphinx_design.tabs import sd_tab_input

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)


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


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
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


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
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


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
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


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
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
=======

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


INVALID_CONFIG_VALUES = {
    "custom_directives": (["not", "a", "dict"], "must be a dictionary"),
    "fontawesome_latex": ("not-a-bool", "must be of type"),
}
"""An invalidly typed value (and expected warning) for every ``SdConfig`` field."""


def _write_index_rst(builder) -> None:
    builder.src_path.joinpath("index.rst").write_text(
        "Test\n====\n\ncontent\n", encoding="utf8"
    )


def test_config_invalid_values_cover_all_fields():
    """Ensure ``INVALID_CONFIG_VALUES`` stays in sync with the ``SdConfig`` fields."""
    assert set(INVALID_CONFIG_VALUES) == {f.name for f in dc.fields(SdConfig)}


@pytest.mark.parametrize("field", dc.fields(SdConfig), ids=lambda field: field.name)
def test_config_invalid_type(field, sphinx_builder):
    """An invalidly typed config value should emit a ``design.config`` warning,
    and fall back to the field default.
    """
    value, expected_warning = INVALID_CONFIG_VALUES[field.name]
    builder = sphinx_builder(
        conf_kwargs={"extensions": ["sphinx_design"], f"sd_{field.name}": value}
    )
    _write_index_rst(builder)
    builder.build(assert_pass=False)
    assert f"sd_{field.name}: " in builder.warnings
    assert expected_warning in builder.warnings
    default = (
        field.default_factory()
        if field.default_factory is not dc.MISSING
        else field.default
    )
    assert getattr(get_sd_config(builder.app.env), field.name) == default


def test_config_custom_directives_invalid_entry(sphinx_builder):
    """An invalid ``sd_custom_directives`` entry should emit a ``design.config``
    warning and be discarded, without affecting valid entries.
    """
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_custom_directives": {
                "dropdown-syntax": {"inherit": "dropdown", "argument": "Syntax"},
                "bad-directive": {"argument": "Other"},
            },
        }
    )
    _write_index_rst(builder)
    builder.build(assert_pass=False)
    assert "'bad-directive' value must have an 'inherit' key" in builder.warnings
    assert list(get_sd_config(builder.app.env).custom_directives) == ["dropdown-syntax"]


def test_config_custom_directives_unknown_inherit(sphinx_builder):
    """An unknown ``inherit`` directive should emit a ``design.config`` warning."""
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_custom_directives": {"foo": {"inherit": "unknown"}},
        }
    )
    _write_index_rst(builder)
    builder.build(assert_pass=False)
    assert "'foo.inherit' is an unknown directive key: unknown" in builder.warnings


def test_config_warnings_suppressible(sphinx_builder):
    """Config warnings are emitted with the ``design.config`` type/subtype,
    so they can be suppressed via ``suppress_warnings``.
    """
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "suppress_warnings": ["design.config"],
            # note, entry-level invalidity is used here, since top-level type
            # mismatches also emit (non-suppressible) sphinx core warnings
            "sd_custom_directives": {"foo": {"inherit": "unknown", "argument": 1}},
        }
    )
    _write_index_rst(builder)
    builder.build()
    assert builder.warnings == ""


def test_config_strict_validation():
    """Directly instantiating ``SdConfig`` with invalid values should raise."""
    with pytest.raises(TypeError, match="'fontawesome_latex' must be of type"):
        SdConfig(fontawesome_latex="not-a-bool")
    with pytest.raises(TypeError, match="'custom_directives' must be a dictionary"):
        SdConfig(custom_directives="not-a-dict")
    with pytest.raises(ValueError, match="must have an 'inherit' key"):
        SdConfig(custom_directives={"foo": {}})


def test_config_toml_round_trip():
    """All configuration values are TOML-representable:
    a TOML document containing every field should load and validate.
    """
    toml_str = """\
    fontawesome_latex = true

    [custom_directives.dropdown-syntax]
    inherit = "dropdown"
    argument = "Syntax"

    [custom_directives.dropdown-syntax.options]
    color = "primary"
    icon = "code"
    """
    data = tomllib.loads(toml_str)
    assert set(data) == {f.name for f in dc.fields(SdConfig)}, (
        "the TOML sample should contain every SdConfig field"
    )
    config = SdConfig(**data)
    assert config.fontawesome_latex is True
    assert config.custom_directives == {
        "dropdown-syntax": {
            "inherit": "dropdown",
            "argument": "Syntax",
            "options": {"color": "primary", "icon": "code"},
        }
    }
