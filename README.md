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
  - mui-grid (optional), mui-grid-item
  - mui-dropdowns (optional), mui-dropdown
  - mui-tabs (optional), mui-tab
  - mui-link-button

- roles:
  - badges: mui-badge, mui-link-badge
  - icons: mui-opticon, mui-fa

`````markdown

````{mui-grid}
:padding: <left> <right> <top> <bottom> | <all>
:margin: <left> <right> <top> <bottom> | <all>

````{mui-grid-item}
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
