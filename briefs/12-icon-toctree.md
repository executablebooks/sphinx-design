# Brief 12: Icon roles must not break toctrees

**Type**: bug fix (investigation-first) | **Size**: medium | **Closes**: #99; answers #117.

## Symptoms

- **#99**: a section title *beginning* with an inline icon role
  (`:octicon:`/`:material-*:`) renders wrongly in a `toctree` listing — entry
  appears tiny and/or is skipped.
- **#117**: icon role syntax written directly in a `toctree` entry title
  (`Quick Start :octicon:\`rocket;1em\``) shows as raw text in the sidebar.

## Root-cause analysis (to verify first)

The octicon/material roles return `nodes.raw(format="html")` containing the
full `<svg>` markup (`sphinx_design/icons.py:140-142` and `339-341`).

- For #99: TocTree entries are built from copies of title children. Two
  failure paths to check: (a) `sphinx.util.nodes.clean_astext` — `astext()`
  of the raw node returns the entire SVG markup as *text*, polluting
  plain-text contexts (toc labels, `html_title`s, search index); (b) some
  toc processing strips raw nodes entirely. Reproduce with a minimal project
  (section title starting with an icon + a toctree listing it) and inspect
  the generated sidebar HTML.
- #117 is different: toctree *entry titles* (`Title <target>` lines inside
  the `toctree` directive) are plain text — roles are never parsed there.
  That is core-Sphinx behaviour, not fixable here.

## What to do

1. **Reproduce** both, capture the bad HTML in the PR description.
2. **Replace `nodes.raw` with a purpose-built inline node** for octicon and
   material roles (fontawesome already uses one — `icons.py:184`):

   ```python
   class sd_icon(nodes.inline, nodes.General):
       """Inline SVG icon; attributes: svg (str), alt text children."""
   ```

   - html visitor: write `node["svg"]`, raise `SkipNode`.
   - latex/text/man/texinfo: `SkipNode` silently (icons are decorative;
     matches current effective behaviour but without raw-node side effects).
   - Crucially `astext()` must return `""` (give the node no Text children),
     so `clean_astext`-based contexts (toc labels, search) get clean text.
3. Check the doctree copy path: the node carries `svg` in `attributes`, so
   `deepcopy` used by TocTreeCollector preserves it and sidebar rendering
   goes through the same html visitor → icon renders in the sidebar at
   correct size. If sidebar SVG sizing is off (icons use `em` heights,
   sidebar font-size differs), that is acceptable/correct behaviour.
4. **#117**: document in `docs/badges_buttons.md` (icons section) that roles
   cannot be used inside `toctree` entry titles (Sphinx parses those as
   plain text), and close #117 with that explanation. Suggest the supported
   alternative: icon in the page's own H1 (#99 now works) or theme-level
   sidebar customization.
5. **Also migrate `article_info.py` icons** to the new node: it wraps
   octicons in `nodes.raw(..., classes=["sd-pr-2"], format="html")`
   (`sphinx_design/article_info.py:151-156` and `:168-173`) — but the HTML
   writer ignores attributes on raw nodes, so the `sd-pr-2` padding class is
   **silently dropped** today. With `sd_icon`, pass the classes through
   `get_octicon(..., classes=[...])` so they land on the `<svg>` element.
   (Fixes a latent spacing bug; check rendered article-info before/after.)

## Tests

- Snippet: document with `# :octicon:\`rocket\` Title` heading + second doc
  with a toctree referencing it → doctree regression (new `sd_icon` node) +
  a misc test asserting the built sidebar HTML contains the entry text
  exactly once and an `<svg` element inside the toc `<li>`.
- Search index sanity: `objects`/`titles` in `searchindex.js` for that doc
  contain no `<svg` markup.
- Existing icon snippets regenerate (raw → sd_icon in XML regressions);
  review that HTML output (`snippet_post_*`) is byte-identical for body
  rendering.

## Acceptance criteria

- #99 reproduction: toctree entry renders full-size text + inline icon (or
  cleanly without icon), never skipped/shrunk.
- No SVG markup leaks into any plain-text context.
- #117 closed as documented limitation with docs link.
