"""Tests for the ``tooltip`` role option of the badge roles.

Every badge role (``bdg``, ``bdg-<color>``, ``-line``, and the ``bdg-link-*``
and ``bdg-ref-*`` families) declares a ``tooltip`` option, in the docutils
convention for role functions (an ``options`` option spec on the role, and an
``options`` dictionary passed to each call). So a reStructuredText custom role
can preset a tooltip::

    .. role:: bdg-stable(bdg-success)
       :tooltip: A released, supported version

and an extension that presets a badge role passes ``options={"tooltip": ...}``.

The tooltip of a badge is, in order of precedence: its ``; tooltip`` suffix,
the ``tooltip`` option, then the role constructor's default. It renders exactly
like a suffix tooltip (an HTML ``title``), and leaves non-HTML output alone.
"""

from unittest.mock import Mock

from docutils import nodes
from docutils.parsers.rst import roles
import pytest

from sphinx_design.badges_buttons import (
    BadgeRole,
    LinkBadgeRole,
    XRefBadgeRole,
    _iter_badge_roles,
    sd_badge,
)


def _build_rst(sphinx_builder, rst, *, buildername="html", assert_pass=True):
    """Build a single reStructuredText document."""
    builder = sphinx_builder(
        buildername=buildername, conf_kwargs={"extensions": ["sphinx_design"]}
    )
    builder.src_path.joinpath("index.rst").write_text(rst, encoding="utf8")
    builder.build(assert_pass=assert_pass)
    return builder


def _badge_refs(doctree):
    """The (resolved) badge references in a doctree."""
    return [r for r in doctree.findall(nodes.reference) if "sd-badge" in r["classes"]]


# ---------------------------------------------------------------------------
# the option spec
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("role_cls", [BadgeRole, LinkBadgeRole, XRefBadgeRole])
def test_option_spec(role_cls):
    """Each badge role declares the ``tooltip`` option, as its own copy.

    docutils adds a ``class`` option to the spec of every role it registers, so
    a spec shared between instances would grow one for every role (this test
    also runs after the other tests have registered the badge roles).
    """
    role = role_cls()
    assert set(role.options) == {"tooltip"}
    assert role.options is role.option_spec
    assert role.options is not role_cls.OPTION_SPEC
    roles.set_implicit_options(role)
    assert set(role.options) == {"class", "tooltip"}
    assert set(role_cls.OPTION_SPEC) == {"tooltip"}


def test_every_badge_role_declares_the_option():
    """Every role of the badge family accepts the option (it shares one mixin)."""
    for name, role_cls, color, outline in _iter_badge_roles():
        role = role_cls(color, outline=outline)
        assert "tooltip" in role.options, name


# ---------------------------------------------------------------------------
# plain badges, through a ``.. role::`` custom role
# ---------------------------------------------------------------------------

PLAIN = """
Heading
=======

.. role:: bdg-stable(bdg-success)
   :tooltip: A released & supported version

Preset :bdg-stable:`v1` here.

Override :bdg-stable:`v2 ; Long-term support` there.

Base :bdg-success:`v3` everywhere.
"""


def test_plain_badge_option(sphinx_builder):
    """The option is the badge's ``title``; a ``; suffix`` overrides it."""
    builder = _build_rst(sphinx_builder, PLAIN)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    classes = "sd-sphinx-override sd-badge sd-bg-success sd-bg-text-success"
    # the option becomes an (escaped) title on the inherited badge
    assert (
        f'<span class="{classes}" title="A released &amp; supported version">'
        "v1</span>" in html
    )
    # a per-instance suffix wins over the option
    assert f'<span class="{classes}" title="Long-term support">v2</span>' in html
    # the base role is unaffected by the custom role's option
    assert f'<span class="{classes}">v3</span>' in html

    badges = list(builder.get_doctree("index").findall(sd_badge))
    assert [b.get("tooltip") for b in badges] == [
        "A released & supported version",
        "Long-term support",
        None,
    ]
    # the custom role renders exactly as its base: no extra (role-name) class
    assert all(b["classes"] == classes.split() for b in badges)


# ---------------------------------------------------------------------------
# link and reference badges
# ---------------------------------------------------------------------------

LINK = """
Heading
=======

.. role:: bdg-docs(bdg-link-info)
   :tooltip: Opens the documentation

Explicit :bdg-docs:`docs <https://example.com>`.

Bare :bdg-docs:`https://example.com/a;b`.

Override :bdg-docs:`docs <https://example.com> ; Other tip`.
"""


def test_link_badge_option(sphinx_builder):
    """A link badge's option is its ``reftitle``, also on the bare form."""
    builder = _build_rst(sphinx_builder, LINK)
    refs = _badge_refs(builder.get_doctree("index"))
    assert [r["refuri"] for r in refs] == [
        "https://example.com",
        # the bare target is never split at ``;`` - yet the option applies
        "https://example.com/a;b",
        "https://example.com",
    ]
    assert [r.get("reftitle") for r in refs] == [
        "Opens the documentation",
        "Opens the documentation",
        "Other tip",
    ]
    assert all("sd-bg-info" in r["classes"] for r in refs)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count('title="Opens the documentation"') == 2
    assert html.count('title="Other tip"') == 1


