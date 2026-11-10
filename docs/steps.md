(sd-steps)=

# Steps

The `steps` directive lays out a numbered, visually connected procedure — useful
for install guides, tutorials and any ordered "do this, then this" content.
Each `step` is numbered automatically, so inserting, removing or re-ordering
steps never means renumbering by hand.

::::{steps}

:::{step} Install the package
Run `pip install sphinx-design`.
:::

:::{step} Configure your project
Add `sphinx_design` to the `extensions` list in your `conf.py`.
:::

:::{step} Build the docs
You are ready to use the components.
:::
::::

`````{dropdown-syntax}

````{tab-set-code}
```{literalinclude} ./snippets/myst/step-basic.txt
:language: markdown
```
```{literalinclude} ./snippets/rst/step-basic.txt
:language: rst
```
````
`````

:::{note}
The visible numbers are drawn with CSS counters, but the underlying markup is an
ordinary ordered list (`<ol>`/`<li>`). This means:

- The numbering is *semantic*: assistive technology announces the step count and
  position, and non-HTML builders (LaTeX, `make text`, …) degrade to a plain
  numbered list.
- No number is stored in the document, so translations and re-ordering can never
  desynchronise the visible numbers.
:::

## Titled and untitled steps

The step title is optional. Provide it as the directive argument, or omit it for
a bare numbered step.

::::{steps}

:::{step} A step with a title
Content for the titled step.
:::

:::{step}
A step with no title — just numbered content.
:::
::::

## Numbering offset

Use the `start` option on `steps` to begin the numbering at a value other than
`1`, for example when a procedure is split across sections. Both the visible
markers and the ordered-list semantics start from that value.

::::{steps}
:start: 4

:::{step} Fourth step
The markers, and the underlying `<ol start="4">`, both start at 4.
:::

:::{step} Fifth step
And continue from there.
:::
::::

## Colours

By default the markers use the `primary` semantic colour, so they retint
automatically with your theme. Use the `color` option to pick another semantic
colour — one of `primary`, `secondary`, `success`, `info`, `warning`, `danger`,
`light`, `muted`, `dark`, `white` or `black`.

::::{steps}
:color: success

:::{step} Prepare
The colour applies to every marker in the set.
:::

:::{step} Deploy
Ship it.
:::
::::

## Nesting other components

A step can contain any content, including code blocks, dropdowns and other
components.

::::::{steps}

:::::{step} Add the configuration
Drop this into your `conf.py`:

```python
extensions = ["sphinx_design"]
```
:::::

:::::{step} Read the details

::::{dropdown} Why this works
`sphinx_design` registers the directives when the extension is loaded.
::::
:::::
::::::

## `steps` options

start
: The number the first step is labelled with (a non-negative integer, default `1`).

color
: The semantic colour of the step markers.
  One of: `primary`, `secondary`, `success`, `info`, `warning`, `danger`, `light`, `muted`, `dark`, `white`, `black`.

class
: Additional CSS classes for the container element.

## `step` options

class
: Additional CSS classes for the step (list item) element.

class-title
: Additional CSS classes for the title element.

class-content
: Additional CSS classes for the content element.
