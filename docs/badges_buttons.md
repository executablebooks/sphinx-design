# Badges, Buttons & Icons

(badges)=

## Badges

Inline badges can be used as a labelling component.
Badges are available in each semantic color, with filled and outline variants:

- {bdg}`plain badge`
- {bdg-primary}`primary`, {bdg-primary-line}`primary-line`
- {bdg-secondary}`secondary`, {bdg-secondary-line}`secondary-line`
- {bdg-success}`success`, {bdg-success-line}`success-line`
- {bdg-info}`info`, {bdg-info-line}`info-line`
- {bdg-warning}`warning`, {bdg-warning-line}`warning-line`
- {bdg-danger}`danger`, {bdg-danger-line}`danger-line`
- {bdg-light}`light`, {bdg-light-line}`light-line`
- {bdg-dark}`dark`, {bdg-dark-line}`dark-line`

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/badge-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/badge-basic.txt
:language: rst
```
````
`````

`bdg-link-` and `bdg-ref-` variants are also available for use with links and references.
The syntax is the same as for the `ref` role.

{bdg-link-primary}`https://example.com`

{bdg-link-primary-line}`explicit title <https://example.com>`

{bdg-ref-primary}`badges`

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/badge-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/badge-link.txt
:language: rst
```
````
`````

See [Bootstrap badges](https://getbootstrap.com/docs/5.0/components/badge/) for more information, and related [Material Design chips](https://material.io/components/chip).

(buttons)=

## Buttons

Buttons allow users to navigate to external (`button-link`) / internal (`button-ref`) links with a single tap.

```{button-link} https://example.com
```

```{button-link} https://example.com
Button text
```

```{button-link} https://example.com
:color: primary
:shadow:
```

```{button-link} https://example.com
:color: primary
:outline:
```

```{button-link} https://example.com
:color: secondary
:expand:
```

```{button-ref} buttons
:color: info
```

```{button-ref} buttons
:color: info

Reference Button text
```

`````{dropdown} Syntax
:icon: code
:color: light

````{tab-set-code}
```{literalinclude} ./snippets/myst/button-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/button-link.txt
:language: rst
```
````
`````

Use the `click-parent` option to make the button's parent container also clickable.

:::{card} Card with an expanded button

```{button-link} https://example.com
:color: info
:expand:
:click-parent:
```

:::

See the [Material Design](https://material.io/components/buttons) and [Bootstrap](https://getbootstrap.com/docs/5.0/components/buttons/) descriptions for further details.

### `button-link` and `button-ref` options

color
: Set the color of the button (background and font).
  One of the semantic color names: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `muted`.

outline
: Outline color variant

expand
: Expand to fit parent width

click-parent
: Make parent container also clickable

tooltip
: Add tooltip on hover

shadow
: Add shadow CSS

class
: Additional CSS classes

(icons)=

## Inline Icons

Inline icon roles are available for both the [GitHub octicon](https://octicons-git-v2.primer.now.sh/octicons/) or [FontAwesome](https://fontawesome.com/icons?d=gallery&m=free) libraries.

Octicon icons are added as SVG's directly into the page, for either 16px (`octicon-16`) or 24px (`octicon-24`) sizes.
Additional CSS classes can be added to the SVG after a semi-colon (`;`) delimiter.

A coloured icon: {octicon-16}`report;sd-text-info`, some more text.

````{tab-set-code}
```markdown
A coloured icon: {octicon-16}`report;sd-text-info`, some more text.
```
```rst
A coloured icon: :octicon-16:`report;sd-text-info`, some more text.
```
````

````{Dropdown} All Octicons (16px)
```{_all-octicon}
:size: 16
```
````

````{Dropdown} All Octicons (24px)
```{_all-octicon}
:size: 24
```
````

FontAwesome icons are added via the Fontawesome CSS classes.
If the theme you are using does not already include the FontAwesome CSS, it should be loaded in your configuration from a [font-awesome CDN](https://cdnjs.com/libraries/font-awesome), with the [html_css_files](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_css_files) option, e.g.:

```python
html_css_files = ["https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/fontawesome.min.css"]
```

Use either `fa` (deprecated in font-awesome v5), `fas` or `fab` for the role name.

````{tab-set-code}
```markdown
An icon {fas}`spinner;sd-bg-primary sd-bg-text-primary`, some more text.
```
```rst
An icon :fas:`spinner;sd-bg-primary sd-bg-text-primary`, some more text.
```
````

An icon {fas}`spinner;sd-bg-primary sd-bg-text-primary`, some more text.

By default, icons will only be output in HTML formats. But if you want fontawesome icons to be output on LaTeX, using the [fontawesome package](https://ctan.org/pkg/fontawesome), you can add to your configuration:

```python
sd_fontawesome_latex = True
```
