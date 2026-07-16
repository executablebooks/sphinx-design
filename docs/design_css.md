# Design: the CSS pipeline

This page records why the stylesheet build is shaped the way it is, and the
invariants that keep it safe to change. For day-to-day commands see the
repository's `AGENTS.md`.

## Context

Until v0.7 the stylesheet was authored in SCSS and compiled with dart-sass via
npm — the only reason Node existed in the toolchain. An audit showed the Sass
usage was shallow: 26 mechanical loops (spacing, grid columns × breakpoints,
colour variants, borders, sizing, display, text utilities), two build-time
colour computations (a contrast picker and a 15% darkening for hover shades),
and concatenation + minification. There were no mixins and no deep nesting.

That shape had real costs: a Node dependency for a Python project (and the
perennial sass version-pin chore); hover shades baked at compile time, so user
overrides of `--sd-color-*` never reached them; and a "supported browsers"
list frozen in 2021.

## Decision

The stylesheet is now plain CSS in two tiers:

- **Hand-authored component CSS** — `style/*.css`, one file per component
  area, written with expanded selectors.
- **Generated utility CSS** — emitted by `tools/generate_css.py` from
  declarative tokens in `style/design.toml` (palette with precomputed contrast
  text colours, spacing scale, breakpoints, column count). A utility variant
  is a data entry, not a loop.

The generator concatenates both tiers in an explicit order, minifies with
[`rcssmin`](https://pypi.org/project/rcssmin/) (a mature, frozen,
pure-Python minifier — deliberately not hand-rolled), and writes the single
committed artifact `sphinx_design/static/sphinx-design.min.css`. Only the
artifact ships; the generator, tokens and sources are development-only.

Alternatives considered: keeping dart-sass (permanent Node dependency for
three shallow features); `libsass-python` (upstream libsass is deprecated by
the Sass team); shipping unminified CSS (workable, but a free 5% wire saving
was kept by using an off-the-shelf minifier).

The hover shades are now computed in the browser:
`--sd-color-*-highlight` is declared twice — a static fallback first, then
`color-mix(in srgb, black 15%, var(--sd-color-*))` — so overriding a theme
colour re-derives its hover shade at runtime, and browsers without
`color-mix()` keep the previous static value.

## The cascade is `ASSEMBLY` order

`tools/generate_css.py` assembles the stylesheet from an explicit `ASSEMBLY`
list interleaving hand-authored files and generated families. This is a
deliberate choice over globbing: **source order is the CSS cascade**, and two
rules with equal specificity resolve by position. An automatic glob would
make the cascade an accident of filenames. The cost — remembering to register
new files — is converted into a loud failure by the completeness guard below.

This is not theoretical: during the migration, two real cascade-order
inversions (grid `col-auto` vs `row-cols` utilities, and the container
max-width media caps) were caught only because the verification tooling was
made order-aware. Any future restructuring of `ASSEMBLY` should be checked
with the equivalence tool's order pass.

## Invariants and their enforcement

Every invariant below is enforced by a named guard — if a guard is removed,
its row here is no longer true.

| Invariant | Enforced by |
|---|---|
| Every `style/*.css` file is registered in `ASSEMBLY` (and vice versa, including generator functions) | `generate_css.py` fails the build on any drift, in either direction |
| `design.toml` is well-formed (keys, types, no unknown fields) | schema validation on every generator run, naming the offending key |
| The committed artifact is never stale | the `css` pre-commit hook (also triggered by generator changes) and `tests/test_css.py::test_artifact_is_up_to_date` in CI |
| The artifact always parses as valid CSS | `test_artifact_parses_cleanly` (tinycss2, zero error nodes) |
| Generated utility families exactly match the token data | `test_generated_family_counts_match_design_toml` (rule counts derived from `design.toml` arithmetic) |
| The `color-mix()` shade always follows its static fallback | `test_highlight_uses_runtime_color_mix` |
| Output is byte-deterministic (across runs, Python versions, platforms) | stdlib + frozen `rcssmin`, `Decimal` rounding, explicit ordering; `.gitattributes` pins the artifact to LF |
| Migrations/restructurings preserve rule sets *and* cascade order | `tools/check_css_equivalence.py` — opt-in via `SD_CSS_EQUIV_BASE=<git-ref>`, diffs rule sets against an allowlist and fails on source-order inversions between co-applicable rules |

## Public API

The following are stable interfaces covered by deprecation policy:

- the `--sd-*` CSS custom property names;
- the `sd-*` utility and component class names;
- the served filename `sphinx-design.min.css`.

Everything else — the generator, `design.toml`'s schema, `style/` file layout,
the checker — is internal and may change without notice.

## Browser support

Styles target **Baseline Widely Available** web features; see the policy in
[Getting started](get_started.md). Individual features may use *Baseline
Newly Available* CSS with graceful degradation (as `color-mix()` does above),
noted where they are documented.
