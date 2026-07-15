# Badges, Buttons & Icons {octicon}`rocket`

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
- {bdg-muted}`muted`, {bdg-muted-line}`muted-line`
- {bdg-dark}`dark`, {bdg-dark-line}`dark-line`
- {bdg-white}`white`, {bdg-white-line}`white-line`
- {bdg-black}`black`, {bdg-black-line}`black-line`

`````{dropdown-syntax}

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

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/badge-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/badge-link.txt
:language: rst
```
````
`````

### Badge tooltips

Any badge can be given a tooltip (shown on hover, via the HTML `title`
attribute) by appending a `; tooltip` suffix to its text.
This works for every badge family:

{bdg-primary}`stable ; A released, supported version`
{bdg-link-info}`docs <https://example.com> ; Opens the documentation`
{bdg-ref-primary}`badges <badges> ; Jump to the badges section`

````{tab-set-code}
```markdown
{bdg-primary}`stable ; A released, supported version`
{bdg-link-info}`docs <https://example.com> ; Opens the documentation`
{bdg-ref-primary}`badges <badges> ; Jump to the badges section`
```
```rst
:bdg-primary:`stable ; A released, supported version`
:bdg-link-info:`docs <https://example.com> ; Opens the documentation`
:bdg-ref-primary:`badges <badges> ; Jump to the badges section`
```
````

The tooltip is the text after the **last** unescaped semicolon; both the badge
text and the tooltip are stripped of surrounding whitespace.
To include a literal semicolon in the badge text, escape it as `\;`
(for example `` {bdg}`step 1\; step 2` ``); a trailing bare `;` (with nothing
after it) is not treated as a tooltip and is kept in the badge text.

Because semicolons are valid in URLs and reference targets, the link and
reference badges (`bdg-link-*`, `bdg-ref-*`) only recognise the tooltip suffix
after the explicit `text <target>` form -- a bare target such as
`` {bdg-link-primary}`https://example.com/a;b` `` is never split. To add a
tooltip to a link/ref badge, use the explicit form:
`` {bdg-link-primary}`docs <https://example.com> ; Opens the docs` ``.
A `bdg-ref` tooltip overrides the reference's automatic title.

```{warning}
`title` tooltips are **not** accessible to keyboard or touch users, and are
not surfaced by all screen readers. Do not put essential information in a
tooltip alone -- keep it in the visible badge text (or nearby prose) as well.
```

