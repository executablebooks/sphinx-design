"""Tests for the FontAwesome icon roles, CDN config and LaTeX package support.

Covers:

- the v6 role names (``fa-solid``/``fa-brands``/``fa-regular``) emit exactly the
  canonical v6 classes, and the legacy ``fa``/``fas``/``fab``/``far`` roles are
  unchanged (backwards compatibility, #174);
- ``sd_fontawesome_source`` adds (or omits) the FontAwesome CDN CSS in HTML;
- ``sd_fontawesome_latex`` selects the LaTeX package, including the new
  ``"fontawesome5"`` mode (``\\faIcon``) and byte-compatible legacy ``True``
  behaviour (``fontawesome`` package, ``\\faicon``) (#242);
- the "icons not in LaTeX output" warning is throttled to once per build;
- ``sd_fontawesome_version`` translates every role spelling to the configured
  FontAwesome class scheme (``"4"``/``"5"``/``"6"``), with the default
  ``"as-named"`` emitting the role name verbatim (parity with previous
  releases), and without affecting LaTeX output.

Written to also run under ``py311-no-myst``: the core assertions use
reStructuredText, and MyST variants are guarded by ``MYST_PARAM``.
"""

from collections.abc import Callable

import pytest

from sphinx_design.icons import fontawesome

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

#: The default v6 CDN URL added by ``sd_fontawesome_source = "cdn"``.
DEFAULT_CDN_URL = (
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
)


def _fa_by_icon(doctree) -> dict[str, list[str]]:
    """Map each fontawesome node's icon name to its list of CSS classes."""
    return {
        node["icon"]: list(node["classes"]) for node in doctree.findall(fontawesome)
    }


def _build_icons(sphinx_builder, fmt, roles):
    """Build a one-page project exercising ``roles`` (a list of ``(name, icon)``).

    ``name`` is the role name, ``icon`` the icon argument.
    """
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        body = ", ".join(f":{name}:`{icon}`" for name, icon in roles)
        builder.src_path.joinpath("index.rst").write_text(
            f"Title\n=====\n\nIcons {body}.\n", encoding="utf8"
        )
    else:
        builder = sphinx_builder()
        body = ", ".join(f"{{{name}}}`{icon}`" for name, icon in roles)
        builder.src_path.joinpath("index.md").write_text(
            f"# Title\n\nIcons {body}.\n", encoding="utf8"
        )
    builder.build()  # asserts no warnings (HTML always renders FA)
    return builder


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_v6_role_classes(fmt, sphinx_builder: Callable[..., SphinxBuilder]):
    """The v6 roles emit exactly the classes their name implies, no legacy alias."""
    builder = _build_icons(
        sphinx_builder,
        fmt,
        [("fa-solid", "rocket"), ("fa-brands", "github"), ("fa-regular", "bell")],
    )
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    assert by_icon["rocket"] == ["fa-solid", "fa-rocket"]
    assert by_icon["github"] == ["fa-brands", "fa-github"]
    assert by_icon["bell"] == ["fa-regular", "fa-bell"]


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_v6_role_extra_classes(fmt, sphinx_builder: Callable[..., SphinxBuilder]):
    """Extra classes after a semicolon are appended to the v6 role classes."""
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
        builder.src_path.joinpath("index.rst").write_text(
            "Title\n=====\n\n:fa-solid:`rocket;sd-text-primary fa-xl`\n",
            encoding="utf8",
        )
    else:
        builder = sphinx_builder()
        builder.src_path.joinpath("index.md").write_text(
            "# Title\n\n{fa-solid}`rocket;sd-text-primary fa-xl`\n", encoding="utf8"
        )
    builder.build()
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    assert by_icon["rocket"] == ["fa-solid", "fa-rocket", "sd-text-primary", "fa-xl"]


@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_legacy_role_classes_unchanged(
    fmt, sphinx_builder: Callable[..., SphinxBuilder]
):
    """The legacy roles keep emitting the v4/v5 class scheme."""
    builder = _build_icons(
        sphinx_builder,
        fmt,
        [("fa", "star"), ("fas", "spinner"), ("fab", "github"), ("far", "bell")],
    )
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    assert by_icon["star"] == ["fa", "fa-star"]
    assert by_icon["spinner"] == ["fas", "fa-spinner"]
    assert by_icon["github"] == ["fab", "fa-github"]
    assert by_icon["bell"] == ["far", "fa-bell"]


def test_fontawesome_source_cdn_adds_link(sphinx_builder):
    """``sd_fontawesome_source="cdn"`` adds the CDN CSS to the HTML head once."""
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_source": "cdn",
        }
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n:fa-solid:`rocket`\n", encoding="utf8"
    )
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count(DEFAULT_CDN_URL) == 1


