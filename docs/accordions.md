(sd-accordions)=

# Accordions

An `accordion` groups a set of [dropdowns](sd-dropdowns) so that they behave as
one *exclusive* set: opening one item automatically closes the others. This is
useful for FAQ-style content, where only one answer should be visible at a time.

The behaviour is native to HTML and requires **no JavaScript**: the directive
simply gives every item a shared `name`, and the browser does the rest.

::::{accordion}

:::{dropdown} What is an accordion?
A container of dropdowns where opening one collapses the others.
:::

:::{dropdown} How do I add one?
Nest `dropdown` directives inside an `accordion` directive (see the syntax
below).
:::

:::{dropdown} Does it need JavaScript?
No. It uses the native `name` attribute shared across `<details>` elements.
:::
::::

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/accordion-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/accordion-basic.txt
:language: rst
```
````
`````

## The `:open:` interaction

Because only one item in an exclusive group can be open at a time, you may mark
**at most one** child dropdown with the [`:open:`](sd-dropdowns) option, to have
the accordion start with that item expanded. If several items are marked
`:open:`, only the first is kept open (the rest are collapsed and a
`design.accordion` warning is emitted).

## Flush variant

Add the `:flush:` flag for an edge-to-edge look (like Bootstrap's
*accordion-flush*): the outer side borders and corner rounding are removed, so
the accordion blends into its parent container.

::::{accordion}
:flush:

:::{dropdown} First item
{{ loremipsum }}
:::

:::{dropdown} Second item
{{ loremipsum }}
:::
::::

## Nested dropdowns

Only the **direct** children of an accordion join the exclusive group. A
dropdown nested inside another item's *body* keeps its own independent
open/close behaviour, so you can freely nest expandable content within an
accordion item.

:::::{accordion}

::::{dropdown} Item with nested content
:open:

This item stays open independently of the dropdown below it:

:::{dropdown} A nested dropdown
:icon: quote

Opening or closing me does not affect the sibling accordion items.
:::
::::

::::{dropdown} Another item
Opening me closes the first item, but the *nested* dropdown is unaffected.
::::
:::::

(sd-accordion-browser-support)=

## Browser support

The exclusive-open behaviour relies on the native `name` attribute on
`<details>` elements, which is
[Baseline *Newly* Available](https://web.dev/baseline) (Chrome/Edge 120+,
Firefox 130+ and Safari 17.2+, all shipped in 2024). This is a deliberate
exception to the project's [*Baseline Widely Available*](get_started.md) policy,
permitted because it **degrades gracefully**: browsers that predate the feature
simply ignore the shared `name` and render each item as an ordinary,
independently collapsible dropdown. Nothing breaks — you only lose the automatic
collapsing of sibling items, and no JavaScript fallback is involved.

## `accordion` options

flush
: Flag. Remove the outer side borders and corner rounding for an edge-to-edge
  (Bootstrap *accordion-flush*) appearance.

class
: Additional CSS classes for the accordion container element.

The individual items are ordinary [dropdowns](sd-dropdowns) and accept all of
the `dropdown` options.
