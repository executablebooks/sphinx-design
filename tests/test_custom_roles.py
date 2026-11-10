"""Tests for config-defined custom badge roles (``sd_custom_roles``).

Each ``sd_custom_roles`` entry registers a new role that inherits a built-in
sphinx-design *badge* role (the v1 scope: ``bdg``/``bdg-<color>``/``-line`` and
the ``bdg-link-*``/``bdg-ref-*`` families), optionally baking in a default
``tooltip``. The custom role renders identically to the role it inherits, and:

* a baked ``tooltip`` becomes the default HTML ``title`` (via the same
  mechanisms as the per-instance ``; tooltip`` suffix - a ``sd_badge`` node for
  plain badges, ``reftitle`` for link/ref badges),
* a per-instance ``; tooltip`` suffix **overrides** the baked value,
* a custom role *without* a tooltip is byte-identical to the inherited role,
* an unknown ``inherit`` or a clash with an existing role warns and is skipped.

Registration is reconciled on every ``config-inited`` against docutils'
process-global role registry, so this module also covers: a clash with a
docutils canonical role (``code``/``strong``/...) is warned and skipped; an
in-process rebuild refreshes an edited tooltip; and a role dropped from the
config is unregistered (rather than leaking into a later build or sibling app).

Written to also run under ``py311-no-myst``: core assertions use
reStructuredText, and the MyST variants are guarded by ``MYST_PARAM``.
"""

import io

from docutils import nodes
import pytest
from sphinx.application import Sphinx
from sphinx.util.docutils import docutils_namespace

from sphinx_design.badges_buttons import sd_badge

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

# the custom roles shared by the rendering tests below
CUSTOM_ROLES = {
    "bdg-stable": {
        "inherit": "bdg-success",
        "tooltip": "A released, supported version",
    },
    "bdg-plain": {"inherit": "bdg-info"},
    "bdg-docs": {"inherit": "bdg-link-info", "tooltip": "Opens the documentation"},
    "bdg-jump": {"inherit": "bdg-ref-primary", "tooltip": "Jump to the target"},
}


def _build(sphinx_builder, fmt, content, *, custom_roles=None, assert_pass=True):
    """Build a single-document project from a ``{"rst": ..., "myst": ...}`` map."""
    custom_roles = CUSTOM_ROLES if custom_roles is None else custom_roles
    if fmt == "rst":
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": ["sphinx_design"],
                "sd_custom_roles": custom_roles,
            }
        )
        builder.src_path.joinpath("index.rst").write_text(
            content["rst"], encoding="utf8"
        )
    else:
        builder = sphinx_builder(
            conf_kwargs={
                "extensions": ["myst_parser", "sphinx_design"],
                "myst_enable_extensions": ["colon_fence"],
                "sd_custom_roles": custom_roles,
            }
        )
        builder.src_path.joinpath("index.md").write_text(
            content["myst"], encoding="utf8"
        )
    builder.build(assert_pass=assert_pass)
    return builder


# ---------------------------------------------------------------------------
# plain badge inheritance: baked tooltip + suffix precedence
# ---------------------------------------------------------------------------

