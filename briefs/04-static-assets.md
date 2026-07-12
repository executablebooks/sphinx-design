# Brief 04: Rework static asset handling

**Type**: refactor + bug fix | **Size**: medium | **Closes**: #200, #235; supersedes PR #241.

## Problem

`update_css_js` (`sphinx_design/extension.py:79-111`) runs on
`builder-inited` for **every** builder and:

1. creates `<outdir>/_sphinx_design_static/` and appends it to
   `html_static_path` — so the directory pollutes LaTeX/other build outputs
   (#200), and `Path.mkdir(exist_ok=True)` (no `parents=True`) crashes when
   the outdir doesn't exist yet (Sphinx ≥8.1 on Windows creates outdir later —
   #235);
2. hand-rolls CSS change detection (`app.env.sphinx_design_css_changed`, an
   unnamespaced env attribute) plus `update_css_links` on `env-updated`
   (`extension.py:114-117`) forcing all-docs rewrites;
3. keeps an md5-hashing branch for Sphinx <7.1 (`extension.py:97-99`) that is
   obsolete once the floor moves to 7.1 (Sphinx ≥7.1 appends a content
   checksum to CSS URLs itself — sphinx-doc/sphinx#11415).

## What to do

1. **Bump the Sphinx floor**: `pyproject.toml` `dependencies = ["sphinx>=7.2,<10"]`.
   (CI installs `sphinx~=7.0` which resolves to 7.4.x, so the matrix is
   unaffected; update the matrix entry name if you want it explicit.)
   7.1 is the minimum for native CSS checksums; going to 7.2 additionally
   lets you delete the `sphinx_path` compat branch in
   `tests/conftest.py:16-20` — do that here.
2. **Create a real static dir in the package**: `sphinx_design/static/`
   containing exactly two files, named as they should appear in the output:
   - `sphinx-design.min.css` (move/rename from `compiled/style.min.css`)
   - `design-tabs.js` (move/rename from `compiled/sd_tabs.js`)

   Update `package.json` (`scripts.css` output path) and the `css` pre-commit
   hook comment (`.pre-commit-config.yaml`) accordingly. The icon JSON/LICENSE
   data stays in `sphinx_design/compiled/` (it must NOT be copied to `_static`,
   which is why the whole `compiled/` dir can't be the static path).
3. **Replace the two event handlers** with a single `builder-inited` hook:

   ```python
   def add_static_assets(app: Sphinx) -> None:
       if app.builder.format != "html":
           return
       app.config.html_static_path.append(str(STATIC_DIR))
       app.add_css_file("sphinx-design.min.css")
       app.add_js_file("design-tabs.js")
   ```

   Delete `update_css_js`, `update_css_links`, the `env-updated` connect, the
   `sphinx_design_css_changed` env attribute, and the md5/`sphinx_version`
   import. Sphinx handles copying, checksumming (`?v=<hash>` cache-busting),
   and incremental-build correctness.
4. **Packaging**: flit includes package dirs automatically; verify with
   `flit build` + inspect the wheel that `sphinx_design/static/*` is present
   and `style/` is still excluded from the sdist (`[tool.flit.sdist]`).
5. **Update `_compat.py`**: `read_text` is still used for icons; `findall` can
   also be dropped in this PR (docutils ≥0.18 guaranteed by Sphinx ≥7 —
   replace the 5 call sites with `node.findall(...)` and delete the shim).

## Tests

- Existing suite must pass (`tox`); regressions should not change (doctrees
  are unaffected).
- New test (uses the builder-parametrized `sphinx_builder` fixture from
  brief 03 / PR #264, or `make_app` directly):
  - `latex` build of a minimal project → assert `_sphinx_design_static` does
    **not** exist in outdir and build succeeds (regression for #200/#235);
  - `html` build → assert `_static/sphinx-design.min.css` and
    `_static/design-tabs.js` exist and are referenced from `index.html` with
    a `?v=` checksum suffix.
- Manual check: `BUILDER=latex tox -e docs-furo` completes; `tox -e docs-furo`
  twice in a row (incremental) still injects CSS on unchanged pages.

## Acceptance criteria

- No writes into `outdir` outside of Sphinx's own copying.
- #200 and #235 reproduction cases pass; PR #241 closed with a comment
  crediting it and pointing here.
- Net LOC in `extension.py` clearly negative.

## Gotchas

- Do not rename the output filenames (`sphinx-design.min.css`,
  `design-tabs.js`) — downstream themes/users may reference them.
- `html_static_path` mutation must happen in `builder-inited` (config is
  already initialized; appending in `setup()` is too early to know the
  builder and would apply to non-HTML builders via config-inited copies).
- The RTD/epub builder: `app.builder.format` for epub is `"epub"`? No —
  epub's format is `"html"`-family (`Epub3Builder.format == "epub"`); decide
  explicitly: gate on `format == "html"` (excludes epub, which previously DID
  get the assets via `html_static_path`). To preserve epub behaviour, gate on
  `isinstance(app.builder, StandaloneHTMLBuilder)` instead and add an epub
  smoke test. Check what v0.7.0 actually did for epub before choosing.
