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

sphinx-design targets [**Baseline** Widely Available](https://web.dev/baseline)
web features (interoperable across Chrome, Edge, Firefox and Safari for at least
30 months — the evergreen browsers of roughly the last 2½ years). Internet
Explorer is not supported. See the [getting started guide](./docs/get_started.md)
for details.

## Theme support

View the documentation in multiple themes:

- [alabaster](https://sphinx-design.readthedocs.io/en/alabaster-theme)
- [sphinx-book-theme](https://sphinx-design.readthedocs.io/en/sbt-theme)
- [pydata-sphinx-theme](https://sphinx-design.readthedocs.io/en/pydata-theme)
- [sphinx-rtd-theme](https://sphinx-design.readthedocs.io/en/rtd-theme)
- [furo](https://sphinx-design.readthedocs.io/en/furo-theme)

## Comparison to sphinx-panels

This package is an iteration on [sphinx-panels](https://github.com/executablebooks/sphinx-panels) and intends to replace it.
See [Migrating from sphinx-panels](./docs/get_started.md) for more information.

## Development

It is recommended to use [tox](https://tox.readthedocs.io/en/latest/) to run the tests and document builds.
Run `tox -va` to see all the available tox environments.

To run linting, formatting and CSS generation, use [pre-commit](https://pre-commit.com/).
`pre-commit run --all css` regenerates the compiled stylesheet
(`sphinx_design/static/sphinx-design.min.css`) from `style/design.toml` and the
hand-authored `style/*.css`; you can also run it directly with
`python tools/generate_css.py`.

## TODO

- note design goal; to be flexible, but limit the amount of directive nesting required.
  This factors in to
  - card header/footer syntax? (don't really want to have to use separate directives for these, hence `^^^`/`+++` syntax)
  - auto-wrap `grid-item` and `tab-item`, if not already inside `grid` or `tab-set`?

grids items cannot contain headers; is this in anyway possible with docutils structure?

naming of directives/roles: standard prefix?

why are cards setup with "word-wrap: break-word;"?

handle latex

horizontal card (grid row inside card, picture on left)

subtitle for card (see <https://material.io/components/cards#anatomy>)


[github-ci]: https://github.com/executablebooks/sphinx-design/workflows/continuous-integration/badge.svg?branch=main
[github-link]: https://github.com/executablebooks/sphinx-design
[codecov-badge]: https://codecov.io/gh/executablebooks/sphinx-design/branch/main/graph/badge.svg
[codecov-link]: https://codecov.io/gh/executablebooks/sphinx-design
[pypi-badge]: https://img.shields.io/pypi/v/sphinx-design.svg
[pypi-link]: https://pypi.org/project/sphinx-design
