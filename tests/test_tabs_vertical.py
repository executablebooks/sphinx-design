"""Tests for the ``:orientation:`` option of ``tab-set`` and ``tab-set-code``.

The vertical layout is CSS only: the directives add one modifier class,
``sd-tab-set-vertical``, and the compiled stylesheet does the rest.
These tests pin both halves:

* the class is emitted for ``vertical`` on both directives, is absent for
  ``horizontal`` or no option, and an unknown value is reported;
* the stylesheet applies the vertical rules only from the ``md`` breakpoint up,
  and uses no physical left/right properties, which would break right-to-left
  pages.

The ``tab-set`` + ``vertical`` doctree is also covered by the
``tab-vertical`` snippet fixtures in ``test_snippets.py``.
"""

from pathlib import Path
import re

import pytest

from sphinx_design.shared import is_component

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)

COMPILED_CSS = (
    Path(__file__).parent.parent / "sphinx_design" / "static" / "sphinx-design.min.css"
)


def _source(fmt: str, directive: str, option: str | None) -> str:
    """A page holding one tab set of ``directive``, with ``option`` if given."""
    if fmt == "rst":
        opts = f"   :orientation: {option}\n" if option is not None else ""
        if directive == "tab-set":
            body = (
                "   .. tab-item:: A\n\n      A content\n\n"
                "   .. tab-item:: B\n\n      B content\n"
            )
        else:
            body = (
                "   .. code-block:: python\n\n      a = 1\n\n"
                "   .. code-block:: javascript\n\n      a = 1;\n"
            )
        return f"Heading\n=======\n\n.. {directive}::\n{opts}\n{body}"
    opts = f":orientation: {option}\n" if option is not None else ""
    if directive == "tab-set":
        body = ":::{tab-item} A\nA content\n:::\n:::{tab-item} B\nB content\n:::\n"
    else:
        body = "```python\na = 1\n```\n```javascript\na = 1;\n```\n"
    return f"# Heading\n\n::::{{{directive}}}\n{opts}{body}::::\n"


def _build(fmt, directive, option, sphinx_builder, assert_pass=True):
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        name = "index.rst"
    else:
        builder = sphinx_builder()
        name = "index.md"
    builder.src_path.joinpath(name).write_text(
        _source(fmt, directive, option), encoding="utf8"
    )
    builder.build(assert_pass=assert_pass)
    return builder


def _tab_set_classes(builder) -> list[list[str]]:
    doctree = builder.get_doctree("index", post_transforms=True)
    return [
        list(node["classes"])
        for node in doctree.findall(lambda n: is_component(n, "tab-set"))
    ]


@pytest.mark.parametrize("directive", ["tab-set", "tab-set-code"])
@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_vertical_adds_modifier_class(fmt, directive, sphinx_builder):
    """``:orientation: vertical`` adds the class right after ``sd-tab-set``."""
    builder = _build(fmt, directive, "vertical", sphinx_builder)
    assert _tab_set_classes(builder) == [["sd-tab-set", "sd-tab-set-vertical"]]
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert "sd-tab-set-vertical" in html


@pytest.mark.parametrize("option", ["horizontal", None])
@pytest.mark.parametrize("directive", ["tab-set", "tab-set-code"])
@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_horizontal_adds_nothing(fmt, directive, option, sphinx_builder):
    """``horizontal`` (the default) leaves the classes exactly as they were."""
    builder = _build(fmt, directive, option, sphinx_builder)
    assert _tab_set_classes(builder) == [["sd-tab-set"]]


@pytest.mark.parametrize("directive", ["tab-set", "tab-set-code"])
def test_vertical_keeps_user_classes_last(directive, sphinx_builder):
    """User classes follow the orientation class, so they can override it."""
    class_opt = "class" if directive == "tab-set" else "class-set"
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        _source("rst", directive, "vertical").replace(
            "   :orientation: vertical\n",
            f"   :orientation: vertical\n   :{class_opt}: my-class\n",
        ),
        encoding="utf8",
    )
    builder.build()
    assert _tab_set_classes(builder) == [
        ["sd-tab-set", "sd-tab-set-vertical", "my-class"]
    ]


@pytest.mark.parametrize(
    ("fmt", "expected"),
    [
        # docutils drops the whole directive and reports an error
        ("rst", []),
        # MyST warns (``myst.directive_option``) and drops only the bad option
        pytest.param("myst", [["sd-tab-set"]], marks=MYST_PARAM.marks),
    ],
)
@pytest.mark.parametrize("directive", ["tab-set", "tab-set-code"])
def test_invalid_orientation_is_reported(fmt, expected, directive, sphinx_builder):
    """An unknown value is reported, naming the allowed values, never rendered."""
    builder = _build(fmt, directive, "diagonal", sphinx_builder, assert_pass=False)
    warnings = builder.warnings
    assert '"diagonal" unknown; choose from "horizontal", or "vertical"' in warnings
    assert _tab_set_classes(builder) == expected


def _media_blocks(css: str) -> list[tuple[str, str]]:
    """Return ``(prelude, body)`` for each top-level ``@media`` block."""
    blocks = []
    for match in re.finditer(r"@media([^{]*)\{", css):
        depth, pos = 1, match.end()
        while depth:
            depth += {"{": 1, "}": -1}.get(css[pos], 0)
            pos += 1
        blocks.append((match.group(1).strip(), css[match.end() : pos - 1]))
    return blocks


def test_vertical_css_is_mobile_first():
    """The vertical rules live only in the ``md`` (768px) min-width query.

    Below the breakpoint a vertical set must render exactly like a horizontal
    one, which holds when no vertical rule applies there at all.
    """
    css = COMPILED_CSS.read_text(encoding="utf8")
    blocks = [
        (prelude, body)
        for prelude, body in _media_blocks(css)
        if "sd-tab-set-vertical" in body
    ]
    assert [prelude for prelude, _ in blocks] == ["(min-width:768px)"]
    inside = blocks[0][1].count("sd-tab-set-vertical")
    assert css.count("sd-tab-set-vertical") == inside


def test_vertical_css_is_direction_agnostic():
    """The vertical rules use logical properties, so right-to-left pages mirror.

    A physical ``left``/``right`` property (or an x-offset box-shadow) would
    put the rail's border and the pane's rule on the wrong side under
    ``dir="rtl"``.
    """
    css = COMPILED_CSS.read_text(encoding="utf8")
    rules = re.findall(r"[^{}]*sd-tab-set-vertical[^{}]*\{([^}]*)\}", css)
    assert rules
    for declarations in rules:
        assert not re.search(r"-(left|right)\s*:", declarations), declarations
        assert not re.search(r":\s*(left|right)\b", declarations), declarations
        assert not re.search(r"box-shadow:\s*-?[.\d]", declarations), declarations
