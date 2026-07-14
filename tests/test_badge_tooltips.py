"""Tests for ``title``-attribute tooltips on the badge roles (#81).

Every ``bdg-*`` role family accepts a trailing ``; tooltip`` suffix (see
:func:`sphinx_design.badges_buttons.split_tooltip`), rendered as a native HTML
``title`` attribute:

* plain badges (``bdg-*``) via a new ``sd_badge`` node,
* external-link badges (``bdg-link-*``) via ``reference`` ``reftitle``,
* cross-reference badges (``bdg-ref-*``) via a ``reftitle`` grafted onto the
  *resolved* reference (the pre-resolution attribute would not survive).

Since ``;`` is a legal character in URLs and reference targets, the link/ref
families only accept the suffix after a complete explicit ``title <target>``
form (the ``;`` must follow the closing ``>``); a bare target is never split,
so pre-existing targets containing ``;`` render exactly as before.

The suffix must not change output when absent, must be HTML-escaped, and must
never leak its transient carry mechanism (marker classes / ``sd_tooltip``
attribute) into the HTML or the post-transform doctree.

Written to also run under ``py311-no-myst``: core assertions use
reStructuredText, and the MyST variants are guarded by ``MYST_PARAM``.
"""

from docutils import nodes
import pytest
from sphinx import addnodes

from sphinx_design.badges_buttons import (
    _BADGE_REF_TOOLTIP_MARKER_PREFIX,
    sd_badge,
    split_tooltip,
)

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
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": ["myst_parser", "sphinx_design"],
                "myst_enable_extensions": ["colon_fence"],
            }
        )
        builder.src_path.joinpath("index.md").write_text(myst, encoding="utf8")
    builder.build(assert_pass=assert_pass)
    return builder


# ---------------------------------------------------------------------------
# split_tooltip unit tests (parser-portable string grammar)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        # no ; -> no tooltip, text unchanged
        ("plain badge", ("plain badge", None)),
        ("", ("", None)),
        # simple split, both parts stripped
        ("stable ; A released version", ("stable", "A released version")),
        ("  a  ;  b  ", ("a", "b")),
        # split on the LAST unescaped ;
        ("a ; b ; c", ("a ; b", "c")),
        # \; escapes a literal ; (resolved in the output)
        (r"a\;b", ("a;b", None)),
        (r"a\;b ; tip", ("a;b", "tip")),
        (r"main ; tip\;with semi", ("main", "tip;with semi")),
        (r"a\;b\;c", ("a;b;c", None)),
        # a trailing (empty) tooltip is ignored: no tooltip, ; kept in text
        ("trailing ;", ("trailing ;", None)),
        ("trailing ; ", ("trailing ;", None)),
    ],
)
def test_split_tooltip(text, expected):
    """``split_tooltip`` implements the documented ``; tooltip`` grammar."""
    assert split_tooltip(text) == expected


# ---------------------------------------------------------------------------
# plain badges (BadgeRole -> sd_badge)
# ---------------------------------------------------------------------------

