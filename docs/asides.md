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
it stays readable on small screens. On themes with a right-hand in-page table
of contents (such as pydata-sphinx-theme), the main column is already narrower,
so a right-floated aside leaves less room for the wrapped text; prefer a smaller
`width` or `:align: left` there.
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

:::{important} Always clear a *trailing* aside
A float is not contained by its parent section, so an aside that is the **last
element of a section** (with no text left to wrap) can extend past the end of
the section and overlap whatever follows — the next heading, or content injected
by the theme. When an aside is the final piece of a section, follow it with a
cleared block:

```
.. aside:: Wrap-up note
   :align: right

   The last content in this section.

.. div:: sd-clear-both
```

Themes can address this globally instead, by clearfixing their main content
column (for example `.article-container { display: flow-root }`), which
contains every float without an explicit clearing element.
:::

## Semantic output

In HTML an aside is rendered as a native
[`<aside>`](https://developer.mozilla.org/en/docs/Web/HTML/Element/aside)
element (not a plain `<div>`), which correctly conveys "tangentially related
content" to assistive technologies and reader modes. In non-HTML outputs
(LaTeX, text, ...) it degrades to a plain titled block. No JavaScript is
involved: the float and the responsive collapse are pure CSS.

A **titled** aside is labelled by its title: the `<aside>` carries an
`aria-labelledby` attribute pointing at the title element (which is given a
stable, automatically generated id when you do not supply a `:name:`), so screen
readers announce the region by its heading. An **untitled** aside has no heading
text to label it with and is intentionally left unlabelled — give it a title if
you want it announced as a named region.

## Cross-referencing

When you give an aside a `:name:`, the target (and therefore the `id` anchor)
lands on the **title** element for a titled aside, or on the `<aside>` itself
for an untitled one. For a titled aside `` :ref:`the-name` `` renders using the
title text, exactly like referencing a section:

```
.. aside:: Design rationale
   :name: rationale

   ...

See the :ref:`rationale` aside.
```

An **untitled** named aside has no caption text, so — as with any captionless
target in Sphinx — a bare `` :ref:`the-name` `` cannot derive its link text: it
warns and renders as plain text without a link. Reference it with **explicit
text** instead: `` :ref:`jump to the note <the-name>` ``.

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
