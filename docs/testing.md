# Testing utilities

`sphinx-design` ships a small, semi-public helper module,
`sphinx_design.testing`, for downstream extensions that write
[doctree](https://docutils.sourceforge.io/docs/ref/doctree.html) regression
tests (for example [`sphinx-design-elements`](https://github.com/tech-writing/sphinx-design-elements)).

The module has **no dependency on `pytest`** or any test extras, so it can be
imported with only `sphinx_design` installed.

## `normalize_doctree_xml`

```python
normalize_doctree_xml(text: str, extra_attributes: Sequence[str] = ()) -> str
```

Normalizes pretty-printed doctree XML (e.g. from `document.pformat()`) so that
a single set of regression fixtures works across docutils versions: docutils
0.22+ serializes boolean node attributes as `"1"`/`"0"` rather than
`"True"`/`"False"`, and this rewrites the former back to the latter. On
docutils < 0.22 it is a no-op.

Only known boolean attributes are rewritten, so non-boolean `"1"`/`"0"` values
(such as text content or numeric attributes) are left untouched. Pass
`extra_attributes` to also normalize boolean attributes on your own custom
nodes.

## `SphinxBuilder`

The `SphinxBuilder` wrapper used by sphinx-design's own `sphinx_builder`
pytest fixture is also exposed. It is a thin wrapper around a
`sphinx.testing.util.SphinxTestApp` that you construct yourself (e.g. with
sphinx's `make_app` pytest fixture) — it does not create the project
scaffolding for you — giving convenient access to build status/warnings and
doctrees with source paths normalized for regression comparison.

## Stability

This is a *semi-public* testing API:

- the **signatures** of the helpers are covered by the deprecation policy;
- the **exact output** of `normalize_doctree_xml` is **not** guaranteed to be
  stable across docutils versions -- it exists only to smooth over docutils'
  changing serialization for regression testing.

## Example

```python
from sphinx_design.testing import normalize_doctree_xml

# ``doctree`` is a docutils document, e.g. from a Sphinx build
xml = normalize_doctree_xml(doctree.pformat())
file_regression.check(xml, extension=".xml")
```
