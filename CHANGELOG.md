# Change Log

## Unreleased

- 🐛 FIX: `card`/`grid-item-card` `:link:` no longer strips whitespace from reference targets (and lowercases them for `link-type: ref`, matching the `:ref:` role), completing the fix for {issue}`110` ({pr}`282`)
- 🐛 FIX: `button-ref` no longer strips whitespace from reference targets, so
  multi-word labels (e.g. from `autosectionlabel`) resolve correctly
  ({pr}`281`, {issue}`110`)
- 🐛 FIX: `button-ref` now renders rich/nested inline content (emphasis, icons,
  etc.) identically to `button-link`, instead of flattening it to plain text
  during cross-reference resolution ({pr}`281`, {issue}`228`)
- 🐛 FIX: Inline icon roles no longer leak SVG markup into toctree labels and the search index ({pr}`279`, {issue}`99`)
- 🐛 FIX: `article-info` octicons regain their `sd-pr-2` spacing class (previously silently dropped by the HTML writer) ({pr}`279`)
- 🐛 FIX: Paragraphs inside dropdowns no longer have user classes overwritten by `sd-card-text`, and card/dropdown body styling is applied only to direct child paragraphs, not nested content ({pr}`278`, {issue}`40`)
- ✨ NEW: `sphinx_design.testing` module with the `normalize_doctree_xml` helper, for downstream extensions' doctree regression tests ({pr}`277`, {issue}`260`)
- ♻️ IMPROVE: Static assets (CSS/JS) are now served via Sphinx's standard
  `html_static_path` mechanism, rather than being written directly into the
  build output; non-HTML builds no longer gain a spurious
  `_sphinx_design_static` directory ({pr}`276`, {issue}`200`, {issue}`235`).
  A stale `_sphinx_design_static` directory left in an existing HTML build
  directory by previous versions is unused and can safely be deleted.
- ⬆️ UPGRADE: Sphinx `>=7.2` is now required ({pr}`276`)
- 🗑️ REMOVE: The private `sphinx_design._compat.findall` helper has been
  removed (docutils `Element.findall` is guaranteed by the Sphinx floor);
  any code importing it should call `node.findall(...)` directly ({pr}`276`)
- 🐛 FIX: buttons are no longer destroyed by gettext translation:
  translated `button-link`/`button-ref` keep their styling and links
  (gettext now targets only the button text), thanks to {user}`sneakers-the-rat`
  in {pr}`264` ({issue}`96`, {issue}`44`, {issue}`263`)

## 0.7.0 - 2025-01-19

### Dependencies

- ⬆️ Drop Python 3.9 & 3.10, support Python 3.14 by {user}`chrisjsewell` in {pr}`250`
- ⬆️ Drop Sphinx v6, add Sphinx v9 support by {user}`chrisjsewell` in {pr}`250` and {pr}`255`
- ⬆️ Update Material Design Icons to v4.0.0-116-ge9da21 by {user}`2bndy5` in {pr}`223`

### Docs

- 📚 Document `muted`, `white`, and `black` semantic colors by {user}`agriyakhetarpal` in {pr}`216`

## 0.6.1 - 2024-08-02

- ⬆️ Update sphinx to >=6,<9 by {user}`chrisjsewell` in {pr}`212`
- 👌 Reduce right-padding of dropdown title by {user}`chrisjsewell` in {pr}`198`

## 0.6.0 - 2024-05-23

### Dependencies

* ⬆️ Python v3.9-3.12 by {user}`chrisjsewell` in {pr}`186`
* ⬆️ Octicon icons to v19.8.0 by {user}`ffvpor` in {pr}`171`

### New

#### ✨ Create custom directives

You can use the `sd_custom_directives` configuration option in your `conf.py` to add custom directives, with default option values:

```python
sd_custom_directives = {
  "dropdown-syntax": {
    "inherit": "dropdown",
    "argument": "Syntax",
    "options": {
      "color": "primary",
      "icon": "code",
    },
  }
}
```

The key is the new directive name to add, and the value is a dictionary with the following keys:

