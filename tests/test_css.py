"""Tests for the compiled CSS artifact and its generator.

The stylesheet is generated from ``style/design.toml`` + ``style/*.css`` by
``tools/generate_css.py`` (see AGENTS.md). These tests guard that:

* the committed artifact is up to date with the sources (the same check the
  pre-commit ``css`` hook enforces, but visible in the normal test run); and
* the migration from Sass stayed rule-set equivalent -- an *opt-in* check,
  gated on ``SD_CSS_EQUIV_BASE`` so it never breaks CI on a deliberate style
  change.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tomllib

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = REPO_ROOT / "tools"
ARTIFACT = REPO_ROOT / "sphinx_design" / "static" / "sphinx-design.min.css"

sys.path.insert(0, str(TOOLS_DIR))

import generate_css  # noqa: E402


def test_artifact_is_up_to_date():
    """The committed CSS must match a fresh generator run (staleness guard).

    If this fails, run ``python tools/generate_css.py`` and commit the result.
    """
    expected = generate_css.build_css(REPO_ROOT)
    actual = ARTIFACT.read_text(encoding="utf8")
    assert actual == expected, (
        "sphinx_design/static/sphinx-design.min.css is out of date; "
        "run `python tools/generate_css.py` and commit the result."
    )


def test_highlight_uses_runtime_color_mix():
    """User overrides of ``--sd-color-<name>`` must reach the hover/focus shade.

    The highlight custom property is emitted as a static fallback followed by a
    ``color-mix()`` referencing ``var(--sd-color-<name>)``, so overriding the
    base colour re-derives the shade at runtime (a behaviour improvement over
    the old build-time ``mix()``). Assert both declarations are present.
    """
    css = ARTIFACT.read_text(encoding="utf8")
    fallback = "--sd-color-primary-highlight:#0060a0"  # static fallback
    color_mix = (
        "--sd-color-primary-highlight:color-mix(in srgb,black 15%,"
        "var(--sd-color-primary))"
    )
    assert fallback in css
    assert color_mix in css
    # the fallback must precede color-mix(): browsers without color-mix()
    # ignore the second declaration and keep the static shade
    assert css.index(fallback) < css.index(color_mix)


def _parse_errors(css: str) -> list:
    """All tinycss2 error nodes in a stylesheet, including inside rule bodies."""
    tinycss2 = pytest.importorskip("tinycss2")
    errors = []

    def walk_body(content):
        errors.extend(
            decl
            for decl in tinycss2.parse_declaration_list(
                content, skip_whitespace=True, skip_comments=True
            )
            if decl.type == "error"
        )

    for node in tinycss2.parse_stylesheet(
        css, skip_whitespace=True, skip_comments=True
    ):
        if node.type == "error":
            errors.append(node)
        elif node.type == "qualified-rule":
            walk_body(node.content)
        elif node.type == "at-rule" and node.content is not None:
            for nested in tinycss2.parse_rule_list(
                node.content, skip_whitespace=True, skip_comments=True
            ):
                if nested.type == "error":
                    errors.append(nested)
                elif nested.type == "qualified-rule":
                    walk_body(nested.content)
    return errors


def test_minify_output_parses_cleanly():
    """Minified (rcssmin) output of tricky-but-valid CSS must stay valid.

    Covers the hazards the previous bespoke minifier had to special-case:
    combinators inside attribute-selector strings, calc() operators, quoted
    content values.
    """
    source = (
        '[title="a > b"] { color: red; }\n'
        ".x { width: calc(1px + 2px); }\n"
        '.y::after { content: "a > b"; }\n'
        ".a > .b ~ .c { margin: 0.25rem !important; }\n"
    )
    minified = generate_css.minify(source)
    assert _parse_errors(minified) == []
    # string contents survive verbatim (never tightened like real combinators)
    assert '"a > b"' in minified
    assert "calc(1px + 2px)" in minified


def test_artifact_parses_cleanly():
    """The committed artifact must contain zero CSS parse errors (permanent)."""
    assert _parse_errors(ARTIFACT.read_text(encoding="utf8")) == []


def _flat_selectors(css: str) -> list[str]:
    """Every rule selector in the artifact, flattened through @media blocks."""
    tinycss2 = pytest.importorskip("tinycss2")
    selectors = []
    for node in tinycss2.parse_stylesheet(
        css, skip_whitespace=True, skip_comments=True
    ):
        if node.type == "qualified-rule":
            selectors.append(tinycss2.serialize(node.prelude).strip())
        elif node.type == "at-rule" and node.content is not None:
            if "keyframes" in (node.lower_at_keyword or ""):
                continue
            selectors.extend(
                tinycss2.serialize(nested.prelude).strip()
                for nested in tinycss2.parse_rule_list(
                    node.content, skip_whitespace=True, skip_comments=True
                )
                if nested.type == "qualified-rule"
            )
    return selectors


def test_generated_family_counts_match_design_toml():
    """Structural smoke: generated-rule counts must follow from design.toml.

    Each expected count is spelled out from the data file so a drifting
    generator (dropped loop, extra emission) fails with readable arithmetic.
    """
    with (REPO_ROOT / "style" / "design.toml").open("rb") as handle:
        data = tomllib.load(handle)
    columns = data["columns"]  # 12
    n_bp = len(data["breakpoints"])  # 4 (sm md lg xl)
    n_colors = len(data["colors"])  # 11
    n_spacings = len(data["spacings"])  # 6 (indexes 0..5)

    selectors = _flat_selectors(ARTIFACT.read_text(encoding="utf8"))

    def count(pattern: str) -> int:
        regex = re.compile(pattern)
        return sum(1 for sel in selectors if regex.fullmatch(sel))

    # grid: one numbered row-cols/col rule per column, at base + each breakpoint
    assert count(r"\.sd-row-cols(-[a-z]+)?-\d+>\*") == columns * (1 + n_bp)
    assert count(r"\.sd-col(-[a-z]+)?-\d+") == columns * (1 + n_bp)
    # col-auto: base + one per breakpoint
    assert count(r"\.sd-col(-[a-z]+)?-auto") == 1 + n_bp
    # container caps: one @media rule per breakpoint
    assert count(r"(\.sd-container[-a-z]*,)+\.sd-container") == n_bp
    # colour families: one bg/text/outline/btn-outline rule per palette colour
    # (matched by exact palette name: the hand-authored .sd-bg-transparent /
    # .sd-outline-transparent utility rules are deliberately not counted)
    palette = [color["name"] for color in data["colors"]]
    for template in (".sd-bg-{}", ".sd-outline-{}", ".sd-btn-outline-{}"):
        family = {template.format(name) for name in palette}
        assert sum(sel in family for sel in selectors) == n_colors, template
    assert count(r"\.sd-text-[a-z]+,\.sd-text-[a-z]+>p") == n_colors
    # steps: one marker-colour variant rule per palette colour
    assert count(r"\.sd-steps-[a-z]+") == n_colors
    # spacing scale: one all-sides padding/margin rule per step
    assert count(r"\.sd-p-\d+") == n_spacings
    assert count(r"\.sd-m-\d+") == n_spacings
    # per-axis spacing pairs: 4 paired rules (t/y, r/x, b/y, l/x) per step
    assert count(r"\.sd-p[trbl]-\d+,\.sd-p[xy]-\d+") == 4 * n_spacings
    assert count(r"\.sd-m[trbl]-\d+,\.sd-m[xy]-\d+") == 4 * n_spacings
    # simple lookup families: one rule per table entry
    assert count(r"\.sd-avatar-[a-z]+") == len(data["avatar_sizes"])
    assert count(r"\.sd-fs-\d+,\.sd-fs-\d+>p") == len(data["font_sizes"])
    assert count(r"\.sd-rounded-[a-z0-9]+") == len(data["rounded"])
    # w/h sizing: width + height rule per size entry
    assert count(r"\.sd-[wh]-[a-z0-9]+") == 2 * len(data["sizes"])
    # carousel: one card-width rule per column count
    assert count(r"\.sd-card-cols-\d+>\.sd-card") == columns


@pytest.fixture
def style_copy(tmp_path):
    """A throwaway copy of the repo's style/ sources (never mutate the real one)."""
    shutil.copytree(REPO_ROOT / "style", tmp_path / "style")
    return tmp_path


