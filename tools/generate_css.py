#!/usr/bin/env python3
"""Generate the compiled sphinx-design stylesheet.

This replaces the old Sass toolchain. The mechanical utility families that used
to be produced by ``@each``/``@for`` loops (spacing, sizing, borders, grid
columns/breakpoints, semantic colours, ...) are generated here from the
declarative data in ``style/design.toml``. The hand-authored component CSS lives
in ``style/*.css`` and is concatenated in around the generated blocks. The whole
thing is passed through a small deterministic minifier and written to
``sphinx_design/static/sphinx-design.min.css`` (the served filename is public
API and must not change).

The script uses only the Python standard library (``tomllib`` is stdlib on
3.11+), so it needs no third-party build dependency and can run inside the
pre-commit ``css`` hook.

Usage::

    python tools/generate_css.py            # (re)write the compiled artifact
    python tools/generate_css.py --check    # fail (exit 1) if the artifact is stale
    python tools/generate_css.py --stdout   # print the artifact instead of writing
"""

from __future__ import annotations

import argparse
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
import re
import sys
import tomllib

# Repository layout -----------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLE_DIR = REPO_ROOT / "style"
DATA_FILE = STYLE_DIR / "design.toml"
OUTPUT_FILE = REPO_ROOT / "sphinx_design" / "static" / "sphinx-design.min.css"

# Order in which hand-authored component files and generated utility blocks are
# concatenated. Mirrors the old ``style/index.scss`` import order so the cascade
# is preserved. Entries are either a filename (read verbatim from ``style/``) or
# a ``("gen", name)`` marker resolved to a generator function below.
ASSEMBLY: list[str | tuple[str, str]] = [
    ("gen", "color_variants"),
    "colors.css",
    ("gen", "spacing_padding"),
    "spacing.css",
    ("gen", "spacing_margin"),
    ("gen", "sizing"),
    "display.css",
    ("gen", "display_media"),
    "text.css",
    ("gen", "font_sizes"),
    ("gen", "borders"),
    "borders.css",
    "animations.css",
    "badge.css",
    "button.css",
    ("gen", "buttons"),
    "icons.css",
    ("gen", "avatars"),
    "cards.css",
    ("gen", "card_cols"),
    "grids.css",
    ("gen", "grids"),
    "dropdown.css",
    "tabs.css",
    "overrides.css",
    ("gen", "root_variables"),
]


# Value formatting helpers ----------------------------------------------------


def strip_leading_zero(value: str) -> str:
    """Drop a redundant leading ``0`` from a decimal (``0.25rem`` -> ``.25rem``).

    Mirrors the number compression Sass applied to ordinary property values.
    Custom-property values keep their leading zero, so this is only used for the
    padding/margin utilities.
    """
    if value.startswith("0.") and len(value) > 2 and value[2].isdigit():
        return value[1:]
    return value


