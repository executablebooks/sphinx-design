# Brief 05: CI modernization (coverage is silently dead)

**Type**: infra | **Size**: small | **Supersedes**: PR #203.

## Problems (`.github/workflows/ci.yml`)

1. **Coverage upload never runs.** Line 66:
   `if: ... && matrix.python-version == '3.9' && ...` — Python 3.9 left the
   matrix in PR #250, so the condition is always false. No coverage has been
   uploaded since v0.7.0 development.
2. `codecov/codecov-action@v3` is deprecated (v5 current).
3. No `concurrency` group — superseded pushes waste runners.
4. Action versions behind: `actions/setup-python@v5` (v6 exists),
   `actions/checkout@v4` (v5 exists).

## What to do

1. Fix the upload condition to a current matrix cell, e.g.:

   ```yaml
   if: github.event.pull_request.head.repo.full_name == github.repository
       && matrix.python-version == '3.13'
       && matrix.sphinx-version == '~=8.0'
       && matrix.os == 'ubuntu-latest'
   ```

   (Also runs on `push` to main: note the first clause is false for pushes —
   replicate the existing intent: keep uploads for same-repo PRs and main
   pushes; `github.event_name == 'push' ||` prefix achieves that.)
2. Bump `codecov/codecov-action` to v5. v5 renames `file:` → `files:`. Keep
   `token: ${{ secrets.CODECOV_TOKEN }}`, `fail_ci_if_error: true`.
3. Add at top level:

   ```yaml
   concurrency:
     group: ${{ github.workflow }}-${{ github.ref }}
     cancel-in-progress: true
   ```

4. Bump `actions/checkout` → v5, `actions/setup-python` → v6 everywhere
   (pre-commit, tests, docs-build-format, publish jobs).
5. Sanity-check `codecov.yml` thresholds still make sense once coverage
   flows again (first upload after a long gap may show a big delta — set
   `informational: true` for the patch status if it would block PRs
   spuriously, or accept as-is; judgement call, document the choice in the PR).

## Acceptance criteria

- A PR run shows the Codecov upload step actually executing on exactly one
  matrix cell, and codecov.io receives the report.
- All jobs green; `check` aggregation job unchanged.
- Pushing twice quickly to the same PR cancels the first run.

## Out of scope

Trusted publishing (brief 06). Switching pip→uv in CI: optional, only if
trivially green; not required.
