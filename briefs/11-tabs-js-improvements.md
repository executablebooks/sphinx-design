# Brief 11: Tabs JS — sync via `change` events, anchor-opens-tab, persistent + configurable storage

**Type**: bug fix + feature | **Size**: medium | **Closes**: #46, #239, #103.
**Depends on**: brief 02 (config field).

> **Correction to the roadmap triage**: the JS header comment claims
> "stored in local storage so that it persists across page loads", but the
> code uses **`window.sessionStorage`** (`sd_tabs.js:64,69,98`) — state does
> NOT survive a new browsing session. #103's first bullet is therefore still
> open; Task 3 below now covers it.

Source file: `sphinx_design/compiled/sd_tabs.js` (shipped as
`design-tabs.js`; location moves to `sphinx_design/static/` if brief 04 has
landed). It is plain JS type-checked by `tsc --allowJs --strict` via
pre-commit (`.pre-commit-config.yaml`, hook `tsc`) — keep JSDoc types valid.

## Task 1 (#46): sync on `change`, not label `onclick`

Today sync fires from `label.onclick` (assigned in `ready()`). A click+drag
released over a label activates the radio natively **without** firing that
handler consistently, desyncing grouped tabs. Also keyboard activation
(arrow keys on radios) never fires label clicks.

Fix: attach the listener to the radio **input**'s `change` event instead
(the input precedes the label: `label.previousElementSibling` or
`document.getElementById(label.getAttribute("for"))`). `change` fires exactly
once per selection regardless of activation method (mouse, drag-release,
keyboard, JS). Keep the handler idempotent: when syncing *other* tabs
programmatically, set `input.checked = true` directly (does not re-fire
`change`), never `.click()`.

## Task 2 (#239): open tab when URL fragment targets it

`:name:` on a `tab-item` puts the id on the label (via `add_name`,
`tabs.py:112`; carried to the label node at `tabs.py:280-281`). Deep links
`page.html#my-tab-name` currently scroll to the label but don't select the
tab (only `?<group>=<sync-id>` query params are handled).

Add to `ready()`: if `window.location.hash` is non-empty and
`document.getElementById(hash)` (or closest ancestor) is a `.sd-tab-label`,
check its radio input. Also listen for `hashchange`. After selecting,
re-scroll the label into view (`el.scrollIntoView()`) since panel visibility
changed. Also handle the case where the hash targets an element *inside* a
non-selected tab panel: walk `closest(".sd-tab-content")`? — content divs are
siblings, not ancestors of labels; instead: if the target is inside a
`.sd-tab-content` element, select the immediately preceding label's input.
(DOM order per `TabSetHtmlTransform`: input, label, content, input, label,
content…, so `content.previousElementSibling.previousElementSibling` is its
input.)

## Task 3 (#103): persistent storage, configurable prefix

Two changes:

1. **Switch `sessionStorage` → `localStorage`** so tab choice (e.g. preferred
   programming language) survives new browsing sessions — this is #103's
   headline ask and what the file's own header comment already (wrongly)
   claims. Note behavioural change in the changelog.
2. `storageKeyPrefix = "sphinx-design-tab-id-"` is global, so two Sphinx
   sites on one origin (e.g. RTD subprojects, versioned docs under one
   domain) share tab state — with `localStorage` this becomes cross-session
   too, so the prefix must become configurable in the same PR. Add config
   field `tabs_storage_prefix: str = "sphinx-design-tab-id-"` to `SdConfig`
   (brief 02); empty string ⇒ disable persistence entirely. Fix the header
   comment while there.

Delivery to JS must stay declarative: pass it as a data attribute on the
script tag — `app.add_js_file("design-tabs.js", **{"data-sd-tabs-storage-prefix": value})`
(Sphinx forwards extra kwargs as HTML attributes). In JS read it at startup:
`document.currentScript?.getAttribute("data-sd-tabs-storage-prefix")` — note
`currentScript` must be captured at eval time (top level), not inside
`ready()`.

## Task 4 (cleanup): remove the `console.log` in the query-param path

(`sd_tabs.js` `ready()` logs on selection) — drop it or gate behind a
`data-sd-debug` attribute.

## Tests

- JS has no test harness today; brief 23 adds Playwright — if it has landed,
  add cases there: drag-release selection syncs the sibling tab-set;
  `#name` deep link opens the tab; two projects with different prefixes
  don't share state (simulate by editing the attribute); keyboard arrow keys
  sync. If brief 23 hasn't landed, do manual verification against
  `tox -e docs-furo` output and record steps in the PR description.
- Python side: regression test that the script tag in built HTML carries the
  data attribute when the config is customized.
- `pre-commit run --all tsc` passes (strict JSDoc).

## Acceptance criteria

- #46 reproduction (click+drag on a synced tab) keeps groups in sync.
- `page.html#tabname` opens the named tab; hash targets inside hidden panels
  reveal the panel.
- Storage prefix configurable and TOML-representable; default behaviour
  unchanged for existing users.
