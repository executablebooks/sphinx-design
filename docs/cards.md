(cards)=

# Cards

Cards contain content and actions about a single subject.
A card is a flexible and extensible content container,
it can be formatted with components including headers and footers, titles and images.

:::{card} Card Title

Card content
:::

See the [Material Design](https://material.io/components/cards) and [Bootstrap card](https://getbootstrap.com/docs/5.0/layout/grid/) descriptions for further details.

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

## Card images

You can also add an image as the background of a card or at the top/bottom of the card, with the `img-background`, `img-top`, `img-bottom` options:

:::::{grid} 2 3 3 4

::::{grid-item}

:::{card} Title
:img-background: images/particle_background.jpg
:class-card: sd-text-black

Text
:::

::::

::::{grid-item-card} Title
:img-top: images/particle_background.jpg

Header
^^^
Content
+++
Footer
::::

::::{grid-item-card} Title
:img-bottom: images/particle_background.jpg

Header
^^^
Content
+++
Footer
::::

:::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-images.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-images.txt
:language: rst
```
````
`````

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

You can use the `text-align` option to align the text in a card,
and also `auto` margins to align the cards horizontally.

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

(cards:carousel)=

## Card carousels

The `card-carousel` directive can be used to create a single row of fixed width, scrollable cards.
The argument should be a number between 1 and 12, to denote the number of cards to display.

When scrolling a carousel, the scroll will snap to the start of the nearest card:

::::{card-carousel} 2

:::{card} card 1
content
:::
:::{card} card 2
Longer

content
:::
:::{card} card 3
:::
:::{card} card 4
:::
:::{card} card 5
:::
:::{card} card 6
:::
::::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-carousel.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-carousel.txt
:language: rst
```
````
`````

(cards:options)=

## `card` options

width
: The width that the card should take up (in %): auto, 25%, 50%, 75%, 100%.

margin
: Outer margin of grid.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

text-align
: Default horizontal text alignment: left, right, center or justify

img-background
: A URI (relative file path or URL) to an image to be placed below the content.

img-top
: A URI (relative file path or URL) to an image to be placed above the content.

img-bottom
: A URI (relative file path or URL) to an image to be placed below the content.

link
: Turn the entire card into a clickable link to an external/internal target.

link-type
: Type of link: `url` (default), `ref`, `doc`, `any`.

shadow
: The size of the shadow below the card: `none`, `sm` (default), `md`, `lg`.

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
