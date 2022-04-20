"""Test the documented snippets run correctly, and are the same for both RST and MyST."""
from pathlib import Path
from typing import Callable

import pytest

from .conftest import SphinxBuilder

SNIPPETS_PATH = Path(__file__).parent.parent / "docs" / "snippets"
SNIPPETS_GLOB_RST = list((SNIPPETS_PATH / "rst").glob("[!_]*"))
SNIPPETS_GLOB_MYST = list((SNIPPETS_PATH / "myst").glob("[!_]*"))


def write_assets(src_path: Path):
    """Write additional assets to the src directory."""
    src_path.joinpath("snippet.py").write_text("a = 1")
    src_path.joinpath("images").mkdir()
    src_path.joinpath("images", "ebp-logo.png").touch()
    src_path.joinpath("images", "particle_background.jpg").touch()


@pytest.mark.parametrize(
    "path",
    SNIPPETS_GLOB_RST,
    ids=[path.name[: -len(path.suffix)] for path in SNIPPETS_GLOB_RST],
)
def test_snippets_rst(
    sphinx_builder: Callable[..., SphinxBuilder], path: Path, file_regression
):
    """Test snippets written in RestructuredText (before post-transforms)."""
    builder = sphinx_builder()
    content = "Heading\n-------" + "\n\n" + path.read_text(encoding="utf8")
    builder.src_path.joinpath("index.rst").write_text(content, encoding="utf8")
    write_assets(builder.src_path)
    builder.build()
    pformat = builder.get_doctree("index").pformat()
    file_regression.check(
        pformat,
        basename=f"snippet_pre_{path.name[:-len(path.suffix)]}",
        extension=".xml",
        encoding="utf8",
    )


@pytest.mark.parametrize(
    "path",
    SNIPPETS_GLOB_MYST,
    ids=[path.name[: -len(path.suffix)] for path in SNIPPETS_GLOB_MYST],
)
def test_snippets_myst(
    sphinx_builder: Callable[..., SphinxBuilder], path: Path, file_regression
):
    """Test snippets written in MyST Markdown (before post-transforms)."""
    builder = sphinx_builder()
    content = "# Heading" + "\n\n\n" + path.read_text(encoding="utf8")
    builder.src_path.joinpath("index.md").write_text(content, encoding="utf8")
    write_assets(builder.src_path)
    builder.build()
    file_regression.check(
        builder.get_doctree("index").pformat(),
        basename=f"snippet_pre_{path.name[:-len(path.suffix)]}",
        extension=".xml",
        encoding="utf8",
    )


@pytest.mark.parametrize(
    "path",
    SNIPPETS_GLOB_RST,
    ids=[path.name[: -len(path.suffix)] for path in SNIPPETS_GLOB_RST],
)
def test_snippets_rst_post(
    sphinx_builder: Callable[..., SphinxBuilder], path: Path, file_regression
):
    """Test snippets written in RestructuredText (after HTML post-transforms)."""
    builder = sphinx_builder()
    content = "Heading\n-------" + "\n\n" + path.read_text(encoding="utf8")
    builder.src_path.joinpath("index.rst").write_text(content, encoding="utf8")
    write_assets(builder.src_path)
    builder.build()
    pformat = builder.get_doctree("index", post_transforms=True).pformat()
    file_regression.check(
        pformat,
        basename=f"snippet_post_{path.name[:-len(path.suffix)]}",
        extension=".xml",
        encoding="utf8",
    )


@pytest.mark.parametrize(
    "path",
    SNIPPETS_GLOB_MYST,
    ids=[path.name[: -len(path.suffix)] for path in SNIPPETS_GLOB_MYST],
)
def test_snippets_myst_post(
    sphinx_builder: Callable[..., SphinxBuilder], path: Path, file_regression
):
    """Test snippets written in MyST Markdown (after HTML post-transforms)."""
    builder = sphinx_builder()
    content = "# Heading" + "\n\n\n" + path.read_text(encoding="utf8")
    builder.src_path.joinpath("index.md").write_text(content, encoding="utf8")
    write_assets(builder.src_path)
    builder.build()
    file_regression.check(
        builder.get_doctree("index", post_transforms=True).pformat(),
        basename=f"snippet_post_{path.name[:-len(path.suffix)]}",
        extension=".xml",
        encoding="utf8",
    )


def test_sd_hide_title_rst(
    sphinx_builder: Callable[..., SphinxBuilder], file_regression
):
    """Test that the root title is hidden."""
    builder = sphinx_builder()
    content = ":sd_hide_title:\n\nHeading\n-------\n\ncontent"
    builder.src_path.joinpath("index.rst").write_text(content, encoding="utf8")
    builder.build()
    file_regression.check(
        builder.get_doctree("index", post_transforms=False).pformat(),
        basename="sd_hide_title",
        extension=".xml",
        encoding="utf8",
    )


def test_sd_hide_title_myst(
    sphinx_builder: Callable[..., SphinxBuilder], file_regression
):
    """Test that the root title is hidden."""
    builder = sphinx_builder()
    content = "---\nsd_hide_title: true\n---\n\n# Heading\n\ncontent"
    builder.src_path.joinpath("index.md").write_text(content, encoding="utf8")
    builder.build()
    file_regression.check(
        builder.get_doctree("index", post_transforms=False).pformat(),
        basename="sd_hide_title",
        extension=".xml",
        encoding="utf8",
    )
