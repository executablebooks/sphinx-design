# sphinx-design (IN-DEVELOPMENT)

A sphinx extension for designing beautiful, size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

**NOTE**: This package is a partially an iteration on sphinx-panels.

## TODO

defaults:

- semantic colors
  - primary
  - secondary
  - success
  - danger
  - warning
  - info
  - light
  - dark
- adaptive breakpoints
  - sm
  - md
  - lg
  - xl

- padding, margin

- directives:
  - sd-grid (optional), sd-grid-item
  - sd-dropdowns (optional), sd-dropdown
  - sd-tabs (optional), sd-tab
  - sd-link-button

- roles:
  - badges: sd-badge, sd-link-badge
  - icons: sd-opticon, sd-fa

`````markdown

````{sd-grid}
:padding: <left> <right> <top> <bottom> | <all>
:margin: <left> <right> <top> <bottom> | <all>

````{sd-grid-item}
:layout: <sm> <md> <lg> <xl> | <all>
:padding: <left> <right> <top> <bottom> | <all>
:margin: <left> <right> <top> <bottom> | <all>

Content
````

````

`````

naming of directives: standard prefix?

How to handle JS

handle latex

is grid/grid-item both having `columns`, with different meanings, confusing?

card header/footer syntax?

card title/subtitle (card tite could be argument?, but ideally would also be ~h5 tag)