- `inherit`: The directive to inherit from (e.g. `dropdown`)
- `argument`: The default argument (optional, only for directives that take a single argument)
- `options`: A dictionary of default options for the directive (optional)

by {user}`chrisjsewell` in {pr}`194`

#### ✨ sync tabs by URL query parameters

Synchronised tabs can now be selected by adding a query parameter to the URL, for that sync-group, such as `?code=python` for

```restructuredtext
.. tab-set-code::

    .. literalinclude:: snippet.py
        :language: python

    .. literalinclude:: snippet.js
        :language: javascript
```

The last selected tab key, per group, is also persisted to `SessionStorage`

by {user}`mikemckiernan` and {user}`chrisjsewell` in {pr}`196`

### Improve

* 👌 Use reference name by default for internal link cards by {user}`gabalafou` in {pr}`183`
* 👌 Improve specificity of JS function name by {user}`danirus` in {pr}`153`
* 👌 Remove duplicate CSS hashing for sphinx >= 7.1 by {user}`chrisjsewell` in {pr}`193`

#### 👌 Improve `dropdown` title bar

There are three visible changes:

1. The "default" behaviour of the right chevron is to go from right-facing (closed) to down-facing (open), instead of down-facing (closed) to up-facing (open). There is also a rotate transition on opening/closing.
The old default behaviour can be retained by using the new `:chevron: down-up` directive option.
2. The prefix icon (optional), title text, and chevron state icon are now all better aligned
3. The top/bottom padding is now 0.5em instead of 1em

The PR also introduces three new CSS variables to control font sizes of the dropdown:

```css
--sd-fontsize-tabs-label: 1rem;
--sd-fontsize-dropdown-title: 1rem;
--sd-fontweight-dropdown-title: 700;
```

Internally, the HTML / CSS is changed, such that the title is now an `inline-flex` box, with three columns arranged with `justify-content: space-between`:

| icon (optional) | text (`flex-grow: 1`) | state chevron |
| -------------- | -------------------- | -------------- |
|                |                      |                |

Also, the state chevron was previously two distinct SVGs (with one hidden), but now is one that get rotated on open/close.

by {user}`chrisjsewell` in {pr}`192`

### Fix

* 🐛 Fix tab-item label with nested syntax by {user}`Praecordi` in {pr}`135`
* 🐛 Fix do not close `input` tag by {user}`chrisjsewell` in {pr}`195`

### Internal

* 📚 Update theme versions by {user}`chrisjsewell` in {pr}`189`
* 📚 Make octicon list a table by {user}`chrisjsewell` in {pr}`188`
* 📚 Add sphinx-immaterial to doc theme builds by {user}`chrisjsewell` in {pr}`190`
* 📚 Change syntax dropdown color by {user}`chrisjsewell` in {pr}`191`

* 🔧 Add FIPS compliant flag to md5 call by {user}`gabor-varga` in {pr}`162`
* 🔧 define `build.os` for RTD to fix build by {user}`sciencewhiz` in {pr}`176`
* 🔧 Move to ruff by {user}`chrisjsewell` in {pr}`185`

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.5.0...v0.6.0>

## 0.5.0 - 2023-07-27

* ⬆️ Drop Python 3.7 support, by {user}`chrisjsewell` in {pr}`146`
* ⬆️ UPGRADE: sphinx>=5,<8, by {user}`chrisjsewell` in {pr}`148`

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.4.1...v0.5.0>

## v0.4.0 - 2023-04-13

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.3.0...v0.4.0>

### Enhancements made

- Make default blue color a11y friendly. {pr}`124` ({user}`feanil`, {user}`choldgraf`)
- Make card titles translatable {pr}`113` ({user}`jpmckinney`, {user}`chrisjsewell`)

### Version upgrades

- Sphinx 6.x. {pr}`106`
- Support for Python 3.11 {pr}`105`

### Contributors to this release

