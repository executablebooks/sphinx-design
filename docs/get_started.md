# Getting Started

```{article-info}
:avatar: images/ebp-logo.png
:avatar-link: https://executablebooks.org
:author: "[Chris Sewell](https://github.com/chrisjsewell)"
:date: "{sub-ref}`today`"
:read-time: "1 min read"
:class-avatar: sd-animate-grow50-rot20
```

## Usage

Simply pip install `sphinx-design` and add the extension to your `conf.py`:

```python
extensions = ["sphinx_design"]
```

For using with [MyST Parser](https://github.com/executablebooks/myst-parser), for Markdown documentation, it is recommended to use the `colon_fence` syntax extension:

```python
extensions = ["myst_parser", "sphinx_design"]
myst_enable_extensions = ["colon_fence"]
```

## Configuration

To hide the the title header on the landing page (i.e. root document), add the following to your `conf.py`:

```python
sd_hide_root_title = True
```

## Supported browsers

- Chrome >= 60
- Firefox >= 60
- Firefox ESR
- iOS >= 12
- Safari >= 12
- Explorer >= 12

(Mirrors: <https://github.com/twbs/bootstrap/blob/v5.0.2/.browserslistrc>)
