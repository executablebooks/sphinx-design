# sphinx-design

[![Github-CI][github-ci]][github-link]
[![Coverage Status][codecov-badge]][codecov-link]
[![PyPI][pypi-badge]][pypi-link]

A sphinx extension for designing beautiful, view size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

## Usage

Simply pip install `sphinx-design` and add the extension to your `conf.py`:

```python
extensions = ["sphinx_design"]
```

## Supported browsers

- Chrome >= 60
- Firefox >= 60
- Firefox ESR
- iOS >= 12
- Safari >= 12
- Explorer >= 12

(Mirrors: <https://github.com/twbs/bootstrap/blob/v5.0.2/.browserslistrc>)

## Theme support

View the documentation in multiple themes:

- [alabaster](https://sphinx-design.readthedocs.io/en/alabaster-theme)
- [sphinx-book-theme](https://sphinx-design.readthedocs.io/en/sbt-theme)
- [pydata-sphinx-theme](https://sphinx-design.readthedocs.io/en/pydata-theme)
- [sphinx-rtd-theme](https://sphinx-design.readthedocs.io/en/rtd-theme)
- [furo](https://sphinx-design.readthedocs.io/en/furo-theme)

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
  - More declarative, easy to understand options, easier to validate
  - Easier to work with non-HTML outputs
  - Easier to improve/refactor
- Updated Bootstrap CSS v4 -> v5
  - top-level grid can define both column numbers and gutter sizes
- All CSS classes are prefixed with `sd-` (no clash with other theme/extension CSS)
- All colors use CSS variables (customisable)

## TODO

- note design goal; to be flexible, but limit the amount of directive nesting required.
  This factors in to
  - card header/footer syntax? (don't really want to have to use separate directives for these, hence `^^^`/`+++` syntax)
  - auto-wrap `grid-item` and `tab-item`, if not already inside `grid` or `tab-set`?

grids items cannot contain headers; is this in anyway possible with docutils structure?

naming of directives/roles: standard prefix?

why are cards setup with "word-wrap: break-word;"?

handle latex

Use autoprefixer when compiling SASS (see <https://getbootstrap.com/docs/5.0/getting-started/browsers-devices/#supported-browsers>)

horizontal card (grid row inside card, picture on left)

subtitle for card (see <https://material.io/components/cards#anatomy>)

paragraph and tab-set in grid-item

rtd PRs not working

[github-ci]: https://github.com/executablebooks/sphinx-design/workflows/continuous-integration/badge.svg?branch=main
[github-link]: https://github.com/executablebooks/sphinx-design
[codecov-badge]: https://codecov.io/gh/executablebooks/sphinx-design/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/sphinx-design
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-design.svg
[pypi-link]: https://pypi.org/project/sphinx-design
