#!/usr/bin/env python3
"""Generate the compiled sphinx-design stylesheet.

This replaces the old Sass toolchain. The mechanical utility families that used
to be produced by ``@each``/``@for`` loops (spacing, sizing, borders, grid
columns/breakpoints, semantic colours, ...) are generated here from the
declarative data in ``style/design.toml``. The hand-authored component CSS lives
in ``style/*.css`` and is concatenated in around the generated blocks. The whole
thing is minified with ``rcssmin`` and written to
``sphinx_design/static/sphinx-design.min.css`` (the served filename is public
API and must not change).

Besides the stdlib (``tomllib`` is stdlib on 3.11+) the script needs only
``rcssmin`` -- a pure-Python, deterministic CSS minifier. It is a *dev-only*
dependency (the ``testing`` extras and the pre-commit ``css`` hook install it);
the runtime package ships the pre-built artifact and depends on nothing.

Both the data file and the assembly list are validated before every build:
a ``style/*.css`` file that is not referenced (or referenced but missing), an
unknown generator name, an orphaned generator function, or a malformed
``design.toml`` all fail the build loudly rather than silently dropping rules.

Usage::

    python tools/generate_css.py            # (re)write the compiled artifact
    python tools/generate_css.py --check    # fail (exit 1) if the artifact is stale
    python tools/generate_css.py --stdout   # print the artifact instead of writing
"""

from __future__ import annotations

import argparse
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
import sys
import tomllib

import rcssmin

# Repository layout -----------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent
STYLE_DIR = REPO_ROOT / "style"
DATA_FILE = STYLE_DIR / "design.toml"
OUTPUT_FILE = REPO_ROOT / "sphinx_design" / "static" / "sphinx-design.min.css"

# Order in which hand-authored component files and generated utility blocks are
# concatenated. Entries are either a filename (read verbatim from ``style/``) or
# a ``("gen", name)`` marker resolved to a generator function below.
#
# THE CASCADE IS THIS ASSEMBLY ORDER. Equal-specificity rules that set the same
# property resolve by source order (last wins), so moving an entry -- or moving
# a rule between a hand file and a generator -- can silently change rendering
# even though every rule still exists (e.g. `.sd-col-auto` vs the row-cols
# width family, or the container max-width caps vs `.sd-row > *`). The list
# mirrors the old ``style/index.scss`` import order; when reordering anything,
# verify with ``tools/check_css_equivalence.py`` (its order pass exists exactly
# for this).
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
    "containers.css",
    ("gen", "container_media"),
    "grids.css",
    ("gen", "grids"),
    "dropdown.css",
    "tabs.css",
    "steps.css",
    ("gen", "steps"),
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


def gen_container_media(data: dict) -> str:
    """Responsive ``.sd-container-*`` max-width caps.

    Emitted as its own family so the assembly can place it directly after the
    hand-authored container rule and *before* ``grids.css`` -- matching the old
    ``_grids.scss`` cascade, where these caps preceded ``.sd-row > *``
    (max-width:100%) and therefore lost to it at equal specificity.
    """
    breakpoints = data["breakpoints"]
    names = [bp["name"] for bp in breakpoints]
    lines: list[str] = []
    # each breakpoint also caps the smaller ones
    for k, bp in enumerate(breakpoints):
        parts = [f".sd-container-{names[j]}" for j in range(k, -1, -1)]
        parts.append(".sd-container")
        selector = ",".join(parts)
        lines.append(
            f"@media (min-width: {bp['min']}) "
            f"{{{selector}{{max-width:{bp['container_max']}}}}}"
        )
    return "\n".join(lines)


def gen_grids(data: dict) -> str:
    """Responsive grid: row-cols, cols and gutters."""
    breakpoints = data["breakpoints"]
    columns = data["columns"]
    spacings = data["spacings"]
    lines: list[str] = []

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

    # base col-auto -- emitted here (after the row-cols families) to match the
    # cascade position in the old _grids.scss: its width:auto must win over the
    # equal-specificity .sd-row-cols-<n>>* width, so it has to come *after* them.
    lines.append(".sd-col-auto {flex:0 0 auto;width:auto}")

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


def gen_steps(data: dict) -> str:
    """Semantic ``.sd-steps-<colour>`` step-marker colour families.

    Each variant only overrides the two custom properties the hand-authored
    ``style/steps.css`` reads for the marker (its default, when no variant class
    is present, is the ``var(..., var(--sd-color-primary))`` fallback there).
    """
    return "\n".join(
        f".sd-steps-{color} "
        f"{{--sd-steps-marker-bg:var(--sd-color-{color});"
        f"--sd-steps-marker-text:var(--sd-color-{color}-text)}}"
        for color in (c["name"] for c in data["colors"])
    )


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
    "container_media": gen_container_media,
    "grids": gen_grids,
    "steps": gen_steps,
    "root_variables": gen_root_variables,
}


# Source validation -----------------------------------------------------------


def _validate_assembly(style_dir: Path) -> None:
    """Fail loudly when ``ASSEMBLY``, ``GENERATORS`` and ``style/`` drift apart.

    A hand-authored file that exists but is not assembled would silently vanish
    from the output; the other three drift directions are outright bugs. All
    problems are collected and reported together.
    """
    on_disk = {path.name for path in style_dir.glob("*.css")}
    listed_files = {entry for entry in ASSEMBLY if isinstance(entry, str)}
    listed_gens = {entry[1] for entry in ASSEMBLY if isinstance(entry, tuple)}

    problems: list[str] = []
    problems += [
        f"style/{name} exists on disk but is not referenced in ASSEMBLY"
        for name in sorted(on_disk - listed_files)
    ]
    problems += [
        f"ASSEMBLY references style/{name} which does not exist"
        for name in sorted(listed_files - on_disk)
    ]
    problems += [
        f"ASSEMBLY references generator {name!r} which has no function in GENERATORS"
        for name in sorted(listed_gens - set(GENERATORS))
    ]
    problems += [
        f"generator {name!r} exists in GENERATORS but is never referenced in ASSEMBLY"
        for name in sorted(set(GENERATORS) - listed_gens)
    ]
    if problems:
        raise ValueError(
            "ASSEMBLY is out of sync with the style/ sources:\n  - "
            + "\n  - ".join(problems)
        )


