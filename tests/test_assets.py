"""Tests for how the extension registers and emits its static assets (CSS/JS).

These tests are intentionally written with plain reStructuredText and only the
``sphinx_design`` extension enabled, so that they also run in the
``py311-no-myst`` environment.
"""

from pathlib import Path

# Keep the config myst-free so these tests run without myst-parser installed.
SD_CONF = {"extensions": ["sphinx_design"]}

INDEX_RST = """
Test Document
=============

Some content.
"""


def _write_index(src_path: Path) -> None:
    src_path.joinpath("index.rst").write_text(INDEX_RST, encoding="utf8")


def test_latex_no_static_dir(sphinx_builder):
    """A latex build must not gain a spurious ``_sphinx_design_static`` directory.

    Regression test for #200 (non-HTML builders getting the static dir) and
    #235 (``mkdir`` crashing when the outdir does not yet exist).
    """
    builder = sphinx_builder(buildername="latex", conf_kwargs=SD_CONF)
    _write_index(builder.src_path)
    builder.build()
    out_path = builder.out_path
    # the old hand-rolled copying wrote this directory for *every* builder
    assert list(out_path.rglob("_sphinx_design_static")) == []
    # and the CSS should never leak into a non-HTML build
    assert list(out_path.rglob("sphinx-design.min.css")) == []


def test_html_static_assets(sphinx_builder):
    """An HTML build copies the assets into ``_static`` and links them with a checksum."""
    builder = sphinx_builder(buildername="html", conf_kwargs=SD_CONF)
    _write_index(builder.src_path)
    builder.build()
    out_path = builder.out_path
    assert out_path.joinpath("_static", "sphinx-design.min.css").exists()
    assert out_path.joinpath("_static", "design-tabs.js").exists()
    index_html = out_path.joinpath("index.html").read_text(encoding="utf8")
    # Sphinx >=7.1 appends a native ``?v=<checksum>`` cache-busting suffix
    assert "sphinx-design.min.css?v=" in index_html
    assert "design-tabs.js?v=" in index_html


def test_epub_static_assets(sphinx_builder):
    """An epub build still receives the assets (preserving pre-existing behaviour).

    ``Epub3Builder.format == "html"``, so it keeps getting the assets exactly as
    before. A minimal epub project emits unrelated EPUB3 metadata warnings (empty
    ``epub_copyright`` / ``version``), so we do not assert a warning-free build;
    we only check that output was produced and the assets are present.
    """
    builder = sphinx_builder(buildername="epub", conf_kwargs=SD_CONF)
    _write_index(builder.src_path)
    builder.build(assert_pass=False)
    out_path = builder.out_path
    # the build produced epub output
    assert list(out_path.rglob("*.epub"))
    # and the assets were copied into the epub tree
    assert list(out_path.rglob("sphinx-design.min.css"))
    assert list(out_path.rglob("design-tabs.js"))