def test_assembly_guard_unreferenced_file(style_copy):
    """A style/*.css file missing from ASSEMBLY must fail the build loudly."""
    (style_copy / "style" / "orphan.css").write_text(".x{color:red}", encoding="utf8")
    with pytest.raises(ValueError, match=r"orphan\.css.*not referenced in ASSEMBLY"):
        generate_css.build_css(style_copy)


def test_assembly_guard_missing_file(style_copy):
    """An ASSEMBLY filename with no file on disk must fail the build loudly."""
    (style_copy / "style" / "cards.css").unlink()
    with pytest.raises(ValueError, match=r"cards\.css which does not exist"):
        generate_css.build_css(style_copy)


def test_assembly_guard_unknown_generator(style_copy, monkeypatch):
    """A ("gen", name) entry without a generator function must fail loudly."""
    monkeypatch.setattr(
        generate_css, "ASSEMBLY", [*generate_css.ASSEMBLY, ("gen", "no_such_family")]
    )
    with pytest.raises(ValueError, match=r"'no_such_family' which has no function"):
        generate_css.build_css(style_copy)


def test_assembly_guard_orphaned_generator(style_copy, monkeypatch):
    """A generator function never referenced by ASSEMBLY must fail loudly."""
    patched = dict(generate_css.GENERATORS)
    patched["orphan_family"] = lambda data: ""
    monkeypatch.setattr(generate_css, "GENERATORS", patched)
    with pytest.raises(ValueError, match=r"'orphan_family'.*never referenced"):
        generate_css.build_css(style_copy)


