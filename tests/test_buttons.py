"""Tests for the ``button-link`` and ``button-ref`` directives.

Covers:

* #110 - ``button-ref`` targets containing whitespace (e.g. the labels that
  ``sphinx.ext.autosectionlabel`` generates from section titles) must be
  preserved, not stripped, so that multi-word labels resolve.
* #228 - rich/nested inline content (emphasis, icons, ...) inside a
  ``button-ref`` must render identically to the same content inside a
  ``button-link``, rather than being flattened to plain text.
* An unresolved ``button-ref`` target must emit a normal missing-reference
  warning and still build (no traceback).
* #156 - a button whose RST content is a line block renders its lines as
  separate lines, rather than keeping the literal ``|`` markers.
"""

import re

from babel.messages.catalog import Catalog
from babel.messages.mofile import write_mo
from docutils import nodes
import pytest

from sphinx_design.badges_buttons import (
    _BUTTON_REF_MARKER_PREFIX,
    ButtonLinkDirective,
    ButtonRefDirective,
    _line_block_lines,
)
from sphinx_design.icons import sd_icon

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

# guard MyST variants so the ``py311-no-myst`` environment still passes
MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)


def _build(sphinx_builder, fmt, rst, myst, *, assert_pass=True):
    """Build a single-document project written in ``rst`` or ``myst``."""
    if fmt == "rst":
        builder = sphinx_builder(
            conf_kwargs={"extensions": ["sphinx_design", "sphinx.ext.autosectionlabel"]}
        )
        builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": [
                    "myst_parser",
                    "sphinx_design",
                    "sphinx.ext.autosectionlabel",
                ],
                "myst_enable_extensions": ["colon_fence"],
            }
        )
        builder.src_path.joinpath("index.md").write_text(myst, encoding="utf8")
    builder.build(assert_pass=assert_pass)
    return builder


def test_get_target_normalisation():
    """The two button directives normalise their argument differently.

    ``button-link`` strips *all* whitespace (URLs cannot contain spaces), while
    ``button-ref`` only collapses internal whitespace runs to single spaces,
    matching Sphinx's own ``XRefRole`` so multi-word labels survive (#110).
    """
    assert ButtonLinkDirective.get_target("my article section") == "myarticlesection"
    assert (
        ButtonRefDirective.get_target("my   article\n section") == "my article section"
    )
    assert ButtonRefDirective.get_target("  spaced-label  ") == "spaced-label"


