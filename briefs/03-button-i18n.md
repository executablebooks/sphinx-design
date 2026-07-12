# Brief 03: Land and complete the button i18n fix (PR #264)

**Type**: bug fix | **Size**: small-medium | **Closes**: #96, #44, #263; supersedes PR #175.
**Priority**: highest — longest-standing high-impact bug cluster.

## Problem

Buttons (`button-link`, `button-ref`) break under gettext translation: the
translated button renders as plain text, losing all CSS classes and sometimes
the link itself (#96, #44, #263).

## Root cause

`_ButtonDirective.run_with_defaults` (`sphinx_design/badges_buttons.py:156-198`)
wraps the reference node in a `nodes.paragraph`. Sphinx's i18n machinery
extracts *paragraphs* as translation units, so the `.pot` message contains the
entire rendered directive; on translation, the paragraph's children (the
styled reference) are replaced wholesale by the parsed translation text.

## Existing work: PR #264 (sneakers-the-rat)

The approach is correct and should be the basis:

- marks the content inline `translatable=True` and gives it proper
  source/line info (`self.set_source_info(content); content.line +=
  self.content_offset`) so gettext targets only the button *text*;
- marks the outer paragraph `translatable=False` so the directive wrapper is
  never a translation unit;
- parametrizes the `sphinx_builder` fixture by builder name
  (`tests/conftest.py`) and adds a `gettext`-builder regression test writing
  `.pot` output (`tests/test_snippets.py::test_i18n_myst` +
  `tests/test_snippets/snippet_i18n_button-link.pot`).

## What to do

1. Check out PR #264, rebase on main, and review line-by-line. Verify the
   regression XML changes (`snippet_pre/post_button-link.xml`) are the *only*
   doctree changes (`translatable` attribute + inline unwrap).
2. **Close the gaps** the PR leaves:
   - It only tests `button-link` extraction. Add `.pot` extraction tests for
     `button-ref` (the pending_xref path, `badges_buttons.py:215-233`) — rst
     *and* myst snippets.
   - Extraction is only half the bug. Add a **translated-build round-trip
     test**: build a project with `language="xx"`, `locale_dirs=["locales"]`,
     a hand-written `.po`/`.mo` (compile with `sphinx.util.i18n` or
     `babel.messages.mofile` — `babel` is already a Sphinx dependency)
     translating the button text, then assert on the built doctree/HTML:
     - the reference/pending-xref node survives with all `sd-btn*` classes,
     - the visible text is the translated string,
     - `button-ref` still resolves its target (this is #44's exact failure).
   - Confirm badge roles (`bdg-*`) are unaffected (they are inline roles, not
     paragraph-wrapped) — add one badge to the i18n snippet as a control.
3. Check `docutils 0.22` serialization of the new `translatable` attributes in
   regression files against `tests/conftest.py::normalize_doctree_xml`
   (booleans serialize as `1/0` in 0.22+; the fixture normalizes — extend its
   attribute list if `translatable` is missing from it).
4. Changelog entry under `Fixes`; credit PR #264's author.

## Acceptance criteria

- `.pot` contains only button text (with correct source line), for both
  button directives, rst + myst.
- Translated build renders styled, working, translated buttons (test above).
- Full matrix passes: `tox -e py311` and `tox -e py311-no-myst`.
- Issues #96/#44/#263 each get a comment pointing at the fix with the release
  it will ship in.

## Gotchas

- The fixture parametrization in #264 changes every existing test id (adds
  `[html]`) — fine, but regenerate nothing blindly; only the two button XML
  files should change content.
- `tests/test_snippets.py` globs snippets from `docs/snippets/` — the i18n
  test reuses doc snippets, so keep doc snippet edits minimal and rendering-
  neutral.
