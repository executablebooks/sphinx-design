# Brief 25: Drop Sass — plain CSS + a Python utility generator, Baseline support policy

**Type**: refactor + infra + docs | **Size**: medium-large | **Closes**: — (removes the
Node/sass toolchain; fixes the stale "Supported browsers" docs; unblocks a
themeability gap).
**Depends on**: briefs 10 and 20 merged (the last SCSS-touching PRs before Phase 3).
**Must land BEFORE** the Phase 3 style-heavy briefs (14, 16, 17, 18, 19) — see
"Sequencing rationale" at the end.

## Motivation (all verified against main)

The Sass dependency reduces to exactly three things:

1. **26 loops** (`@each`/`@for`, across 11 of 16 partials) generating the
   mechanical utility families: spacing, grid columns × breakpoints,
   semantic-color variants, borders, sizing, display, text.
2. **Two build-time color computations**: `text-color()` (contrast picker,
   `style/_colors.scss:45`) and `mix(black, $value, 15%)` for the
   `--sd-color-*-highlight` hover shades (`style/_variables.scss:10`).
3. **Concat + minify** of ~1360 SCSS lines into the 49KB
   `sphinx_design/static/sphinx-design.min.css`.

There are **zero** mixins/includes and zero darken/lighten calls.

Costs of keeping it:

- Node in the toolchain solely for `sass` (`package.json` pins dart-sass
  `^1.35.2`, from 2021; the perennial "bump the sass pin" chore).
- **Baked hover shades don't track user theme overrides**: `mix()` runs at
  compile time, so overriding `--sd-color-primary` does NOT update
  `--sd-color-primary-highlight`. Runtime `color-mix()` fixes this.
- ~150 hand-maintained dead vendor prefixes (`-ms-flex*` for IE10/11 flexbox
  etc.) for browsers that cannot run the package anyway (dropdowns are
  `<details>`, theming is CSS custom properties — neither ever worked in IE).
- The docs' "Supported browsers" list (`docs/get_started.md:89-98`) is a 2021
  copy of Bootstrap v5.0.2's browserslist, claiming "Explorer >= 12" — false
  for years; there is no `.browserslistrc` and no autoprefixer, so the list
  never described reality.

## What to do

### 1. Two-tier plain CSS replaces `style/*.scss`

- **Hand-authored component CSS**: `style/` becomes plain `.css` files
  (`cards.css`, `dropdown.css`, `tabs.css`, `badge.css`, `button.css`,
  `icons.css`, `animations.css`, `overrides.css`, …) — a mostly-mechanical
  port of the non-loop SCSS. Avoid native CSS nesting in the ported output
  (write expanded selectors) so the shipped CSS stays maximally compatible;
  revisit once nesting is comfortably inside the support policy.
- **Generated utility CSS**: a Python generator emits the loop-derived
  families (spacing, grid columns/breakpoints, color variants, borders,
  sizing, display, text) from declarative data.

### 2. The generator

- Location: `tools/generate_css.py` (NOT shipped in the wheel). Input: a
  declarative data file — prefer TOML (`style/design.toml`) holding the
  palette (with per-color precomputed `text` contrast values, replacing the
  Sass `text-color()` function), spacing scale, breakpoints map, and column
  count. This aligns with the project's declarative/TOML direction, and the
  data file is reusable by any future non-Python implementation.
- Output: deterministic CSS (stable ordering); the script concatenates
  hand-authored files + generated utilities and writes the single minified
  artifact `sphinx_design/static/sphinx-design.min.css` (same path/name — the
  served filename is public API). Minification can be a simple deterministic
  pass (strip comments/whitespace); gzip does the heavy lifting on the wire.
- Pre-commit: replace the `css` hook (`language: node`, `npm run css`) with a
  `language: python` hook running the generator. **Delete `package.json`**
  (it exists only for sass). The `tsc` hook STAYS — pre-commit manages its
  node env via `additional_dependencies: [typescript]` with no repo-level
  node config needed.
- Add a pytest that runs the generator and asserts the committed artifact is
  up to date (staleness guard, mirroring what the hook enforces — CI-visible).

### 3. Runtime `color-mix()` for highlight shades

