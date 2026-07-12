# Brief 01: Backlog hygiene — merge/close open PRs, refresh dev pins

**Type**: maintenance | **Size**: small | **Requires maintainer permissions** for merge/close actions.

## Goal

Clear the open-PR backlog so real work starts from a clean slate, and stop
dependabot generating one PR per theme pin.

## Actions

### Merge (after a standard review)

- **PR #205** (`refactor: Remove unused constants`): verified — `OCTICON_CSS`
  in `sphinx_design/icons.py:21-26` has zero references outside its
  definition (`grep -rn OCTICON_CSS sphinx_design/` returns only the
  definition). Rebase on main if needed, merge.
- **PR #262** (pre-commit autoupdate: ruff v0.15.20, mypy v2.1.0): merge; if
  new ruff/mypy versions raise new errors, fix them in the same PR. Note
  `pyproject.toml` `[dependency-groups]` pins `mypy==1.19.1` / `ruff==0.14.11`
  — bump those to match the pre-commit revs so tox and pre-commit agree.

### Close with a short explanatory comment

- **PR #237**: `.readthedocs.yml` on main already contains
  `sphinx: configuration: docs/conf.py` — the fix landed independently.
- **PR #220**: `pyproject.toml` already has `myst-parser>=4,<6`.
- **PR #203**: superseded by brief 05 (codecov-action v5 + fixing the dead
  upload condition).
- **PR #175**: superseded by PR #264 (see brief 03).
- **PRs #221, #225, #226, #227**: superseded by the pin-refresh below.

### Pin refresh (one PR)

In `pyproject.toml`:

- `theme-furo`: `furo~=2024.7.18` → latest (check PyPI; 2025.x exists)
- `theme-pydata`: `pydata-sphinx-theme~=0.15.2` → `>=0.15,<0.18` (check latest)
- `theme-rtd`: `sphinx-rtd-theme~=2.0` → `>=2,<4`
- `theme-sbt` / `theme-im`: check PyPI for latest, widen similarly
- `code-style`: `pre-commit>=3,<4` → `>=3,<5`

Then run every docs build to confirm compatibility:
`tox -e docs-furo`, `docs-pydata`, `docs-rtd`, `docs-sbt`, `docs-im`,
`docs-alabaster` (all must pass with `-nW --keep-going`).

### Issue sweep (close / answer with a short comment)

- **#6** (2021 "Initial Feedback"): thank + close — served its purpose.
- **#77**: `more info needed` since 2022 with no response — close as
  not-reproducible, invite reopen with a minimal example.
- **#80** (per-page default options): answer → largely addressed by
  `sd_custom_directives` (v0.6.0); link the docs section, close.
- **#103**: comment correcting the record — persistence currently uses
  `sessionStorage` (not localStorage as the JS comment claims); fix is
  scheduled (brief 11). Leave open until that lands.
- **#165** (menu dropdowns): close as out-of-scope for a content-component
  library (interactive nav belongs to themes), per the roadmap decision.
- **#177** (shibuya example): close as nice-to-have — link shibuya's own
  sphinx-design page as the reference rendering.
- **#182**: comment explaining single-value `:columns:` semantics (fixed
  across breakpoints by design) and link the docs section added in brief 08;
  close unless a behaviour change is requested.

### Dependabot grouping

In `.github/dependabot.yml`, add grouping so future pin bumps arrive as a
single PR per ecosystem:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    commit-message:
      prefix: ⬆️
    schedule:
      interval: monthly
    groups:
      actions:
        patterns: ["*"]
  - package-ecosystem: pip
    directory: /
    commit-message:
      prefix: ⬆️
    schedule:
      interval: monthly
    groups:
      python-deps:
        patterns: ["*"]
```

## Acceptance criteria

- Open PR count reduced to the actively-reviewed set (#158, #230, #241, #264
  — handled by briefs 03, 04, 10).
- The seven issue-sweep items above each closed or answered as specified.
- All six theme docs builds green with refreshed pins.
- `pre-commit run --all-files` and `tox -e mypy` pass with the updated tool pins.
