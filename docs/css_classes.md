# CSS Classes

For most roles/directive, it is preferentially recommended to use the available options to style components since, for example, this allows for better cross-output-format styling.

But for custom cases, these roles/directives also provide `class` options for adding CSS classes directly to element, or you can directly use the `div` directive.
All CSS classes that are part of sphinx-design are prefixed with `sd-`.

:::{div} sd-text-center sd-font-italic sd-text-primary
Some CSS styled text
:::

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/div-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/div-basic.txt
:language: rst
```
````
`````

If you find yourself using a class(es) often, consider opening an issue to request a new role/directive or option!

## Text

Classes are available for styling and alignment:

- Alignment:
  - `sd-text-justify`
  - `sd-text-left`
  - `sd-text-right`
  - `sd-text-center`
- Weight:
  - `sd-font-weight-light`
  - `sd-font-weight-lighter`
  - `sd-font-weight-normal`
  - `sd-font-weight-bold`
  - `sd-font-weight-bolder`
- Style
  - `sd-font-italic`
  - `sd-text-decoration-none`
  - `sd-text-lowercase`
  - `sd-text-uppercase`
  - `sd-text-capitalize`
- Wrapping
  - `sd-text-wrap`
  - `sd-text-nowrap`
  - `sd-text-truncate` (requires `display: inline-block` or `display: block`)
- Color
  - `sd-text-{semantic color name}` (uses `--sd-color-{semantic color name}` CSS variable)
  - `sd-bg-text-{semantic color name}` (uses `--sd-color-{semantic color name}-text` CSS variable)

## Display

Define the layout of an element and its children (see [`display`](https://developer.mozilla.org/en-US/docs/Web/CSS/display)):

- `sd-d-none`
- `sd-d-inline`
- `sd-d-inline-block`
- `sd-d-block`
- `sd-d-grid`
- `sd-d-flex`
- `sd-d-inline-flex`

Variants are also available for screen-sizes (xs, sm, md, lg), e.g. `sd-d-sm-none`.

Items within a flex box can also be aligned:

- `sd-align-items-start`
- `sd-align-items-end`
- `sd-align-items-center`

## Sizing

Size objects width/height by percentage:

- `sd-width-25`, `sd-height-25`
- `sd-width-50`, `sd-height-50`
- `sd-width-75`, `sd-height-75`
- `sd-width-100`, `sd-height-100`
- `sd-width-auto`, `sd-height-auto`

## Spacing

Padding (`p`) and margins (`m`) can be controlled with these classes for; (`t`)op, (`r`)ight, (`b`)ottom, (`l`)eft, `x` (left and right), and `y` (top and bottom).

Spacing are defined on a scale of 0 to 5, for example `sd-px-1` or `sd-mt-5`.

Note, for grids the special gutter classes `sd-g-{screen-size}-{spacing}` are used to set margins, or for only `x`/`y`; `sd-gx-{screen-size}-{spacing}`.

## Colors

Colors can be set using [CSS variable](./css_variables.md), they are defined for the semantic color names: primary, secondary, success, warning, danger, info, light, dark, and muted.

- `sd-bg-{name}`
- `sd-bg-text-{name}`
- `sd-text-{name}`
- `sd-outline-{name}`

Additional transparent colouring:

- `sd-bg-transparent`
- `sd-outline-transparent`
- `sd-text-transparent`

## Borders

Borders can be applied to elements of thickness 0 to 5, for all are a specific side:

- `sd-border-{thickness}`
- `sd-border-top-{thickness}`
- `sd-border-bottom-{thickness}`
- `sd-border-right-{thickness}`
- `sd-border-left-{thickness}`

````{grid} 1 2 3 3
:gutter: 1

```{grid-item-card}
:shadow: none
:class-card: sd-border-0

`sd-border-0`
```
```{grid-item-card}
:shadow: none
:class-card: sd-border-1

`sd-border-1`
```
```{grid-item-card}
:shadow: none
:class-card: sd-border-2

`sd-border-2`
```
```{grid-item-card}
:shadow: none
:class-card: sd-border-3

`sd-border-3`
```
```{grid-item-card}
:shadow: none
:class-card: sd-border-4

`sd-border-4`
```
```{grid-item-card}
:shadow: none
:class-card: sd-border-5

`sd-border-5`
```
````

Border can be rounded by different amounts using:

- `sd-rounded-0`
- `sd-rounded-1`
- `sd-rounded-2`
- `sd-rounded-3`
- `sd-rounded-pill`
- `sd-rounded-circle`

````{grid} 1 2 3 3
:gutter: 1

```{grid-item-card}
:shadow: none
:class-card: sd-rounded-0

`sd-rounded-0`
```
```{grid-item-card}
:shadow: none
:class-card: sd-rounded-1

`sd-rounded-1`
```
```{grid-item-card}
:shadow: none
:class-card: sd-rounded-2

`sd-rounded-2`
```
```{grid-item-card}
:shadow: none
:class-card: sd-rounded-3

`sd-rounded-3`
```
```{grid-item-card}
:shadow: none
:class-card: sd-rounded-pill

`sd-rounded-pill`
```
```{grid-item-card}
:shadow: none
:class-card: sd-rounded-circle

`sd-rounded-circle`
```
````

## Shadows

Shadows can be applied to box elements (the color of the shadow is defined using `--sd-color-shadow` CSS variable):

- `sd-shadow-none`
- `sd-shadow-sm`
- `sd-shadow-md`
- `sd-shadow-lg`

````{grid} 1 2 3 4
:gutter: 3

```{grid-item-card}
:shadow: none

`sd-shadow-none`
```
```{grid-item-card}
:shadow: sm

`sd-shadow-sm`
```
```{grid-item-card}
:shadow: md

`sd-shadow-md`
```
```{grid-item-card}
:shadow: lg

`sd-shadow-lg`
```
````

## Avatars

Avatars can represent a user or a brand,with a logo or branded graphic ([see Material Design imagery](https://material.io/design/communication/imagery.html#informational-imagery)).

These classes center an image, set their size and add a circular crop:

- `sd-avatar-xs`
- `sd-avatar-sm`
- `sd-avatar-md`
- `sd-avatar-lg`
- `sd-avatar-xl`

````{grid} 1 2 3 3
:gutter: 1

```{grid-item-card} sd-avatar-xs
<img src="images/ebp-logo.png" class="sd-avatar-xs sd-border-1">
```
```{grid-item-card} sd-avatar-sm
<img src="images/ebp-logo.png" class="sd-avatar-sm sd-border-1">
```
```{grid-item-card} sd-avatar-md
<img src="images/ebp-logo.png" class="sd-avatar-md sd-border-1">
```
```{grid-item-card} sd-avatar-lg
<img src="images/ebp-logo.png" class="sd-avatar-lg sd-border-1">
```
```{grid-item-card} sd-avatar-xl
<img src="images/ebp-logo.png" class="sd-avatar-xl sd-border-1">
```
````