def test_fontawesome_source_none_omits_link(sphinx_builder):
    """The default ``sd_fontawesome_source="none"`` adds no FontAwesome CSS."""
    builder = sphinx_builder(conf_kwargs={"extensions": ["sphinx_design"]})
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n:fa-solid:`rocket`\n", encoding="utf8"
    )
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert DEFAULT_CDN_URL not in html
    assert "font-awesome" not in html


def test_fontawesome_source_cdn_custom_url(sphinx_builder):
    """``sd_fontawesome_cdn_url`` overrides the CSS URL that is added."""
    url = "https://example.com/my-fontawesome.css"
    builder = sphinx_builder(
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_source": "cdn",
            "sd_fontawesome_cdn_url": url,
        }
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n:fa-solid:`rocket`\n", encoding="utf8"
    )
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    assert html.count(url) == 1
    assert DEFAULT_CDN_URL not in html


LATEX_SRC = (
    "Title\n=====\n\nIcons :fas:`rocket`, :fab:`github`, :far:`bell`, :fa:`star`.\n"
)


def _latex_tex(builder) -> str:
    """Return the built ``.tex`` output."""
    return next(builder.out_path.glob("*.tex")).read_text(encoding="utf8")


def test_latex_fontawesome5(sphinx_builder):
    """``"fontawesome5"`` loads that package and maps styles per its manual."""
    builder = sphinx_builder(
        buildername="latex",
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_latex": "fontawesome5",
        },
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\n"
        "Icons :fa-solid:`rocket`, :fa-brands:`github`, :fa-regular:`bell`.\n",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    tex = _latex_tex(builder)
    assert "\\usepackage{fontawesome5}" in tex
    assert "\\faIcon{rocket}" in tex  # solid -> default style
    assert "\\faIcon{github}" in tex  # brands -> resolved by name
    assert "\\faIcon[regular]{bell}" in tex  # regular -> optional style arg
    # the fontawesome5 mode never emits the legacy lowercase macro
    assert "\\faicon{" not in tex
    assert "not included in LaTeX output" not in builder.warnings


@pytest.mark.parametrize("value", [True, "fontawesome"])
def test_latex_legacy_fontawesome_parity(value, sphinx_builder):
    """``True`` and ``"fontawesome"`` give the legacy, byte-identical output.

    (Compared against a captured ``main`` build: ``\\usepackage{fontawesome}``
    and ``\\faicon{<name>}`` for every icon, regardless of style.)
    """
    builder = sphinx_builder(
        buildername="latex",
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_latex": value,
        },
    )
    builder.src_path.joinpath("index.rst").write_text(LATEX_SRC, encoding="utf8")
    builder.build(assert_pass=False)
    tex = _latex_tex(builder)
    assert "\\usepackage{fontawesome}" in tex
    assert "\\usepackage{fontawesome5}" not in tex
    for icon in ("rocket", "github", "bell", "star"):
        assert f"\\faicon{{{icon}}}" in tex
    # legacy uses the lowercase macro, never the fontawesome5 \faIcon
    assert "\\faIcon{" not in tex
    assert "not included in LaTeX output" not in builder.warnings


@pytest.mark.parametrize("value", [False, "none"])
def test_latex_disabled_warns_once(value, sphinx_builder):
    """With icons disabled in LaTeX, the warning fires exactly once per build."""
    builder = sphinx_builder(
        buildername="latex",
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_latex": value,
        },
    )
    builder.src_path.joinpath("index.rst").write_text(LATEX_SRC, encoding="utf8")
    builder.build(assert_pass=False)
    # four icons in the source, but the throttled warning appears only once
    assert builder.warnings.count("not included in LaTeX output") == 1
    tex = _latex_tex(builder)
    assert "\\faicon{" not in tex
    assert "\\faIcon{" not in tex


#: One icon per role spelling (distinct names, so doctree lookups don't clash).
ALL_FA_ROLES = {
    "fa": "star",
    "fas": "rocket",
    "fab": "github",
    "far": "bell",
    "fa-solid": "fire",
    "fa-brands": "gitkraken",
    "fa-regular": "clock",
}

#: Expected leading class per role spelling, for every version scheme.
VERSION_LEADING_CLASS = {
    "as-named": {role: role for role in ALL_FA_ROLES},
    "4": dict.fromkeys(ALL_FA_ROLES, "fa"),
    "5": {
        "fa": "fas",
        "fas": "fas",
        "fa-solid": "fas",
        "fab": "fab",
        "fa-brands": "fab",
        "far": "far",
        "fa-regular": "far",
    },
    "6": {
        "fa": "fa-solid",
        "fas": "fa-solid",
        "fa-solid": "fa-solid",
        "fab": "fa-brands",
        "fa-brands": "fa-brands",
        "far": "fa-regular",
        "fa-regular": "fa-regular",
    },
}


