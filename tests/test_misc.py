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