See [Bootstrap badges](https://getbootstrap.com/docs/5.0/components/badge/) for more information, and related [Material Design chips](https://material.io/components/chip).

(buttons)=

## Buttons

Buttons in Sphinx Design are actually links:

- Links that can be styled to look like
  [Bootstrap buttons](https://getbootstrap.com/docs/5.0/components/buttons/)
- Links that are either external (`button-link`) or internal (`button-ref`)

Most of the time, you should create links using the link syntax for the language
you've chosen:

- [Markdown/MyST links and cross-references](https://myst-parser.readthedocs.io/en/latest/syntax/cross-referencing.html#examples)
- [rST links and cross-references](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#hyperlinks)

Sometimes, though, you may want to call attention to a particular link or set of
links, or set them apart visually from other links on the site.

:::{admonition} Note on accessibility

Despite the name, `button-link` and `button-ref` do **not** convert to
`<button>` tags in HTML. They are output as `<a>` tags and use CSS to achieve
the button look. This has important accessibility implications. For example,
assistive tech will include Sphinx Design "buttons" when asked to present a list
of all the links on the page.
:::

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

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/button-link.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/button-link.txt
:language: rst
```
````
`````

The content of a `button-ref` supports rich inline formatting (such as emphasis
and icons), which is rendered in the button, just as it is for `button-link`:

```{button-ref} buttons
:ref-type: ref
:color: primary

**Bold text**
```

Reference targets may also contain spaces, for example the labels that
`sphinx.ext.autosectionlabel` generates from section titles.

When using [myst-parser](https://myst-parser.readthedocs.io/), you can also set
`ref-type` to `myst` to resolve Markdown-style references.

Use the `click-parent` option to make the button's parent container also clickable.

:::{card} Card with an expanded button

```{button-link} https://example.com
:color: info
:expand:
:click-parent:
```

:::

### `button-link` and `button-ref` options

ref-type (`button-ref` only)
: Type of reference to use; `any` (default), `ref`, `doc`, or `myst`

color
: Set the color of the button (background and font).
  One of the semantic color names: `primary`, `secondary`, `success`, `danger`, `warning`, `info`, `light`, `dark`, `muted`.

outline
: Outline color variant

align
: Align the button on the page; `left`, `right`, `center` or `justify`

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

Inline icon roles are available for the [GitHub octicon](https://primer.style/octicons/), [Google Material Design Icons](https://github.com/google/material-design-icons), or [FontAwesome](https://fontawesome.com/icons?d=gallery&m=free) libraries.

Octicon icons and Material icons are added as SVG's directly into the page with the `octicon` and `material-<flavor>` roles. See below for the different flavors of Material Design Icons.

By default the icon will be of height `1em` (i.e. the height of the font).
A specific height can be set after a semi-colon (`;`) with units of either `px`, `em` or `rem`.
Additional CSS classes can also be added to the SVG after a second semi-colon (`;`) delimiter.

Icon roles can be used within section titles, and the icon is preserved when the
title is referenced from a `toctree` (whilst no longer leaking its SVG markup
into plain-text contexts such as the search index).

:::{note}
Icon roles cannot be used inside a `toctree` *entry title*
(the `Title <target>` form written directly in the `toctree` directive),
because Sphinx parses those titles as plain text, so roles are never processed.
To show an icon next to a page's toctree entry, place the icon role in that
page's own top-level heading instead, and reference the page without an explicit
title.
:::

### Octicon Icons

A coloured icon: {octicon}`report;1em;sd-text-info`, some more text.

````{tab-set-code}
```{literalinclude} ./snippets/myst/icon-octicon.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/icon-octicon.txt
:language: rst
```
````

````{dropdown} All Octicons
:open:

```{_all-octicon}
```
````

### Material Design Icons

Material Design icons come as several flavors. Each flavor represents a different role used in sphinx-design. These flavors are:

- `material-regular`
- `material-outlined`
- `material-round`
- `material-sharp`
- `material-twotone`

Not all icons are available for each flavor, but most are. Instead of displaying the 10660+ icons here, you are encouraged to browse the available icons from the [Material Design Icons' showcase](https://fonts.google.com/icons) hosted by Google.

- A regular icon: {material-regular}`data_exploration;2em`, some more text
- A coloured regular icon: {material-regular}`settings;3em;sd-text-success`, some more text.
- A coloured outline icon: {material-outlined}`settings;3em;sd-text-success`, some more text.
- A coloured sharp icon: {material-sharp}`settings;3em;sd-text-success`, some more text.
- A coloured round icon: {material-round}`settings;3em;sd-text-success`, some more text.
- A coloured two-tone icon: {material-twotone}`settings;3em;sd-text-success`, some more text.

````{tab-set-code}
```{literalinclude} ./snippets/myst/icon-material-design.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/icon-material-design.txt
:language: rst
```
````

### FontAwesome Icons

FontAwesome icons are added via the FontAwesome CSS classes.
The role name selects the icon *style* — solid (`fa-solid`/`fas`/`fa`),
brands (`fa-brands`/`fab`) or regular (`fa-regular`/`far`) — and you can pick
any spelling:

- A solid icon {fa-solid}`rocket;sd-text-primary`, some more text.
- A brand icon {fa-brands}`github`, some more text.
- A regular icon {fa-regular}`bell;sd-text-warning`, some more text.

By default each role emits exactly the classes it is named after: the
`fa-solid` role applied to `rocket` produces
`<span class="fa-solid fa-rocket">`, while the `fas` role produces
`<span class="fas fa-rocket">`.

#### Matching your FontAwesome version

Set `sd_fontawesome_version` to the major version of the FontAwesome CSS you
load, and every role spelling is translated to that version's class scheme —
so the role names are version-agnostic: write whichever spelling you prefer,
and upgrading (or downgrading) FontAwesome is a one-line `conf.py` change:

```python
sd_fontawesome_version = "6"
```

| Roles | Style | `"4"` | `"5"` | `"6"` |
| ----- | ----- | ----- | ----- | ----- |
| `fa`, `fas`, `fa-solid` | solid | `fa` | `fas` | `fa-solid` |
| `fab`, `fa-brands` | brands | `fa` | `fab` | `fa-brands` |
| `far`, `fa-regular` | regular | `fa` | `far` | `fa-regular` |

The default, `"as-named"`, emits the role name verbatim as the leading class
(the behaviour shown above, and of previous sphinx-design versions).

```{note}
The bare `fa` role maps to *solid* under `"5"`/`"6"` (FontAwesome 4's single
style became solid in v5). Conversely, `"4"` collapses all style distinctions
to `fa` in the HTML classes, since FontAwesome 4 had no style prefixes —
LaTeX output is unaffected (it always uses the role's own style).

Only the leading *style* class is translated — icon **names** that FontAwesome
renamed between versions (e.g. v4 `external-link` vs v6
`arrow-up-right-from-square`) are emitted as written, just like in the LaTeX
note below.
```

#### Loading the FontAwesome CSS

sphinx-design does **not** bundle the FontAwesome CSS.
By default (`sd_fontawesome_source = "none"`) you, or your theme, are
responsible for making it available (many themes already include it).

To have sphinx-design load it for you from a
[FontAwesome CDN](https://cdnjs.com/libraries/font-awesome),
so you no longer have to hand-edit
[`html_css_files`](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_css_files),
set:

```python
sd_fontawesome_source = "cdn"
```

This adds `sd_fontawesome_cdn_url` (a FontAwesome v6 `all.min.css` by default)
to the HTML output. Override `sd_fontawesome_cdn_url` to pin a different
version or a self-hosted copy.

````{warning}
Since the FontAwesome icons are fetched directly from their distributed CSS, specifying a height/size to the icon roles is not supported.
However, you can always add your custom CSS class that controls the `font-size` property.

If a height/size is supplied to an icon role, then it will be interpreted as a CSS class.
There can only be a maximum of 1 `;` in the roles' arguments
````

````{tab-set-code}
```markdown
- An icon {fa-solid}`spinner;sd-text-primary`, some more text.
- An icon {fa-brands}`github`, some more text.
- An icon {fa-brands}`gitkraken;sd-text-success fa-xl`, some more text.
- An icon {fa-solid}`skull;sd-text-danger`, some more text.
```
```rst
- An icon :fa-solid:`spinner;sd-text-primary`, some more text.
- An icon :fa-brands:`github`, some more text.
- An icon :fa-brands:`gitkraken;sd-text-success fa-xl`, some more text.
- An icon :fa-solid:`skull;sd-text-danger`, some more text.
```
````

- An icon {fa-solid}`spinner;sd-text-primary`, some more text.
- An icon {fa-brands}`github`, some more text.
- An icon {fa-brands}`gitkraken;sd-text-success fa-xl`, some more text.
- An icon {fa-solid}`skull;sd-text-danger`, some more text.

#### Using FontAwesome Pro kits

If you use a [FontAwesome Pro kit](https://fontawesome.com/kits), keep
`sd_fontawesome_source = "none"` (do **not** also load the free CDN, whose
own font-face would fight your kit), load the kit as usual, and either use the
v6 role names (`fa-solid`/`fa-brands`/`fa-regular`) directly, or set
`sd_fontawesome_version = "6"`, which makes every spelling — including the
concise `fas`/`fab`/`far` — emit exactly the classes a Pro kit expects.

#### Concise role names

The `fas`, `fab` and `far` roles (and `fa`, which FontAwesome itself
deprecated in v5) are equally supported, with no plans to remove them. By
default (`sd_fontawesome_version = "as-named"`) each role name is emitted
verbatim as the leading CSS class, so these produce the v4/v5 class scheme
(`fas fa-...`):

- An icon {fas}`spinner;sd-text-primary`, some more text.
- An icon {fab}`github`, some more text.
- An icon {far}`bell`, some more text.

The free CDN builds define both class schemes, so the concise names work fine
there as-is. And combined with `sd_fontawesome_version`, the concise names are
future-proof for *any* setup: keep writing `fas`/`fab`/`far` and set the
version knob to match the CSS you load — no source churn when FontAwesome (or
your theme's bundled copy) moves on. The `fa-solid`/`fa-brands`/`fa-regular`
spellings remain handy for matching what fontawesome.com shows for each icon.
Note that not all regular style icons are free; `far`/`fa-regular` only work
with the free ones.

#### FontAwesome in LaTeX output

By default, icons are only rendered for HTML builders.
To also render them in LaTeX output, set `sd_fontawesome_latex` to the LaTeX
package you want to use:

| `sd_fontawesome_latex` | LaTeX package | Rendering |
| ---------------------- | ------------- | --------- |
| `False` / `"none"` (default) | – | icons skipped (one warning per build) |
| `True` / `"fontawesome"` | [`fontawesome`](https://ctan.org/pkg/fontawesome) | `\faicon{name}` |
| `"fontawesome5"` | [`fontawesome5`](https://ctan.org/pkg/fontawesome5) | `\faIcon{name}` (see below) |

```python
sd_fontawesome_latex = "fontawesome5"
```

With `"fontawesome5"`, the icon style is mapped to that package's conventions:
brand icons resolve by name (`\faIcon{github}`), regular-style icons use the
optional style argument (`\faIcon[regular]{name}`), and solid icons use the
default (`\faIcon{name}`). Note that `sd_fontawesome_version` only selects the
*HTML* class scheme; LaTeX rendering is driven by the role's style and
`sd_fontawesome_latex` alone.

If your theme (or another extension) already loads the `fontawesome5` package,
set `sd_fontawesome_latex = "fontawesome5"` so both agree, avoiding the LaTeX
error that comes from mixing the `fontawesome` and `fontawesome5` packages.

```{note}
The LaTeX packages predate FontAwesome 6 and resolve icons by their **v5**
(or v4, for `fontawesome`) names. Icons that were renamed in v6 (for example
`arrow-up-right-from-square`, formerly `external-link-alt`) render in HTML
but will raise an "icon not found" error when building PDF output — use the
older name if you need LaTeX support for such an icon.
```