MULTIWORD = {
    "rst": """
Heading
=======

My Article Section
------------------

Some content.

.. button-ref:: my article section
    :ref-type: ref

    Go to the section
""",
    "myst": """
# Heading

## My Article Section

Some content.

```{button-ref} my article section
:ref-type: ref

Go to the section
```
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_button_ref_multiword_target(fmt, sphinx_builder):
    """A ``button-ref`` to a multi-word (autosectionlabel) label resolves (#110)."""
    builder = _build(sphinx_builder, fmt, MULTIWORD["rst"], MULTIWORD["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the whitespace-containing target resolves to the section anchor
    assert 'href="#my-article-section"' in html
    assert "Go to the section" in html


NESTED = {
    "rst": """
Heading
=======

.. _target-section:

Target Section
--------------

.. button-ref:: target-section
    :ref-type: ref

    Go *emphasis* :octicon:`heart` end

.. button-link:: https://example.com

    Go *emphasis* :octicon:`heart` end
""",
    "myst": """
# Heading

(target-section)=

## Target Section

```{button-ref} target-section
:ref-type: ref

Go *emphasis* {octicon}`heart` end
```

```{button-link} https://example.com
Go *emphasis* {octicon}`heart` end
```
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_button_nested_content(fmt, sphinx_builder):
    """Nested inline markup renders the same in ``button-ref`` and
    ``button-link`` - it must not be flattened to (escaped) text (#228)."""
    builder = _build(sphinx_builder, fmt, NESTED["rst"], NESTED["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # both buttons keep the emphasis and the (real, unescaped) octicon svg
    assert html.count("<em>emphasis</em>") == 2
    assert html.count("sd-octicon-heart") == 2
    # the octicon must not leak through as escaped text (the #228 symptom)
    assert "&lt;svg" not in html

    # structurally, both resolved references carry the same rich child nodes
    doctree = builder.get_doctree("index", post_transforms=True)
    refs = [
        ref
        for ref in doctree.findall(nodes.reference)
        if "sd-btn" in ref.get("classes", [])
    ]
    assert len(refs) == 2
    for ref in refs:
        assert any(isinstance(child, nodes.emphasis) for child in ref.findall())
        # the octicon is an sd_icon inline node (since #279)
        assert any(isinstance(child, sd_icon) for child in ref.findall())

    # the transient stash/graft marker classes must never leak into output
    assert _BUTTON_REF_MARKER_PREFIX not in html
    assert _BUTTON_REF_MARKER_PREFIX not in doctree.pformat()


UNRESOLVED_RST = """
Heading
=======

.. button-ref:: nonexistent-label
    :ref-type: ref

    Broken *ref* content
"""


def test_button_ref_unresolved_warns(sphinx_builder):
    """An unresolved ``button-ref`` warns and still builds (no crash), keeping
    its (now unlinked) rich content."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(UNRESOLVED_RST, encoding="utf8")
    # a missing-reference warning is emitted, but the build completes
    builder.build(assert_pass=False)
    assert "undefined label: 'nonexistent-label'" in builder.warnings

    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the content survives (unlinked) rather than crashing the build
    assert "<em>ref</em>" in html
    assert 'href="#nonexistent-label"' not in html

    # the transient stash/graft marker classes must never leak into output,
    # even on the unresolved path (where the content node inherits the
    # pending_xref's classes)
    doctree = builder.get_doctree("index", post_transforms=True)
    assert _BUTTON_REF_MARKER_PREFIX not in html
    assert _BUTTON_REF_MARKER_PREFIX not in doctree.pformat()


PLAIN_RST = """
Heading
=======

.. _target-section:

Target Section
--------------

.. button-ref:: target-section
    :ref-type: ref

    Single word ref

.. button-link:: https://example.com

    A link button
"""


def test_button_plain_targets_unchanged(sphinx_builder):
    """Single-word ref targets and ``button-link`` URLs behave as before (#110
    must not regress the simple cases)."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(PLAIN_RST, encoding="utf8")
    builder.build()  # asserts no warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'href="#target-section"' in html
    assert "Single word ref" in html
    assert 'href="https://example.com"' in html
    assert "A link button" in html


NO_CONTENT_RST = """
Heading
=======

.. _target-section:

My Fancy Section
----------------

.. button-ref:: target-section
    :ref-type: ref
"""


def test_button_ref_without_content_shows_title(sphinx_builder):
    """A ``button-ref`` without content displays the resolved target's title
    (built by the resolver), which must not be overwritten by the
    content-preservation machinery for #228."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(NO_CONTENT_RST, encoding="utf8")
    builder.build()  # asserts no warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'href="#target-section"' in html
    # the button text is the resolved section title, not the raw target
    assert "My Fancy Section</span></a>" in html
    assert _BUTTON_REF_MARKER_PREFIX not in html


NESTED_XREF = {
    "rst": """
Heading
=======

.. _jump-target:

Target Section
--------------

Some content.

.. button-ref:: jump-target

    Jump to :ref:`jump-target` now
""",
    "myst": """
# Heading

(jump-target)=

## Target Section

Some content.

```{button-ref} jump-target

Jump to {ref}`jump-target` now
```
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_button_ref_nested_xref_no_crash(fmt, sphinx_builder):
    """A cross-reference role inside ``button-ref`` content must not crash.

    Such content is deliberately not stash/grafted (re-inserting it after
    resolution would leave an unresolved ``pending_xref`` for the writer);
    it falls back to the pre-existing std-domain text flattening.
    """
    builder = _build(sphinx_builder, fmt, NESTED_XREF["rst"], NESTED_XREF["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'href="#jump-target"' in html
    assert "Jump to" in html
    assert _BUTTON_REF_MARKER_PREFIX not in html


def test_button_ref_titlecase_ref_type(sphinx_builder):
    """A Title-Case target with ``ref-type: ref`` resolves like ``:ref:`` does.

    Sphinx's ``:ref:`` role lowercases its target (std labels are stored
    lowercased), so ``button-ref`` matches it - the visible heading text can
    be pasted verbatim as the target.
    """
    src = MULTIWORD["rst"].replace(
        ".. button-ref:: my article section",
        ".. button-ref:: My Article Section",
    )
    assert src != MULTIWORD["rst"]
    builder = _build(sphinx_builder, "rst", src, MULTIWORD["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'href="#my-article-section"' in html


_BUTTON_RE = re.compile(
    r'<a [^>]*class="[^"]*\bsd-btn\b[^"]*"[^>]*>(.*?)</a>', re.DOTALL
)


def _button_texts(html: str) -> list[str]:
    """Return the inner HTML of each button, without ``<span>`` wrappers."""
    return [
        " ".join(re.sub(r"</?span[^>]*>", "", inner).split())
        for inner in _BUTTON_RE.findall(html)
    ]


def _build_rst(sphinx_builder, rst, buildername="html", **files):
    builder = sphinx_builder(buildername, conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    for name, text in files.items():
        builder.src_path.joinpath(f"{name}.rst").write_text(text, encoding="utf8")
    builder.build()  # asserts no warnings
    return builder


LINE_BLOCK_CASES = {
    "plain": ("    | hey\n    | new line\n", "hey<br />new line"),
    # the markup of #156: the bars are indented one column past the options,
    # so docutils parses a block quote around the line block
    "indented-past-options": ("     | hey\n     | new line\n", "hey<br />new line"),
    "blank-line-between": ("    | hey\n\n    | new line\n", "hey<br />new line"),
    "continuation-line": (
        "    | hey there\n      continued\n    | new line\n",
        "hey there continued<br />new line",
    ),
    "nested": ("    | hey\n    |    indented\n", "hey<br />indented"),
    "inline-markup": (
        "    | *hey*\n    | new :octicon:`heart` line\n",
        "<em>hey</em><br />new",
    ),
    # the text is parsed once, so the autonumbered footnote reference is
    # registered once, and numbered and resolved as in a paragraph
    "footnote-reference": (
        "    | hey\n    | new line [#]_\n\n.. [#] A footnote.\n",
        "hey<br />new line <a",
    ),
}


@pytest.mark.parametrize(
    "body,expected", LINE_BLOCK_CASES.values(), ids=LINE_BLOCK_CASES.keys()
)
def test_button_link_line_block(body, expected, sphinx_builder):
    """An RST line block in a ``button-link`` renders as separate lines (#156)."""
    rst = f"Heading\n=======\n\n.. button-link:: https://example.com\n    :expand:\n\n{body}"
    builder = _build_rst(sphinx_builder, rst)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith(expected), text
    assert "|" not in text


def test_button_link_line_block_exact_html(sphinx_builder):
    """The exact HTML of a line block, which ``_button_texts`` normalises away.

    A bare bar is an empty line, so it adds a break and no empty element.
    The whitespace after a bar is kept as docutils keeps it, so a no-break or
    ideographic space can indent a line's text (the nesting is flattened).
    """
    rst = (
        "Heading\n=======\n\n"
        ".. button-link:: https://example.com\n\n"
        "    | hey\n    |\n    | new line\n\n"
        ".. button-link:: https://example.com\n\n"
        "    | \xa0hey\n    | \u3000new line\n"
    )
    builder = _build_rst(sphinx_builder, rst)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _BUTTON_RE.findall(html) == [
        "<span><span>hey</span><br /><br /><span>new line</span></span>",
        "<span><span>\xa0hey</span><br /><span>\u3000new line</span></span>",
    ]


def test_button_ref_line_block(sphinx_builder):
    """``button-ref`` shares the line-block path, including after resolution."""
    rst = """\
Heading
=======

.. button-ref:: other
    :ref-type: doc

    | hey
    | new line

.. toctree::

    other
"""
    builder = _build_rst(sphinx_builder, rst, other="Other\n=====\n")
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'href="other.html"' in html
    assert _button_texts(html) == ["hey<br />new line"]


NOT_A_LINE_BLOCK_RST = """\
Heading
=======

.. |sub| replace:: Download

.. button-link:: https://example.com

    |sub| the notes [#]_

.. [#] A footnote.
"""


def test_button_link_bar_text_is_not_a_line_block(sphinx_builder):
    """Text that starts with a substitution is parsed once, as inline text.

    ``|sub| text`` is not a docutils line block (a bar must be followed by a
    space or end the line), so it must not be block-parsed first: a second
    parse would duplicate side effects, such as the autonumbered footnote
    reference here (a spurious "Too many autonumbered footnote references").
    """
    builder = _build_rst(sphinx_builder, NOT_A_LINE_BLOCK_RST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith("Download the notes"), text


LEADING_BAR_CASES = {
    # a leading "| " is a line-block marker, as anywhere else in RST: the
    # label is a one-line line block, whose marker is consumed
    "line-block": ("    | Docs | API |\n", "Docs | API |"),
    # an escaped leading bar is not a marker, so it renders literally
    "escaped": ("    \\| Docs | API |\n", "| Docs | API |"),
}


@pytest.mark.parametrize(
    "body,expected", LEADING_BAR_CASES.values(), ids=LEADING_BAR_CASES.keys()
)
def test_button_link_leading_bar(body, expected, sphinx_builder):
    """A single-line label starting with ``| `` reads as a line block.

    Its leading ``| `` is consumed as the line-block marker, and only that one:
    later bars are text. A literal leading bar is written ``\\|``.
    """
    rst = f"Heading\n=======\n\n.. button-link:: https://example.com\n\n{body}"
    builder = _build_rst(sphinx_builder, rst)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _button_texts(html) == [expected]


LINE_BLOCK_THEN_PARAGRAPH_RST = """\
Heading
=======

.. button-link:: https://example.com

    | hey
    | new line [#]_

    trailing paragraph

.. [#] A footnote.
"""


def test_button_link_line_block_then_paragraph_parsed_once(sphinx_builder):
    """A line block followed by other text is parsed once, as inline text.

    Such text is not only line blocks, so it keeps its bars (as before #156);
    block-parsing it first, then falling back to inline text, would parse the
    footnote reference twice (a spurious "Too many autonumbered footnote
    references", and the reference left unresolved).
    """
    builder = _build_rst(sphinx_builder, LINE_BLOCK_THEN_PARAGRAPH_RST)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith("| hey | new line <a"), text
    assert "[#]" not in text, text
    assert 'class="footnote-reference' in text, text


@pytest.mark.parametrize(
    "indent", ["    ", "     "], ids=["plain", "indented-past-options"]
)
def test_button_link_line_block_with_message_parsed_once(indent, sphinx_builder):
    """A line block whose inline markup reports a message is still lines, parsed once.

    A message of a line's inline markup (here, an unknown role) does not stop
    the text being read as lines, and each line is parsed once: the message
    is reported once, at its own line, there is no spurious "Too many
    autonumbered footnote references", the footnote reference resolves, and
    the bars are not kept.
    """
    rst = (
        "Heading\n=======\n\n.. button-link:: https://example.com\n    :expand:\n\n"
        f"{indent}| hey\n{indent}| there :notarole:`x` [#]_\n\n.. [#] A footnote.\n"
    )
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    builder.build(assert_pass=False)
    assert builder.warnings.count('Unknown interpreted text role "notarole"') == 1, (
        builder.warnings
    )
    # reported at the line it is on, the second line of the line block
    assert re.search(
        r"index\.rst:8: ERROR: Unknown interpreted text role", builder.warnings
    ), builder.warnings
    assert "Too many autonumbered" not in builder.warnings, builder.warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith("hey<br />there <a"), text
    assert 'class="footnote-reference' in html
    assert "[#]" not in html


@pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed")
def test_button_link_myst_bars_unchanged(sphinx_builder):
    """Line blocks are RST syntax: MyST button text keeps its bars, parsed once.

    Block-parsing the MyST text as well would report its parse-time warnings
    (here, an unknown role) twice.
    """
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["myst_parser", "sphinx_design"],
            "myst_enable_extensions": ["colon_fence"],
        }
    )
    builder.src_path.joinpath("index.md").write_text(
        "# Heading\n\n"
        "```{button-link} https://example.com\n| hey\n| new {notarole}`line`\n```\n",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    assert builder.warnings.count('Unknown interpreted text role "notarole"') == 1, (
        builder.warnings
    )
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith("| hey | new"), text


LINE_BLOCK_RST = """\
Heading
=======

.. button-link:: https://example.com

    | hey
    | new line
"""


def test_button_link_line_block_text(sphinx_builder):
    """Builders without a line break separate the lines with a space."""
    builder = _build_rst(sphinx_builder, LINE_BLOCK_RST, "text")
    text = (builder.out_path / "index.txt").read_text(encoding="utf8")
    assert "hey new line" in text, text
    doctree = builder.get_doctree("index", post_transforms=True)
    [button] = [r for r in doctree.findall(nodes.reference) if "sd-btn" in r["classes"]]
    assert button.astext() == "hey new line"


def test_button_link_line_block_latex(sphinx_builder):
    """LaTeX output breaks the line inside the link (``\\sphinxhref``)."""
    builder = _build_rst(sphinx_builder, LINE_BLOCK_RST, "latex")
    [tex] = builder.out_path.glob("*.tex")
    assert r"\sphinxhref{https://example.com}{hey\newline{}new line}" in tex.read_text(
        encoding="utf8"
    )


def test_button_link_line_block_gettext(sphinx_builder):
    """Each line is its own message, with no line break in it.

    sphinx extracts no message from a node without a source, so each line's
    message carries the source and line of that line, on every docutils.
    """
    builder = _build_rst(sphinx_builder, LINE_BLOCK_RST, "gettext")
    pot = (builder.out_path / "index.pot").read_text(encoding="utf8")
    # each message is located at its own line, not at the first line's
    assert 'index.rst:6\nmsgid "hey"' in pot, pot
    assert 'index.rst:7\nmsgid "new line"' in pot, pot
    assert "hey new line" not in pot, pot
    assert "<br" not in pot, pot


def test_button_link_line_block_gettext_markup(sphinx_builder):
    """A line's message keeps its inline markup, for the translator to keep.

    The message is the line's source text, as a paragraph's is,
    not the text that its markup renders.
    """
    rst = LINE_BLOCK_RST.replace("| hey", "| **hey** there")
    builder = _build_rst(sphinx_builder, rst, "gettext")
    pot = (builder.out_path / "index.pot").read_text(encoding="utf8")
    assert 'index.rst:6\nmsgid "**hey** there"' in pot, pot
    assert 'msgid "hey there"' not in pot, pot


def test_button_link_line_block_translated(sphinx_builder):
    """The lines are translated one by one, and keep their order."""
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "language": "de",
            "locale_dirs": ["locales"],
        }
    )
    builder.src_path.joinpath("index.rst").write_text(LINE_BLOCK_RST, encoding="utf8")
    catalog = Catalog(locale="de", domain="index")
    catalog.add("hey", "hallo")
    catalog.add("new line", "*neue* Zeile")
    mo_dir = builder.src_path / "locales" / "de" / "LC_MESSAGES"
    mo_dir.mkdir(parents=True)
    with (mo_dir / "index.mo").open("wb") as handle:
        write_mo(handle, catalog)
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert _button_texts(html) == ["hallo<br /><em>neue</em> Zeile"]


# Bodies that look like a line block at their outermost indent, but are not
# only line-block lines. Each must be parsed once, as inline text, exactly as
# before #156 was fixed: ``(body, expected button text, expected warnings)``.
NOT_ONLY_LINE_BLOCK_CASES = {
    # docutils: a line block, then a block quote holding another line block
    "blank-then-deeper-bar": (
        "    | a [#]_\n\n        | b\n",
        "| a <a",
        [],
    ),
    # docutils: a line block, then a block quote holding a paragraph
    "blank-then-deeper-paragraph": (
        "    | a [#]_\n\n        b\n",
        "| a <a",
        [],
    ),
    # docutils: a block quote that ends without a blank line, then a line block
    "first-line-deeper": (
        "      | a [#]_\n    | b\n",
        "| a <a",
        [],
    ),
    # a second parse would register the target twice (a "Duplicate explicit
    # target name" warning, and the target's id renamed)
    "blank-then-deeper-paragraph-target": (
        "    | _`tgt` a [#]_\n\n        b\n",
        "| tgt a <a",
        [],
    ),
    # docutils: a line block, then a block quote holding a directive
    "blank-then-deeper-directive": (
        "    | a [#]_\n\n        .. note:: x\n",
        "| a <a",
        [],
    ),
    # a block parse would define ``zz`` in the document; as inline text,
    # ``|zz|`` is a reference to an undefined substitution, as before
    "blank-then-deeper-substitution-definition": (
        "    | a [#]_\n\n        .. |zz| replace:: Z\n",
        "| a <a",
        ['Undefined substitution referenced: "zz"'],
    ),
}


@pytest.mark.parametrize(
    "body,expected,warnings",
    NOT_ONLY_LINE_BLOCK_CASES.values(),
    ids=NOT_ONLY_LINE_BLOCK_CASES.keys(),
)
def test_button_link_not_only_line_block_parsed_once(
    body, expected, warnings, sphinx_builder
):
    """Text that is not only line-block lines is parsed once, as inline text.

    The line-block check is textual and the text is never block-parsed, so a
    body that docutils would parse as a line block plus something else keeps
    its bars, and shows none of the side effects of a second parse: a spurious
    "Too many autonumbered footnote references" (and the reference left
    unresolved), a duplicate explicit target, a "Block quote ends without a
    blank line" warning, or a substitution definition leaking into the page.
    """
    rst = (
        "Heading\n=======\n\n.. button-link:: https://example.com\n\n"
        f"{body}\nAfter.\n\n.. [#] A footnote.\n"
    )
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    builder.build(assert_pass=False)
    reported = [line for line in builder.warnings.splitlines() if line.strip()]
    assert len(reported) == len(warnings), builder.warnings
    for line, warning in zip(reported, warnings, strict=True):
        assert warning in line, builder.warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    [text] = _button_texts(html)
    assert text.startswith(expected), text
    assert "[#]" not in html
    assert "<br" not in text, text
    if "_`tgt`" in body:
        assert '<span class="target" id="tgt">' in html


SPLIT_CASES = {
    "plain": (["| a", "| b"], [(0, "a"), (1, "b")]),
    "indented": ([" | a", " | b"], [(0, "a"), (1, "b")]),
    "blank-between": (["| a", "", "| b"], [(0, "a"), (2, "b")]),
    "bare-bar": (["| a", "|", "| b"], [(0, "a"), (1, ""), (2, "b")]),
    "continuation": (["| a", "  more", "| b"], [(0, "a\nmore"), (2, "b")]),
    # docutils strips only the common indent of the continuation lines
    "continuation-relative-indent": (["| a", "    b", "  c"], [(0, "a\n  b\nc")]),
    # docutils drops the empty first line of a bare bar with a continuation
    "bare-bar-continuation": (["|", "  x"], [(0, "x")]),
    "nested": (["| a", "|    b"], [(0, "a"), (1, "b")]),
    # docutils keeps the text after the bar as is, other whitespace included
    "nbsp-after-bar": (["| \xa0a"], [(0, "\xa0a")]),
    "ideographic-space-after-bar": (["| \u3000a"], [(0, "\u3000a")]),
    # only spaces indent a line: a no-break space before a bar is text
    "nbsp-indent": (["| a", "\xa0| b"], None),
    "nbsp-first-line": (["\xa0| a"], None),
    "empty": ([], None),
    "substitution-first": (["|sub| a"], None),
    # a line at the bar's indent with no bar is not a continuation, even
    # directly after a bar (docutils: "Line block ends without a blank line")
    "paragraph-directly-after": (["| a", "b"], None),
    "paragraph-after": (["| a", "", "b"], None),
    "deeper-after-blank": (["| a", "", "  | b"], None),
    "first-line-deeper": (["  | a", "| b"], None),
    "deeper-first-line-only": (["  | a"], [(0, "a")]),
}


@pytest.mark.parametrize(
    "content,expected", SPLIT_CASES.values(), ids=SPLIT_CASES.keys()
)
def test_line_block_lines(content, expected):
    """The text is split into line-block lines, or rejected, without parsing it.

    A deeper line continues the previous line only directly after it, as in
    docutils; after a blank line it starts a block quote, which is not a line.
    """
    assert _line_block_lines(content) == expected


INLINE_LINES_RST = """\
Heading
=======

.. button-link:: https://example.com

    top one
    top :notarole:`x`

.. dropdown:: Drop

    para

    .. button-link:: https://example.com

        in one
        in :notarole:`y`

.. include:: inc.txt
"""

INLINE_LINES_INC = """\
.. button-link:: https://example.com

    inc one
    inc :notarole:`z`
"""


def test_button_link_inline_text_lines(sphinx_builder):
    """Button text is located at its first content line, in its own file.

    ``content_offset`` is the offset of the content in the whole input, so
    adding it to the directive's line counted the lines before the directive
    twice: messages and gettext locations named a later line, past the end of
    the file inside a nested directive, and the included file's line plus the
    offset into the including one. As for a paragraph, docutils reports the
    messages of the inline markup at the text's first line.
    """
    builder = sphinx_builder("gettext", conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(INLINE_LINES_RST, encoding="utf8")
    builder.src_path.joinpath("inc.txt").write_text(INLINE_LINES_INC, encoding="utf8")
    builder.build(assert_pass=False)
    reported = re.findall(
        r"(\w+\.(?:rst|txt)):(\d+): ERROR: Unknown interpreted text role",
        builder.warnings,
    )
    assert reported == [("index.rst", "6"), ("index.rst", "15"), ("inc.txt", "3")], (
        builder.warnings
    )
    pot = (builder.out_path / "index.pot").read_text(encoding="utf8")
    for location, msgid in [
        ("index.rst:6", "top one top :notarole:`x`"),
        ("index.rst:15", "in one in :notarole:`y`"),
        ("inc.txt:3", "inc one inc :notarole:`z`"),
    ]:
        assert f'{location}\nmsgid "{msgid}"' in pot, pot


LINE_BLOCK_LINES_INC = """\
Included
--------

.. button-link:: https://example.com

    | inc one
    | inc :notarole:`z`
"""


def test_button_link_line_block_lines(sphinx_builder):
    """Each line of a line block is located at its own line, in its own file.

    A message of a line's inline markup is reported at that line, and the
    line's gettext message is located there, also in an included file.
    """
    builder = sphinx_builder("gettext", conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        "Heading\n=======\n\n.. include:: inc.txt\n", encoding="utf8"
    )
    builder.src_path.joinpath("inc.txt").write_text(
        LINE_BLOCK_LINES_INC, encoding="utf8"
    )
    builder.build(assert_pass=False)
    reported = re.findall(
        r"(\w+\.(?:rst|txt)):(\d+): ERROR: Unknown interpreted text role",
        builder.warnings,
    )
    assert reported == [("inc.txt", "7")], builder.warnings
    pot = (builder.out_path / "index.pot").read_text(encoding="utf8")
    assert 'inc.txt:6\nmsgid "inc one"' in pot, pot
    assert 'inc.txt:7\nmsgid "inc :notarole:`z`"' in pot, pot
