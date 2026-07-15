"""Unit tests for the public :mod:`sphinx_design.testing` module.

These feed literal strings and toggle the internal docutils-version flag, so
they exercise both code paths regardless of the installed docutils version.
"""

import pytest

from sphinx_design import testing
from sphinx_design.testing import normalize_doctree_xml


@pytest.fixture
def force_0_22(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the >= 0.22 (normalize) code path."""
    monkeypatch.setattr(testing, "_DOCUTILS_0_22_PLUS", True)


@pytest.fixture
def force_pre_0_22(monkeypatch: pytest.MonkeyPatch) -> None:
    """Force the < 0.22 (no-op) code path."""
    monkeypatch.setattr(testing, "_DOCUTILS_0_22_PLUS", False)


def test_normalize_pre_0_22_is_noop(force_pre_0_22: None) -> None:
    """On docutils < 0.22 the text is returned unchanged."""
    text = '<container is_div="1" selected="0">'
    assert normalize_doctree_xml(text) == text


def test_normalize_booleans(force_0_22: None) -> None:
    """On docutils >= 0.22, known boolean attributes are normalized."""
    text = '<container is_div="1" selected="0" opened="1">'
    expected = '<container is_div="True" selected="False" opened="True">'
    assert normalize_doctree_xml(text) == expected


def test_extra_attributes_respected(force_0_22: None) -> None:
    """Custom boolean attributes are normalized only when passed explicitly."""
    text = '<custom_node my_flag="1" other_flag="0">'
    # unknown attributes are not normalized by default
    assert normalize_doctree_xml(text) == text
    # ... but are when declared via ``extra_attributes``
    assert (
        normalize_doctree_xml(text, extra_attributes=["my_flag", "other_flag"])
        == '<custom_node my_flag="True" other_flag="False">'
    )


def test_non_boolean_values_untouched(force_0_22: None) -> None:
    """Non-boolean "1"/"0" values are left alone."""
    # unknown attribute with a "1" value
    assert normalize_doctree_xml('<image scale="1">') == '<image scale="1">'
    # text content that happens to be "1"
    assert (
        normalize_doctree_xml("<paragraph>1</paragraph>") == "<paragraph>1</paragraph>"
    )


def test_bool_attributes_constant() -> None:
    """The module exposes the boolean-attribute list as a tuple constant."""
    assert isinstance(testing._BOOL_ATTRIBUTES, tuple)
    assert "is_div" in testing._BOOL_ATTRIBUTES
