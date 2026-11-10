# Change Log

## 0.8.0 - 2026-11-10

New components (accordion, aside, steps, vertical tab sets, and explicit card header and footer directives),
links that open in a new tab, badge tooltips, a plain-CSS build with no Sass,
tab selections that persist across pages and visits, accessibility fixes, FontAwesome v6 support,
and Octicons v19.42.0. Sphinx 7.2 or later is now required.

### Upgrade notes

- **Sphinx `>=7.2` is required** (Sphinx 7.0 and 7.1 are no longer supported); Python stays at `>=3.11` ({pr}`276`).
- **The `^^^` and `+++` card separators are deprecated and warn by default.**
  They still render as before, but the first card in a document that uses them emits one
  `design.card_legacy` warning, so a build run with `-W` fails until you do one of two things:
  - move the header and footer into the new `card-header` and `card-footer` directives
    (or the one-line `:header:` and `:footer:` options), which need sphinx-design 0.8.0 or later; or
  - add `"design.card_legacy"` to `suppress_warnings` in your `conf.py`.

  Once every card is migrated, set `sd_card_legacy_separators = False` to stop scanning for the separators.
  The plan is to turn the separators off by default in 1.0 and remove them in 2.0;
  the cards page has a migration table ({pr}`294`).
- **Tab selections persist in `localStorage`** instead of `sessionStorage`, so a chosen tab is remembered
  across browsing sessions as well as across pages.
  The storage key prefix is set by the new `sd_tabs_storage_prefix` option;
  set it to an empty string to disable persistence ({pr}`284`).
- **Static assets are served through Sphinx's `html_static_path`**, only for HTML-format builders.
  A `_sphinx_design_static` directory left in an existing build directory by an earlier version is unused
  and can be deleted ({pr}`276`).
- **The stylesheet is plain CSS**, generated without Sass.
  The `--sd-color-*-highlight` hover and focus shades are now derived at runtime with `color-mix()`
  (behind the old value as a static fallback), so overriding a `--sd-color-*` variable now also changes its hover shade ({pr}`290`).
- **The private `sphinx_design._compat.findall` helper is removed**; call `node.findall(...)` directly ({pr}`276`).
  The private `CardDirective._create_component` method is renamed `_create_slot`;
  the old name stays as an alias for one release ({pr}`294`).
- **`sd-card-text` is added only to the direct child paragraphs** of a card or dropdown body, and is added to
  a paragraph's classes instead of replacing them; paragraphs nested deeper (in admonitions, lists, nested tab sets)
  no longer get it ({pr}`278`).

### New

- ✨ `accordion` directive: groups `dropdown`s so that opening one closes the others,
  using the browser's native `<details name>` behaviour with no JavaScript; `:flush:` renders it edge to edge
  by {user}`chrisjsewell` in {pr}`291`
- ✨ `aside` directive: a call-out box floated beside the body text (`:align:`, `:width:`),
  rendered as a semantic `<aside>` in HTML and a plain titled container elsewhere
  by {user}`chrisjsewell` in {pr}`292` ({issue}`97`)
- ✨ `steps` and `step` directives for numbered procedures, with CSS-only number markers on an ordered list,
  `:start:` and `:color:` options by {user}`chrisjsewell` in {pr}`293`
- ✨ `card-header` and `card-footer` directives, and `:header:` and `:footer:` options,
  for card and grid-item-card headers and footers: the card body is parsed once as ordinary content,
  and errors in a header or footer report their own line (see the upgrade notes for the legacy separators)
  by {user}`chrisjsewell` in {pr}`294`
- ✨ Vertical tab sets: `tab-set` and `tab-set-code` take `:orientation: vertical`, which stacks the labels
  in a rail beside the selected panel from the `md` breakpoint up
  by {user}`kdeldycke` in {pr}`304` ({issue}`219`)
- ✨ Open links in a new tab: the `link-new-tab` flag on `card` and `grid-item-card`, and `new-tab` on
  `button-link` and `button-ref`, for URLs and internal references alike
  by {user}`dipinknair` in {pr}`298` ({issue}`170`)
