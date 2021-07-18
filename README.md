# sphinx-design (IN-DEVELOPMENT)

A sphinx extension for designing beautiful, size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

## Supported browsers

- Chrome >= 60
- Firefox >= 60
- Firefox ESR
- iOS >= 12
- Safari >= 12
- Explorer >= 12

(Mirrors: <https://github.com/twbs/bootstrap/blob/v5.0.2/.browserslistrc>)

## Comparison to sphinx-panels

This package is an iteration on sphinx-panels and intends to replace it.

- Replaces `panel` directive with top-level `grid` + children `grid-item-card`
  - less "bespoke" syntax
  - `grid-item` can be used when no card is needed
  - `card` can be used independently of grids
- Minimises direct use of CSS classes (encourage to not use them)
  - More declarative, easy to understand options
  - Easier to work with non-HTML outputs
  - Easier to improve/refactor
- Updated Bootstrap CSS v4 -> v5
  - top-level grid can define both column numbers and gutter sizes
- All CSS classes are prefixed with `sd-` (no clash with other theme/extension CSS)
- All colors use CSS variables (customisable)

## TODO

- directives:
  - dropdowns (optional), dropdown
  - tabs (optional), tab

- roles:
  - icons: opticon, fa

naming of directives/roles: standard prefix?

How to handle JS

handle latex

is `grid`/`grid-item` both having `columns`, with different meanings, confusing?

card header/footer syntax?

Use autoprefixer when compiling SASS (see <https://getbootstrap.com/docs/5.0/getting-started/browsers-devices/#supported-browsers>)

horizontal card (grid row inside card),
avatars (rounded images)