PLAIN = {
    "rst": """
Heading
=======

Baked :bdg-stable:`v1` here.

Override :bdg-stable:`v1 ; Custom override` there.
""",
    "myst": """
# Heading

Baked {bdg-stable}`v1` here.

Override {bdg-stable}`v1 ; Custom override` there.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_baked_tooltip_and_suffix_override(fmt, sphinx_builder):
    """A baked tooltip is the default ``title``; a ``; suffix`` overrides it."""
    builder = _build(sphinx_builder, fmt, PLAIN)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # inherits bdg-success's classes, and bakes in the default tooltip
    assert (
        '<span class="sd-sphinx-override sd-badge sd-bg-success sd-bg-text-success"'
        ' title="A released, supported version">v1</span>' in html
    )
    # the per-instance suffix overrides the baked default
    assert (
        '<span class="sd-sphinx-override sd-badge sd-bg-success sd-bg-text-success"'
        ' title="Custom override">v1</span>' in html
    )
    # the baked default never appears alongside the override
    assert 'title="A released, supported version">v1</span>' in html

    doctree = builder.get_doctree("index")
    badges = list(doctree.findall(sd_badge))
    assert len(badges) == 2
    assert badges[0]["tooltip"] == "A released, supported version"
    assert badges[1]["tooltip"] == "Custom override"


# ---------------------------------------------------------------------------
# byte-identity: a no-tooltip custom role == the inherited role
# ---------------------------------------------------------------------------

IDENTICAL = {
    "rst": """
Heading
=======

Custom :bdg-plain:`hello` and inherited :bdg-info:`hello`.
""",
    "myst": """
# Heading

Custom {bdg-plain}`hello` and inherited {bdg-info}`hello`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_no_tooltip_custom_role_byte_identical(fmt, sphinx_builder):
    """A tooltip-less custom role renders byte-identically to its inherited role."""
    builder = _build(sphinx_builder, fmt, IDENTICAL)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    span = '<span class="sd-sphinx-override sd-badge sd-bg-info sd-bg-text-info">hello</span>'
    # the custom and the inherited badge produce the exact same span (no title)
    assert html.count(span) == 2

    # ... and the doctree nodes are equivalent: neither carries a tooltip
    doctree = builder.get_doctree("index")
    badges = list(doctree.findall(sd_badge))
    assert len(badges) == 2
    for badge in badges:
        assert "tooltip" not in badge
        assert badge["classes"] == [
            "sd-sphinx-override",
            "sd-badge",
            "sd-bg-info",
            "sd-bg-text-info",
        ]


# ---------------------------------------------------------------------------
# link badge inheritance (reference reftitle)
# ---------------------------------------------------------------------------

LINK = {
    "rst": """
Heading
=======

Baked :bdg-docs:`docs <https://example.com>`.

Override :bdg-docs:`docs <https://example.com> ; Other tip`.
""",
    "myst": """
# Heading

Baked {bdg-docs}`docs <https://example.com>`.

Override {bdg-docs}`docs <https://example.com> ; Other tip`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_link_badge_custom_role(fmt, sphinx_builder):
    """A custom link badge bakes its tooltip into ``reftitle``; a suffix wins."""
    builder = _build(sphinx_builder, fmt, LINK)
    doctree = builder.get_doctree("index")
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 2
    assert refs[0]["refuri"] == "https://example.com"
    assert refs[0]["reftitle"] == "Opens the documentation"
    assert refs[1]["reftitle"] == "Other tip"
    # inherits the bdg-link-info colour classes
    assert "sd-bg-info" in refs[0]["classes"]


LINK_BARE = {
    "rst": """
Heading
=======

Bare :bdg-docs:`https://example.com/a;b`.
""",
    "myst": """
# Heading

Bare {bdg-docs}`https://example.com/a;b`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_link_badge_baked_tooltip_bare_form(fmt, sphinx_builder):
    """A baked tooltip applies even to a bare-form link badge.

    The ``; tooltip`` *suffix* is only recognised after the explicit
    ``text <target>`` form for link/ref badges (``;`` is legal in URLs), so a
    bare target is never split. A *baked* tooltip is not a suffix, so it still
    applies here - reaching a use where the per-instance grammar could not.
    """
    builder = _build(sphinx_builder, fmt, LINK_BARE)
    doctree = builder.get_doctree("index")
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 1
    # the bare target is untouched (the whole text is the URL, ``;`` and all)
    assert refs[0]["refuri"] == "https://example.com/a;b"
    # yet the baked tooltip is applied
    assert refs[0]["reftitle"] == "Opens the documentation"


# ---------------------------------------------------------------------------
# cross-reference badge inheritance (reftitle grafted post-resolution)
# ---------------------------------------------------------------------------

REF = {
    "rst": """
Heading
=======

.. _my-target:

My Target Section
-----------------

Baked :bdg-jump:`Target <my-target>`.

Override :bdg-jump:`Target <my-target> ; Other tip`.
""",
    "myst": """
# Heading

(my-target)=

## My Target Section

Baked {bdg-jump}`Target <my-target>`.

Override {bdg-jump}`Target <my-target> ; Other tip`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_ref_badge_custom_role(fmt, sphinx_builder):
    """A custom ref badge bakes its tooltip, applied to the resolved reference."""
    builder = _build(sphinx_builder, fmt, REF)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count('href="#my-target"') == 2

    doctree = builder.get_doctree("index", post_transforms=True)
    refs = [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]
    assert len(refs) == 2
    titles = {r.get("reftitle") for r in refs}
    assert titles == {"Jump to the target", "Other tip"}
    # inherits the bdg-ref-primary colour classes
    assert all("sd-bg-primary" in r["classes"] for r in refs)


# ---------------------------------------------------------------------------
# registration edge cases: clash + unknown inherit warn and skip
# ---------------------------------------------------------------------------

CLASH = {
    "rst": """
Heading
=======

A :bdg-primary:`p` badge.
""",
    "myst": """
# Heading

A {bdg-primary}`p` badge.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_clash_with_existing_role_warns_and_skips(fmt, sphinx_builder):
    """A custom role named like an existing role warns and leaves it untouched."""
    builder = _build(
        sphinx_builder,
        fmt,
        CLASH,
        custom_roles={"bdg-primary": {"inherit": "bdg-danger", "tooltip": "nope"}},
        assert_pass=False,
    )
    assert (
        "sd_custom_roles: 'bdg-primary' clashes with an existing role, skipping"
        in builder.warnings
    )
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # the built-in bdg-primary is retained (primary classes, no baked tooltip)
    assert (
        '<span class="sd-sphinx-override sd-badge sd-bg-primary sd-bg-text-primary">'
        "p</span>" in html
    )
    assert 'title="nope"' not in html


CONTENT = {
    "rst": "Heading\n=======\n\ncontent\n",
    "myst": "# Heading\n\ncontent\n",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_unknown_inherit_warns_and_skips(fmt, sphinx_builder):
    """A custom role inheriting an unknown badge role warns and is not registered."""
    builder = _build(
        sphinx_builder,
        fmt,
        CONTENT,
        custom_roles={"bdg-foo": {"inherit": "not-a-badge"}},
        assert_pass=False,
    )
    assert (
        "sd_custom_roles: 'bdg-foo.inherit' is an unknown badge role: not-a-badge"
        in builder.warnings
    )


CANONICAL = {
    "rst": """
Heading
=======

Bold **b**, role :strong:`s`, and code :code:`x = 1`.
""",
    "myst": """
# Heading

Bold **b**, role {strong}`s`, and code {code}`x = 1`.
""",
}


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_canonical_role_clash_warns_and_skips(fmt, sphinx_builder):
    """A custom role named after a docutils canonical role is skipped, not a hijack.

    ``strong``/``code``/... live in docutils' canonical registry (not the local
    one Sphinx's ``add_role`` checks), so they must be recognised as clashes -
    otherwise a custom role would silently override ``**bold**`` / ``:code:``.
    """
    builder = _build(
        sphinx_builder,
        fmt,
        CANONICAL,
        custom_roles={
            "strong": {"inherit": "bdg-danger", "tooltip": "HIJACK"},
            "code": {"inherit": "bdg-info", "tooltip": "HIJACK"},
        },
        assert_pass=False,
    )
    assert "'strong' clashes with an existing role, skipping" in builder.warnings
    assert "'code' clashes with an existing role, skipping" in builder.warnings
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    # neither canonical role was overridden: no badge, no baked tooltip
    assert "HIJACK" not in html
    assert "sd-badge" not in html
    # ``**b**`` and ``:strong:`s``` still render as real ``<strong>``
    assert html.count("<strong>") == 2


def _raw_build(tmp_path, sub, custom_roles):
    """Build a tiny rST project with a raw ``Sphinx`` app (no fixture isolation).

    Returns the rendered ``index.html``. Used to exercise the process-global
    docutils role registry that the fixtures otherwise reset between apps.
    """
    src = tmp_path / sub
    src.mkdir()
    (src / "conf.py").write_text(
        "extensions = ['sphinx_design']\n" + f"sd_custom_roles = {custom_roles!r}\n",
        encoding="utf8",
    )
    (src / "index.rst").write_text("H\n=\n\nUse :bdg-stable:`v1`.\n", encoding="utf8")
    app = Sphinx(
        str(src),
        str(src),
        str(src / "_out"),
        str(src / "_dt"),
        "html",
        warningiserror=False,
        status=None,
        warning=io.StringIO(),
    )
    app.build()
    return (src / "_out" / "index.html").read_text(encoding="utf8")


def test_reconcile_refresh_and_unregister_in_process(tmp_path):
    """In one process (shared role registry): edits refresh, drops unregister.

    The pytest fixtures reset docutils' global role state between apps, which
    would mask the reconciliation; building several raw apps inside a single
    ``docutils_namespace`` exercises the real shared registry (and restores it
    on exit, so other tests are unaffected).
    """
    stable = {"inherit": "bdg-success"}
    with docutils_namespace():
        html1 = _raw_build(
            tmp_path, "a", {"bdg-stable": {**stable, "tooltip": "FIRST"}}
        )
        assert 'title="FIRST"' in html1

        # an edited tooltip is picked up on the in-process rebuild (no stale value)
        html2 = _raw_build(
            tmp_path, "b", {"bdg-stable": {**stable, "tooltip": "SECOND"}}
        )
        assert 'title="SECOND"' in html2
        assert 'title="FIRST"' not in html2

        # dropping the role unregisters it: it no longer resolves as a badge
        html3 = _raw_build(tmp_path, "c", {})
        assert "sd-badge" not in html3
        assert "problematic" in html3  # the now-unknown role errors instead