- ✨ Badge tooltips: badge roles accept a trailing `` ; tooltip `` suffix, rendered as a native HTML `title`;
  for link and ref badges it applies after the explicit `text <target>` form, and `` \; `` escapes a literal semicolon
  by {user}`chrisjsewell` in {pr}`286` ({issue}`81`)
- ✨ Every badge role (plain, line, link and ref, in every colour) accepts a `tooltip` role option,
  so a reStructuredText custom role (`.. role:: bdg-stable(bdg-success)` with `:tooltip:`) or an extension
  can preset a tooltip; a `; tooltip` suffix still takes precedence
  by {user}`chrisjsewell` in {pr}`316`
- ✨ A line block in `button-link` or `button-ref` text renders as separate lines
  (`<br />` in HTML, `\newline{}` in LaTeX), each line its own gettext message
  by {user}`Cherith1222` in {pr}`308` and {user}`chrisjsewell` in {pr}`315` ({issue}`156`)
- ✨ A URL fragment that targets a tab (e.g. `page.html#tab-name`), or an element inside a tab panel,
  opens that tab, on load and on `hashchange` by {user}`chrisjsewell` in {pr}`284` ({issue}`239`)
- ✨ FontAwesome v6 roles (`fa-solid`, `fa-brands`, `fa-regular`), and CSS loading via the new
  `sd_fontawesome_source` and `sd_fontawesome_cdn_url` options (the supported path for FontAwesome Pro kits)
  by {user}`chrisjsewell` in {pr}`285` ({issue}`174`)
- ✨ `sd_fontawesome_version` makes icon role names version-agnostic: any spelling (`fas`, `fa-solid`, ...)
  can emit the FontAwesome `"4"`, `"5"` or `"6"` class scheme, so upgrading FontAwesome is a one-line `conf.py` change;
  the default `"as-named"` keeps emitting the role name as before by {user}`chrisjsewell` in {pr}`288` ({issue}`174`)
- ✨ `sphinx_design.testing` module with the `normalize_doctree_xml` helper, for downstream extensions'
  doctree regression tests by {user}`chrisjsewell` in {pr}`277` ({issue}`260`)

### Improve

- 👌 Keyboard focus rings restored on tab labels, dropdown summaries, buttons and stretched-link cards
  (with `:focus-visible`, so they do not show on mouse click) by {user}`gabalafou` in {pr}`230`, carried in {pr}`283`
- 👌 Each tab label carries an `aria-controls` attribute naming its panel
  (this is not the full WAI-ARIA tabs pattern) by {user}`chrisjsewell` in {pr}`283` ({issue}`30`)
- 👌 The tab hover colour is the active colour at 80% opacity, so a hovered tab no longer looks selected
  by {user}`dchaudhari7177` in {pr}`303` ({issue}`301`)
- 👌 `sd_fontawesome_latex` also accepts `"fontawesome5"` (loading `fontawesome5.sty` and emitting `\faIcon{...}`),
  resolving package clashes with themes that load it; `True` and `False` work as before
  by {user}`chrisjsewell` in {pr}`285` ({issue}`242`)
- 👌 All `sd_*` settings are declared in one typed configuration, and an invalid value warns
  (`design.config`) and falls back to the default by {user}`chrisjsewell` in {pr}`274`
- 👌 Plain-CSS stylesheet generated by a dependency-free Python tool (no Sass or Node),
  with the dead vendor-prefixed declarations removed by {user}`chrisjsewell` in {pr}`290`

### Fix

- 🐛 Synced tabs stay in sync when activated by keyboard or click-and-drag
  by {user}`chrisjsewell` in {pr}`284` ({issue}`46`)
- 🐛 A `tab-set` with children other than `tab-item` warns for each one and renders the valid tabs,
  instead of crashing with a `ValueError` by {user}`chrisjsewell` in {pr}`258` ({issue}`243`)
