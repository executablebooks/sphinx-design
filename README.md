# sphinx-design (IN-DEVELOPMENT)

A sphinx extension for designing beautiful, size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

**NOTE**: This package is an iteration on sphinx-panels and intends to replace it.

Difference:

- Replaces `panel` directive with top-level `grid` + children `grid-item-card`
  - less "bespoke" syntax
  - `grid-item` can be used when no card is needed
  - `card` can be used independently of grids
- Minimises direct use of CSS classes (encourage to not use them)
- Updated Bootstrap CSS v4 -> v5
  - top-level grid can define both column numbers and gutter sizes
- All CSS classes are prefixed with `sd-` (no clash with other theme/extension CSS)
- All colors use CSS variables (customisable)

## TODO

- directives:
  - dropdowns (optional), dropdown
  - tabs (optional), tab
  - link-button

- roles:
  - icons: opticon, fa

naming of directives/roles: standard prefix?

How to handle JS

handle latex

is grid/grid-item both having `columns`, with different meanings, confusing?

card header/footer syntax?

card title/subtitle (card tite could be argument?, but ideally would also be ~h5 tag)

Use autoprefixer when compiling SASS

horizontal card (grid row inside card),
avatars (rounded images)
