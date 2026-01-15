## Add AGENTS.md and tox environments for code quality

This PR adds developer tooling and documentation for AI coding agents.

### Changes

- **Add `AGENTS.md`**: Comprehensive guide for AI agents working on this repository, including project overview, repository structure, development commands, code style guidelines, testing patterns, and architecture documentation.

- **Add tox environments for code quality**:
  - `tox -e mypy` — Type checking
  - `tox -e ruff-check` — Linting (auto-fix by default)
  - `tox -e ruff-fmt` — Formatting

- **Add `[dependency-groups]` to `pyproject.toml`**: Pinned versions for mypy and ruff matching `.pre-commit-config.yaml` for consistency between CI and local development.
