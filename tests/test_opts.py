"""Test extension configuration options."""
from pathlib import Path
from typing import Callable

from .conftest import SphinxBuilder


def test_tabs_opts_default_values(sphinx_builder: Callable[..., SphinxBuilder]):
    """Test the sphinx_design_sync_tabs_xxx options default values."""
    builder = sphinx_builder()
    assert "sphinx_design_sync_tabs_storage_key" in builder.app.env.config
    assert "sphinx_design_sync_tabs_url_param" in builder.app.env.config
    assert (
        builder.app.env.config.sphinx_design_sync_tabs_storage_key
        == "sphinx-design-last-tab"
    )
    assert builder.app.env.config.sphinx_design_sync_tabs_url_param is None
    content = "Heading\n-------\n\ncontent"
    builder.src_path.joinpath("index.rst").write_text(content, encoding="utf8")
    builder.build()
    design_tabs_js = Path(builder.out_path) / "_static" / "design-tabs.js"
    with design_tabs_js.open() as f:
        lines = f.read()
        assert "sphinx-design-last-tab" in lines


def test_tabs_storage_key_set(sphinx_builder: Callable[..., SphinxBuilder]):
    """Test the sphinx_design_sync_tabs_storage_key option."""
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["myst_parser", "sphinx_design"],
            "myst_enable_extensions": ["colon_fence"],
            "sphinx_design_sync_tabs_storage_key": "spam-42",
            "sphinx_design_sync_tabs_url_param": "bag_of_ham",
        }
    )
    assert "sphinx_design_sync_tabs_storage_key" in builder.app.env.config
    assert builder.app.env.config.sphinx_design_sync_tabs_storage_key == "spam-42"
    content = "Heading\n-------\n\ncontent"
    builder.src_path.joinpath("index.rst").write_text(content, encoding="utf8")
    builder.build()
    design_tabs_js = Path(builder.out_path) / "_static" / "design-tabs.js"
    with design_tabs_js.open() as f:
        lines = f.read()
        assert "spam-42" in lines
        assert "bag_of_ham" in lines
        assert "sphinx-design-last-tab" not in lines
