"""Tests for the tabs JavaScript integration (``design-tabs.js``).

Covers the Python side of the tab-syncing behaviour: the configurable
``sd_tabs_storage_prefix`` and its delivery to the browser as a ``data-``
attribute on the script tag, plus the HTML DOM ordering that the JavaScript
relies on (input, label, content siblings).

The JavaScript behaviour itself has no automated harness here; the DOM-order
assertions in :func:`test_tab_dom_order` pin the structural assumptions that
``design-tabs.js`` makes (``label.previousElementSibling`` is the input,
``content.previousElementSibling.previousElementSibling`` is the input, and a
``:name:`` id lands on the label).

These tests deliberately use plain reStructuredText and only the
``sphinx_design`` extension, so that they also run under ``py311-no-myst`` (the
one exception, :func:`test_tab_dom_order`, is parametrized and guards its myst
case with the shared ``MYST_PARAM`` skip marker).
"""

import re

import pytest

from sphinx_design.config import SdConfig

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)

# Keep the config myst-free so these tests run without myst-parser installed.
SD_CONF = {"extensions": ["sphinx_design"]}

INDEX_RST = """
Test Document
=============

Some content.
"""


def _script_tag(builder) -> str:
    """Build the project and return the ``design-tabs.js`` script tag."""
    builder.src_path.joinpath("index.rst").write_text(INDEX_RST, encoding="utf8")
    builder.build()
    index_html = builder.out_path.joinpath("index.html").read_text(encoding="utf8")
    match = re.search(r"<script[^>]*design-tabs\.js[^>]*>", index_html)
    assert match, "no design-tabs.js script tag found in the built HTML"
    return match.group(0)


def test_script_tag_default_prefix(sphinx_builder):
    """By default the script tag carries the default storage-prefix attribute."""
    builder = sphinx_builder(conf_kwargs=SD_CONF)
    tag = _script_tag(builder)
    assert 'data-sd-tabs-storage-prefix="sphinx-design-tab-id-"' in tag
    # the native cache-busting suffix must not be lost by adding the attribute
    assert "design-tabs.js?v=" in tag


def test_script_tag_custom_prefix(sphinx_builder):
    """A customized ``sd_tabs_storage_prefix`` is forwarded to the script tag."""
    builder = sphinx_builder(
        conf_kwargs={**SD_CONF, "sd_tabs_storage_prefix": "custom-"}
    )
    tag = _script_tag(builder)
    assert 'data-sd-tabs-storage-prefix="custom-"' in tag


def test_script_tag_empty_prefix(sphinx_builder):
    """An empty ``sd_tabs_storage_prefix`` renders an empty attribute value.

    (In the browser this disables persistence, since ``getAttribute`` returns
    the empty string rather than ``null``.)
    """
    builder = sphinx_builder(conf_kwargs={**SD_CONF, "sd_tabs_storage_prefix": ""})
    tag = _script_tag(builder)
    assert 'data-sd-tabs-storage-prefix=""' in tag


def test_config_tabs_storage_prefix_invalid_type():
    """Directly instantiating ``SdConfig`` with a non-string prefix should raise."""
    with pytest.raises(TypeError, match="'tabs_storage_prefix' must be of type"):
        SdConfig(tabs_storage_prefix=123)


TAB_SET = {
    "rst": """
Test
====

.. tab-set::

   .. tab-item:: Label A
      :name: my-tab-a
      :sync: a

      Content A.

   .. tab-item:: Label B
      :sync: b

      Content B.

.. tab-set::

   .. tab-item:: Label A2
      :sync: a

      Second A.

   .. tab-item:: Label B2
      :sync: b

      Second B.
""",
    "myst": """
# Test

````{tab-set}
```{tab-item} Label A
:name: my-tab-a
:sync: a

Content A.
```
```{tab-item} Label B
:sync: b

Content B.
```
````

````{tab-set}
```{tab-item} Label A2
:sync: a

Second A.
```
```{tab-item} Label B2
:sync: b

Second B.
```
````
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_tab_dom_order(fmt, sphinx_builder):
    """The built HTML must place input, label and content as siblings in that
    order, since ``design-tabs.js`` navigates between them by DOM position:

    - ``label.previousElementSibling`` (and ``for``) must resolve to the input;
    - ``content.previousElementSibling.previousElementSibling`` must be the
      input (for hashes targeting content inside a hidden panel);
    - a ``:name:`` id must land on the label (so ``#name`` selects the tab).
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs=SD_CONF)
        builder.src_path.joinpath("index.rst").write_text(
            TAB_SET["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            TAB_SET["myst"], encoding="utf8"
        )
    builder.build()  # asserts no warnings
    html = builder.out_path.joinpath("index.html").read_text(encoding="utf8")

    # the first three component tags, in document (== sibling) order
    tags = re.findall(
        r'<input[^>]*\bid="sd-tab-item[^>]*>'
        r'|<label[^>]*\bclass="sd-tab-label[^>]*>'
        r'|<div[^>]*\bclass="sd-tab-content',
        html,
    )
    assert tags[0].startswith("<input"), tags[:3]
    assert tags[1].startswith("<label"), tags[:3]
    assert tags[2].startswith("<div"), tags[:3]

    # the label's ``for`` must reference the preceding input's id
    input_match = re.search(r'\bid="(sd-tab-item-\d+)"', tags[0])
    assert input_match
    assert f'for="{input_match.group(1)}"' in tags[1]

    # the ``:name:`` id must be carried on a label (targetable via ``#my-tab-a``)
    named_label = re.search(
        r'<label[^>]*\bclass="sd-tab-label[^>]*\bid="my-tab-a"[^>]*>', html
    )
    assert named_label, "the :name: id should be rendered on the tab label"
