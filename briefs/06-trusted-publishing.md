# Brief 06: PyPI Trusted Publishing (OIDC)

**Type**: infra/security | **Size**: small | **Requires**: PyPI project-owner action (one-time).

## Problem

The `publish` job (`.github/workflows/ci.yml:114-135`) authenticates with a
long-lived API token (`FLIT_PASSWORD: ${{ secrets.PYPI_KEY }}`). Long-lived
tokens are the legacy mechanism; PyPI Trusted Publishing (OIDC) removes the
stored secret and enables PEP 740 attestations.

## What to do

1. Replace the publish job:

   ```yaml
   publish:
     name: Publish to PyPI
     needs: [pre-commit, tests]
     if: github.event_name == 'push' && startsWith(github.event.ref, 'refs/tags')
     runs-on: ubuntu-latest
     environment:
       name: pypi
       url: https://pypi.org/p/sphinx_design
     permissions:
       id-token: write
     steps:
       - uses: actions/checkout@v5
       - uses: actions/setup-python@v6
         with:
           python-version: "3.11"
       - name: Build sdist and wheel
         run: pipx run flit build
       - name: Publish
         uses: pypa/gh-action-pypi-publish@release/v1
   ```

   (`gh-action-pypi-publish` publishes `dist/*` by default and generates
   attestations automatically under OIDC.)
2. **Maintainer one-time setup** (document in the PR description as a
   required pre-merge step):
   - PyPI → project `sphinx-design` → Settings → Publishing → add GitHub
     publisher: owner `executablebooks`, repo `sphinx-design`, workflow
     `ci.yml`, environment `pypi`.
   - GitHub repo → Settings → Environments → create `pypi` (optionally add
     required reviewers for release gating).
   - After the first successful OIDC release: delete the `PYPI_KEY` secret.
3. Dry-run validation without releasing: add a `workflow_dispatch`-guarded
   job step or verify via a TestPyPI publisher first (optional but
   recommended; TestPyPI supports the same trusted-publisher flow with
   `repository-url: https://test.pypi.org/legacy/`).

## Acceptance criteria

- Tag push builds and publishes with no stored PyPI credential.
- Release on PyPI shows provenance/attestation metadata.
- `PYPI_KEY` secret removed after first successful release.

## Gotchas

- The `environment:` name must exactly match the PyPI publisher config.
- `permissions: id-token: write` must be on the job (not only workflow) if a
  workflow-level `permissions` block restricting defaults is ever added.
- Keep `needs: [pre-commit, tests]` — do not publish on red tests.
