# Implementation briefs

Self-contained work briefs for sphinx-design, derived from a full backlog triage
(56 open issues, 14 open PRs) and code review. Each brief is sized as **one PR**
and written so an autonomous agent can pick it up and complete it without extra
context. Read `AGENTS.md` first for repo conventions (tox commands, test
patterns, commit/PR format).

All file/line references are against commit `bbaf94a` (post v0.7.0).

## Cross-cutting principles (apply to every brief)

1. **Declarative configuration.** All `sd_*` config values must be expressible
   as plain TOML-compatible data (str/bool/int/list/dict of primitives — no
   callables, no Python objects, string enums rather than sentinel objects).
   New options go through the central config pattern established in brief 02.
   Rationale: config may later be read from a TOML file.
2. **Parser-portable syntax.** No new authored syntax whose meaning exists only
   in imperative Python raw-text processing. Components must be expressible as
   generic directives/roles + doctree transforms, so non-Python MyST
   implementations (a future Rust parser, formatters, LSPs) can understand
   documents structurally. Role microsyntax (e.g. `icon;height;classes`) is
   fine but must be documented as a stable grammar.
3. **Declarative tests.** Keep the snippet-file → XML/HTML regression pattern
   (`tests/test_snippets/`); fixtures double as a language-agnostic conformance
   suite.

## Index

| # | Brief | Type | Closes / supersedes | Depends on |
|---|-------|------|---------------------|------------|
| 01 | [backlog-hygiene](01-backlog-hygiene.md) | maintenance | PRs #205 #262 #237 #220 #203 #175 #221 #225 #226 #227 | — |
| 02 | [declarative-config](02-declarative-config.md) | refactor | — (foundation) | — |
| 03 | [button-i18n](03-button-i18n.md) | bug | #96 #44 #263 (via PR #264) | — |
| 04 | [static-assets](04-static-assets.md) | refactor/bug | #200 #235 (supersedes PR #241) | — |
| 05 | [ci-modernization](05-ci-modernization.md) | infra | dead codecov upload | — |
| 06 | [trusted-publishing](06-trusted-publishing.md) | infra | — | — |
| 07 | [spurious-child-warnings](07-spurious-child-warnings.md) | bug | #86 | — |
| 08 | [docs-quick-fixes](08-docs-quick-fixes.md) | docs | #172 #122 #184 #247 | — |
| 09 | [dropdown-card-text-classes](09-dropdown-card-text-classes.md) | bug | #40 + unreported class-wipe bug | — |
| 10 | [a11y-focus-and-aria](10-a11y-focus-and-aria.md) | a11y | #30 (+ lands PR #230) | — |
| 11 | [tabs-js-improvements](11-tabs-js-improvements.md) | bug/feature | #46 #239 #103(remainder) | 02 |
| 12 | [icon-toctree](12-icon-toctree.md) | bug | #99 #117 | — |
| 13 | [fontawesome-modernize](13-fontawesome-modernize.md) | feature/bug | #174 #242 #233 | 02 |
| 14 | [card-link-image-options](14-card-link-image-options.md) | feature | #170 #261 #152 #211 | — |
| 15 | [button-ref-targets](15-button-ref-targets.md) | bug | #110 #228 | — |
| 16 | [card-pure-parse](16-card-pure-parse.md) | refactor/feature | card `^^^`/`+++` redesign | 02 |
| 17 | [accordion](17-accordion.md) | new component | — | — |
| 18 | [steps](18-steps.md) | new component | — | — |
| 19 | [aside](19-aside.md) | new component | #97 | — |
| 20 | [tooltips](20-tooltips.md) | feature | #81 | — |
| 21 | [latex-output](21-latex-output.md) | bug | #107 #218 #179 | 04 |
| 22 | [testing-module](22-testing-module.md) | feature | #260 | — |
| 23 | [js-testing](23-js-testing.md) | infra | — | 11 helpful |
| 24 | [packaging-1.0](24-packaging-1-0.md) | release | — | most others |

