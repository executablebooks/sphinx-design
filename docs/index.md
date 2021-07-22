# sphinx-design

```{article-info}
:avatar: images/mugshot.jpeg
:avatar-link: https://github.com/chrisjsewell
:author: "[Chris Sewell](https://github.com/chrisjsewell)"
:date: "{sub-ref}`today`"
:read-time: "5 min read"
```

A sphinx extension for designing beautiful, screen-size responsive web components.

Conflict free CSS
: All CSS classes are prefixed, to avoid conflicts with other frameworks.

Works without JavaScript
: JavaScript is not required for any "essential" functionality.

Configurable
: All colors can be configured using CSS variables.

Supports non-HTML output formats
: Components degrade gracefully for non-HTML formats.

```{toctree}
:caption: Components
:hidden:

grids
cards
dropdowns
tabs
other
```

```{toctree}
:caption: Themes
:hidden:

alabaster <https://sphinx-design.readthedocs.io/en/latest>
sphinx-book-theme <https://sphinx-design.readthedocs.io/en/sbt-theme>
pydata-sphinx-theme <https://sphinx-design.readthedocs.io/en/pydata-theme>
sphinx-rtd-theme <https://sphinx-design.readthedocs.io/en/rtd-theme>
furo <https://sphinx-design.readthedocs.io/en/furo-theme>
```

::::{grid} 1 2 2 3
:margin: 4 4 0 0
:gutter: 1

:::{grid-item-card} {octicon-16}`table` Grids
:link: grids
:link-type: doc

Screen size adaptable grid layouts.
:::

:::{grid-item-card} {octicon-16}`note` Cards
:link: cards
:link-type: doc

Flexible and extensible content containers.
:::

:::{grid-item-card} {octicon-16}`chevron-down` Dropdowns
:link: dropdowns
:link-type: doc

Hide content in expandable containers.
:::

:::{grid-item-card} {octicon-16}`duplicate` Tabs
:link: tabs
:link-type: doc

Synchronisable, tabbed content sets.
:::

:::{grid-item-card} {octicon-16}`plus-circle` Badges, Buttons & Icons
:link: other
:link-type: doc

Roles and directives for {bdg-primary}`badges` and other components.
:::

::::

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

## Supported browsers

- Chrome >= 60
- Firefox >= 60
- Firefox ESR
- iOS >= 12
- Safari >= 12
- Explorer >= 12

(Mirrors: <https://github.com/twbs/bootstrap/blob/v5.0.2/.browserslistrc>)
