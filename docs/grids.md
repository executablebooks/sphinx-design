(grids)=

# Grids

Grids are based on a 12 column system, which can adapt to the size of the viewing screen.

A `grid` directive can be set with the number of default columns (1 to 12);
either a single number for all screen sizes, or four numbers for extra-small (<576px), small (768px), medium (992px) and large screens (>1200px),
then child `grid-item` directives should be set for each item.

Try re-sizing the screen to see the number of columns change:

::::{grid} 1 2 3 4
:outline:

:::{grid-item}
A
:::
:::{grid-item}
B
:::
:::{grid-item}
C
:::
:::{grid-item}
D
:::
::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/grid-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/grid-basic.txt
:language: rst
```
````
`````

The `grid-item-card` directive is a short-hand for placing a card content container inside a grid item (see [Cards](./cards.md)). Most of the `card` directive's options can be used also here:

::::{grid} 2
:::{grid-item-card} Title 1
A
:::
:::{grid-item-card} Title 2
B
:::
::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/grid-card.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/grid-card.txt
:language: rst
```
````
`````

You can set the spacing between grid items with the `gutter` option.
Like for grid columns, you can either provide a single number or four for small, medium and large and extra-large screens.

::::{grid} 2
:gutter: 1

:::{grid-item-card}
A
:::
:::{grid-item-card}
B
:::
::::

::::{grid} 2
:gutter: 3 3 4 5

:::{grid-item-card}
A
:::
:::{grid-item-card}
B
:::
::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/grid-gutter.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/grid-gutter.txt
:language: rst
```
````
`````

You can override the number of columns a single item takes up by using the `columns` option of the `grid-item` directive.
Given the total columns are 12, this means 12 would indicate a single item takes up the entire grid row, or 6 half.
Alternatively, use `auto` to automatically decide how many columns to use based on the item content.
Like for grid columns, you can either provide a single number or four for small, medium and large and extra-large screens.

::::{grid} 2
:::{grid-item-card}
:columns: auto

A
:::
:::{grid-item-card}
:columns: 12 6 6 6

B
:::
:::{grid-item-card}
:columns: 12

C
:::
::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/grid-card-columns.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/grid-card-columns.txt
:language: rst
```
````
`````

Grids can be nested in other grids to create complex, adaptive layouts:

::::::{grid} 1 1 2 2
:gutter: 1

:::::{grid-item}

::::{grid} 1 1 1 1
:gutter: 1

:::{grid-item-card} Item 1.1

Multi-line

content

:::

:::{grid-item-card} Item 1.2

Content

:::

::::

:::::

:::::{grid-item}

::::{grid} 1 1 1 1
:gutter: 1

:::{grid-item-card} Item 2.1

Content

:::

:::{grid-item-card} Item 2.2

Content

:::

:::{grid-item-card} Item 2.3

Content

:::

::::

:::::

::::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/grid-nested.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/grid-nested.txt
:language: rst
```
````
`````

See the [Bootstrap Grid system](https://getbootstrap.com/docs/5.0/layout/grid/) for further details.

## `grid` options

gutter
: Spacing between items.
  One or four integers (for "xs sm md lg") between 0 and 5.

margin
: Outer margin of grid.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

padding
: Inner padding of grid.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5.

text-align
: Default horizontal text alignment: left, right, center or justify

outline
: Create a border around the grid.

class-container
: Additional CSS classes for the grid container element.

class-row
: Additional CSS classes for the grid row element.

## `grid-item` options

columns
: The number of columns (out of 12) a grid-item will take up.
  One or four integers (for "xs sm md lg") between 1 and 12 (or `auto` to adapt to the content).

margin
: Outer margin of grid item.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

padding
: Inner padding of grid item.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5.

outline
: Create a border around the grid item.

text-align
: Default horizontal text alignment: left, right, center or justify

class
: Additional CSS classes for the grid item element.
