# Brief 24: Packaging polish and the 1.0 release

**Type**: release engineering | **Size**: small (mechanics) — release timing is a maintainer call.
**Do last**: assumes briefs 03, 04, 05, 06 (and ideally 16's deprecation cycle started).

## Packaging changes (`pyproject.toml`)

1. **PEP 639 license metadata**: flit_core ≥3.12 supports it —
   `requires = ["flit_core>=3.12,<4"]`, replace
   `license = {file = "LICENSE"}` with `license = "MIT"` +
   `license-files = ["LICENSE"]`, and drop the
   `License :: OSI Approved :: MIT License` classifier (superseded by the
   expression).
2. **Development status**: `Development Status :: 4 - Beta` →
   `5 - Production/Stable`. The extension is 5 years old and used by major
   projects (matplotlib et al.); Beta undersells stability guarantees.
3. Verify classifiers list Python 3.11–3.14 only (matches
   `requires-python = ">=3.11"`); Sphinx floor after brief 04 is `>=7.1,<10`.
4. Add `[project.urls]` entries: `Changelog`, `Issues` (nice for PyPI page).

## 1.0 release checklist

Preconditions (verify each, list status in the release PR):

- [ ] i18n buttons fixed and released once in a 0.x (brief 03)
- [ ] static-asset rework shipped in a 0.x with no regressions reported
      (brief 04) — the `_static` path change is the riskiest user-visible
      change; give it one minor-release soak
- [ ] trusted publishing live (briefs 05/06)
- [ ] card legacy-separator deprecation warning shipped in ≥1 minor release
      (brief 16) — **1.0 keeps the legacy syntax working** (default flag
      still True); flipping the default is 2.0 per the migration plan
- [ ] changelog: consolidated 1.0 section, including a "stability policy"
      statement: what is public API (directives/roles/options/config,
      `sd-` CSS class names, `sphinx_design.testing`) vs internal (python
      module internals, node classes)

Mechanics: bump `sphinx_design/__init__.py` version → `1.0.0`, tag `v1.0.0`
on main after the release PR merges (tag push triggers publish per
`ci.yml`).

## Docs

- README: replace any "beta" language; add the stability policy.
- `docs/`: changelog page renders the 1.0 notes; migration guide (brief 16)
  linked from the release notes.

## Acceptance criteria

- `flit build` produces sdist+wheel with correct PEP 639 metadata
  (`pip show`/`importlib.metadata` shows `License-Expression: MIT`).
- `twine check dist/*` passes (or the pypa-publish action's built-in check).
- PyPI page renders classifiers/urls correctly on the first 1.0.x release.