def _build_all_role_spellings(sphinx_builder, fmt, conf_extra=None):
    """Build a one-page project using every fontawesome role spelling."""
    conf = {"extensions": ["sphinx_design"], **(conf_extra or {})}
    if fmt == "rst":
        builder = sphinx_builder(conf_kwargs=conf)
        body = ", ".join(f":{name}:`{icon}`" for name, icon in ALL_FA_ROLES.items())
        builder.src_path.joinpath("index.rst").write_text(
            f"Title\n=====\n\nIcons {body}.\n", encoding="utf8"
        )
    else:
        conf = {
            "extensions": ["myst_parser", "sphinx_design"],
            "myst_enable_extensions": ["colon_fence"],
            **(conf_extra or {}),
        }
        builder = sphinx_builder(conf_kwargs=conf)
        body = ", ".join(f"{{{name}}}`{icon}`" for name, icon in ALL_FA_ROLES.items())
        builder.src_path.joinpath("index.md").write_text(
            f"# Title\n\nIcons {body}.\n", encoding="utf8"
        )
    return builder


@pytest.mark.parametrize("version", ["as-named", "4", "5", "6"])
@pytest.mark.parametrize("fmt", ["rst", MYST_PARAM])
def test_version_class_mapping(
    fmt, version, sphinx_builder: Callable[..., SphinxBuilder]
):
    """Each role spelling emits the exact class list for the configured version."""
    builder = _build_all_role_spellings(
        sphinx_builder, fmt, {"sd_fontawesome_version": version}
    )
    builder.build()
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    for role, icon in ALL_FA_ROLES.items():
        expected = [VERSION_LEADING_CLASS[version][role], f"fa-{icon}"]
        assert by_icon[icon] == expected, f"role {role!r} with version {version!r}"


@pytest.mark.parametrize("explicit", [False, True], ids=["default", "explicit"])
def test_version_as_named_parity(
    explicit, sphinx_builder: Callable[..., SphinxBuilder]
):
    """The default (and explicit) ``"as-named"`` emits the role name verbatim.

    The asserted spans are byte-identical to those produced by sphinx-design
    before ``sd_fontawesome_version`` existed (verified against a build from
    ``main``), for every one of the seven role spellings.
    """
    conf = {"sd_fontawesome_version": "as-named"} if explicit else None
    builder = _build_all_role_spellings(sphinx_builder, "rst", conf)
    builder.build()
    html = (builder.out_path / "index.html").read_text(encoding="utf8")
    for role, icon in ALL_FA_ROLES.items():
        assert f'<span class="{role} fa-{icon}"' in html
    # the doctree carries exactly the same (verbatim) classes
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    for role, icon in ALL_FA_ROLES.items():
        assert by_icon[icon] == [role, f"fa-{icon}"]


def test_version_invalid_falls_back(sphinx_builder: Callable[..., SphinxBuilder]):
    """An invalid ``sd_fontawesome_version`` warns and falls back to as-named."""
    builder = _build_all_role_spellings(
        sphinx_builder, "rst", {"sd_fontawesome_version": "7"}
    )
    builder.build(assert_pass=False)
    assert "sd_fontawesome_version: " in builder.warnings
    assert "must be one of" in builder.warnings
    by_icon = _fa_by_icon(builder.get_doctree("index"))
    for role, icon in ALL_FA_ROLES.items():
        assert by_icon[icon] == [role, f"fa-{icon}"]


@pytest.mark.parametrize("version", ["as-named", "4", "5", "6"])
def test_version_latex_unaffected(version, sphinx_builder):
    """``sd_fontawesome_version`` does not change LaTeX output — for ANY value.

    The semantic style travels on the node (``icon_style``), so the
    ``fontawesome5`` LaTeX rendering is identical regardless of the HTML
    class scheme — including ``"4"``, whose HTML classes collapse all styles
    to ``fa``.
    """
    builder = sphinx_builder(
        buildername="latex",
        conf_kwargs={
            "extensions": ["sphinx_design"],
            "sd_fontawesome_latex": "fontawesome5",
            "sd_fontawesome_version": version,
        },
    )
    builder.src_path.joinpath("index.rst").write_text(
        "Title\n=====\n\nIcons :fas:`rocket`, :fab:`github`, :far:`bell`.\n",
        encoding="utf8",
    )
    builder.build(assert_pass=False)
    tex = _latex_tex(builder)
    assert "\\usepackage{fontawesome5}" in tex
    assert "\\faIcon{rocket}" in tex
    assert "\\faIcon{github}" in tex
    assert "\\faIcon[regular]{bell}" in tex
    assert "not included in LaTeX output" not in builder.warnings
