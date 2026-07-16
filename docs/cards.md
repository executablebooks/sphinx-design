(sd-cards)=

# Cards

Cards contain content and actions about a single subject.
A card is a flexible and extensible content container,
it can be formatted with components including headers and footers, titles and images.

:::{card} Card Title

Card content
:::

See the [Material Design](https://material.io/components/cards) and [Bootstrap card](https://getbootstrap.com/docs/5.0/layout/grid/) descriptions for further details.

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-basic.txt
:language: rst
```
````
`````

## Card headers and footers

Add a header and/or footer to a card with the `card-header` and `card-footer` directives.
They always render in their slots — the header at the top and the footer at the bottom of
the card — regardless of where they appear within the card body (the recommended order is
header, then body, then footer):

::::{card} Card Title

:::{card-header}
Header
:::

Card content

:::{card-footer}
Footer
:::
::::

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-head-foot.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-head-foot.txt
:language: rst
```
````
`````

For a single line of content, the `header` and `footer` options are a convenient
short-hand (they accept inline markup, and compose with the card body):

:::{card} Card Title
:header: A **header**
:footer: A footer

Card content
:::

When using cards in grids (see [`grid-item-card`](./grids.md)) footers can be aligned.

::::::{grid} 2
:::::{grid-item-card} Card Title

::::{card-header}
Header
::::

Card content

::::{card-footer}
Footer
::::
:::::
:::::{grid-item-card} Card Title

::::{card-header}
Header
::::

Longer

Card content

::::{card-footer}
Footer
::::
:::::
::::::

## Card images

You can also add an image as the background of a card or at the top/bottom of the card, with the `img-background`, `img-top`, `img-bottom` options:

:::::{grid} 2 3 3 4

::::{grid-item}

:::{card} Title
:img-background: images/particle_background.jpg
:class-card: sd-text-black
:img-alt: your desired alt text

Text
:::

::::

::::{grid-item-card} Title
:img-top: images/particle_background.jpg
:img-alt: your desired alt text

:::{card-header}
Header
:::

Content

:::{card-footer}
Footer
:::
::::

::::{grid-item-card} Title
:img-bottom: images/particle_background.jpg
:img-alt: your desired alt text

:::{card-header}
Header
:::

Content

:::{card-footer}
Footer
:::
::::

:::::

`````{dropdown-syntax}

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
:link-alt: example.com

The entire card can be clicked to navigate to `https://example.com`.
:::

:::{card} Clickable Card (internal)
:link: cards-clickable
:link-type: ref

The entire card can be clicked to navigate to the `cards-clickable` reference target.
:::

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/card-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/card-link.txt
:language: rst
```
````
`````

The **external link** created above is equivalent to using `<https://example.com>`
(<https://example.com>),
or if the `link-alt` option is provided, `[alt text](https://example.com)`
([alt text](https://example.com)).

:::{tip}
Using URLs as link text makes it harder
for disabled people and for search engines to digest your web page,
so it's best to provide link text via the `link-alt` option.
:::

The **internal link** created above is equivalent to using `` {ref}`cards-clickable` ``
({ref}`cards-clickable`),
or if the `link-alt` option is provided, `` {ref}`alt text <cards-clickable>` ``
({ref}`alt text <cards-clickable>`).

:::{note}
You cannot add additional links to the clickable card, neither in the card
title nor in the card body. The entire card becomes a single link to the
destination you specify, which overrides any other links inside the card.
:::



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

`````{dropdown-syntax}

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

img-alt
: Alternative text for the image (that will be used by screen-readers).

link
: Turn the entire card into a clickable link to an external/internal target.

link-type
: Type of link: `url` (default), `ref`, `doc`, `any`.

link-alt
: Alternative text for the link (that will be used by screen-readers).

shadow
: The size of the shadow below the card: `none`, `sm` (default), `md`, `lg`.

header
: Inline-markup short-hand for a single-line header
  (equivalent to a `card-header` directive; the two are mutually exclusive).

footer
: Inline-markup short-hand for a single-line footer
  (equivalent to a `card-footer` directive; the two are mutually exclusive).

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

class-img-top
: Additional CSS classes for the top image (if present).

class-img-bottom
: Additional CSS classes for the bottom image (if present).

(legacy-separator-syntax)=

## Legacy separator syntax

:::{deprecated} 0.8
Prefer the `card-header` / `card-footer` directives (above).
The `^^^` / `+++` separators are **deprecated**: they scan the card's raw source
lines, so a `^^^` or `+++` line inside nested content (for example a code block)
is mistaken for a separator, and they have no meaning to non-Python MyST tools.
:::

Historically, a card header and footer were delimited within the body itself:
all content before the first line of three-or-more `^^^` became the header,
and all content after the final line of three-or-more `+++` became the footer.

::::{card} Card Title
Header
^^^
Card content
+++
Footer
::::

This syntax is still recognised by default, but emits a deprecation warning
(once per document). The rewrite is mechanical:

| Legacy separators | Header / footer directives |
| --- | --- |
| `Header` above a `^^^` line | a `card-header` directive |
| `Footer` below a `+++` line | a `card-footer` directive |

`````{tab-set}
````{tab-item} MyST
```markdown
:::{card} Card Title
Header
^^^
Body
+++
Footer
:::
```
becomes
```markdown
::::{card} Card Title

:::{card-header}
Header
:::

Body

:::{card-footer}
Footer
:::
::::
```
````
````{tab-item} reStructuredText
```rst
.. card:: Card Title

   Header
   ^^^
   Body
   +++
   Footer
```
becomes
```rst
.. card:: Card Title

   .. card-header::

      Header

   Body

   .. card-footer::

      Footer
```
````
`````

:::{important} Migrate, then flip the flag
While the legacy separators are enabled (the default), the raw-line scan runs
on **every** card, so a stray column-0 `^^^` or `+++` — even inside a code
block, and even in a card that has already migrated to the `card-header` /
`card-footer` directives — is still treated as a separator (mis-splitting the
card and emitting a mixed-syntax warning). The single-parse robustness is only
realized once the separators are turned off.

The recommended order is therefore **migrate first, then flip the flag**:
convert every card to the directives, then set
`sd_card_legacy_separators = False` in your `conf.py`.
:::

With `sd_card_legacy_separators = False`, `^^^` / `+++` lines are no longer
scanned — but they do **not** reliably render as literal text, so migrate
before flipping:

- in MyST, a bare `+++` line is a block break and silently disappears;
- in reStructuredText, a `^^^` / `++++` line can raise a docutils `CRITICAL`
  "Unexpected section title or transition" error.

To keep the legacy syntax on but silence the deprecation warning, add
`"design.card_legacy"` to the Sphinx `suppress_warnings` list.

**Timeline**: deprecated now (default on) → default off at `1.0` → removed at `2.0`.
