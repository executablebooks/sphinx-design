# Brief 20: Tooltips for badges (and consistent tooltip support)

**Type**: feature | **Size**: small | **Closes**: #81.

## Current state

- Buttons already support `:tooltip:` → `reftitle` → HTML `title` attribute
  (`sphinx_design/badges_buttons.py:174-175`, with a `TODO escape HTML` to
  resolve — verify docutils attribute escaping makes it a non-issue: the
  html writer escapes attribute values, so the TODO can likely just be
  removed after a test proves escaping).
- Badges (#81) have no tooltip mechanism. Badge roles:
  `BadgeRole`/`LinkBadgeRole`/`XRefBadgeRole`
  (`badges_buttons.py:61-125`).

## Design

Native `title`-attribute tooltips only (no CSS tooltip framework in this
brief — keep scope tight; a styled CSS tooltip can be a follow-up if ever
wanted). Syntax: extend the role microsyntax with a `;`-suffix, consistent
with the icon roles' documented `name;height;classes` grammar
(parser-portable: it's a documented string grammar, no Python-only
semantics):

```rst
:bdg-primary:`stable ; A released, supported version`
:bdg-link-info:`docs <https://example.com> ; Opens the documentation`
```

Rule: text is split on the **last** unescaped `;`; the suffix (stripped) is
the tooltip. No `;` → no tooltip (fully backwards compatible; badge text
containing `;` today is unaffected unless followed by nothing — decide and
test the edge: trailing `;` yields empty tooltip → ignore).

## Implementation

1. Shared helper in `badges_buttons.py`: `split_tooltip(text) ->
   tuple[str, str | None]`.
2. `BadgeRole.run` (`:69-77`): plain badges are `nodes.inline` — the html
   writer does not emit `title` for inline. Wrap in the existing pattern:
   set `classes` + a `title` via a minimal custom node? Simplest: use
   `nodes.abbreviation`? No — semantics wrong. Add tiny node `sd_badge`
   subclassing `nodes.inline` with html visitor emitting
   `<span title="...">` when the attribute is set, else plain span
   (follow `fontawesome` node precedent, `sphinx_design/icons.py:184-214`).
   Non-HTML visitors: fall through to inline rendering (register only html
   visitors and let it inherit inline behaviour — verify docutils dispatch:
   for unknown node classes latex uses `unknown_visit`; safer to register
   explicit visitors for latex/text/man/texinfo that render children like
   inline; copy the `PassthroughTextElement` registration pattern from
   `extension.py:39-46`).
3. `LinkBadgeRole` (`:88-100`): `nodes.reference` supports `reftitle` →
   `title` attr natively; set it. (This also resolves the commented-out
   `reftitle` code at `:97-98` — delete the dead comment.)
4. `XRefBadgeRole` (`:111-125`): stash tooltip on the pending_xref
   (`reftitle`? no — resolved reference gets `reftitle` from the *target*
   doc title for some domains and would overwrite) — set an `sd_tooltip`
   attribute and copy to `reftitle` in a small post-resolution transform,
   or simpler: document that tooltip on `bdg-ref-*` overrides the
   auto-title; implement via post-transform setting `reftitle` after
   resolution (share the transform with brief 14's newtab post-transform if
   both land — coordinate).
5. Buttons: no syntax change; add the escaping test and remove the TODO.

## Docs

`docs/badges_buttons.md`: tooltip syntax for all badge variants + note that
`title` tooltips are not keyboard/touch accessible — for essential
information use visible text (a11y honesty note).

## Tests

- Doctree + post-HTML regressions: each badge variant with/without tooltip;
  text containing internal `;` without tooltip intent (escaped/no-split
  case); tooltip with quotes/`<`/`&` → correctly escaped in HTML output.
- bdg-ref tooltip survives reference resolution.

## Acceptance criteria

- #81 syntax works on all `bdg-*` role families; buttons' existing tooltip
  verified escaped; docs updated; no rendering change without `;`-suffix.
