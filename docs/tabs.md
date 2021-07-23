(tabs)=

# Tabs

Tabs organize and allow navigation between groups of content that are related and at the same level of hierarchy.
Each tab should contain content that is distinct from other tabs in a set.

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/tab-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/tab-basic.txt
:language: rst
```
````
`````

See the [Material Design](https://material.io/components/tabs) description for further details.

## Synchronised Tabs

Use the `sync` option to synchronise the selected tab items across multiple tab-sets.

::::{tab-set}

:::{tab-item} Label1
:sync: key1

Content 1
:::

:::{tab-item} Label2
:sync: key2

Content 2
:::

::::

::::{tab-set}

:::{tab-item} Label1
:sync: key1

Content 1
:::

:::{tab-item} Label2
:sync: key2

Content 2
:::

::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/tab-sync.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/tab-sync.txt
:language: rst
```
````
`````

## Tabs in other components

Tabs can be nested inside other components, such as inside [dropdowns](./dropdowns.md) or within [grid items](./grids.md).

:::::{dropdown} Tabs in dropdown
:open:

Paragraph

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::
:::::

::::::{grid} 1 1 2 2

:::::{grid-item}

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::

:::::

:::::{grid-item}

::::{tab-set}

:::{tab-item} Label1
Content 1
:::

:::{tab-item} Label2
Content 2
:::

::::

:::::

::::::

## `tab-item` options

selected
: a flag indicating whether the tab should be selected by default.

sync
: A key that is used to sync the selected tab across multiple tab-sets.

name
: Set a reference-able name for the dropdown container.

class-container
: Additional CSS classes for the container element.

class-label
: Additional CSS classes for the label element.

class-content
: Additional CSS classes for the content element.
