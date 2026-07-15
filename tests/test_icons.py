"""Tests for the inline icon roles (octicon / material-* / fontawesome).

Regression tests for https://github.com/executablebooks/sphinx-design/issues/99:
an inline icon role starting a section title must not leak its ``<svg>`` markup
into plain-text contexts (toctree labels, the search index), while the icon is
still rendered (as inline SVG) in the HTML output.

These tests are written to also run in the ``py311-no-myst`` environment: the
core assertions use reStructuredText, and the MyST variants are guarded by
``MYST_PARAM`` (skipped when myst-parser is not installed).
"""

import json
import re

import pytest
from sphinx import version_info as sphinx_version_info

from sphinx_design.icons import get_octicon

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)

# A minimal project: a page whose section title *starts* with an octicon role,
# referenced from another page's toctree (the #99 reproduction).
ICON_TITLE_TOCTREE = {
    "rst": {
        "index.rst": "Home\n====\n\n.. toctree::\n\n   page1\n",
        "page1.rst": (
            ":octicon:`rocket` Rocket Page\n"
            "=================================\n\n"
            "Body content here.\n"
        ),
    },
    "myst": {
        "index.md": "# Home\n\n```{toctree}\npage1\n```\n",
        "page1.md": "# {octicon}`rocket` Rocket Page\n\nBody content here.\n",
    },
}


def _build(sphinx_builder, fmt, files):
    """Build a project from a ``{filename: content}`` mapping."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    else:
        builder = sphinx_builder()
    for name, content in files.items():
        builder.src_path.joinpath(name).write_text(content, encoding="utf8")
    builder.build()  # asserts no warnings
    return builder


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_icon_title_in_toctree(fmt, sphinx_builder):
    """An icon-leading title renders cleanly in a toctree entry (#99).

    The toctree label must contain the title text exactly once (not mangled or
    emptied), and the icon is preserved as an inline ``<svg>`` inside the entry.
    """
    builder = _build(sphinx_builder, fmt, ICON_TITLE_TOCTREE[fmt])
    index_html = (builder.out_path / "index.html").read_text(encoding="utf8")

    # the resolved toctree, rendered inline in the referring page's body
    wrapper = re.search(
        r'<div class="toctree-wrapper compound">.*?</div>', index_html, re.S
    )
    assert wrapper, "resolved toctree not found in index.html"
    region = wrapper.group(0)

    entries = re.findall(r'<li class="toctree-l1">.*?</li>', region, re.S)
    assert len(entries) == 1, "expected exactly one toctree entry"
    entry = entries[0]

    # the icon is preserved in the toc entry (rendered as inline SVG)
    assert "<svg" in entry
    assert "sd-octicon-rocket" in entry

    # the visible label is the clean title text, exactly once, not mangled/empty
    label = " ".join(re.sub(r"<[^>]+>", "", entry).split())
    assert label == "Rocket Page"
    assert region.count("Rocket Page") == 1

    # and the raw SVG never leaks as *text* into the label
    assert "&lt;svg" not in region


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_icon_title_search_index_clean(fmt, sphinx_builder):
    """No SVG junk leaks into the search index for an icon-leading title (#99).

    The ``titleterms`` (indexed words) are clean on all supported Sphinx
    versions — that is the actual #99 fix. The ``titles`` *display* field is
    only plain text on Sphinx >= 9: older Sphinx stores the rendered title
    HTML there (icon SVG included), which is upstream behaviour that predates
    and is unchanged by this fix.
    """
    builder = _build(sphinx_builder, fmt, ICON_TITLE_TOCTREE[fmt])
    raw = (builder.out_path / "searchindex.js").read_text(encoding="utf8")
    data = json.loads(raw[len("Search.setIndex(") : -1])

    # the search terms derived from the title are the real words only,
    # not SVG attribute names or path-data fragments (all sphinx versions)
    titleterms = set(data.get("titleterms", {}))
    assert titleterms <= {"home", "page", "rocket"}, titleterms
    for junk in ("svg", "path", "viewbox", "width", "height", "aria", "hidden"):
        assert junk not in titleterms

    if sphinx_version_info >= (9,):
        # sphinx >= 9 stores plain-text titles: no SVG markup anywhere
        assert "<svg" not in raw
        assert any(title.strip() == "Rocket Page" for title in data["titles"]), data[
            "titles"
        ]
        assert not any("svg" in title.lower() for title in data["titles"])


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_icon_body_svg_unchanged(fmt, sphinx_builder):
    """An icon in normal body text renders the exact ``get_octicon`` SVG markup.

    This locks the (byte-identical) body rendering that the previous
    ``nodes.raw`` implementation produced.
    """
    content = "A coloured icon: {octicon}`report;1em;sd-text-info`, some text."
    if fmt == "rst":
        files = {
            "index.rst": (
                "Heading\n=======\n\n"
                "A coloured icon: :octicon:`report;1em;sd-text-info`, some text.\n"
            )
        }
    else:
        files = {"index.md": f"# Heading\n\n{content}\n"}
    builder = _build(sphinx_builder, fmt, files)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")

    expected_svg = get_octicon("report", height="1em", classes=["sd-text-info"])
    assert expected_svg in html


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_article_info_icon_spacing_class(fmt, sphinx_builder):
    """Article-info octicons carry the ``sd-pr-2`` spacing class on the ``<svg>``.

    Previously the class was set on a ``nodes.raw`` wrapper and silently dropped
    by the HTML writer; it must now land on the rendered ``<svg>`` element.
    """
    if fmt == "rst":
        files = {
            "index.rst": (
                "Article\n=======\n\n"
                ".. article-info::\n"
                "   :author: Jane Doe\n"
                "   :date: Jan 1, 2026\n"
                "   :read-time: 5 min read\n"
            )
        }
    else:
        files = {
            "index.md": (
                "# Article\n\n"
                "```{article-info}\n"
                ":author: Jane Doe\n"
                ":date: Jan 1, 2026\n"
                ":read-time: 5 min read\n"
                "```\n"
            )
        }
    builder = _build(sphinx_builder, fmt, files)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")

    for name in ("calendar", "clock"):
        svg = re.search(rf"<svg[^>]*sd-octicon-{name}[^>]*>", html)
        assert svg, f"{name} octicon not rendered"
        assert "sd-pr-2" in svg.group(0), f"sd-pr-2 missing on {name} svg"
