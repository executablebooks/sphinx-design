# Brief 22: Public testing helpers (`sphinx_design.testing`)

**Type**: feature (developer-facing) | **Size**: small | **Closes**: #260.

## Ask

`sphinx-design-elements` (and other downstream extensions) reimplement the
doctree-XML normalization that lives in this repo's test suite. #260 asks to
ship it as a public helper.

## Current state

`normalize_doctree_xml` is a pytest fixture in `tests/conftest.py:99+`
returning a closure that normalizes docutils ≥0.22 boolean attribute
serialization (`"1"/"0"` vs `"True"/"False"`) against a hard-coded
attribute list. `tests/test_snippets.py` imports/uses it (`:39,50,67`).

## What to do

1. Create `sphinx_design/testing.py`:
   - `normalize_doctree_xml(text: str) -> str` — move the pure function out
     of the fixture (the fixture body is already a closure over a pure
     function; lift it verbatim, keep the attribute list as a module
     constant `_BOOL_ATTRIBUTES` and accept an optional
     `extra_attributes: Sequence[str] = ()` parameter for downstream nodes).
   - Docstring stating the support policy explicitly: *semi-public testing
     API — covered by deprecation policy for signature, not for exact
     output stability across docutils versions.*
   - No pytest import in this module (keep runtime deps zero; it must be
     importable without test extras).
2. `tests/conftest.py`: fixture becomes a thin wrapper importing from
   `sphinx_design.testing` (keeps existing test signatures working). While
   there, fix the docstring/comment typo at `conftest.py:109`
   ("Normalize new format (1/0) to old format (1/0)" — second should read
   "(True/False)").
3. Consider (and do, if trivial) also exporting the `SphinxBuilder`
   conftest helper class the same way — inspect `tests/conftest.py`; if it
   depends only on `sphinx.testing`, move it to `sphinx_design.testing` and
   re-export in conftest. If it drags pytest/monkeypatch specifics, leave
   it and note why in the PR.
4. Docs: short "Testing utilities" section (docs page or README section)
   documenting the module and the stability caveat; changelog entry.
5. Comment on #260 once merged, pointing at the module and inviting
   sphinx-design-elements to drop its workaround.

## Tests

- Unit tests for `normalize_doctree_xml` itself: pre-0.22-style input is a
  no-op; 0.22-style booleans normalize; `extra_attributes` respected;
  non-boolean `"1"` values (e.g. text content) untouched.
- Existing snippet suite passes unchanged on docutils 0.21 and 0.22 (CI
  matrix Sphinx ~=7.0/8.0/9.0 spans both — confirm which docutils each
  resolves and note in PR).

## Acceptance criteria

- `from sphinx_design.testing import normalize_doctree_xml` works in a
  fresh env with only `sphinx_design` installed.
- #260 closeable; no test-suite behaviour change.
