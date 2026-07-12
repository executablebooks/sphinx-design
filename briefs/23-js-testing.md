# Brief 23: Browser-level JS testing (Playwright smoke suite)

**Type**: test infra | **Size**: medium | **Enables verification for briefs 10, 11, 17.**

## Problem

`design-tabs.js` behaviour (tab sync, localStorage persistence, URL query
selection) has **zero** automated coverage — doctree/HTML regressions cannot
catch bugs like #46 (click+drag desync) or interaction regressions from CSS
changes. Every JS-touching PR currently relies on manual clicking.

## Design

Small, hermetic Playwright (Python) suite:

1. **Fixture site**: build a minimal Sphinx project (not the full docs) with
   `sphinx.testing`/the existing `sphinx_builder` fixture at session scope:
   two synced tab-sets (same `sync-group`), a named tab (`:name:`), a
   dropdown, an accordion (once brief 17 lands). Serve the built HTML via
   `http.server` on a free port in a background thread (or `file://` —
   NOTE: localStorage is origin-scoped and flaky on `file://`; use the
   HTTP server).
2. **Tests** (`tests/test_js.py`, marked `@pytest.mark.js`):
   - clicking tab B in set 1 selects tab B in set 2 (sync);
   - selection persists across a page reload (localStorage);
   - `?<group>=<id>` query param selects the tab on load;
   - `#<name>` fragment selects the named tab (after brief 11);
   - keyboard: arrow-key radio navigation keeps sets in sync (after 11);
   - accordion exclusivity (after 17).
   Keep assertions on `input.checked` / element visibility, not pixels.
3. **Dependencies**: new optional extra in `pyproject.toml`:
   `testing-js = ["pytest~=8.3", "playwright", "pytest-playwright"]`; tox env
   `js` running `playwright install chromium --with-deps` is NOT needed
   where a system chromium exists — support env var
   `PLAYWRIGHT_BROWSERS_PATH` passthrough in `tox.ini` (`passenv`). Default
   `pytest` run must skip js tests when playwright isn't importable
   (`pytest.importorskip` in module).
4. **CI**: separate job `js-tests` in `ci.yml` (ubuntu, py3.12, one Sphinx
   version), `pip install -e .[testing-js] && playwright install --with-deps
   chromium && pytest -m js`. Add to the `check` job's `needs`. Keep it
   required-but-fast (<2 min).
5. Optional (recommended): fold an `axe-core` scan into the same suite
   (`page.add_script_tag` with the axe bundle vendored under `tests/assets/`
   — no CDN at test time) asserting no *new* violations on the fixture page;
   store the baseline count in the test.

## Non-goals

Visual regression screenshots (flaky across renderer versions) — out of
scope. Cross-browser matrix — chromium only.

## Acceptance criteria

- `tox -e js` (new env) green locally and in CI; `tox -e py311` unaffected
  without playwright installed.
- The #46 drag scenario is encoded: simulate `mouse.down` on label A of one
  set, `mouse.move`, `mouse.up` — with brief 11 landed this passes; if this
  brief lands first, mark that one test `xfail(reason="#46, brief 11")` so
  the fix flips it.
- README/AGENTS.md updated with how to run JS tests.
