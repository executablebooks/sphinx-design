# sphinx-design (IN-DEVELOPMENT)

A sphinx extension for implementing [Material Design](https://material.io) system web components, for building beautiful, responsive, mobile-friendly sites.

Also takes inspiration from [Material-UI](https://material-ui.com/) and [Bootstrap](https://getbootstrap.com/).

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

How to handle the other things in panels, e.g. cards, headers, footers etc?

How to handle JS

handle latex
