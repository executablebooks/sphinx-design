# Getting Started

```{article-info}
:avatar: images/ebp-logo.png
:avatar-link: https://executablebooks.org
:author: "[Chris Sewell](https://github.com/chrisjsewell)"
:date: "{sub-ref}`today`"
:read-time: "1 min read"
:class-avatar: sd-animate-grow50-rot20
```

## Usage

Simply pip install `sphinx-design` and add the extension to your `conf.py`:

```python
extensions = ["sphinx_design"]
```

For using with [MyST Parser](https://github.com/executablebooks/myst-parser), for Markdown documentation, it is recommended to use the `colon_fence` syntax extension:

```python
extensions = ["myst_parser", "sphinx_design"]
myst_enable_extensions = ["colon_fence"]
```

:::{note}
The MyST Markdown examples in this documentation assume that certain optional [MyST syntax extensions](https://myst-parser.readthedocs.io/en/latest/syntax/optional.html) are enabled — extend the `myst_enable_extensions` list shown above with them as needed:

- `colon_fence`: used by all examples, to write directives delimited by `:::` fences
- `html_image`: only for examples using raw HTML `<img>` tags, such as the avatar images in [CSS Classes](./css_classes.md)
- `attrs_inline`: only for examples adding attributes to inline elements, such as the links to synchronised [Tabs](./tabs.md)
:::

## Configuration

### Global options

All global configuration options are prefixed with `sd_`, and can be set in your `conf.py`.
Values are always simple, TOML-compatible, data types:

{{ sd_config_options }}

### Hiding the page title

To hide the title header of a page, add to the top of the page:

::::{tab-set}
:::{tab-item} MyST Markdown
```markdown
---
sd_hide_title: true
---
```
:::
:::{tab-item} RestructuredText
```rst
:sd_hide_title:
```
:::
::::

### Creating custom directives

:::{versionadded} 0.6.0
:::

You can use the `sd_custom_directives` configuration option in your `conf.py` to add custom directives, with default option values:

```python
sd_custom_directives = {
    "dropdown-syntax": {
        "inherit": "dropdown",
        "argument": "Syntax",
        "options": {
            "color": "primary",
            "icon": "code",
        },
    }
}
```

The key is the new directive name to add, and the value is a dictionary with the following keys:

- `inherit`: The directive to inherit from (e.g. `dropdown`)
- `argument`: The default argument (optional, only for directives that take a single argument)
- `options`: A dictionary of default options for the directive (optional)

## Supported browsers

sphinx-design targets [**Baseline** Widely Available](https://web.dev/baseline)
web features — those interoperable across Chrome, Edge, Firefox and Safari for
at least 30 months (in practice, the evergreen browsers of roughly the last
2½ years). Internet Explorer is not supported.

Individual features may additionally use *Baseline Newly Available* CSS where it
degrades gracefully; such exceptions are noted in the relevant feature's
documentation.

## Migrating from sphinx-panels

This package arose as an iteration on [sphinx-panels](https://github.com/executablebooks/sphinx-panels), with the intention to make it more flexible, easier to use, and minimise CSS clashes wth sphinx themes.

Notable changes:

### Reduce direct use of CSS classes

These are replaced by the use of directive options, which are:

- Easier to understand
- Easier to validate
- Easier to work with non-HTML outputs
- Easier to improve/refactor

### `panel` directive replaced

The `panel` directive is replaced by the use of the top-level `grid` directive,
then using `grid-item-card` directive children, rather than delimiting cards by `---`.

If no card is needed, then the `grid-item` directive can be used instead and `card` can be also used independently of grids.

Approximately, `.. panels::` is equivalent to `.. grid:: 1 2 2 2` with option `:gutter: 2`.

### `tabbed` directive replaced

The `tabbed` directive is replaced by the use of the top-level `tab-set` directive,
then using `tab-item` directive children.

The `:sync:` option allows to synchronize tab selection across sets.

The `tab-set-code` directive provides a shorthand for synced code examples.

### `link-button` directive replaced

The `link-button` directive is replaced by the use of `button-ref`/`button-link`.

Directive options have also been added to replace the use of classes:

- `stretched-link` -> `:click-parent:`
- `btn-block` -> `:expand:`

### `octicon` icon role

The default SVGs produced are now sized relative to the surrounding text (i.e. using `1em`).
The syntax for specifying a custom size and adding classes is also changed.

This is similar for favicon icons, where the `,` delimiter is also replaced by `;`, e.g. ``:fa:`name,class` `` -> ``:fa:`name;class` ``.

### Improved CSS

Updated Bootstrap CSS from v4 -> v5,
which in particular allows top-level grid to define both column numbers and gutter sizes.

All CSS classes are prefixed with `sd-` (no clash with other theme/extension CSS)

All colors use CSS variables (customisable)
