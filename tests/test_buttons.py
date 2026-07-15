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
"""

from docutils import nodes
import pytest

from sphinx_design.badges_buttons import (
    _BUTTON_REF_MARKER_PREFIX,
    ButtonLinkDirective,
    ButtonRefDirective,
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