# expected shape of design.toml: {table: (required keys, value check, description)}
_COLOR_KEYS = {"name", "value", "rgb", "text", "highlight"}
_BREAKPOINT_KEYS = {"name", "min", "container_max"}
_TOP_LEVEL_KEYS = {
    "columns",
    "spacings",
    "root_fixed",
    "breakpoints",
    "sizes",
    "borders",
    "rounded",
    "font_sizes",
    "avatar_sizes",
    "colors",
}


def _is_str_dict(value: object) -> bool:
    return isinstance(value, dict) and all(
        isinstance(k, str) and isinstance(v, str) for k, v in value.items()
    )


def _scalar_problems(data: dict) -> list[str]:
    """Problems with the scalar / flat-table top-level keys."""
    problems: list[str] = []
    if "columns" in data and not (
        isinstance(data["columns"], int) and data["columns"] > 0
    ):
        problems.append(
            f"'columns' must be a positive integer, got {data['columns']!r}"
        )
    if "spacings" in data and not (
        isinstance(data["spacings"], list)
        and all(isinstance(s, str) for s in data["spacings"])
    ):
        problems.append("'spacings' must be a list of strings")
    if "root_fixed" in data and not (
        isinstance(data["root_fixed"], list)
        and all(
            isinstance(pair, list)
            and len(pair) == 2
            and all(isinstance(p, str) for p in pair)
            for pair in data["root_fixed"]
        )
    ):
        problems.append("'root_fixed' must be a list of [name, value] string pairs")
    problems.extend(
        f"'{key}' must be a table of string values"
        for key in ("sizes", "borders", "rounded", "font_sizes", "avatar_sizes")
        if key in data and not _is_str_dict(data[key])
    )
    return problems


def _entry_problems(
    table: str, entries: list, allowed: set[str], str_keys: set[str]
) -> list[str]:
    """Problems inside an array-of-tables key (``breakpoints`` / ``colors``)."""
    problems: list[str] = []
    for i, entry in enumerate(entries):
        where = f"{table}[{i}]"
        if not isinstance(entry, dict):
            problems.append(f"'{where}' must be a table")
            continue
        problems.extend(
            f"unknown key {key!r} in '{where}'" for key in sorted(set(entry) - allowed)
        )
        problems.extend(
            f"missing key {key!r} in '{where}'" for key in sorted(allowed - set(entry))
        )
        problems.extend(
            f"'{where}.{key}' must be a string"
            for key in sorted(str_keys & set(entry))
            if not isinstance(entry[key], str)
        )
    return problems


def _rgb_problems(colors: list) -> list[str]:
    return [
        f"'colors[{i}].rgb' must be a list of three integers"
        for i, color in enumerate(colors)
        if isinstance(color, dict)
        and "rgb" in color
        and not (
            isinstance(color["rgb"], list)
            and len(color["rgb"]) == 3
            and all(isinstance(c, int) for c in color["rgb"])
        )
    ]


def _validate_data(data: dict) -> None:
    """Schema-check ``design.toml``; error messages name the offending key."""
    problems: list[str] = []
    problems.extend(
        f"unknown top-level key {key!r}" for key in sorted(set(data) - _TOP_LEVEL_KEYS)
    )
    problems.extend(
        f"missing required key {key!r}" for key in sorted(_TOP_LEVEL_KEYS - set(data))
    )
    problems.extend(_scalar_problems(data))

    if isinstance(data.get("breakpoints"), list):
        problems.extend(
            _entry_problems(
                "breakpoints", data["breakpoints"], _BREAKPOINT_KEYS, _BREAKPOINT_KEYS
            )
        )
    elif "breakpoints" in data:
        problems.append("'breakpoints' must be an array of tables")

    if isinstance(data.get("colors"), list):
        problems.extend(
            _entry_problems(
                "colors", data["colors"], _COLOR_KEYS, _COLOR_KEYS - {"rgb"}
            )
        )
        problems.extend(_rgb_problems(data["colors"]))
    elif "colors" in data:
        problems.append("'colors' must be an array of tables")

    if problems:
        raise ValueError("design.toml is invalid:\n  - " + "\n  - ".join(problems))


# Assembly + minification -----------------------------------------------------


def minify(css: str) -> str:
    """Minify with ``rcssmin`` (pure Python, deterministic, string-aware).

    ``rcssmin`` operates strictly at the whitespace/comment level: it never
    merges, reorders or rewrites rules, so the cascade proven by
    ``tools/check_css_equivalence.py`` is untouched.
    """
    return rcssmin.cssmin(css)


def build_css(root: Path = REPO_ROOT) -> str:
    """Build the full minified stylesheet from the data file and hand CSS.

    Raises :class:`ValueError` when the assembly list or the data file are
    inconsistent (see :func:`_validate_assembly` / :func:`_validate_data`).
    """
    style_dir = root / "style"
    _validate_assembly(style_dir)
    with (style_dir / "design.toml").open("rb") as handle:
        data = tomllib.load(handle)
    _validate_data(data)

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

    try:
        css = build_css()
    except ValueError as exc:
        sys.stderr.write(f"error: {exc}\n")
        return 1

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
