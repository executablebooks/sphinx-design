# Brief 16: Card header/footer as pure parse (retire `^^^`/`+++` pre-processing)

**Type**: refactor + feature (flagship syntax change) | **Size**: large
**Depends on**: brief 02 (config field). Coordinate with brief 09 (touches the same class-stamping code).

## Why

`CardDirective.split_content` (`sphinx_design/cards.py:203-226`) regex-scans
the **raw source lines** of the card body for the first `^{3,}` line
(header separator, `REGEX_HEADER`, `cards.py:28`) and the last `\+{3,}`
line (footer separator, `REGEX_FOOTER`, `cards.py:29`), slicing the
`StringList` into up to three chunks that are parsed separately
(`_create_component`, `cards.py:228-244`).

Problems:

1. **False positives**: a `+++`/`^^^` line inside nested content — a
   code-block showing Jupytext cell markers, an rST example with `^^^`
   underlines — is treated as a separator. "Last `+++` wins" mitigates, but
   any legitimate trailing `+++` in content still mis-splits.
2. **Broken source mapping**: `_create_component` has a literal
   `TODO set proper lines` (`cards.py:241`); errors inside cards point to
   wrong lines.
3. **Not parser-portable**: the syntax has no meaning outside this Python
   pre-process — MyST formatters/linters/LSPs, and any future non-Python
   (e.g. Rust) MyST implementation, cannot understand card structure. This
   is the canonical violation of the "parser-portable syntax" principle
   (briefs/README.md).

`grid-item-card` inherits all of this via `CardDirective.create_card`.

## Target syntax

```rst
.. card:: Card title

   .. card-header::

      Header *content*

   Body content.

   .. card-footer::

      Footer content
```

MyST equivalent nests fences exactly like `tab-set`/`tab-item`. Position of
sub-directives within the body is free; header/footer render in their slots
regardless (document that recommended order is header, body, footer).

## Implementation

1. **New directives** `card-header`, `card-footer`
   (`sphinx_design/cards.py`, registered in `setup_cards`): `has_content`,
   `option_spec = {"class": directives.class_option}`; each produces
   `create_component("card-header"| "card-footer", ...)` with a single
   `nested_parse` of its content. Warn (subtype `design.card`) when the
   parse parent is not a card body context — mirror the tab-item parent
   check (`sphinx_design/tabs.py:89-95`), using a marker on the temp
   container (see next point) so it works for `card` and `grid-item-card`.
2. **Rework `create_card`**: parse the *whole* content once into a temp
   container marked as card context; then partition children:
   `card-header` components → header slot (warn+merge or warn+use-first if
   multiple), `card-footer` → footer slot, everything else in order → body.
   Then assemble exactly the structure produced today
   (`cards.py:126-160`): header, body (+title from argument), footer, so
   downstream CSS/regressions are unchanged. Correct source lines come free.
3. **Legacy path**: config field (brief 02)
   `card_legacy_separators: bool = True`.
   - When `True` and the raw content matches `REGEX_HEADER`/`REGEX_FOOTER`,
     run the *old* splitter, and emit a deprecation notice once per
     document: subtype `design.card_legacy` (suppressible via
     `suppress_warnings = ["design.card_legacy"]`), message linking the
     migration guide.
   - When `False`: no raw-line scanning at all; separators parse as
     ordinary rST (a `^^^^` line becomes a section underline/transition —
     users must have migrated).
   - Using both separators **and** sub-directives in one card: warn
     (`design.card`), sub-directives win.
4. **Ergonomic option** (decide during implementation, default to yes):
   `:header:` / `:footer:` string options on `card`/`grid-item-card` for
   one-liner slots, parsed with `inline_text` (same treatment as the title
   argument, `cards.py:138-152`). Mutually exclusive with the corresponding
   sub-directive (warn, sub-directive wins).
5. **Migration guide**: `docs/` page: mapping table (separator example →
   sub-directive example, rst + myst), the config flag, the timeline
   (deprecated now → default-off at 1.0 → removed at 2.0). Update every
   card/grid snippet in `docs/snippets/{rst,myst}/card-*` and
   `grid-item-card` docs to the new syntax (this also feeds the snippet
   regression suite — regenerate and review).
6. Keep `split_content` + regexes intact (used by the legacy path) but move
   them behind a clearly-marked "legacy" section with a removal note.

## Tests

- New-syntax snippets (rst + myst): header only, footer only, both,
  out-of-order (footer directive before body text), options on sub-directives,
  `grid-item-card` with header/footer sub-directives.
- Legacy snippets: existing ones keep passing with the flag default-True and
  emit exactly one `design.card_legacy` warning per document.
- The killer regression: card containing a code-block whose content includes
  a `+++` line → with sub-directive syntax (and legacy flag False) the
  code-block survives intact.
- Mixed-syntax warning test; multiple-header warning test.
- Line-attribution test: an intentional error inside a card-footer reports
  the footer's line, not the card's.

## Acceptance criteria

- New syntax fully documented and default in all docs/snippets.
- Zero behaviour change for legacy users beyond one suppressible warning.
- `pytest` + all `tox -e docs-*` builds green.
- Doctree output for equivalent legacy/new inputs is identical (same
  component structure) — assert with a dedicated test comparing both parses.