The following people contributed discussions, new ideas, code and documentation contributions, and review.
See [our definition of contributors](https://github-activity.readthedocs.io/en/latest/#how-does-this-tool-define-contributions-in-the-reports).

([GitHub contributors page for this release](https://github.com/executablebooks/sphinx-design/graphs/contributors?from=2022-08-22&to=2023-04-12&type=c))

## v0.3.0 - 2022-08-22

- ⬆️ Update Materials Design Icons to v4.0.0-46-gc9e5528, thanks to {user}`2bndy5` ({pr}`69`)
- 🐛 FIX: dropdown/tab-item `:name:` options ({pr}`91`)
- 🐛 FIX: Docs build against non-html formats ({pr}`88`)
- 👌 IMPROVE: Add card options `class-img-top`/`class-img-bottom` ({pr}`92`)
- 👌 IMPROVE: Add `link-alt` to fix card link accessibility ({pr}`89`)
  - adds the `link-alt` option to `card` (and `grid-item-card`) directives, in order to assign a discernable name to the link (for screen readers).
- 👌 IMPROVE: Make tab ids deterministic ({pr}`93`)
  - Use increasing indices, rather than UUIDs
- 🔧 MAINTAIN: Fix docutils `PendingDeprecationWarning` ({pr}`94`)
- 📚 DOCS: Update font awesome icons ({pr}`64`)

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.2.0...v0.3.0>

## v0.2.0 - 2022-06-14

- ⬆️ Support Sphinx v5, drop v3
- ⬆️ Add Python 3.10 support

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.1.0...v0.2.0>

## v0.1.0 - 2022-04-21

- ✨ NEW: Add material design icons roles, thanks to {user}`2bndy5` in {pr}`41`
- ⬆️ UPGRADE: octicons to v16.1.1, thanks to {user}`pocek` in {pr}`43`
- 🐛 FIX: Links in card titles by {user}`chrisjsewell` in {pr}`59`
- 🐛 FIX: Exception on missing card link by {user}`chrisjsewell` in {pr}`60`
- 🔧 MAINTAIN: Move from setuptools to flit for package build by {user}`chrisjsewell` in {pr}`58`
- 🔧 MAINTAIN: Drop furo-specific stylesheet, thanks to {user}`pradyunsg` in {pr}`22`

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.0.13...v0.1.0>

## v0.0.13 - 2021-10-27

✨ NEW: add icon `far` role ({pr}`35`), thanks to {user}`OriolAbril`

👌 IMPROVE: Styling for tabs ({pr}`21`), thanks to {user}`pradyunsg`

👌 IMPROVE: Properly remove the border on dropdown card body ({pr}`23`), thanks to {user}`pradyunsg`

🐛 FIX: `sd-outline-*` classes color ({pr}`25`)

## v0.0.11 - 2021-09-08

✨ NEW: Add `ref-type` option to `button-ref` directive

## v0.0.10 - 2021-08-08

✨ NEW: Add `grid-item` directive `child-direction` and `child-align` options

✨ NEW: Add `card` directive `img-background` option

## v0.0.9 - 2021-06-08

♻️ REFACTOR: `test_sd_hide_root_title` to `sd_hide_title` front-matter

👌 IMPROVE: dropdown chevrons

## v0.0.8 - 2021-06-08

✨ NEW: Add `test_sd_hide_root_title` config option to hide the root title.

👌 IMPROVE: `sd-card-hover:hover` add scale 101%

📚 DOCS: Update landing page

## v0.0.7 - 2021-05-08

✨ NEW: Add `reverse` option for `grid` directive

✨ NEW: Add animations

## v0.0.6 - 2021-04-08

✨ NEW: Add `card-carousel` directive

## v0.0.5 - 2021-28-07

👌 IMPROVE: Make octicon's size variable

## v0.0.4 - 2021-28-07

👌 IMPROVE: Allow `auto` for grid columns

## v0.0.3 - 2021-26-07

👌 IMPROVE: Add more CSS classes and add documentation 📚

## v0.0.2 - 2021-23-07

Improve documentation 📚

## v0.0.1 - 2021-22-07

Initial release 🎉
