(sd-tabs)=

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

`````{dropdown-syntax}

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

The Selection of tab items can be synchronised across multiple tab-sets.
For a `tab-item` to be synchronisable, add the `sync` option to the `tab-item` directive with a key unique to that set.
Now when you select a tab in one set, tabs in other sets with the same key will be selected.

:::{note}
Synchronisation requires that JavaScript is enabled.
:::

:::{versionadded} 0.6.0
To synchronise tabs only across certain tab-sets, add the `:sync-group:` option to each `tab-set` directive with the same group name, such as `:sync-group: category`.

You can also add an [HTML query string](https://en.wikipedia.org/wiki/Query_string) to the end of the page's URL,
to automatically select a tab with a specific key across all tab-sets of the group, for example:

- [`?category=key1#synchronised-tabs`](?category=key1#synchronised-tabs){.external}
- [`?category=key2#synchronised-tabs`](?category=key2#synchronised-tabs){.external}
:::

::::{tab-set}
:sync-group: category

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
:sync-group: category

:::{tab-item} Label1
:sync: key1

Content 1
:::

:::{tab-item} Label2
:sync: key2

Content 2
:::

::::

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/tab-sync.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/tab-sync.txt
:language: rst
```
````
`````

### Linking to synchronised tabs

To author a link that pre-selects a tab, append the query string (and optionally a page anchor) to the URL of the **built** HTML page.
Sphinx referencing roles, such as `ref` and `doc`, cannot output URLs containing query strings,
so instead write the URL directly:

- In MyST Markdown, add an `external` class to the link (using the [`attrs_inline` extension](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html)), so that the URL is output as-is, rather than being resolved as a cross-reference.
- In reStructuredText, use a standard (external) hyperlink.

````{tab-set-code}
```{code-block} markdown
[Open with key2 selected](tabs.html?category=key2#synchronised-tabs){.external}
```
```{code-block} rst
`Open with key2 selected <tabs.html?category=key2#synchronised-tabs>`_
```
````

For example: [open the tabs above with `key2` selected](tabs.html?category=key2#synchronised-tabs){.external}

:::{warning}
Such URLs are relative to the location of the current page in the built HTML output, not to the source files
(for example, a page in a sub-folder would require `../tabs.html?...`).
They are not checked by Sphinx, so they will break silently if the target page is moved,
and they do not apply to other output formats.
:::

## Tabbed code examples

The `tab-set-code` directive provides a shorthand for synced code examples.
You can place any directives in a `tab-set-code` that produce a `literal_block` node with a `language` attribute, for example `code`, `code-block` and `literalinclude`.
Tabs will be labelled and synchronised by the `language` attribute (in upper-case).

:::{versionadded} 0.6.0
You can also add an [HTML query string](https://en.wikipedia.org/wiki/Query_string) to the end of the page's URL,
to automatically select a tab with a specific code across all tab-sets of the group, for example:

- [`?code=markdown#tabbed-code-examples`](?code=markdown#tabbed-code-examples){.external}
- [`?code=rst#tabbed-code-examples`](?code=rst#tabbed-code-examples){.external}
:::

```````{tab-set}
:sync-group: code

``````{tab-item} Markdown
:sync: markdown

````{literalinclude} ./snippets/myst/tab-code-set.txt
:language: markdown
````
``````

``````{tab-item} RST
:sync: rst

````{literalinclude} ./snippets/rst/tab-code-set.txt
:language: rst
````
``````

```````

## Tabs in other components

Tabs can be nested inside other components, such as inside [dropdowns](./dropdowns.md) or within [grid items](./grids.md).

:::::{dropdown} Tabs in dropdown
:open:

Paragraph

::::{tab-set}

:::{tab-item} Label1
:sync: label-1

Content 1
:::

:::{tab-item} Label2
:sync: label-2

Content 2
:::

::::
:::::

::::::{grid} 1 1 2 2

:::::{grid-item}
:outline:

Initial paragraph

::::{tab-set}

:::{tab-item} Label1
:sync: label-1

Content 1
:::

:::{tab-item} Label2
:sync: label-2

Content 2
:::

::::

:::::

:::::{grid-item}
:outline:

::::{tab-set}

:::{tab-item} Label1
:sync: label-1

Content 1
:::

:::{tab-item} Label2
:sync: label-2

Content 2
:::

::::

Ending paragraph

:::::

::::::

Tab set, within tab set:

::::::{tab-set}
:::::{tab-item} Label 1
::::{tab-set}
:::{tab-item} Label 1a
Content 1a
:::
:::{tab-item} Label 1b
Content 1b
:::
::::
:::::
:::::{tab-item} Label 2
Content 2
:::::
::::::

## `tab-set` options

sync-group
: A group name for synchronised tab sets (default `tab`).

class
: Additional CSS classes for the container element.

## `tab-set-code` options

no-sync
: Disable synchronisation of tabs.

sync-group
: A group name for synchronised tab sets (default `code`).

class-set
: Additional CSS classes for the set container element.

class-item
: Additional CSS classes for the item container element.

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
