# sphinx-design (IN-DEVELOPMENT)

A sphinx extension for designing beautiful, view size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

All components are principally based on CSS (not JavaScript),
meaning they will be responsively rendered on any device.

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
- tabs changed:
  - top-level `tab-set`
  - `tabbed` -> `tab-item`
  - include `:sync:` option to synchronize tab selection across sets
- Minimises direct use of CSS classes (encourage to not use them)
  - More declarative, easy to understand options
  - Easier to work with non-HTML outputs
  - Easier to improve/refactor
- Updated Bootstrap CSS v4 -> v5
  - top-level grid can define both column numbers and gutter sizes
- All CSS classes are prefixed with `sd-` (no clash with other theme/extension CSS)
- All colors use CSS variables (customisable)

## TODO

note that directly using classes should be used as a "last resort",
and to please open an issue if you find you are commonly using a certain class.

grids items cannot contain headers; is this in anyway possible with docutils structure?

naming of directives/roles: standard prefix?

check grid-items and tab-items are inside parents (or auto-wrap?)

handle latex

card header/footer syntax?

Use autoprefixer when compiling SASS (see <https://getbootstrap.com/docs/5.0/getting-started/browsers-devices/#supported-browsers>)

horizontal card (grid row inside card, picture on left)

avatars (rounded images)

horizontally scrollable cards: (see <https://stackoverflow.com/questions/35993300/horizontally-scrollable-list-of-cards-in-bootstrap>)

from inline-tabs:

- **Elegant design**: Small footprint in the markup and generated website, while looking good.
- **Configurable**: All the colors can be configured using CSS variables.
- **Works without JavaScript**: JavaScript is not required for "essential" functionality, only for tab synchronisation.
