# Brief 10: Accessibility pass — land PR #230 and add ARIA wiring for tabs

**Type**: a11y | **Size**: medium | **Closes**: #30; lands PR #230.

## Part A: land PR #230 (focus rings, gabalafou, Dec 2024)

The PR adds `:focus-visible` rings to dropdown summaries and tab labels and
reduces an oversized dropdown hit-target. To land it:

1. Rebase onto main. It predates the Sass `@import`→`@use` migration (#259),
   so the SCSS will conflict — port its rule changes into the current
   `@use`-based partials (`style/_dropdown.scss`, `style/_tabs.scss`).
2. Recompile CSS (`npm run css`) and commit the regenerated
   `sphinx_design/compiled/style.min.css` (or `sphinx_design/static/…` if
   brief 04 has landed — check first).
3. Verify keyboard-only: Tab to a closed dropdown → visible ring; Tab into a
   tab-set → ring on focused label; mouse click → no ring (`:focus-visible`,
   not `:focus`). Test on furo + pydata + alabaster (`tox -e docs-*`).
4. Credit the original author (keep their commits or co-author trailer).

## Part B: ARIA relationships for tabs (#30)

Current HTML (built by `TabSetHtmlTransform`, `sphinx_design/tabs.py:212-291`
and visitors at `tabs.py:187-209`): hidden radio `input` + `label` +
content `div`, with no programmatic link between label and content.

Minimal, robust improvement (keep the CSS-only radio mechanism — do NOT
attempt the full WAI-ARIA tabs pattern with roving tabindex in this PR):

1. In `TabSetHtmlTransform.run`, give each content container a stable id:
   `tab_content["ids"].insert(0, f"{tab_item_identity}-content")` — the
   content node is a `container`, rendered via the overridden container
   visitor (`extension.py:120-132`), which already emits ids via `starttag`.
2. In `visit_tab_label` (`tabs.py:200-205`), add
   `attributes["aria-controls"] = node["input_id"] + "-content"` (pass the id
   through a node attribute set in the transform rather than string-deriving
   in the visitor).
3. Add `aria-hidden="true"` is NOT appropriate for unselected panels here
   (CSS controls visibility) — skip panel-state ARIA; the radio group already
   conveys selection state to AT.
4. Run an axe-core scan (via the Playwright harness if brief 23 has landed;
   otherwise `npx @axe-core/cli` against a built docs page) on `docs/tabs`
   output — record before/after violation counts in the PR.

## Tests

- Update HTML/doctree regressions for the new ids/attributes
  (`tests/test_snippets/snippet_post_tab-*.xml` etc.).
- Snippet asserting: label `aria-controls` == content div id, ids unique
  across two tab-sets on one page.

## Acceptance criteria

- Keyboard focus visible on dropdowns and tab labels across the three main
  themes; no rings on mouse click.
- Every tab label programmatically references its panel.
- No regression in existing tests; axe violations for the tabs page do not
  increase.
