import pytest

from sphinx_design.icons import get_material_icon_data, get_octicon_data


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


def test_tab_set_with_invalid_children(sphinx_builder, file_regression, normalize_doctree_xml):
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
        extension=".xml",
        encoding="utf8",
    )
