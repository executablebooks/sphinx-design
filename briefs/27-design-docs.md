# Brief 27: Design documents for settled architecture

**Type**: docs | **Size**: small-medium | **Closes**: — (extends the pattern
started by the CSS pipeline design page in PR #290).
**Depends on**: none hard; best written after Phase 3 settles the card
redesign so its rationale can be recorded once.

## Motivation

PR descriptions and the roadmap issue hold most of the project's design
rationale, where it is invisible to future contributors. PR #290 introduced
the durable alternative: a rendered "Design:" page under the docs Development
section whose **invariants each name the guard that enforces them** — claims
backed by named tests/hooks cannot silently rot. This brief extends that
pattern to the other settled aspects.

## Pages to write (one PR, one page each; same format as design_css.md:
context → decision → alternatives → invariants-with-enforcement → public API)

1. **Configuration** — the `SdConfig` dataclass principles: every `sd_*`
   option TOML-representable (str/bool/int/list/dict of primitives), central
   validators, flat confval naming, `rebuild="env"` semantics; enforcement:
   the `test_misc.py` meta-tests (INVALID_CONFIG_VALUES, TOML round-trip) and
   the docs options table generated from the dataclass.
2. **Syntax portability** — the parser-portable rule: no authored syntax
   whose meaning exists only in imperative raw-text processing; components
   are generic directives/roles + doctree transforms; role microsyntax
   (`style;name`, `; tooltip`) documented as stable grammar. Context: the
   card `^^^`/`+++` redesign rationale (roadmap §4). Enforcement: the snippet
   fixture suite doubling as a language-agnostic conformance corpus.
3. **Static assets & public API surface** — `html_static_path` serving model,
   `?v=` checksums, HTML-format-builders-only gating; the 1.0 promise:
   `sd-*` classes, `--sd-*` variables, served filenames, `sphinx_design.testing`
   signatures. Enforcement: asset tests from #276, the CSS design page's
   guards. This page becomes the reference for brief 24's 1.0 gates.
4. **Testing strategy** — snippet→XML regression as the conformance suite,
   builder-parametrized fixtures, the two-tier LaTeX strategy (PDF-compile
   smoke in CI + per-component .tex regressions landing with brief 21),
   version rails rationale (the `~=7.0` floor gap).

## Notes

- Keep each page short (design_css.md is the size ceiling); link rather than
  duplicate AGENTS.md content (AGENTS = how, design pages = why).
- Toctree: extend the Development caption; consider an index blurb explaining
  the invariants-with-enforcement convention.
- No behaviour changes; docs-only PR; standard matrix + docs builds.

## Acceptance criteria

- Four pages rendered under Development, each with an enforcement-mapped
  invariants table; cross-links from AGENTS.md and the roadmap issue.