def _valid_data() -> dict:
    with (REPO_ROOT / "style" / "design.toml").open("rb") as handle:
        return tomllib.load(handle)


def test_design_schema_accepts_the_real_file():
    generate_css._validate_data(_valid_data())


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d.pop("columns"), r"missing required key 'columns'"),
        (lambda d: d.update(columns="12"), r"'columns' must be a positive integer"),
        (lambda d: d.update(bogus=1), r"unknown top-level key 'bogus'"),
        (
            lambda d: d["colors"][0].update(extra="x"),
            r"unknown key 'extra' in 'colors\[0\]'",
        ),
        (
            lambda d: d["breakpoints"][0].pop("min"),
            r"missing key 'min' in 'breakpoints\[0\]'",
        ),
        (
            lambda d: d["colors"][1].update(rgb=[1, 2]),
            r"'colors\[1\]\.rgb' must be a list of three integers",
        ),
        (lambda d: d.update(sizes={"25": 25}), r"'sizes' must be a table of string"),
    ],
)
def test_design_schema_rejects(mutate, message):
    """Schema failures must name the offending key."""
    data = _valid_data()
    mutate(data)
    with pytest.raises(ValueError, match=message):
        generate_css._validate_data(data)


@pytest.mark.parametrize(
    ("selector", "expected"),
    [
        # :not() contributes only its argument's specificity (reviewer example)
        ("details.sd-dropdown:not([open]).sd-card", (0, 3, 1)),
        (".sd-tab-set>input:not(:checked)+label", (0, 2, 2)),
        # :where() is always zero; :is() takes its most specific argument
        (":where(.a,.b#x) .c", (0, 1, 0)),
        (":is(.a,#b) .c", (1, 1, 0)),
        # other functional pseudo-classes still count as one pseudo-class
        (".a:nth-child(2)", (0, 2, 0)),
    ],
)
def test_checker_specificity_model(selector, expected):
    """``:not()``/``:is()`` are argument-only, ``:where()`` zero (per spec)."""
    pytest.importorskip("tinycss2")
    import check_css_equivalence  # noqa: PLC0415

    assert check_css_equivalence._specificity_of_simple(selector) == expected


def test_checker_catches_cross_context_inversion():
    """The order pass must flag flips across co-applying @media contexts."""
    pytest.importorskip("tinycss2")
    import check_css_equivalence  # noqa: PLC0415

    base = "@media (min-width:1px){.a{color:blue}}\n.a{color:red}"
    flipped = ".a{color:red}\n@media (min-width:1px){.a{color:blue}}"
    ok, report = check_css_equivalence.check(base, flipped, "base", "new")
    assert not ok
    assert "SOURCE-ORDER INVERSIONS" in report
    # and the unflipped pair passes
    ok_same, _ = check_css_equivalence.check(base, base, "base", "new")
    assert ok_same


@pytest.mark.skipif(
    not os.environ.get("SD_CSS_EQUIV_BASE"),
    reason="set SD_CSS_EQUIV_BASE=<git-ref> to run the CSS rule-set equivalence check",
)
def test_css_rule_set_equivalence():
    """Opt-in: the artifact is rule-set equivalent to a base git ref.

    Only the enumerated intentional differences (dropped vendor prefixes and the
    added ``color-mix()`` highlights) are tolerated. Intended to run against the
    pre-migration commit; kept out of the default suite because it necessarily
    breaks on the first deliberate style change.
    """
    pytest.importorskip("tinycss2")  # skip cleanly if the testing extra is absent

    # imported lazily so the module (and its tinycss2 dependency) is only needed
    # when this opt-in check actually runs
    import check_css_equivalence  # noqa: PLC0415

    base_ref = os.environ["SD_CSS_EQUIV_BASE"]
    base_css = subprocess.run(
        ["git", "show", f"{base_ref}:sphinx_design/static/sphinx-design.min.css"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    new_css = ARTIFACT.read_text(encoding="utf8")

    ok, report = check_css_equivalence.check(
        base_css, new_css, base_ref, "committed artifact"
    )
    assert ok, "\n" + report
