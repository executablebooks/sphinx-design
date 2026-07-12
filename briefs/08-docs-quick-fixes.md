# Brief 08: Documentation quick fixes

**Type**: docs | **Size**: small | **Closes**: #172, #122, #184, #247.

## Fixes

### 1. Sizing CSS classes are documented wrong (#172) — verified

`docs/css_classes.md:98-102` lists `sd-width-25`/`sd-height-25` etc., but
`style/_sizing.scss:11-17` generates abbreviated names:
`sd-w-{25,50,75,100,auto}` and `sd-h-{25,50,75,100,auto}`. Fix the doc list.
Grep the docs for any other `sd-width`/`sd-height` occurrences.

### 2. Getting-started prerequisites for MyST examples (#122)

`docs/get_started.md` examples (e.g. the avatar/image card) assume MyST
extensions that aren't stated. Add an explicit note near the top of the MyST
usage section: required `myst_enable_extensions = ["colon_fence"]`, plus
`html_image` (or `attrs_inline`) when using raw `<img>`/image options as in
the examples; link to the myst-parser docs for each. Cross-check
`docs/conf.py`'s own `myst_enable_extensions` and mention every extension the
shipped snippets rely on.

### 3. Grid docs: multi-row and wrapping behaviour (#184, #182-docs part)

`docs/grids.md`: add a section "Multiple rows" showing that items wrap into
new rows automatically when columns are exhausted, and an explicit example of
adding a second `grid` for deliberate row separation. Also document (from
#182): when the grid argument is a **single** value, that column count is
fixed across all screen sizes — use the four-value form (`1 2 2 3`) for
responsive re-flow; note the interaction with per-item `:columns:`.

### 4. Linking to tabs with query args from Markdown (#247)

`docs/tabs.md` documents `?category=key2#synchronised-tabs` linking but not
how to author such a link in MyST (plain `[text](path.html?category=x#anchor)`
myst link, since `{ref}`/`{doc}` cannot carry query strings). Add a short
sub-section with a working MyST and rST (`raw`/external-link) example and the
caveat that these are builder-output-relative URLs.

## Process

- Build docs for at least two themes (`tox -e docs-furo`, `tox -e docs-pydata`)
  with `-nW --keep-going` (default in tox env) — zero new warnings.
- These are `docs/` only changes: no snippet files that feed
  `tests/test_snippets.py` should change rendering (if a snippet must change,
  regenerate regressions and justify in the PR).
- Close each issue with a link to the built RTD page section.

## Acceptance criteria

- All four issues addressed and closeable; docs build clean on all themes.
