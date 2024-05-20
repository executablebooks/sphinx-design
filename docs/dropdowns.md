(sd-dropdowns)=

# Dropdowns

Dropdowns can be used to toggle, usually *non-essential*, content and show it only when a user clicks on the header panel.

The dropdown can have a title, as the directive argument, and the `open` option can be used to initialise the dropdown in the open state.

:::{dropdown}
Dropdown content
:::

:::{dropdown} Dropdown title
Dropdown content
:::

:::{dropdown} Open dropdown
:open:

Dropdown content
:::

`````{dropdown} Syntax
:icon: code
:color: primary

````{tab-set-code}
```{literalinclude} ./snippets/myst/dropdown-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/dropdown-basic.txt
:language: rst
```
````
`````

## Dropdown opening animations

Use `:animate: fade-in` or `:animate: fade-in-slide-down` options to animate the reveal of the hidden content.

:::{dropdown} Dropdown `fade-in`
:animate: fade-in

{{ loremipsum }}
:::

:::{dropdown} Dropdown `fade-in-slide-down`
:animate: fade-in-slide-down

{{ loremipsum }}
:::

## Dropdowns in other components

Dropdowns can be nested inside other components, such as inside parent dropdowns or within [grid items](./grids.md).

::::{dropdown} Parent dropdown title
:open:

:::{dropdown} Child dropdown title
:color: warning
:icon: alert

Dropdown content
:::
::::

:::::{grid} 1 1 2 2
:gutter: 1

::::{grid-item}
:::{dropdown} Dropdown Column 1
Dropdown content
:::
::::

::::{grid-item}
:::{dropdown} Dropdown Column 2
Dropdown content
:::
::::

:::::

## `dropdown` options

open
: Open the dropdown by default.

color
: Set the color of the dropdown header (background and font).
  One of the semantic color names: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `muted`.

icon
: Set an [octicon icon](icons) to prefix the dropdown header.

animate
: Animate the dropdown opening (`fade-in` or `fade-in-slide-down`).

margin
: Outer margin of grid.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

name
: Set a reference-able name for the dropdown container.

class-container
: Additional CSS classes for the container element.

class-title
: Additional CSS classes for the title element.

class-body
: Additional CSS classes for the body element.