Replace the baked `--sd-color-<color>-highlight` values with:

```css
--sd-color-primary-highlight: #0056b3;                     /* static fallback */
--sd-color-primary-highlight: color-mix(in srgb, black 15%, var(--sd-color-primary));
```

(fallback line first — old browsers ignore the second declaration). This is a
**behavioural improvement**: user overrides of `--sd-color-primary` now
propagate to hover states. Changelog-note it. Keep the computed fallback
values byte-identical to today's baked output.

### 4. Vendor-prefix purge

Drop all `-ms-*` (flexbox-for-IE) and the `-moz-`/`-webkit-` animation /
box-sizing / user-select prefixes **after checking each against current
caniuse data** at implementation time. Expected keepers (comment each in the
source with why): `-webkit-details-marker`, `-webkit-tap-highlight-color`
(genuine Safari-specific resets); re-verify `-webkit-user-select` (needed
until Safari 16.4 — keep if the policy floor still includes it, else drop).

### 5. Baseline support policy (docs)

Replace the version list in `docs/get_started.md` ("Supported browsers")
with a policy statement:

> sphinx-design targets **Baseline Widely Available** web features —
> everything interoperable across Chrome, Edge, Firefox and Safari for at
> least 30 months (in practice: evergreen browsers from the last ~2½ years).
> Internet Explorer is not supported. Individual features may additionally
> use *Baseline Newly Available* CSS with graceful degradation, noted in
> their documentation.

Link to <https://web.dev/baseline>. Remove the Bootstrap browserslistrc
"mirror" sentence. This policy is the gate for future CSS decisions (e.g.
the planned accordion's `<details name>` is Newly Available and degrades to
independently-collapsible dropdowns — document such exceptions per feature).

### 6. Repo docs

Update `AGENTS.md` (two sections describe the SCSS/npm pipeline) and the
briefs README's compiled-CSS rule to the new generator command. Changelog:
one `♻️ IMPROVE` entry (toolchain + color-mix theming note + prefix purge)
and one `📚 DOCS` entry (support policy).

## Verification (the migration must be provable, not eyeballed)

1. **Rule-set equivalence check**: a script (committed under `tools/`,
   invoked by a test) parses the pre-migration artifact (from
   `git show <base>:sphinx_design/static/sphinx-design.min.css`) and the new
   output with `tinycss2`, normalizes (whitespace, serialization), and
   asserts the rule sets are identical EXCEPT an explicit allowlist of
   intentional diffs: (a) dropped prefixes (enumerated), (b) the
   `color-mix()` + fallback pairs (enumerated), (c) nothing else. The PR
   description shows the allowlist verbatim.
2. **Visual spot check**: docs build on all theme envs; optional Playwright
   screenshot diff (chromium at /opt/pw-browsers) of a cards/tabs/dropdowns
   page before/after — record outcome either way.
3. Standard validation matrix + pinned rails (the Python suite is mostly
   unaffected, but the artifact-staleness test and docs builds run
   everywhere).

## Acceptance criteria

- `package.json` gone; no `sass` anywhere; pre-commit `css` hook is Python;
  `tsc` hook still green.
- Equivalence check passes with only the enumerated intentional diffs.
- Overriding `--sd-color-primary` in a test page changes button/badge hover
  shades (new behaviour, asserted in a test or documented repro).
- Docs support-policy section replaced; AGENTS.md pipeline sections updated.
- Served artifact path/name unchanged; `--sd-*` variable names unchanged
  (public API).

## Sequencing rationale (why before Phase 3)

Phase 3 briefs (14, 16, 17, 18, 19) all ADD styles. Landing 25 first means:
(1) new component styles are authored once, in the final system — not
written in SCSS and migrated later; (2) the equivalence check runs against a
quiet stylesheet, keeping the migration provably no-op; (3) the compiled
artifact — which conflicts on every cross-merge — is only being touched by
one branch; (4) Phase 3 features get the Baseline policy and the generator's
data-driven color/utility families from day one (an accordion color variant
is a data entry, not a new `@each`). It must land AFTER briefs 10/20 so
their SCSS changes are migrated rather than rebased under the migration.
