# Brief 09: Fix paragraph class handling in dropdowns and cards (`sd-card-text`)

**Type**: bug fix | **Size**: small | **Closes**: #40, plus an unreported class-wiping bug.

## Bug 1 (unreported, verified): dropdown transform wipes paragraph classes

`sphinx_design/dropdown.py:230-234`:

```python
if use_card:
    for para in findall(body_node)(nodes.paragraph):
        para["classes"] = ([] if "classes" in para else para["classes"]) + [
            "sd-card-text"
        ]
```

The conditional is **inverted**, and docutils Elements always initialise a
`classes` attribute — so `"classes" in para` is always true and every
paragraph in every dropdown body has its existing classes **replaced** by
`["sd-card-text"]`. Any user class added to a paragraph inside a dropdown
(e.g. via the `class` directive or MyST `attrs_block`) is silently destroyed.
Compare the correct pattern in `cards.py:249-250`:
`para["classes"] = [*para.get("classes", []), "sd-card-text"]`.

## Bug 2 (#40): `sd-card-text` applied too deeply

Both `CardDirective.add_card_child_classes` (`cards.py:246-250`) and the
dropdown loop above use `findall` — stamping `sd-card-text` on **all
descendant** paragraphs, including paragraphs inside nested admonitions,
list items, nested dropdowns, etc. `sd-card-text` sets card typography
(margin adjustments) meant for direct body text; applying it to nested
content causes the spacing artefacts reported in #40 (extra
first-line spacing for multi-paragraph dropdown content).

## What to do

1. Fix the inverted conditional (append, never replace).
2. Restrict stamping to **direct children** in both sites:

   ```python
   for para in node.children:
       if isinstance(para, nodes.paragraph):
           para["classes"] = [*para.get("classes", []), "sd-card-text"]
   ```

   In the dropdown transform, "node" is `body_node`'s children
   (`body_children`); in cards, each of header/body/footer components.
3. Evaluate (and note in the PR) the alternative of dropping the Python
   stamping entirely for a CSS child selector
   (`.sd-card-body > p { ... }` in `style/_cards.scss`) — do NOT do it in
   this PR (it changes specificity against themes); record it as a follow-up
   for the card redesign (brief 16).

## Tests

- Regenerate affected doctree regressions (`tox -- --force-regen`, then
  review the diff carefully: only `classes` attributes on paragraphs should
  change).
- New snippets:
  - dropdown containing a paragraph with a user class (rst
    `.. rst-class::` / myst attrs) → class survives alongside `sd-card-text`;
  - card and dropdown each containing an admonition with paragraphs → nested
    paragraphs do **not** get `sd-card-text`;
  - the #40 reproduction (dropdown with two paragraphs) → both direct
    paragraphs styled identically.
- Visual check with `tox -e docs-furo`: dropdown/card spacing in the docs
  pages unchanged for the standard examples.

## Acceptance criteria

- No user-authored class is ever removed.
- `sd-card-text` appears only on direct child paragraphs of card/dropdown
  bodies (and header/footer for cards).
- #40 reproduction renders with consistent spacing.
