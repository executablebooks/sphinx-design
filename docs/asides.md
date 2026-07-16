(sd-asides)=

# Asides

Asides are floated call-out boxes that the surrounding text wraps around, ideal
for pull-outs, margin notes and short side comments that sit *beside* the flow
rather than interrupting it.

:::{aside} A pull-out note
:align: right
:width: 33%

Asides float to the side of the main text. On narrow screens they fall back to
a full-width block, so nothing is ever squeezed.
:::

{{ loremipsum }}

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/aside-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/aside-basic.txt
:language: rst
```
````
`````

```{seealso}
Asides *complement* [admonitions](https://myst-parser.readthedocs.io/en/latest/syntax/admonitions.html)
and [cards](./cards.md): use an **admonition** for a note that interrupts the
flow as a full-width block, a **card** for a self-contained boxed unit inside a
[grid](./grids.md), and an **aside** when you want the body text to keep
flowing *around* a side box.
```

## Alignment

Use the `align` option to float the box `left` or `right` (the default is
`right`).

:::{aside} Floated left
:align: left
:width: 33%

`:align: left` floats the box to the left, with the text wrapping down its
right-hand side.
:::

{{ loremipsum }}

## Widths

The `width` option accepts `25%`, `33%` (the default) or `50%`, controlling how
much horizontal space the box occupies (and therefore how much room is left for
the wrapping text).

:::{aside} A 50% aside
:align: right
:width: 50%

At `:width: 50%` the box takes up half the content width.
:::

{{ loremipsum }}

+++

```{note}
Widths are only applied from the `md` breakpoint (768&nbsp;px) upwards. Below
that the aside becomes a full-width block regardless of the `width` option, so
it stays readable on small screens. If a right-floated aside collides with a
theme's in-page (right-hand) table of contents at narrow widths, prefer a
smaller `width` or `:align: left`.
```

## Stopping the wrap

Text keeps wrapping around an aside until it runs out. To force following
content to start *below* the box instead, add the `sd-clear-both` utility class
to it, for example with an empty `div` directive:

```{aside} Short aside
:align: right
:width: 25%

A short aside.
```

```{div} sd-clear-both

```

This paragraph is pushed below the aside because the preceding empty `div` has
the `sd-clear-both` class.

## Semantic output

In HTML an aside is rendered as a native
[`<aside>`](https://developer.mozilla.org/en/docs/Web/HTML/Element/aside)
element (not a plain `<div>`), which correctly conveys "tangentially related
content" to assistive technologies and reader modes. In non-HTML outputs
(LaTeX, text, ...) it degrades to a plain titled block. No JavaScript is
involved: the float and the responsive collapse are pure CSS.

## `aside` options

align
: Float direction of the aside: `left` or `right` (default `right`).

width
: Width of the aside from the `md` breakpoint up: `25%`, `33%` or `50%`
  (default `33%`).

margin
: Outer margin of the aside.
  One (all) or four (top bottom left right) values from: 0, 1, 2, 3, 4, 5, auto.

name
: Set a reference-able name for the aside (attached to the title, where
  present, so it can be used as the cross-reference text).

class
: Additional CSS classes for the (outer) `<aside>` element.

class-title
: Additional CSS classes for the title element.

class-body
: Additional CSS classes for the body element.

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/aside-options.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/aside-options.txt
:language: rst
```
````
`````
