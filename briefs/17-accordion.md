# Brief 17: New component — `accordion` (exclusive dropdown group)

**Type**: new component | **Size**: small-medium | **Zero JS.**

## Concept

A container of `dropdown`s where opening one closes the others. Native HTML
does this: `<details>` elements sharing a `name` attribute are mutually
exclusive (Baseline 2024: Chrome 120+, Safari 17.2+, Firefox 130+). Dropdowns
already render as `<details>` (`sphinx_design/dropdown.py:36-44`), so the
component is: a wrapper directive that stamps a shared group name onto child
dropdowns + the visitor emitting it.

Graceful degradation is automatic: older browsers ignore `name` and treat
the dropdowns as independent — acceptable.

## Syntax

```rst
.. accordion::

   .. dropdown:: First section

      Content

   .. dropdown:: Second section
      :open:

      Content
```

Options: `class` (class_option); `flush` (flag — edge-to-edge styling,
Bootstrap's accordion-flush look). No name option: group names are
auto-generated (`sd-accordion-<docname-hash>-<n>`) to avoid cross-page or
cross-project collisions; determinism per page keeps builds reproducible.

## Implementation

1. `sphinx_design/accordion.py` (or extend `dropdown.py`):
   `AccordionDirective(SdDirective)` — `nested_parse` content, validate
   children are `dropdown` components (`is_component(child, "dropdown")`),
   warn subtype `design.accordion` otherwise (skip inert nodes per brief 07's
   `is_ignorable_child`). Set `child["in_accordion"] = True` and wrap all in
   `create_component("accordion", ["sd-accordion", *flush/class classes])`.
2. Group naming: a post-transform is unnecessary — assign in the directive:
   generate `self.env.new_serialno("sd-accordion")` based name combined with
   `self.env.docname` slug; store on each child dropdown component as
   `details_name`.
3. `DropdownHtmlTransform` (`dropdown.py:151-237`): pass `details_name`
   through to the `dropdown_main` node; `visit_dropdown_main`
   (`dropdown.py:36-40`) emits `name="..."` when present. At most one child
   may have `:open:` (warn and keep the first otherwise — exclusive groups
   with multiple `open` are invalid HTML behaviourally).
4. SCSS `style/_dropdown.scss` (or new `_accordion.scss` + `@use` in
   `index.scss`): collapse inter-item margins inside `.sd-accordion`
   (children currently get `sd-mb-3`), optional `flush` variant (no outer
   border-radius/borders except separators). Recompile CSS.
5. Non-HTML builders: the accordion container renders as a plain container;
   dropdowns degrade exactly as today. No extra latex work (brief 21 covers
   dropdown latex).
6. Register in `setup_extension` (`extension.py:47-56`) so it participates
   in `sd_custom_directives` inheritance.

## Docs

New `docs/accordions.md` (+ toctree entry): concept, browser-support note,
`:open:` interaction, flush variant, rst + myst snippets under
`docs/snippets/`.

## Tests

- Doctree regression (rst + myst): two dropdowns in accordion → components
  carry the group attribute; unique group names for two accordions on one
  page.
- Post-HTML regression: `<details name="...">` present, same name across
  siblings, differs between accordions.
- Warning tests: non-dropdown child; multiple `:open:` children.
- (If brief 23 landed) Playwright: opening the second item closes the first.

## Acceptance criteria

- Component documented, tested, CSS committed, warnings typed
  `design.accordion`. No JS added.
