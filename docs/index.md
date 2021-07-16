# sphinx-design

A sphinx extension for designing beautiful, size responsive web components.

Created with inspiration from [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io) and [Material-UI](https://material-ui.com/) design frameworks.

::::{grid}
:columns: 1 2 2 3
:gutter: 1 3 3 3

:::{grid-item}

hallo

:::

:::{grid-item-card}
:img-top: https://via.placeholder.com/150
:img-bottom: https://via.placeholder.com/150

there df sdf  dsf  dsf  dfs   dsf  fds dsf

:::

:::{grid-item-card}
:text-align: center

a header
^^^
again [abc](https://google.com)
+++
a footer

:::

:::{grid-item-card} My title
:columns: 12 6 6 6

bigger

:::

:::{grid-item-card}
:columns: 12 6 6 6

bigger

:::

::::

:::{card}
:width: 25

other [abc](https://google.com)
:::

:::{card}
:width: 25

other [abc](https://google.com)
:::

next paragraph 1

::::{grid}
:columns: 1 1 2 2
:gutter: 0 0 2 4
:text-align: justify

:::{grid-item}
{{ loremipsum }}
:::

:::{grid-item}
{{ loremipsum }}
:::

::::
