# Change Log

## v0.3.0 - 2022-08-22

- ⬆️ Update Materials Design Icons to v4.0.0-46-gc9e5528, thanks to @2bndy5 (#69)
- 🐛 FIX: dropdown/tab-item `:name:` options (#91)
- 🐛 FIX: Docs build against non-html formats (#88)
- 👌 IMPROVE: Add card options `class-img-top`/`class-img-bottom` (#92)
- 👌 IMPROVE: Add `link-alt` to fix card link accessibility (#89)
  - adds the `link-alt` option to `card` (and `grid-item-card`) directives, in order to assign a discernable name to the link (for screen readers).
- 👌 IMPROVE: Make tab ids deterministic (#93)
  - Use increasing indices, rather than UUIDs
- 🔧 MAINTAIN: Fix docutils `PendingDeprecationWarning` (#94)
- 📚 DOCS: Update font awesome icons (#64)

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.2.0...v0.3.0>

## v0.2.0 - 2022-06-14

- ⬆️ Support Sphinx v5, drop v3
- ⬆️ Add Python 3.10 support

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.1.0...v0.2.0>

## v0.1.0 - 2022-04-21

- ✨ NEW: Add material design icons roles, thanks to @2bndy5 in [#41](https://github.com/executablebooks/sphinx-design/pull/41)
- ⬆️ UPGRADE: octicons to v16.1.1, thanks to @pocek in [#43](https://github.com/executablebooks/sphinx-design/pull/43)
- 🐛 FIX: Links in card titles by @chrisjsewell in [#59](https://github.com/executablebooks/sphinx-design/pull/59)
- 🐛 FIX: Exception on missing card link by @chrisjsewell in [#60](https://github.com/executablebooks/sphinx-design/pull/60)
- 🔧 MAINTAIN: Move from setuptools to flit for package build by @chrisjsewell in [#58](https://github.com/executablebooks/sphinx-design/pull/58)
- 🔧 MAINTAIN: Drop furo-specific stylesheet, thanks to @pradyunsg in [#22](https://github.com/executablebooks/sphinx-design/pull/22)

**Full Changelog**: <https://github.com/executablebooks/sphinx-design/compare/v0.0.13...v0.1.0>

## v0.0.13 - 2021-10-27

✨ NEW: add icon `far` role (#35), thanks to @OriolAbril

👌 IMPROVE: Styling for tabs (#21), thanks to @pradyunsg

👌 IMPROVE: Properly remove the border on dropdown card body (#23), thanks to @pradyunsg

🐛 FIX: `sd-outline-*` classes color (#25)

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
