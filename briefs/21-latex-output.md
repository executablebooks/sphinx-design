# Brief 21: LaTeX output pass (graceful degradation)

**Type**: bug fix / output quality | **Size**: large | **Closes**: #107, #218; improves #179.
**Depends on**: brief 04 (removes `_sphinx_design_static` from latex outdir, #200).

## Problem

sphinx-design defines almost no LaTeX-specific rendering. The generic
doctree (containers + rubrics) falls through to Sphinx defaults:

- **Dropdowns** (#107): title is a `nodes.rubric` → LaTeX renders
  `\subsubsection*{title}` — dropdown content masquerades as a heading.
- **Tabs** (#218): each tab-item's rubric label becomes a
  `\subsubsection*`, flattening tab semantics into fake headings inside
  `sphinxuseclass` wrappers.
- **Grids/cards** (#179): grid items render sequentially (acceptable) but
  images keep no width constraint → oversized/deformed layout.

The HTML post-transforms (`DropdownHtmlTransform`, `TabSetHtmlTransform`)
are `formats = ("html",)`, so LaTeX sees the "default rendering" doctree
described in the directive docstrings (`sphinx_design/dropdown.py:56-70`,
`sphinx_design/tabs.py:57-73`).

## Approach: a LaTeX post-transform per component

Add `sphinx_design/latex.py` with `SphinxPostTransform`s,
`formats = ("latex",)`, converting components into standard docutils nodes
that Sphinx's LaTeX writer already renders well — no hand-written `.sty`
maintenance:

1. **Dropdown → admonition-like box.** Replace the dropdown container with
   `nodes.admonition` (class `sd-dropdown`) whose first child is
   `nodes.title` built from the rubric's children (or "…" octicon-free
   fallback text when untitled — plain `nodes.title("", "")` with the
   kebab-omitted; use the argument text). Sphinx renders admonitions as
   `sphinxadmonition`/shadow boxes. `:open:`/icons/chevrons are ignored.
2. **Tab-set → sequence of boxed items.** For each tab-item: replace rubric
   with `nodes.strong` label inside a `nodes.container`, or better: one
   `nodes.admonition` per tab-item titled by the label (clearest visual
   grouping in PDF). Drop sync attributes.
3. **Grid images / cards** (#179 mitigation): in latex, constrain images
   inside grid-item/card components: set `node["width"] = "100%"` on
   `nodes.image` descendants that have no explicit width (LaTeX writer maps
   % widths to `\linewidth` fractions). Cards themselves: leave as
   containers (already acceptable); ensure card titles (PassthroughTextElement
   + `sd-card-title`) render as bold text not headings — they are inline
   containers already, verify and lock with a regression.
4. **article-info** (`sphinx_design/article_info.py:73` TODO "only in html"):
   hide in latex — post-transform removes the component for latex builds.

Register the module from `setup_extension` (`extension.py`).

## Non-goals

- True tabbed/interactive PDF widgets; multi-column grid layout in LaTeX
  (explicitly out of scope — document as such).
- `sd_fontawesome_latex` changes (brief 13 owns #242).

## Tests

The builder-parametrized `sphinx_builder` fixture (landed with brief 03 /
PR #264) supports `latex`:

- New regression set `tests/test_snippets.py::test_snippet_latex` running a
  curated subset of snippets (dropdown, tab-set, grid-item-card with image,
  article-info) through the `latex` builder, regressing the doctree after
  post-transforms (pformat XML) — avoids brittle full `.tex` comparison —
  plus targeted assertions that the generated `.tex` contains
  `\begin{sphinxadmonition}` for dropdowns and **no** `\subsubsection*`
  from any sphinx-design component.
- `BUILDER=latex tox -e docs-furo` builds clean; if a TeX toolchain is
  available in CI (`docs-build-format` job already builds `latex` format —
  extend it to run `latexmk`? NO — keep CI TeX-free; the format build
  already catches writer errors).


## Test strategy (two tiers — decided 2026-07)

1. **PDF-compile smoke in CI** (landing separately, before this brief): a
   `doc-builds-pdf` job compiling the latex docs build via
   `xu-cheng/latex-action` (myst-parser's pattern; consider
   `latex_use_xindy = False` to avoid its xindy workaround). This catches
   compile-time breakage (package clashes like #242, undefined icons) that
   `-b latex` output checks cannot. The docs dogfood `sd_fontawesome_latex`,
   so the FA LaTeX path is exercised on every PR.
2. **Systematic per-component `.tex` regressions land WITH this brief, not
   before**: broad `.tex` fixtures written today would lock in the known-bad
   degradation (dropdowns → `\subsubsection*`, etc.) as golden output. When
   this brief's LaTeX pass reworks the rendering, per-component `.tex`
   regression fixtures become its acceptance harness (following the
   `\usepackage{fontawesome5}`/`\faIcon` assertions started in #285).

## Acceptance criteria

- #107: dropdown renders as a titled box, not a heading; PDF bookmarks/toc
  contain no dropdown titles.
- #218: tab items render as labelled boxes, no fake headings.
- #179 example: grid images no longer overflow the page width.
- HTML output byte-identical (transforms are latex-only).