## Execution plan

Each brief is one PR. Within a phase, briefs on **different tracks** can be
worked in parallel (including by parallel agents); briefs on the same track
share files and must land serially, in the order given.

**Phase 0 — unblock** *(serial, needs maintainer)*
- 01 backlog-hygiene — clears the open-PR queue and the close/answer issue
  sweep that later briefs reference.

**Phase 1 — foundations** *(after 01)*
- Track A: 02 declarative-config (three later briefs add fields to it)
- Track B: 03 button-i18n (also lands the builder-parametrized test fixture
  that 04 and 21 use) → then 04 static-assets (both touch
  `tests/conftest.py`; 04 also moves the asset paths that 10/11/23 refer to)
- Track C: 05 ci-modernization → 06 trusted-publishing (same workflow file)
- Track D: 07 spurious-child-warnings
- Track E: 08 docs-quick-fixes

**Phase 2 — independent fixes** *(after phase 1)*
- Track A (`badges_buttons.py`): 15 button-ref-targets → 20 tooltips
- Track B (`icons.py`): 12 icon-toctree → 13 fontawesome-modernize
- Track C (`dropdown.py`/`cards.py`): 09 dropdown-card-text-classes
- Track D: 22 testing-module
- Track E (tabs): 10 a11y-focus-and-aria (CSS + transform) ∥ 11
  tabs-js-improvements (JS only) — different files, safe in parallel

**Phase 3 — components & redesign** *(after 09, since 16 reworks the same
card code)*
- Track C continued: 16 card-pure-parse → 14 card-link-image-options
  (both rework `cards.py`; 14 last avoids three-way conflicts)
- Tracks F/G/H: 17 accordion, 18 steps, 19 aside — independent source
  files, but see the CSS-artifact rule below

**Phase 4 — long tail**
- 21 latex-output (needs 04) ∥ 23 js-testing (best after 11)

**Phase 5 — release**
- 24 packaging-1.0 (gates listed in the brief)

### File-conflict matrix (why the tracks are shaped this way)

| Shared file | Briefs touching it |
|---|---|
| `sphinx_design/cards.py` | 09, 14, 16 |
| `sphinx_design/badges_buttons.py` | 03, 15, 20 |
| `sphinx_design/icons.py` | 12, 13 |
| `sphinx_design/tabs.py` | 07, 10 |
| `sphinx_design/dropdown.py` | 09, 17 |
| `sphinx_design/extension.py` (registrations only) | 02, 04, 12, 17, 18, 19 — trivial conflicts, rebase freely |
| `tests/conftest.py` | 03, 04, 22 |
| `.github/workflows/ci.yml` | 05, 06, 23 |
| `pyproject.toml` | 01, 04, 23, 24 |

### The compiled-CSS rule (important for parallel agents)

Briefs 10, 14, 17, 18, 19 all change SCSS, and the committed minified
artifact (`sphinx_design/compiled/style.min.css`, moved by brief 04) will
conflict on **every** cross-merge. Never hand-merge it: after any rebase,
rerun `npm run css` (or `pre-commit run --all css`) and commit the freshly
regenerated file. Treat the SCSS sources as the merge surface, the compiled
file as derived output.

## Consciously not briefed (backlog — tracked in the roadmap issue)

Lower-priority/needs-decision items from the triage, deliberately excluded
from this set: #56 (download ref type), #133/#181 (carousel controls),
#157 (card colours), #164 (hyperlink targets as card links), #165 (menu
dropdowns — proposed out of scope), #177 (shibuya example), #182
(single-value `:columns:` behaviour change), #215 (pydata badge colours),
#217/#232 (nesting inside custom directives), #219 (vertical tabs), #234
(i18n of tables in tabs — investigation), plus two code TODOs: arbitrary
badge classes (`badges_buttons.py:15`) and a card-less dropdown style
(`dropdown.py:155`). Promote any of these to a brief when prioritised.
