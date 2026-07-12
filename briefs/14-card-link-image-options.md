# Brief 14: Card link & image options

**Type**: feature | **Size**: medium | **Closes**: #170, #261, #152; part-addresses #211.

All changes centre on `CardDirective.create_card`
(`sphinx_design/cards.py:80-201`) and are inherited by `grid-item-card`
(which delegates to `create_card` — verify in `sphinx_design/grids.py`).

## Task 1 (#170): `:link-newtab:` flag

Option `link-newtab` (flag) on `card`/`grid-item-card` (and, for
consistency, `button-link`): open the link in a new tab
(`target="_blank" rel="noopener"`).

Implementation: the HTML5 writer's `visit_reference` does not emit
arbitrary attributes, so introduce a small post-transform or node subclass:

- Add attribute `link_newtab=True` to the `nodes.reference` (external links,
  `cards.py:176-182`) or `pending_xref` (internal, `cards.py:184-196` — the
  resolved reference inherits attributes? **No** — pending_xref resolution
  creates a fresh reference; instead run a `SphinxPostTransform`
  (html-only, priority > 5 i.e. after `ReferencesResolver`) that finds
  references whose `classes` include a marker class `sd-link-newtab` and
  sets `node["target"] = "_blank"`).
- Emit the actual HTML attributes with a tiny override: register a custom
  node `sd_reference`? Simpler robust path: keep standard reference nodes,
  add marker class, and override `visit_reference` is NOT allowed (breaks
  themes). Final approach: post-transform wraps nothing — instead extend the
  existing HTML translator behaviour via `app.add_node`? References can't be
  re-registered safely.

  **Decision**: implement with a `SphinxPostTransform` that replaces the
  resolved `nodes.reference` with a subclass `sd_link(nodes.reference)`
  registered with its own visitor that copies Sphinx's `visit_reference`
  logic minimally: call `self.visit_reference(node)` is fine — it uses
  `starttag`-built markup internally; instead simplest correct visitor:

  ```python
  def visit_sd_link(self, node):
      self.visit_reference(node)  # builds the <a ...> via translator
      # patch the just-appended start tag to inject target/rel
      self.body[-1] = self.body[-1].replace(
          "<a ", '<a target="_blank" rel="noopener" ', 1)
  def depart_sd_link(self, node):
      self.depart_reference(node)
  ```

  It's a string patch but on markup we just generated; add a unit test
  locking the output. (Alternative if distasteful: data attribute + 3-line
  JS in design-tabs.js — avoid; keep zero-JS.)

## Task 2 (#261): `:class-link:` option

`class-link` (`directives.class_option`) appended to the link node's classes
(`_classes` list at `cards.py:173`). One-liner plus docs + regression. Do the
same for `button-link`/`button-ref` (`class` already exists there — skip).

## Task 3 (#152): equal-height card images

Add utility CSS in `style/_cards.scss` (recompile CSS):

```scss
.sd-card-img-top-fixed {  // apply via :class-img-top: sd-card-img-top-fixed
  height: var(--sd-card-img-height, 10rem);
  object-fit: cover;
}
```

Document under cards: fixed-height thumbnails via
`:class-img-top: sd-card-img-top-fixed` + overriding the CSS variable for a
different height. No new directive option needed (keeps the option surface
flat); mention in #152 that combining with grid `:class-card: sd-h-100`
equalises card heights.

## Task 4 (#211, minimal viable): horizontal card images

Full Bootstrap "horizontal card" is significant; ship the constrained
version: options `img-left`/`img-right` (uri, mutually exclusive with each
other; combinable with `img-alt`). Structure: wrap image + existing
body/header/footer container in a flex row:

- card gets class `sd-card-horizontal`; image classes
  `sd-card-img-left`/`-right` (`object-fit: cover; width: 33%` default,
  overridable via `--sd-card-img-width`); content wrapped in a div with
  `sd-card-content-col`.
- SCSS: flex row, image order first/last, stack vertically below the `sm`
  breakpoint (reuse the grid breakpoint variables in
  `style/_variables.scss`).
- Error if combined with `img-top`/`img-bottom`/`img-background`.

## Task 5 (#26): card padding lands on the wrong element

Verified root cause: `grid-item-card` applies `:padding:` (and `:margin:`)
to the outer `sd-col` column div (`sphinx_design/grids.py:250-251`) and
explicitly clears card margin (`grids.py:281`); `CardDirective` itself has
**no `padding` option at all** (`cards.py:56-75`). So users cannot pad the
card surface, and padding a grid-item-card pads the invisible column (#26).

Fix:

- add `padding` (existing `padding_option` validator, `shared.py:186-190`)
  to `CardDirective.option_spec`, applied to the **card** classes
  (`card_classes` at `cards.py:86-90`);
- `grid-item-card`: pass `padding` through to `card_options`
  (`grids.py:255-278`) instead of the column. This is a behaviour change
  for anyone relying on column padding — changelog `Breaking`-adjacent
  note; keep `margin` behaviour as-is (column margin is meaningful for
  grid spacing).

## Tests

Doctree + post-HTML regressions for each option (rst + myst snippets);
error-path test for conflicting image options; padding test asserting
`sd-p-*` classes land on the `sd-card` element for both `card` and
`grid-item-card` (#26 reproduction); CSS recompiled and committed.
Docs sections for all options with rendered examples.

## Acceptance criteria

- All four options documented, tested, rendering on furo + pydata.
- `link-newtab` produces `target="_blank" rel="noopener"` for external AND
  resolved internal links; regular links unchanged.
- No JS added.
