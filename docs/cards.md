(cards)=

# Cards

A card is a flexible and extensible content container.
It can be formatted with components including headers and footers, titles and images.

:::{card} Card Title

Card content
:::

See the [Bootstrap card](https://getbootstrap.com/docs/5.0/layout/grid/) for further details.

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-basic.txt
:language: rst
```
````
`````

All content before the first occurrence of three or more `^^^` is considered as a header,
and all content after the final occurrence of three or more `+++` is considered as a footer:

:::{card} Card Title
Header
^^^
Card content
+++
Footer
:::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-head-foot.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-head-foot.txt
:language: rst
```
````
`````

When using cards in grids (see [`grid-item-card`](./grids.md)) footers can be aligned.

::::{grid} 2
:::{grid-item-card} Card Title
Header
^^^
Card content
+++
Footer
:::
:::{grid-item-card} Card Title
Header
^^^
Longer

Card content
+++
Footer
:::
::::

You can also add images to the top and bottom of the card, with the `img-top` and `img-bottom` options:

::::{grid} 1 2 2 2
:::{grid-item-card} Card Title
:img-top: images/banner.png
:img-bottom: images/banner.png

Header
^^^
Card content
+++
Footer
:::
::::

(cards-clickable)=

## Clickable cards

Using the `link` and `link-type` options, you can turn an entire card into a clickable link.
Try hovering over then clicking on the cards below:

:::{card} Clickable Card (external)
:link: https://example.com

The entire card can be clicked to navigate to <https://example.com>.
:::

:::{card} Clickable Card (internal)
:link: cards-clickable
:link-type: ref

The entire card can be clicked to navigate to the `cards-clickable` reference target.
:::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-link.txt
:language: rst
```
````
`````

## Aligning cards

:::{card} Align Center
:width: 75%
:margin: 0 2 auto auto
:text-align: center

Content
:::

:::{card} Align Right
:width: 50%
:margin: 0 2 auto 0
:text-align: right

Content
:::

:::{card} Align Left
:width: 50%
:margin: 0 2 0 auto
:text-align: left

Content
:::

## `card` options

width
: The width that the card should take up (in %): auto, 25%, 50%, 75%, 100%.

margin
: Outer margin of grid.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

text-align
: Default horizontal text alignment: left, right, center or justify

img-top
: A URI (relative file path or URL) to an image to be placed above the content.

img-bottom
: A URI (relative file path or URL) to an image to be placed below the content.

link
: Turn the entire card into a clickable link to an external/internal target.

link-type
: Type of link: `url` (default), `ref`, `doc`, `any`.

no-shadow
: Do not draw a shadow around the card.

class-card
: Additional CSS classes for the card container element.

class-header
: Additional CSS classes for the header element.

class-body
: Additional CSS classes for the body element.

class-title
: Additional CSS classes for the title element.

class-footer
: Additional CSS classes for the footer element.
