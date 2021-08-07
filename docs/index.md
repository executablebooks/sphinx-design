---
sd_hide_title: true
---

# sphinx-design

::::{grid}
:reverse:
:gutter: 2 1 1 1
:margin: 4 4 1 1

:::{grid-item}
:columns: 12 4 4 4

```{image} ./_static/logo_square.svg
:width: 200px
:class: sd-m-auto sd-animate-grow50-rot20
```
:::

:::{grid-item}
:columns: 12 8 8 8
:child-align: justify
:class: sd-fs-3

A sphinx extension for designing beautiful, screen-size responsive web-components.

```{button-ref} get_started
:color: primary
:class: sd-fs-5

Get Started
```

:::
::::

Conflict free CSS
: All CSS classes are prefixed, to avoid conflicts with other frameworks.

Works without JavaScript
: JavaScript is not required for any "essential" functionality.

Configurable
: All colors can be configured using CSS variables.

Supports non-HTML output formats
: Components degrade gracefully for non-HTML formats.

```{toctree}
:hidden:

get_started
```

```{toctree}
:caption: Components
:hidden:

grids
cards
dropdowns
tabs
badges_buttons
additional
```

```{toctree}
:caption: Styling
:hidden:

css_variables
css_classes
```

```{toctree}
:caption: Themes
:hidden:

alabaster <https://sphinx-design.readthedocs.io/en/alabaster-theme>
sphinx-book-theme <https://sphinx-design.readthedocs.io/en/sbt-theme>
pydata-sphinx-theme <https://sphinx-design.readthedocs.io/en/pydata-theme>
sphinx-rtd-theme <https://sphinx-design.readthedocs.io/en/rtd-theme>
furo <https://sphinx-design.readthedocs.io/en/furo-theme>
```

::::{grid} 1 2 2 3
:margin: 4 4 0 0
:gutter: 1

:::{grid-item-card} {octicon}`table` Grids
:link: grids
:link-type: doc

Screen size adaptable grid layouts.
:::

:::{grid-item-card} {octicon}`note` Cards
:link: cards
:link-type: doc

Flexible and extensible content containers.
:::

:::{grid-item-card} {octicon}`chevron-down` Dropdowns
:link: dropdowns
:link-type: doc

Hide content in expandable containers.
:::

:::{grid-item-card} {octicon}`duplicate` Tabs
:link: tabs
:link-type: doc

Synchronisable, tabbed content sets.
:::

:::{grid-item-card} {octicon}`plus-circle` Badges, Buttons & Icons
:link: badges_buttons
:link-type: doc

Roles and directives for {bdg-primary}`badges` and other components.
:::

:::{grid-item-card} {octicon}`image` CSS Styling
:link: css_variables
:link-type: doc

Change the default colors and other CSS.
:::

::::

-----------

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.