def fmt_percent(numerator: int, denominator: int) -> str:
    """Format ``numerator / denominator`` as a percentage string.

    Rounds to 10 decimal places (matching Sass's ``math.div`` output) and strips
    trailing zeros, e.g. ``fmt_percent(100, 3) == "33.3333333333%"`` and
    ``fmt_percent(100, 4) == "25%"``.
    """
    quotient = (Decimal(numerator) / Decimal(denominator)).quantize(
        Decimal("1.0000000000"), rounding=ROUND_HALF_UP
    )
    text = format(quotient, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return f"{text}%"


# Generated utility families --------------------------------------------------


def gen_color_variants(data: dict) -> str:
    """``.sd-bg-*`` / ``.sd-text-*`` / ``.sd-outline-*`` (+ button/link states)."""
    colors = [c["name"] for c in data["colors"]]
    lines: list[str] = []
    for c in colors:
        lines += [
            f".sd-bg-{c} {{background-color:var(--sd-color-{c}) !important}}",
            f".sd-bg-text-{c} {{color:var(--sd-color-{c}-text) !important}}",
            f"button.sd-bg-{c}:focus,button.sd-bg-{c}:hover "
            f"{{background-color:var(--sd-color-{c}-highlight) !important}}",
            f"button.sd-bg-{c}:focus-visible "
            f"{{outline-color:var(--sd-color-{c}-highlight) !important}}",
            f"a.sd-bg-{c}:focus,a.sd-bg-{c}:hover "
            f"{{background-color:var(--sd-color-{c}-highlight) !important}}",
            f"a.sd-bg-{c}:focus-visible "
            f"{{outline-color:var(--sd-color-{c}-highlight) !important}}",
        ]
    for c in colors:
        lines += [
            f".sd-text-{c},.sd-text-{c}>p {{color:var(--sd-color-{c}) !important}}",
            f"a.sd-text-{c}:focus,a.sd-text-{c}:hover "
            f"{{color:var(--sd-color-{c}-highlight) !important}}",
        ]
    for c in colors:
        lines += [
            f".sd-outline-{c} {{border-color:var(--sd-color-{c}) !important;"
            f"border-style:solid !important;border-width:1px !important}}",
            f"a.sd-outline-{c}:focus,a.sd-outline-{c}:hover "
            f"{{border-color:var(--sd-color-{c}-highlight) !important}}",
            f"a.sd-outline-{c}:focus-visible "
            f"{{outline-color:var(--sd-color-{c}-highlight) !important}}",
        ]
    return "\n".join(lines)


def _spacing_block(data: dict, prop: str, abbrev: str) -> str:
    lines: list[str] = []
    for idx, raw in enumerate(data["spacings"]):
        value = strip_leading_zero(raw)
        lines += [
            f".sd-{abbrev}-{idx} {{{prop}:{value} !important}}",
            f".sd-{abbrev}t-{idx},.sd-{abbrev}y-{idx} "
            f"{{{prop}-top:{value} !important}}",
            f".sd-{abbrev}r-{idx},.sd-{abbrev}x-{idx} "
            f"{{{prop}-right:{value} !important}}",
            f".sd-{abbrev}b-{idx},.sd-{abbrev}y-{idx} "
            f"{{{prop}-bottom:{value} !important}}",
            f".sd-{abbrev}l-{idx},.sd-{abbrev}x-{idx} "
            f"{{{prop}-left:{value} !important}}",
        ]
    return "\n".join(lines)


def gen_spacing_padding(data: dict) -> str:
    """``.sd-p-*`` padding utilities."""
    return _spacing_block(data, "padding", "p")


def gen_spacing_margin(data: dict) -> str:
    """``.sd-m-*`` margin utilities (the ``auto`` variants are hand-authored)."""
    return _spacing_block(data, "margin", "m")


def gen_sizing(data: dict) -> str:
    """``.sd-w-*`` / ``.sd-h-*`` width and height utilities."""
    lines: list[str] = []
    for prop, abbrev in (("width", "w"), ("height", "h")):
        for size, length in data["sizes"].items():
            lines.append(f".sd-{abbrev}-{size} {{{prop}:{length} !important}}")
    return "\n".join(lines)


def gen_display_media(data: dict) -> str:
    """Responsive ``.sd-d-<breakpoint>-*`` display utilities."""
    blocks: list[str] = []
    for bp in data["breakpoints"]:
        cat = bp["name"]
        inner = "".join(
            [
                f".sd-d-{cat}-none{{display:none !important}}",
                f".sd-d-{cat}-inline{{display:inline !important}}",
                f".sd-d-{cat}-inline-block{{display:inline-block !important}}",
                f".sd-d-{cat}-block{{display:block !important}}",
                f".sd-d-{cat}-grid{{display:grid !important}}",
                f".sd-d-{cat}-flex{{display:flex !important}}",
                f".sd-d-{cat}-inline-flex{{display:inline-flex !important}}",
            ]
        )
        blocks.append(f"@media (min-width: {bp['min']}) {{{inner}}}")
    return "\n".join(blocks)


def gen_font_sizes(data: dict) -> str:
    """Responsive ``.sd-fs-*`` font-size utilities."""
    lines: list[str] = []
    for idx, value in data["font_sizes"].items():
        lines.append(
            f".sd-fs-{idx},.sd-fs-{idx}>p "
            f"{{font-size:{value} !important;line-height:unset !important}}"
        )
    return "\n".join(lines)


def gen_borders(data: dict) -> str:
    """``.sd-border-*`` and ``.sd-rounded-*`` utilities."""
    lines: list[str] = []
    for name, value in data["borders"].items():
        lines += [
            f".sd-border-{name} {{border:{value} solid !important}}",
            f".sd-border-top-{name} {{border-top:{value} solid !important}}",
            f".sd-border-bottom-{name} {{border-bottom:{value} solid !important}}",
            f".sd-border-right-{name} {{border-right:{value} solid !important}}",
            f".sd-border-left-{name} {{border-left:{value} solid !important}}",
        ]
    for name, value in data["rounded"].items():
        lines.append(f".sd-rounded-{name} {{border-radius:{value} !important}}")
    return "\n".join(lines)


def gen_buttons(data: dict) -> str:
    """Semantic ``.sd-btn-*`` / ``.sd-btn-outline-*`` colour families."""
    lines: list[str] = []
    for color in (c["name"] for c in data["colors"]):
        lines += [
            f".sd-btn-{color},.sd-btn-outline-{color}:hover,"
            f".sd-btn-outline-{color}:focus "
            f"{{color:var(--sd-color-{color}-text) !important;"
            f"background-color:var(--sd-color-{color}) !important;"
            f"border-color:var(--sd-color-{color}) !important;"
            f"border-width:1px !important;border-style:solid !important}}",
            f".sd-btn-{color}:hover,.sd-btn-{color}:focus "
            f"{{color:var(--sd-color-{color}-text) !important;"
            f"background-color:var(--sd-color-{color}-highlight) !important;"
            f"border-color:var(--sd-color-{color}-highlight) !important;"
            f"border-width:1px !important;border-style:solid !important}}",
            f".sd-btn-outline-{color} "
            f"{{color:var(--sd-color-{color}) !important;"
            f"border-color:var(--sd-color-{color}) !important;"
            f"border-width:1px !important;border-style:solid !important}}",
            f".sd-btn-{color}:focus-visible "
            f"{{outline-color:var(--sd-color-{color}) !important}}",
            f".sd-btn-{color}:focus-visible::after "
            f"{{outline-color:var(--sd-color-{color}) !important}}",
        ]
    return "\n".join(lines)


def gen_avatars(data: dict) -> str:
    """``.sd-avatar-*`` sizing utilities."""
    lines: list[str] = []
    for size, value in data["avatar_sizes"].items():
        lines.append(
            f".sd-avatar-{size} {{border-radius:50%;object-fit:cover;"
            f"object-position:center;width:{value};height:{value}}}"
        )
    return "\n".join(lines)


def gen_card_cols(data: dict) -> str:
    """``.sd-card-cols-<n>`` carousel card widths."""
    # slightly under 100% so the (i+1)th card peeks in, hinting at more.
    return "\n".join(
        f".sd-card-cols-{i}>.sd-card {{width:{fmt_percent(90, i)}}}"
        for i in range(1, data["columns"] + 1)
    )


def gen_grids(data: dict) -> str:
    """Responsive grid: containers, row-cols, cols and gutters."""
    breakpoints = data["breakpoints"]
    columns = data["columns"]
    spacings = data["spacings"]
    names = [bp["name"] for bp in breakpoints]
    lines: list[str] = []

    # responsive container max-widths (each breakpoint also caps the smaller ones)
    for k, bp in enumerate(breakpoints):
        parts = [f".sd-container-{names[j]}" for j in range(k, -1, -1)]
        parts.append(".sd-container")
        selector = ",".join(parts)
        lines.append(
            f"@media (min-width: {bp['min']}) "
            f"{{{selector}{{max-width:{bp['container_max']}}}}}"
        )

    # base row-cols-<n>
    lines.extend(
        f".sd-row-cols-{i}>* {{flex:0 0 auto;width:{fmt_percent(100, i)}}}"
        for i in range(1, columns + 1)
    )

    # responsive col-<breakpoint> and row-cols-<breakpoint>-<n>
    for bp in breakpoints:
        cat = bp["name"]
        inner = [
            f".sd-col-{cat}{{flex:1 0 0%}}",
            f".sd-row-cols-{cat}-auto{{flex:1 0 auto;width:100%}}",
        ]
        inner.extend(
            f".sd-row-cols-{cat}-{i}>*{{flex:0 0 auto;width:{fmt_percent(100, i)}}}"
            for i in range(1, columns + 1)
        )
        lines.append(f"@media (min-width: {bp['min']}) {{{''.join(inner)}}}")

    # base col-<n>
    lines.extend(
        f".sd-col-{i} {{flex:0 0 auto;width:{fmt_percent(100 * i, columns)}}}"
        for i in range(1, columns + 1)
    )

    # base gutters
    for idx, value in enumerate(spacings):
        lines += [
            f".sd-g-{idx},.sd-gy-{idx} {{--sd-gutter-y: {value}}}",
            f".sd-g-{idx},.sd-gx-{idx} {{--sd-gutter-x: {value}}}",
        ]

    # responsive col-<breakpoint>-<n> and gutters
    for bp in breakpoints:
        cat = bp["name"]
        inner = [f".sd-col-{cat}-auto{{flex:0 0 auto;width:auto}}"]
        inner.extend(
            f".sd-col-{cat}-{i}{{flex:0 0 auto;width:{fmt_percent(100 * i, columns)}}}"
            for i in range(1, columns + 1)
        )
        for idx, value in enumerate(spacings):
            inner += [
                f".sd-g-{cat}-{idx},.sd-gy-{cat}-{idx}{{--sd-gutter-y: {value}}}",
                f".sd-g-{cat}-{idx},.sd-gx-{cat}-{idx}{{--sd-gutter-x: {value}}}",
            ]
        lines.append(f"@media (min-width: {bp['min']}) {{{''.join(inner)}}}")

    return "\n".join(lines)


def gen_root_variables(data: dict) -> str:
    """The ``:root`` custom-property block (colours + fixed design tokens)."""
    decls: list[str] = []
    colors = data["colors"]
    decls.extend(f"--sd-color-{c['name']}: {c['value']};" for c in colors)
    for c in colors:
        name = c["name"]
        # static fallback first (byte-identical to the old baked value), then the
        # runtime color-mix() so user overrides of --sd-color-<name> now flow
        # through to the hover/focus shade. Engines without color-mix() ignore
        # the second declaration and keep the fallback.
        decls.append(f"--sd-color-{name}-highlight: {c['highlight']};")
        decls.append(
            f"--sd-color-{name}-highlight: "
            f"color-mix(in srgb, black 15%, var(--sd-color-{name}));"
        )
    decls.extend(
        f"--sd-color-{c['name']}-bg: "
        f"rgba({c['rgb'][0]}, {c['rgb'][1]}, {c['rgb'][2]}, 0.2);"
        for c in colors
    )
    decls.extend(f"--sd-color-{c['name']}-text: {c['text']};" for c in colors)
    decls.extend(f"{name}: {value};" for name, value in data["root_fixed"])
    return ":root {\n  " + "\n  ".join(decls) + "\n}"


GENERATORS = {
    "color_variants": gen_color_variants,
    "spacing_padding": gen_spacing_padding,
    "spacing_margin": gen_spacing_margin,
    "sizing": gen_sizing,
    "display_media": gen_display_media,
    "font_sizes": gen_font_sizes,
    "borders": gen_borders,
    "buttons": gen_buttons,
    "avatars": gen_avatars,
    "card_cols": gen_card_cols,
    "grids": gen_grids,
    "root_variables": gen_root_variables,
}


# Assembly + minification -----------------------------------------------------


def _strip_combinator_spaces(css: str) -> str:
    """Remove spaces around ``>``/``~``/``+`` selector combinators only.

    Combinators are stripped at parenthesis-depth 0 (selector context); spaces
    inside ``(...)`` -- notably the ``+``/``-`` operators of ``calc()`` -- are
    left untouched so values stay valid.
    """
    out: list[str] = []
    depth = 0
    for i, char in enumerate(css):
        if char == "(":
            depth += 1
            out.append(char)
        elif char == ")":
            depth -= 1
            out.append(char)
        elif char == " " and depth == 0:
            prev = out[-1] if out else ""
            nxt = css[i + 1] if i + 1 < len(css) else ""
            if prev in ">~+" or nxt in ">~+":
                continue  # this space hugs a combinator; drop it
            out.append(char)
        else:
            out.append(char)
    return "".join(out)


def minify(css: str) -> str:
    """Deterministically strip comments and insignificant whitespace.

    Intentionally simple (no external minifier): comments go, whitespace runs
    collapse, spaces around structural characters (and after ``:``) are removed,
    and selector combinators are tightened. Spaces around ``+``/``-`` inside
    ``calc()`` are preserved so values stay valid.
    """
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.DOTALL)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    css = _strip_combinator_spaces(css)
    css = css.replace(";}", "}")
    return css.strip()


def build_css(root: Path = REPO_ROOT) -> str:
    """Build the full minified stylesheet from the data file and hand CSS."""
    style_dir = root / "style"
    with (style_dir / "design.toml").open("rb") as handle:
        data = tomllib.load(handle)

    parts: list[str] = []
    for entry in ASSEMBLY:
        if isinstance(entry, tuple):
            parts.append(GENERATORS[entry[1]](data))
        else:
            parts.append((style_dir / entry).read_text(encoding="utf8"))
    return minify("\n".join(parts)) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the committed artifact is out of date",
    )
    group.add_argument(
        "--stdout",
        action="store_true",
        help="write the generated CSS to stdout instead of the artifact",
    )
    args = parser.parse_args(argv)

    css = build_css()

    if args.stdout:
        sys.stdout.write(css)
        return 0

    if args.check:
        current = OUTPUT_FILE.read_text(encoding="utf8") if OUTPUT_FILE.exists() else ""
        if current != css:
            sys.stderr.write(
                f"{OUTPUT_FILE.relative_to(REPO_ROOT)} is out of date; "
                "run `python tools/generate_css.py`\n"
            )
            return 1
        return 0

    OUTPUT_FILE.write_text(css, encoding="utf8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
