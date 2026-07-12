# Brief 15: `button-ref` target and nested-content fixes

**Type**: bug fix (one confirmed root cause + one investigation) | **Size**: small-medium
**Closes**: #110; investigates/fixes #228.

## Bug 1 (#110): ref targets are mangled by `directives.uri`

`_ButtonDirective.run_with_defaults` (`sphinx_design/badges_buttons.py:157-158`):

```python
rawtext = self.arguments[0]
target = directives.uri(rawtext)
```

`docutils.parsers.rst.directives.uri` **strips all whitespace**
(`''.join(argument.split())`). Correct for `button-link` URLs, but the same
code path runs for `button-ref`, so a multi-word reference target — exactly
what `sphinx.ext.autosectionlabel` generates from section titles ("My
Article Section" → label `my article section`) — becomes
`myarticlesection` and fails to resolve: `undefined label: myarticlesection`
(the literal error reported in #110).

**Fix**: apply `directives.uri` only in `ButtonLinkDirective`; for
`ButtonRefDirective` use the stripped raw argument
(`self.arguments[0].strip()`) as the target — matching how Sphinx's own
`:ref:` role treats targets (also `ws_re` whitespace-collapse to single
spaces: use `sphinx.util.nodes.ws_re.sub(" ", ...)` like XRefRole does).
Move the `target =` computation into `create_ref_node` implementations or
pass both raw and uri-fied values down.

## Bug 2 (#228): nested parse of button-ref content

Report: rich content (e.g. emphasis/icons) inside `button-ref` renders
wrongly, while identical content in `button-link` is fine.

Both paths build content identically (`badges_buttons.py:177-185`) and
append it to the link node, so the divergence is in **pending_xref
resolution**: when the std/any domain resolves the xref, some resolvers
build the result from `contnode` — which Sphinx passes as
`node[0].astext()`-ish or `node[0]` (the *first child only*) — dropping or
flattening sibling/nested inline nodes, and `refexplicit` interacts with
whether the domain replaces content with the target's title.

Investigation steps:

1. Reproduce with the #228 snippet (button-ref with nested formatting) and
   diff the pre/post-resolution doctrees (`snippet_pre_*` vs
   `snippet_post_*` regression pattern in `tests/test_snippets.py` already
   captures both — add the snippet and inspect).
2. Check `sphinx.transforms.post_transforms.ReferencesResolver.run`: it
   passes `contnode = node[0].deepcopy()` — with the current structure the
   single `nodes.inline` wrapper (`badges_buttons.py:181-182`) *is*
   `node[0]`, so nesting should survive… unless brief 03/PR #264 changed
   the child structure, or messages/system nodes from `inline_text` get
   appended. Verify against the post-#264 structure and fix accordingly
   (likely: ensure exactly one wrapper child; attach inline_text `messages`
   to the *paragraph*, not the xref).
3. Also verify the long-standing TODO at `badges_buttons.py:224` /
   `cards.py:185` ("presence of classes raises an error if the link cannot
   be found"): reproduce an unresolved button-ref → if it crashes rather
   than warning, fix by catching in a `missing-reference` handler or
   stripping classes into the wrapper — separate commit in the same PR.

## Tests

- `button-ref` targeting an autosectionlabel-style multi-word label (rst +
  myst) resolves — build-level test asserting the reference href.
- Nested-markup button content regression (pre and post XML) for both
  button directives.
- Unresolved button-ref → build completes with a `design`-typed or standard
  Sphinx missing-ref warning, no traceback.

## Acceptance criteria

- #110 reproduction resolves correctly; whitespace handling documented in
  the button docs (targets may contain spaces).
- #228 reproduction renders identical inline content for button-link and
  button-ref.
- No behaviour change for plain single-word targets or URL buttons.