PLAIN = {
    "rst": """
Heading
=======

Here is a :bdg-primary:`stable ; A released version` badge.

And a plain :bdg:`no tooltip` badge.
""",
    "myst": """
# Heading

Here is a {bdg-primary}`stable ; A released version` badge.

And a plain {bdg}`no tooltip` badge.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_plain_badge_tooltip(fmt, sphinx_builder):
    """A plain badge renders its tooltip as a ``title`` on the ``<span>``."""
    builder = _build(sphinx_builder, fmt, PLAIN["rst"], PLAIN["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the tooltipped badge: title set, suffix stripped from the visible text
    assert (
        '<span class="sd-sphinx-override sd-badge sd-bg-primary sd-bg-text-primary"'
        ' title="A released version">stable</span>' in html
    )
    # the plain badge is unchanged: a bare span, no title
    assert '<span class="sd-sphinx-override sd-badge">no tooltip</span>' in html

    # the doctree uses the sd_badge node, carrying the tooltip only when set
    doctree = builder.get_doctree("index")
    badges = list(doctree.findall(sd_badge))
    assert len(badges) == 2
    assert badges[0]["tooltip"] == "A released version"
    assert "tooltip" not in badges[1]


ESCAPE = {
    "rst": r"""
Heading
=======

Danger :bdg-danger:`x ; a <b> & "q"` here.
""",
    "myst": r"""
# Heading

Danger {bdg-danger}`x ; a <b> & "q"` here.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_plain_badge_tooltip_escaped(fmt, sphinx_builder):
    """Special characters in a badge tooltip are HTML-escaped in ``title``."""
    builder = _build(sphinx_builder, fmt, ESCAPE["rst"], ESCAPE["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'title="a &lt;b&gt; &amp; &quot;q&quot;"' in html
    # the raw (unescaped) characters never appear inside the attribute
    assert 'title="a <b>' not in html


ESCAPED_SEMICOLON = {
    "rst": r"""
Heading
=======

E1 :bdg:`step 1\; step 2` here.

E2 :bdg-secondary:`a\;b ; tip` there.
""",
    "myst": r"""
# Heading

E1 {bdg}`step 1\; step 2` here.

E2 {bdg-secondary}`a\;b ; tip` there.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_plain_badge_escaped_semicolon_label(fmt, sphinx_builder):
    r"""``\;`` renders as a literal ``;`` in the badge text, in both parsers.

    reStructuredText NUL-encodes backslash escapes while MyST forwards them
    verbatim; both must end up as a plain ``;`` (no backslash) in the output,
    and an escaped ``;`` must never act as a tooltip separator.
    """
    builder = _build(
        sphinx_builder, fmt, ESCAPED_SEMICOLON["rst"], ESCAPED_SEMICOLON["myst"]
    )
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the escaped ; is literal text (not a separator) and loses its backslash
    assert '<span class="sd-sphinx-override sd-badge">step 1; step 2</span>' in html
    assert "step 1\\; step 2" not in html
    # an escaped ; in the label coexists with a real tooltip suffix
    assert (
        '<span class="sd-sphinx-override sd-badge sd-bg-secondary sd-bg-text-secondary"'
        ' title="tip">a;b</span>' in html
    )


# ---------------------------------------------------------------------------
# external-link badges (LinkBadgeRole -> reference reftitle)
# ---------------------------------------------------------------------------

LINK = {
    "rst": """
Heading
=======

Docs :bdg-link-info:`docs <https://example.com> ; Opens the documentation`.

Plain :bdg-link-primary:`https://example.com`.
""",
    "myst": """
# Heading

Docs {bdg-link-info}`docs <https://example.com> ; Opens the documentation`.

Plain {bdg-link-primary}`https://example.com`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_link_badge_tooltip(fmt, sphinx_builder):
    """An external-link badge renders its tooltip as ``title`` on the ``<a>``."""
    builder = _build(sphinx_builder, fmt, LINK["rst"], LINK["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the explicit title, the target and the tooltip are all handled
    assert 'href="https://example.com"' in html
    assert 'title="Opens the documentation"' in html
    assert ">docs</span></a>" in html
    # the no-tooltip link badge gains no title attribute
    doctree = builder.get_doctree("index")
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 2
    assert refs[0]["reftitle"] == "Opens the documentation"
    assert "reftitle" not in refs[1]


LINK_SEMI = {
    "rst": """
Heading
=======

L1 :bdg-link-primary:`https://example.com/a;b` bare.

L2 :bdg-link-info:`docs <https://example.com/a;b>` explicit.

L3 :bdg-link-success:`docs <https://example.com/a;b> ; Opens the docs` tooltip.

L4 :bdg-link-warning:`https://example.com ; tip` bare-suffix.
""",
    "myst": """
# Heading

L1 {bdg-link-primary}`https://example.com/a;b` bare.

L2 {bdg-link-info}`docs <https://example.com/a;b>` explicit.

L3 {bdg-link-success}`docs <https://example.com/a;b> ; Opens the docs` tooltip.

L4 {bdg-link-warning}`https://example.com ; tip` bare-suffix.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_link_badge_semicolon_in_target(fmt, sphinx_builder):
    """``;`` is legal in URLs: a link badge target is never corrupted by the
    tooltip grammar.

    Only a ``;`` *after* the closing ``>`` of the explicit ``text <target>``
    form starts a tooltip; bare targets (with or without a would-be suffix)
    pass through byte-identically to the pre-tooltip behaviour.
    """
    builder = _build(sphinx_builder, fmt, LINK_SEMI["rst"], LINK_SEMI["myst"])
    doctree = builder.get_doctree("index")
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 4
    # L1: bare URL containing ';' - never split, no tooltip
    assert refs[0]["refuri"] == "https://example.com/a;b"
    assert "reftitle" not in refs[0]
    assert refs[0].astext() == "https://example.com/a;b"
    # L2: explicit form, ';' inside <target> - never split
    assert refs[1]["refuri"] == "https://example.com/a;b"
    assert "reftitle" not in refs[1]
    assert refs[1].astext() == "docs"
    # L3: explicit form, ';' after '>' - tooltip split, target intact
    assert refs[2]["refuri"] == "https://example.com/a;b"
    assert refs[2]["reftitle"] == "Opens the docs"
    assert refs[2].astext() == "docs"
    # L4: bare form with a would-be suffix - no explicit target, no split
    # (the whole text is the target, exactly as before this feature)
    assert refs[3]["refuri"] == "https://example.com ; tip"
    assert "reftitle" not in refs[3]

    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count('href="https://example.com/a;b"') == 3


# ---------------------------------------------------------------------------
# cross-reference badges (XRefBadgeRole -> reftitle grafted post-resolution)
# ---------------------------------------------------------------------------

REF = {
    "rst": """
Heading
=======

.. _my-target:

My Target Section
-----------------

See :bdg-ref-primary:`Target <my-target> ; Jump to the target` for details.

Also :bdg-ref-primary:`my-target` without a tooltip.
""",
    "myst": """
# Heading

(my-target)=

## My Target Section

See {bdg-ref-primary}`Target <my-target> ; Jump to the target` for details.

Also {bdg-ref-primary}`my-target` without a tooltip.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_ref_badge_tooltip_survives_resolution(fmt, sphinx_builder):
    """A ``bdg-ref`` tooltip is applied to the *resolved* reference (#81).

    The tooltip (given after the explicit ``text <target>`` form) is carried
    across cross-reference resolution and rendered as a ``title``; a
    ``bdg-ref`` *without* a tooltip keeps the resolver's behaviour (no
    ``title`` is invented).
    """
    builder = _build(sphinx_builder, fmt, REF["rst"], REF["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")

    # both badges resolve to the target anchor
    assert html.count('href="#my-target"') == 2
    # the tooltipped one carries the title; it survived resolution
    assert (
        '<a class="sd-sphinx-override sd-badge sd-bg-primary sd-bg-text-primary'
        ' reference internal" href="#my-target" title="Jump to the target">' in html
    )

    doctree = builder.get_doctree("index", post_transforms=True)
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 2
    # one has the tooltip (with its explicit title as the badge text); the
    # other was left untouched (no reftitle invented for the tooltip-less one)
    with_tooltip = [r for r in refs if r.get("reftitle") == "Jump to the target"]
    without = [r for r in refs if "reftitle" not in r]
    assert len(with_tooltip) == 1
    assert with_tooltip[0].astext() == "Target"
    assert len(without) == 1


REF_SEMI = {
    "rst": """
Heading
=======

R1 :bdg-ref-primary:`my-target ; tip` bare-suffix.

R2 :bdg-ref-info:`text <my;label>` semi-in-target.
""",
    "myst": """
# Heading

R1 {bdg-ref-primary}`my-target ; tip` bare-suffix.

R2 {bdg-ref-info}`text <my;label>` semi-in-target.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_ref_badge_semicolon_target_never_split(fmt, sphinx_builder):
    """``;`` is legal in reference targets: a ``bdg-ref`` target is never
    corrupted by the tooltip grammar.

    A bare target with a would-be suffix, and a ``;`` inside an explicit
    ``<target>`` group, are both passed through intact (here: unresolved,
    exactly as on the pre-tooltip code, since no such labels exist).
    """
    builder = _build(
        sphinx_builder, fmt, REF_SEMI["rst"], REF_SEMI["myst"], assert_pass=False
    )
    # the *full* target strings reach the resolver (proof of no split) ...
    doctree = builder.get_doctree("index")
    targets = [x["reftarget"] for x in doctree.findall(addnodes.pending_xref)]
    assert targets == ["my-target ; tip", "my;label"]
    # ... and its missing-reference warnings name them verbatim
    assert "my-target ; tip" in builder.warnings
    assert "my;label" in builder.warnings

    # no tooltip was produced anywhere, and nothing transient leaks
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    post = builder.get_doctree("index", post_transforms=True)
    assert 'title="tip"' not in html
    assert not [r for r in post.findall(nodes.reference) if "reftitle" in r]
    assert not [n for n in post.findall(nodes.Element) if "sd_tooltip" in n]
    for haystack in (html, post.pformat()):
        assert _BADGE_REF_TOOLTIP_MARKER_PREFIX not in haystack
        assert "sd_tooltip" not in haystack


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_ref_badge_no_marker_or_attr_leak(fmt, sphinx_builder):
    """The transient tooltip carry mechanism never leaks into any output."""
    builder = _build(sphinx_builder, fmt, REF["rst"], REF["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    doctree = builder.get_doctree("index", post_transforms=True)
    pformat = doctree.pformat()

    for haystack in (html, pformat):
        assert _BADGE_REF_TOOLTIP_MARKER_PREFIX not in haystack
        assert "sd_tooltip" not in haystack


# ---------------------------------------------------------------------------
# buttons: existing :tooltip: option must be HTML-escaped
# ---------------------------------------------------------------------------

BUTTON = {
    "rst": """
Heading
=======

.. button-link:: https://example.com
    :tooltip: a <b> & "q"

    Button
""",
    "myst": """
# Heading

```{button-link} https://example.com
:tooltip: a <b> & "q"

Button
```
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_button_tooltip_escaped(fmt, sphinx_builder):
    """A ``button`` ``:tooltip:`` is HTML-escaped in the ``title`` attribute."""
    builder = _build(sphinx_builder, fmt, BUTTON["rst"], BUTTON["myst"])
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert 'title="a &lt;b&gt; &amp; &quot;q&quot;"' in html
    assert 'title="a <b>' not in html
