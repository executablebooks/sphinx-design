# Brief 07: Stop warning on comments/targets inside grids, carousels, tab-sets

**Type**: bug fix | **Size**: small | **Closes**: #86.

## Problem

Putting a comment (rST `..` or MyST `%`) — or a hyperlink target — inside a
`grid`, `card-carousel`, or `tab-set` produces a confusing
"All children of X should be Y" warning (#86). Comments/targets/system
messages are structurally inert and should be tolerated silently.

## Where (verified against `bbaf94a`)

1. `sphinx_design/grids.py:143-153` — `GridDirective`: warns for any
   non-`grid-item` child of the row (does not remove the child).
2. `sphinx_design/cards.py:286-295` — `CardCarouselDirective`: warns for any
   non-`card` child (does not remove).
3. `sphinx_design/tabs.py:38-53` — `TabSetDirective`: warns for any
   non-`tab-item` child and **drops it** from `tab_set.children`.
4. `sphinx_design/tabs.py:144-154` — `TabSetCodeDirective`: warns for any
   non-`literal_block` child and drops it.

## What to do

Define once in `sphinx_design/shared.py`:

```python
#: node types that are structurally inert inside component containers
SKIP_CHILD_TYPES = (nodes.comment, nodes.target, nodes.system_message)

def is_ignorable_child(node: nodes.Node) -> bool:
    return isinstance(node, SKIP_CHILD_TYPES)
```

Then in each of the four loops: `if is_ignorable_child(item): continue`
(placed *before* the warning check), preserving current keep/drop behaviour
for genuinely-invalid children.

**Special care for `TabSetDirective`**: it rebuilds `tab_set.children` from
`valid_children`, and `TabSetHtmlTransform` (`tabs.py:246-248`) also skips
non-tab-item children. Comments/system-messages may be dropped safely
(render nothing), but **targets must be preserved** or references to them
break: append targets to `valid_children`, and confirm the HTML transform
carries non-tab-item nodes through (it currently drops them when rebuilding
`children` at `tabs.py:291` — move preserved targets to the front of the
rebuilt list).

## Tests

Add snippets to `tests/test_misc/` (or extend `test_misc.py`) building with
`-W`-equivalent warning capture, for rst and myst:

1. grid with a comment between grid-items → no warnings;
2. card-carousel with a comment between cards → no warnings;
3. tab-set with a comment between tab-items → no warnings, tabs render;
4. tab-set with a hyperlink target before a tab-item + a reference to it
   elsewhere → no warnings, reference resolves;
5. control: a paragraph directly inside tab-set still warns
   (`design.tab` subtype), preserving intentional validation.

## Acceptance criteria

- #86 reproduction (comment inside grid with cards) builds clean.
- Existing warning behaviour for real mistakes unchanged (existing tests
  still pass, e.g. any test covering the #258 skip behaviour).
