"""Tests for the ``steps`` / ``step`` directives.

The doctree regressions lock the structure the CSS relies on (a real
``enumerated_list`` of ``list_item``s, with an optional ``rubric`` title and a
``step-content`` container), and check the RST and MyST syntaxes produce the
same tree where the two markups are expected to agree.
"""

from collections.abc import Callable
import re

from docutils import nodes
import pytest

from sphinx_design.shared import is_component

from .conftest import SphinxBuilder

try:
    import myst_parser  # noqa: F401

    MYST_INSTALLED = True
except ImportError:
    MYST_INSTALLED = False

MYST_PARAM = pytest.param(
    "myst",
    marks=pytest.mark.skipif(not MYST_INSTALLED, reason="myst-parser not installed"),
)


def _build(fmt: str, source: str, sphinx_builder: Callable[..., SphinxBuilder]):
    """Build a one-page project in ``fmt`` (``"rst"`` or ``"myst"``)."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            "Heading\n=======\n\n" + source, encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            "# Heading\n\n" + source, encoding="utf8"
        )
    return builder


# scenarios where RST and MyST are expected to yield an identical doctree,
# so they share a single regression fixture (the shared basename asserts it)
EQUIVALENT_SOURCES = {
    "titled": {
        "rst": (
            ".. steps::\n\n"
            "   .. step:: First\n\n      Content one.\n\n"
            "   .. step:: Second\n\n      Content two.\n"
        ),
        "myst": (
            "::::{steps}\n\n"
            ":::{step} First\nContent one.\n:::\n\n"
            ":::{step} Second\nContent two.\n:::\n::::\n"
        ),
    },
    "untitled": {
        "rst": ".. steps::\n\n   .. step::\n\n      Just content, no title.\n",
        "myst": "::::{steps}\n\n:::{step}\nJust content, no title.\n:::\n::::\n",
    },
    "start": {
        "rst": (
            ".. steps::\n   :start: 3\n\n"
            "   .. step:: Third\n\n      Content.\n\n"
            "   .. step:: Fourth\n\n      Content.\n"
        ),
        "myst": (
            "::::{steps}\n:start: 3\n\n"
            ":::{step} Third\nContent.\n:::\n\n"
            ":::{step} Fourth\nContent.\n:::\n::::\n"
        ),
    },
}

# a code-block nested in a step: RST ``code-block`` and MyST fenced code produce
# slightly different ``literal_block`` attributes, so these get per-format fixtures
NESTED_SOURCES = {
    "rst": (
        ".. steps::\n\n   .. step:: Setup\n\n"
        "      .. code-block:: python\n\n         a = 1\n"
    ),
    "myst": "::::{steps}\n\n:::{step} Setup\n```python\na = 1\n```\n:::\n::::\n",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
@pytest.mark.parametrize("name", list(EQUIVALENT_SOURCES))
def test_steps_doctree(
    name, fmt, sphinx_builder, file_regression, normalize_doctree_xml
):
    """Titled / untitled / ``start`` doctrees, shared between RST and MyST."""
    builder = _build(fmt, EQUIVALENT_SOURCES[name][fmt], sphinx_builder)
    builder.build()
    doctree = builder.get_doctree("index", post_transforms=False)
    doctree.attributes.pop("translation_progress", None)
    file_regression.check(
        normalize_doctree_xml(doctree.pformat()),
        basename=f"steps_{name}",
        extension=".xml",
        encoding="utf8",
    )


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_steps_nested_code_block(
    fmt, sphinx_builder, file_regression, normalize_doctree_xml
):
    """A code-block nested inside a step (per-format, since the two markups differ)."""
    builder = _build(fmt, NESTED_SOURCES[fmt], sphinx_builder)
    builder.build()
    doctree = builder.get_doctree("index", post_transforms=False)
    doctree.attributes.pop("translation_progress", None)
    file_regression.check(
        normalize_doctree_xml(doctree.pformat()),
        basename=f"steps_nested_{fmt}",
        extension=".xml",
        encoding="utf8",
    )


def test_step_outside_steps_warns(sphinx_builder):
    """A ``step`` whose parent is not a ``steps`` should warn (like a stray tab-item)."""
    builder = _build(
        "rst", ".. step:: Lonely\n\n   No enclosing steps.\n", sphinx_builder
    )
    builder.build(assert_pass=False)
    assert "The parent of a 'step' should be a 'steps'" in builder.warnings
    assert "[design.steps]" in builder.warnings


def test_non_step_child_warns(sphinx_builder):
    """A non-``step`` child of ``steps`` should warn and be dropped."""
    builder = _build(
        "rst",
        (
            ".. steps::\n\n"
            "   .. step:: A\n\n      A content\n\n"
            "   not a step\n\n"
            "   .. step:: B\n\n      B content\n"
        ),
        sphinx_builder,
    )
    builder.build(assert_pass=False)
    assert "All children of a 'steps' should be 'step'" in builder.warnings
    assert "[design.steps]" in builder.warnings
    # the two valid steps survive; the stray paragraph is dropped
    doctree = builder.get_doctree("index")
    steps = list(doctree.findall(lambda n: is_component(n, "steps")))
    assert len(steps) == 1
    step_items = [c for c in steps[0].children if is_component(c, "step")]
    assert len(step_items) == 2
    assert len(steps[0].children) == 2


TARGET_SOURCES = {
    "rst": (
        ".. steps::\n\n"
        "   .. _step-two-target:\n\n"
        "   .. step:: One\n\n      first\n\n"
        "   .. step:: Two\n\n      second\n\n"
        "See :ref:`the second step <step-two-target>`.\n"
    ),
    "myst": (
        "::::{steps}\n\n"
        "(step-two-target)=\n\n"
        ":::{step} One\nfirst\n:::\n\n"
        ":::{step} Two\nsecond\n:::\n::::\n\n"
        "See {ref}`the second step <step-two-target>`.\n"
    ),
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_target_between_steps_resolves(fmt, sphinx_builder):
    """A hyperlink target between steps is kept, so references still resolve.

    docutils PropagateTargets moves the id onto the following step (list_item),
    which survives to the HTML output. Mirrors the tab-set target policy.
    """
    builder = _build(fmt, TARGET_SOURCES[fmt], sphinx_builder)
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index", post_transforms=True)
    references = list(doctree.findall(nodes.reference))
    assert len(references) == 1
    refid = references[0]["refid"]
    assert refid == "step-two-target"
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert f'id="{refid}"' in html


def test_steps_role_list_in_html(sphinx_builder):
    """The rendered ``<ol>`` carries ``role="list"`` (restores list semantics
    for screen readers once the native marker is hidden)."""
    builder = _build("rst", ".. steps::\n\n   .. step:: A\n\n      a\n", sphinx_builder)
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert re.search(r'<ol[^>]*\brole="list"[^>]*\bclass="[^"]*sd-steps', html) or (
        re.search(r'<ol[^>]*\bclass="[^"]*sd-steps[^"]*"[^>]*\brole="list"', html)
    )


@pytest.mark.parametrize("builder_name", ["text", "latex"])
def test_steps_degrades_in_non_html(builder_name, sphinx_builder):
    """Non-HTML builders render the steps as a plain numbered list (no
    ``role`` attribute leaks, numbering honours ``start``)."""
    builder = sphinx_builder(
        builder_name, conf_kwargs={"extensions": ["sphinx_design"]}
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n"
        ".. steps::\n   :start: 3\n\n"
        "   .. step:: First\n\n      alpha\n\n"
        "   .. step:: Second\n\n      beta\n",
        encoding="utf8",
    )
    builder.build()
    out = builder.out_path
    if builder_name == "text":
        text = (out / "index.txt").read_text(encoding="utf8")
        assert "role=" not in text
        # numbered list starting at the ``start`` offset
        assert "3." in text and "4." in text
    else:
        text = next(out.glob("*.tex")).read_text(encoding="utf8")
        assert "role=" not in text
        # a real LaTeX enumerate, offset by ``start`` (\setcounter to start-1)
        assert "\\begin{enumerate}" in text
        assert "\\setcounter{enumi}{2}" in text


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_comment_between_steps_no_warning(fmt, sphinx_builder):
    """A comment between steps must not trigger a warning (cf. issue #86)."""
    sources = {
        "rst": (
            ".. steps::\n\n"
            "   .. a comment\n\n"
            "   .. step:: A\n\n      A content\n\n"
            "   .. step:: B\n\n      B content\n"
        ),
        "myst": (
            "::::{steps}\n\n"
            "% a comment\n\n"
            ":::{step} A\nA content\n:::\n\n"
            ":::{step} B\nB content\n:::\n::::\n"
        ),
    }
    builder = _build(fmt, sources[fmt], sphinx_builder)
    builder.build()  # asserts no warnings
    doctree = builder.get_doctree("index")
    steps = list(doctree.findall(lambda n: is_component(n, "step")))
    assert len(steps) == 2
