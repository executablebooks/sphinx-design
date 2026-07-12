# Brief 19: New component — `aside` (floated side-box)

**Type**: new component | **Size**: small-medium | **Closes**: #97. **CSS-only.**

## Concept

A floated box that main text wraps around — for asides/pull-outs/margin
notes (#97). Complements (not replaces) admonitions: admonitions are block
interruptions; asides float beside the flow.

## Syntax

```rst
.. aside:: Optional title
   :align: right
   :width: 33%

   Aside content.
```

Options:

- `align`: `left | right` (default `right`) — `make_choice`.
- `width`: `25% | 33% | 50%` (default `33%`) — `make_choice`; maps to
  classes `sd-aside-w-{25,33,50}` (33 needs a new width utility or a
  dedicated rule; do NOT generate inline styles).
- `margin` (existing `margin_option`), `class`, `class-title`, `class-body`.

## Implementation

1. `sphinx_design/aside.py`: `AsideDirective(SdDirective)` producing
   `create_component("aside", ["sd-aside", f"sd-aside-{align}",
   f"sd-aside-w-{width}", ...])` with optional rubric title
   (`sd-aside-title`, via `inline_text` — same pattern as dropdown title,
   `sphinx_design/dropdown.py:123-130`) + nested-parsed body. Support
   `:name:` via `add_name`.
2. Render as `<aside>` not `<div>` for semantics: either register a small
   custom node with html visitors (like `dropdown_main`,
   `dropdown.py:28-44`) or — simpler — keep `nodes.container` and accept
   `div` (decide; `<aside>` preferred, it's ~15 lines following the
   dropdown_main precedent, transform html-only).
3. SCSS `style/_aside.scss` + `@use` in `index.scss`:
   - float left/right with appropriate `margin-inline`, width classes;
   - card-like surface (reuse card border/background variables from
     `style/_cards.scss` / `_variables.scss`) so it matches themes;
   - **below the `md` breakpoint: `float: none; width: 100%`** (full-width
     block) — reuse grid breakpoint variables;
   - `clear` utility note: document `.sd-clearfix`? Add
     `.sd-clear-both { clear: both !important; }` to `_display.scss` so
     authors can stop wrap explicitly.
4. Non-HTML: plain container + rubric — acceptable degradation (LaTeX:
   sequential box via brief 21's approach later; do not block on it).

## Docs

Section in a new `docs/asides.md` or within an existing page (decide;
prefer own page + toctree entry): overwrapping example, alignment, widths,
responsive behaviour, the clear utility, and "when to use aside vs
admonition vs card". rst + myst snippets.

## Tests

- Doctree regressions (rst + myst): titled/untitled, both alignments, width
  variants, `:name:` referencing.
- Post-HTML regression locking element name + classes.
- Docs build visual check on furo/pydata; confirm no overlap disasters with
  right-hand local toc themes (pydata) — if the right float collides with
  pydata's in-page toc column at narrow widths, cap aside width or note it
  in docs.

## Acceptance criteria

- #97 use case reproducible from docs example; responsive collapse works;
  CSS committed; zero JS.