REF = """
Heading
=======

.. _my-target:

My Target Section
-----------------

.. role:: bdg-jump(bdg-ref-primary)
   :tooltip: Jump to the target

Explicit :bdg-jump:`Target <my-target>`.

Bare :bdg-jump:`my-target`.

Override :bdg-jump:`Target <my-target> ; Other tip`.
"""


def test_ref_badge_option(sphinx_builder):
    """A ref badge's option survives resolution, replacing the automatic title."""
    builder = _build_rst(sphinx_builder, REF)
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count('href="#my-target"') == 3
    assert html.count('title="Jump to the target"') == 2
    assert html.count('title="Other tip"') == 1

    refs = _badge_refs(builder.get_doctree("index", post_transforms=True))
    assert [r.get("reftitle") for r in refs] == [
        "Jump to the target",
        "Jump to the target",
        "Other tip",
    ]
    assert all("sd-bg-primary" in r["classes"] for r in refs)


# ---------------------------------------------------------------------------
# the option spec survives use of the role
# ---------------------------------------------------------------------------

AFTER_USE = """
Heading
=======

First :bdg-info:`a`, then :bdg-info:`b ; Suffix`.

.. role:: bdg-later(bdg-info)
   :tooltip: Defined after use
   :class: foo

.. role:: bdg-bare(bdg-info)

Later :bdg-later:`c`, bare :bdg-bare:`d`.
"""


def test_option_spec_survives_role_use(sphinx_builder):
    """A custom role defined after its base role has been used still takes the option.

    ``SphinxRole`` stores each call's options on the role instance, which would
    shadow the option spec docutils' ``role`` directive reads; the badge roles
    restore the spec after the call. The restored spec is the one docutils
    registered, so it still includes the ``class`` option docutils added then.
    """
    builder = _build_rst(sphinx_builder, AFTER_USE)
    assert not builder.warnings
    badges = list(builder.get_doctree("index").findall(sd_badge))
    assert [b.get("tooltip") for b in badges] == [
        None,
        "Suffix",
        "Defined after use",
        None,
    ]


def test_option_spec_restored_when_the_role_raises(monkeypatch):
    """The option spec is restored even when the base role raises."""
    role = BadgeRole("info")
    roles.set_implicit_options(role)
    spec = role.options

    def _raise(self):
        raise RuntimeError("boom")

    monkeypatch.setattr(BadgeRole, "run", _raise)
    with pytest.raises(RuntimeError, match="boom"):
        role("bdg-info", ":bdg-info:`a`", "a", 1, Mock(), {"tooltip": "T"})
    assert role.options is spec
    assert set(role.options) == {"class", "tooltip"}


EMPTY = """
Heading
=======

.. role:: bdg-empty(bdg-info)
   :tooltip:

Text.
"""


def test_empty_option_is_an_error(sphinx_builder):
    """An empty ``:tooltip:`` is refused, as the button ``:tooltip:`` option is."""
    builder = _build_rst(sphinx_builder, EMPTY, assert_pass=False)
    assert 'Error in "role" directive' in builder.warnings
    assert "tooltip" in builder.warnings


# ---------------------------------------------------------------------------
# calling a role with the option, as an extension would
# ---------------------------------------------------------------------------


def test_options_dict_and_constructor_default(sphinx_builder):
    """The ``options`` dictionary of a call beats the constructor default.

    This is how an extension presets a badge role: wrap it, or register a
    ``docutils`` ``CustomRole`` around it, and pass the ``tooltip`` option.
    """
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    # register, for this app only (the fixture resets docutils' role registry):
    # a role with a constructor default, and a docutils custom role over it
    roles.register_local_role(
        "bdg-default", BadgeRole("warning", tooltip="Constructor default")
    )
    roles.register_local_role(
        "bdg-preset",
        roles.CustomRole(
            "bdg-preset",
            roles._roles["bdg-default"],
            {"tooltip": "From options"},
        ),
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Heading\n=======\n\n"
        ":bdg-default:`a` :bdg-preset:`b` :bdg-preset:`c ; From suffix`\n",
        encoding="utf8",
    )
    builder.build()
    badges = list(builder.get_doctree("index").findall(sd_badge))
    assert [b.get("tooltip") for b in badges] == [
        "Constructor default",
        "From options",
        "From suffix",
    ]


# ---------------------------------------------------------------------------
# non-HTML builders
# ---------------------------------------------------------------------------

NON_HTML = """
Heading
=======

.. _my-target:

My Target Section
-----------------

.. role:: bdg-stable(bdg-success)
   :tooltip: TIP-PLAIN

.. role:: bdg-docs(bdg-link-info)
   :tooltip: TIP-LINK

.. role:: bdg-jump(bdg-ref-primary)
   :tooltip: TIP-REF

Plain :bdg-stable:`v1`, link :bdg-docs:`docs <https://example.com>`,
ref :bdg-jump:`Target <my-target>`.
"""


@pytest.mark.parametrize(
    ("buildername", "suffix"), [("text", ".txt"), ("latex", ".tex"), ("man", ".1")]
)
def test_non_html_builders_unaffected(sphinx_builder, buildername, suffix):
    """Non-HTML output shows the badge text only, never the option's tooltip."""
    builder = _build_rst(sphinx_builder, NON_HTML, buildername=buildername)
    (outfile,) = builder.out_path.glob(f"*{suffix}")
    output = outfile.read_text(encoding="utf8")
    assert "v1" in output
    assert "docs" in output
    assert "Target" in output
    assert "TIP-" not in output
