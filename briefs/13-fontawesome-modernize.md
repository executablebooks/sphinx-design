# Brief 13: FontAwesome modernization (v6 classes, Pro compatibility, LaTeX package)

**Type**: feature + bug fix | **Size**: medium | **Closes**: #174, #242, #233.
**Depends on**: brief 02 (config fields).

## Context (verified)

- sphinx-design does **not** bundle FontAwesome CSS. Docs instruct users to
  load it from a CDN (`docs/badges_buttons.md:233-246`); the docs' own
  `conf.py` loads `font-awesome/6.1.1/all.min.css`.
- Roles registered: `fa`, `fas`, `fab`, `far` (`sphinx_design/icons.py:32-34`)
  emitting `<span class="fas fa-<icon> ...">` — the **v4/v5 class scheme**.
  FA6 canonical classes are `fa-solid`/`fa-brands`/`fa-regular`; the old
  names still work in FA6 free but are the source of Pro-kit conflicts
  (#174: free-CDN + `fas` classes fight the user's Pro kit which expects
  v6 names and its own font-face).
- LaTeX: `sd_fontawesome_latex` (bool) adds the **`fontawesome`** package
  (`icons.py:217-219`) and renders `\faicon{...}` (`icons.py:222-234`). #242:
  themes/other extensions load `fontawesome5`, which errors if `fontawesome`
  ideas of the font are already loaded (and vice versa); `fontawesome5` also
  uses different macros (`\faIcon{...}`).

## What to do

### 1. Add v6-style roles (#174 groundwork, #233 enabler)

Register `fa-solid`, `fa-brands`, `fa-regular` roles alongside the existing
four (which stay for compatibility). Emit exactly the classes the role name
implies (`fa-solid fa-rocket`), no legacy aliases mixed in. Docs: mark
`fa`/`fas`/`fab`/`far` as legacy, recommend v6 names.

### 2. Config for icon-font expectations (#174)

Add to `SdConfig` (brief 02), TOML-friendly string enum:

```python
fontawesome_source: str = "none"  # "none" | "cdn"
fontawesome_cdn_url: str = "<current documented cdnjs 6.x URL>"
```

- `"none"` (default — current behaviour): sphinx-design loads nothing; user
  or theme provides FA. Pro users (#174) simply don't opt in and remove
  their own duplicate free import.
- `"cdn"`: sphinx-design adds the CSS via `app.add_css_file(url)` so users
  stop hand-editing `html_css_files` (removes the docs' copy-paste step).
Update `docs/badges_buttons.md` FA section around this config, including an
explicit "using FontAwesome Pro kits" subsection: set `"none"`, load the kit,
use v6 role names.

### 3. LaTeX package selection (#242)

Replace bool-only behaviour with a string enum (keep the bool working):

```python
fontawesome_latex: str | bool = False
# False/"none": skip icons in latex (warn once per build, not per icon)
# True/"fontawesome": current behaviour (\faicon via fontawesome.sty)
# "fontawesome5": add fontawesome5.sty, emit \faIcon{<icon>} (and
#                 \faIcon[regular]{...} for far/fa-regular styles)
```

Accept the legacy `True` (== "fontawesome") for compatibility; validator
normalises. For "fontawesome5", pass through the style: `fab`→`\faIcon[brands]`
isn't valid — check the fontawesome5 manual: brands use `\faIcon{github}`
resolved by name; regular via optional arg. Implement per the manual and note
the mapping in docs. Do **not** attempt collision detection with
theme-loaded packages; instead document: "if your theme already loads
fontawesome5, set `sd_fontawesome_latex = 'fontawesome5'` so both agree"
(this resolves the #242 clash, which comes from mixing the two packages).

### 4. Warning hygiene

`visit_fontawesome_warning` and the latex warning fire **per icon node**
(`icons.py:222-246`); throttle to once per builder run (module-level flag or
`logger.warning(..., once=True)` — Sphinx supports `once=True`).

## Tests

- Role output: `fa-solid` role → span classes exactly
  `["fa-solid", "fa-rocket"]` (doctree regression, rst + myst snippets).
- Config: `fontawesome_source="cdn"` → built HTML head contains the CDN link
  exactly once; `"none"` → absent.
- LaTeX: with `fontawesome_latex="fontawesome5"`, `latex` build of an FA
  snippet contains `\usepackage{fontawesome5}` and `\faIcon{...}`; with
  `False`, exactly one warning per build.

## Acceptance criteria

- #174: documented, supported Pro path with no forced free import.
- #242 reproduction: latexpdf build with fontawesome5-based setup succeeds.
- #233 (FA icons for dropdowns) is NOT implemented here, but note in the PR
  that the `sd_icon`/role groundwork makes a `:icon: fa-solid;rocket` option
  on dropdowns feasible — file/refresh a follow-up comment on #233.
- All legacy spellings keep working (roles `fa*`, config `True`/`False`).
