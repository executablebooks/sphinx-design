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
import subprocess
import sys

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
    assert "--sd-color-primary-highlight:#0060a0" in css  # static fallback
    assert (
        "--sd-color-primary-highlight:color-mix(in srgb,black 15%,"
        "var(--sd-color-primary))" in css
    )


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
