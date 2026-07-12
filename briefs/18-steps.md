# Brief 18: New component — `steps` (numbered procedure)

**Type**: new component | **Size**: medium | **CSS-only (counters).**

## Concept

Numbered, visually-connected procedure steps (install guides, tutorials) —
one of the most commonly hand-rolled CSS snippets in Sphinx sites. Pure
directive pair + CSS counters; no JS, no bespoke syntax (parser-portable).

## Syntax

```rst
.. steps::

   .. step:: Install the package

      Run ``pip install sphinx-design``.

   .. step:: Configure

      Add the extension to ``conf.py``.
```

- `steps` options: `class` (class_option), `start` (nonnegative_int,
  default 1 — sets `counter-reset` offset via inline
  `style="--sd-steps-start: N"`).
- `step` options: `class`, `class-title`, `class-content`. Title argument
  optional (`optional_arguments = 1`, `final_argument_whitespace = True`),
  parsed with `inline_text` like tab labels (`sphinx_design/tabs.py:103`).

## Implementation

1. `sphinx_design/steps.py`, following the grid/grid-item pattern
   (`sphinx_design/grids.py`): `StepsDirective` creates
   `create_component("steps", ["sd-steps", ...])`, nested-parses, validates
   children are `step` components (warn `design.steps`; skip inert nodes —
   brief 07 helper). `StepDirective` creates
   `create_component("step", ["sd-step", ...])` containing an optional
   title node (`nodes.rubric` with class `sd-step-title`, matching the
   tab-label/dropdown-title precedent) + a `step-content` component.
   Parent check mirrors `tabs.py:89-95`.
2. Doctree stays a plain container tree → non-HTML builders degrade to
   sequential content with rubric titles (LaTeX acceptable by default;
   note for brief 21).
3. SCSS `style/_steps.scss` + `@use` in `style/index.scss`:
   - `.sd-steps { counter-reset: sd-step calc(var(--sd-steps-start, 1) - 1); }`
   - `.sd-step { counter-increment: sd-step; }` with `::before` circled
     number (`content: counter(sd-step)`), left rail line connecting
     markers (border-left on a padding gutter; hide on last child),
     spacing via existing spacing variables; colors from the semantic
     palette (`style/_colors.scss`) so themes retint automatically.
   - Respect RTL: use `padding-inline-start`/`border-inline-start`.
4. Register via `setup_extension`; works with `sd_custom_directives`.

## Docs

`docs/steps.md` (+ toctree): basic use, `start` offset, titled vs untitled
steps, nesting other components inside a step (code blocks, dropdowns),
rst + myst snippets under `docs/snippets/`.

## Tests

- Doctree regressions (rst + myst): titled, untitled, `start` option,
  nested code-block in step.
- Warning tests: non-step child of steps; step outside steps.
- Post-HTML regression to lock class structure for CSS.
- Visual check on furo + pydata + rtd (`tox -e docs-*`) — include a
  screenshot in the PR.

## Acceptance criteria

- Component documented, tested, CSS committed; markers/rail render
  correctly in light + dark furo modes; degrades readably in `make text`.