- 🐛 Comments, hyperlink targets and system messages inside `grid`, `card-carousel`, `tab-set` and `tab-set-code`
  no longer warn as invalid children, and targets are kept so references to them resolve,
  including anchors to targets inside tabs by {user}`chrisjsewell` in {pr}`271` and {pr}`275` ({issue}`86`)
- 🐛 Buttons survive gettext translation: translated `button-link` and `button-ref` keep their styling and links
  by {user}`sneakers-the-rat` in {pr}`264`, carried in {pr}`270` ({issue}`96`, {issue}`44`, {issue}`263`)
- 🐛 `button-ref` keeps whitespace in reference targets (so multi-word labels, such as those from
  `autosectionlabel`, resolve; `ref` targets are lowercased like the `:ref:` role), and renders nested inline content
  like `button-link` by {user}`chrisjsewell` in {pr}`281` ({issue}`110`, {issue}`228`)
- 🐛 The card and grid-item-card `:link:` option keeps whitespace in reference targets
  by {user}`chrisjsewell` in {pr}`282` ({issue}`110`)
- 🐛 Messages and gettext locations for button text name its first content line in reStructuredText
  (they named a later line, or the including page for a button in an included file)
  by {user}`chrisjsewell` in {pr}`315`
- 🐛 Icon roles no longer leak SVG markup into toctree labels and the search index,
  and `article-info` icons regain their `sd-pr-2` spacing by {user}`chrisjsewell` in {pr}`279` ({issue}`99`)
- 🐛 Dropdowns no longer overwrite user classes on their paragraphs with `sd-card-text`
  by {user}`chrisjsewell` in {pr}`278` ({issue}`40`)
- 🐛 Non-HTML builds no longer gain a spurious `_sphinx_design_static` directory
  by {user}`chrisjsewell` in {pr}`276` ({issue}`200`, {issue}`235`)
- 🐛 The `sd_fontawesome_latex` row of the global options table no longer splits into an extra cell
  by {user}`yvonnefroehlich` in {pr}`297`

### Dependencies

- ⬆️ Sphinx `>=7.2,<10` by {user}`chrisjsewell` in {pr}`276`
- ⬆️ Octicons v19.8.0 to v19.42.0: 81 new icons (such as `agent`, `library`, `release` and `sparkle`),
  12 redrawn icons and 37 extra sizes; no icon is removed (`commit` stays available)
  by {user}`kdeldycke` in {pr}`309`
- ⬆️ Theme extras refreshed to current releases by {user}`chrisjsewell` in {pr}`267`,
  and the `theme-pydata` extra allows `pydata-sphinx-theme<0.25` ({pr}`313`)
- ⬆️ The build backend allows `flit_core>=3.4,<5` by {user}`chrisjsewell` in {pr}`312`

### Docs

- 📚 Buttons are documented as links styled as buttons, with an accessibility note
  by {user}`gabalafou` in {pr}`158`, carried in {pr}`287`
- 📚 Sizing classes, multiple grid rows, links to synchronised tabs, and the MyST extensions the examples need
  by {user}`chrisjsewell` in {pr}`273` ({issue}`172`, {issue}`122`, {issue}`184`, {issue}`247`)
- 📚 A browser support policy (Baseline Widely Available) and a "Design: the CSS pipeline" page
  by {user}`chrisjsewell` in {pr}`290`
- 📚 Fix a typo in the get started page by {user}`stefmolin` in {pr}`229`

### Internal

- 🔧 Releases are published to PyPI with trusted publishing, and every pull request builds and checks the
  distributions by {user}`chrisjsewell` in {pr}`311`
- 🔧 CI compiles the documentation PDF by {user}`chrisjsewell` in {pr}`289`
- ♻️ Remove the unused `OCTICON_VERSION` and `OCTICON_CSS` constants by {user}`ftnext` in {pr}`205`, carried in {pr}`266`

## 0.7.0 - 2026-01-19

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
