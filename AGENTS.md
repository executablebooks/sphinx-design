# AGENTS.md

This file provides guidance for AI coding agents working on the **sphinx-design** repository.

## Project Overview

sphinx-design is a Sphinx extension for designing beautiful, view size responsive web components. It provides:

- Grids, cards, dropdowns, tabs, badges, buttons, and icons
- Responsive design inspired by [Bootstrap](https://getbootstrap.com/) (v5), [Material Design](https://material.io), and [Material-UI](https://material-ui.com/)
- Support for both reStructuredText and [MyST Markdown](https://myst-parser.readthedocs.io/) (via integration with myst-parser)

The extension works with multiple Sphinx themes including alabaster, sphinx-rtd-theme, pydata-sphinx-theme, sphinx-book-theme, furo, and sphinx-immaterial.

## Repository Structure

```
pyproject.toml          # Project configuration and dependencies
tox.ini                 # Tox test environment configuration

sphinx_design/          # Main source code
├── __init__.py         # Package init with setup() entry point
├── _compat.py          # Compatibility utilities
├── extension.py        # Main Sphinx extension setup
├── shared.py           # Shared constants and base classes
├── badges_buttons.py   # Badge and button directives
├── cards.py            # Card directives
├── dropdown.py         # Dropdown directive
├── grids.py            # Grid directives
├── tabs.py             # Tab directives
├── icons.py            # Icon roles (Material, FontAwesome, Octicons)
├── article_info.py     # Article info directive
└── compiled/           # Compiled static assets (CSS, JS)

style/                  # CSS sources (compiled by tools/generate_css.py)
├── design.toml         # Declarative tokens for the generated utility families
├── cards.css           # Hand-authored card styles
├── tabs.css            # Hand-authored tab styles
├── dropdown.css        # Hand-authored dropdown styles
└── ...                 # Other hand-authored component styles

tools/                  # Dev-only tooling (not shipped in the wheel)
├── generate_css.py     # Builds sphinx_design/static/sphinx-design.min.css
└── check_css_equivalence.py  # CSS rule-set equivalence verifier (tinycss2)

tests/                  # Test suite
├── conftest.py         # Pytest fixtures
├── test_snippets.py    # Snippet-based tests
├── test_misc.py        # Miscellaneous tests
├── test_snippets/      # Test fixture files for snippets
└── test_misc/          # Test fixture files for misc tests

docs/                   # Documentation source (MyST Markdown)
├── conf.py             # Sphinx configuration
├── index.md            # Documentation index
├── get_started.md      # Getting started guide
├── grids.md            # Grid documentation
├── cards.md            # Card documentation
├── tabs.md             # Tab documentation
├── dropdowns.md        # Dropdown documentation
├── badges_buttons.md   # Badge and button documentation
└── snippets/           # Code snippets for docs (myst/, rst/)
```

## Development Commands

All commands should be run via [`tox`](https://tox.wiki) for consistency. The project uses `tox-uv` for faster environment creation.

### Testing

```bash
# Run all tests (default Python version)
tox

# Run tests with a specific Python version
tox -e py311
tox -e py312

# Run a specific test file
tox -- tests/test_snippets.py

# Run a specific test function
tox -- tests/test_snippets.py::test_function_name

# Run tests without myst-parser dependency
tox -e py311-no-myst

# Run with coverage
tox -- --cov=sphinx_design

# Update regression test fixtures
tox -- --force-regen
```

### Documentation

```bash
# Build docs with different themes
tox -e docs-alabaster
tox -e docs-rtd
tox -e docs-pydata
tox -e docs-sbt
tox -e docs-furo
tox -e docs-im

# Clean build (set CLEAN env var)
CLEAN=1 tox -e docs-furo

# Build with a different builder (e.g., linkcheck)
BUILDER=linkcheck tox -e docs-furo
```

### Code Quality

```bash
# Type checking with mypy
tox -e mypy

# Linting with ruff (auto-fix enabled)
tox -e ruff-check -- --fix

# Formatting with ruff
tox -e ruff-fmt

# Run pre-commit hooks on all files
pre-commit run --all-files

# Regenerate the compiled CSS artifact
python tools/generate_css.py
# or via pre-commit
pre-commit run --all css
```

## Code Style Guidelines

- **Formatter/Linter**: Ruff (configured in `pyproject.toml`)
- **Type Checking**: Mypy (configured in `pyproject.toml`)
- **Pre-commit**: Use pre-commit hooks for consistent code style

### Best Practices

- **Type annotations**: Use complete type annotations for all function signatures.
- **Docstrings**: Use Sphinx-style docstrings (`:param:`, `:return:`, `:raises:`).
- **Directive classes**: Extend `SdDirective` (from `shared.py`) for new directives.
- **Warning messages**: Use `WARNING_TYPE = "design"` for consistent warning categorization.
- **Testing**: Write tests for all new functionality. Use `pytest-regressions` for output comparison.

### Docstring Example

```python
def create_component(
    name: str,
    rawtext: str,
    *,
    classes: Sequence[str] = (),
) -> nodes.container:
    """Create a component container node.

    :param name: The component name.
    :param rawtext: The raw text content.
    :param classes: Additional CSS classes to apply.
    :return: A container node with the component.
    """
    ...
```

## Testing Guidelines

### Test Structure

- Tests use `pytest` with fixtures from `conftest.py`
- Regression testing uses `pytest-regressions` for output comparison
- The `sphinx_builder` fixture creates temporary Sphinx projects for testing

### Writing Tests

1. Use the `sphinx_builder` fixture to create test Sphinx applications
2. Add test content as `.txt` files in `tests/test_snippets/` or `tests/test_misc/`
3. Use `file_regression` or `data_regression` fixtures for comparing output

### Example Test Pattern

`````python
def test_grid_basic(sphinx_builder, file_regression):
    builder = sphinx_builder()
    builder.src_path.joinpath("index.md").write_text(
        """
# Test

````{grid} 2
:gutter: 1

```{grid-item}
Item 1
```

```{grid-item}
Item 2
```
````
""",
        encoding="utf8",
    )
    builder.build()
    doctree = builder.get_doctree("index")
    file_regression.check(doctree.pformat(), extension=".xml")
`````

## Commit Message Format

Use this format:

```
<EMOJI> <KEYWORD>: Summarize in 72 chars or less (#<PR>)

Optional detailed explanation.
```

Keywords:

- `✨ NEW:` – New feature
- `🐛 FIX:` – Bug fix
- `👌 IMPROVE:` – Improvement (no breaking changes)
- `‼️ BREAKING:` – Breaking change
- `📚 DOCS:` – Documentation
- `🔧 MAINTAIN:` – Maintenance changes only (typos, etc.)
- `🧪 TEST:` – Tests or CI changes only
- `♻️ REFACTOR:` – Refactoring

If the commit only makes changes to a single module,
consider including the name in the title.

## PR title and description format

Use the same as for the commit message format,
but for the title you can omit the `KEYWORD` and only use `EMOJI`

## Pull Request Requirements

When submitting changes:

1. **Description**: Include a meaningful description or link explaining the change
2. **Tests**: Include test cases for new functionality or bug fixes
3. **Documentation**: Update docs if behavior changes or new features are added
4. **Changelog**: Update `CHANGELOG.md` under the appropriate section
5. **Code Quality**: Ensure `pre-commit run --all-files` passes

## Architecture Overview

### Extension Setup

The extension follows a modular architecture where each component type has its own module:

```
setup() in __init__.py
    └── setup_extension() in extension.py
            ├── setup_badges_and_buttons()
            ├── setup_cards()
            ├── setup_grids()
            ├── setup_dropdown()
            ├── setup_icons()
            ├── setup_tabs()
            └── setup_article_info()
```

### Key Components

#### Base Classes (`sphinx_design/shared.py`)

- `SdDirective`: Base class for sphinx-design directives (extends `SphinxDirective`)
- `create_component()`: Factory function for creating component nodes
- `WARNING_TYPE`: Constant for warning categorization

#### Directives

Each component type has its own module with directives:

- **Grids** (`grids.py`): `grid`, `grid-item`, `grid-item-card` directives
- **Cards** (`cards.py`): `card`, `card-header`, `card-footer`, `card-carousel` directives
- **Tabs** (`tabs.py`): `tab-set`, `tab-item` directives
- **Dropdowns** (`dropdown.py`): `dropdown` directive
- **Badges/Buttons** (`badges_buttons.py`): `button-link`, `button-ref` directives and `bdg-*` roles
- **Icons** (`icons.py`): Icon roles for Material, FontAwesome, and Octicons

#### Static Assets

Compiled CSS and JS are stored in `sphinx_design/static/`:

- CSS is generated from the `style/` sources (see below)
- JavaScript for tab functionality

### Styling

The extension uses plain CSS, built by a small Python generator (no Node/Sass):

1. Hand-authored component CSS lives in `style/*.css`, expanded selectors only
   (no native CSS nesting), so the shipped stylesheet stays widely compatible.
2. The mechanical utility families (spacing, sizing, borders, grid
   columns/breakpoints, semantic colours, ...) are data-driven: edit
   `style/design.toml` rather than hand-writing repetitive rules.
3. `python tools/generate_css.py` concatenates the hand-authored CSS with the
   generated utilities, minifies the result, and writes the single artifact
   `sphinx_design/static/sphinx-design.min.css` (the served filename is public
   API — do not rename it). The pre-commit `css` hook runs this and fails if the
   committed artifact is stale.
4. CSS is automatically copied to build output during Sphinx builds.

Runtime hover/focus shades use `color-mix()` with a static fallback, so a user
overriding a `--sd-color-*` custom property gets a matching hover shade. New CSS
should follow the [Baseline Widely Available](https://web.dev/baseline) support
policy; a *Baseline Newly Available* feature is acceptable only where it
degrades gracefully (document the exception).

## Key Files

- `pyproject.toml` - Project configuration, dependencies, and tool settings
- `sphinx_design/__init__.py` - Package entry point with `setup()` for Sphinx
- `sphinx_design/extension.py` - Main extension setup, CSS/JS handling
- `sphinx_design/shared.py` - Base classes and shared utilities
- `sphinx_design/grids.py` - Grid layout directives
- `sphinx_design/cards.py` - Card component directives
- `sphinx_design/tabs.py` - Tab component directives

## Debugging

- Build docs with `-v` flag for verbose output
- Check `docs/_build/html/<theme>/` for build outputs
- Use `tox -- -v --tb=long` for verbose test output with full tracebacks
- Inspect generated HTML to debug styling issues

## Common Patterns

### Adding a New Component

1. Create a new module in `sphinx_design/` (e.g., `my_component.py`)
2. Define directive class(es) extending `SdDirective`
3. Create a `setup_my_component(app: Sphinx)` function
4. Call the setup function from `setup_extension()` in `extension.py`
5. Add styles: hand-authored rules in `style/<my_component>.css`, or (for
   repetitive/data-driven families) tokens in `style/design.toml`
6. Wire the new file into the `ASSEMBLY` order in `tools/generate_css.py` and
   run it to regenerate the artifact
7. Document in `docs/`
8. Add tests in `tests/`

### Adding a New Directive Option

1. Add the option to the directive's `option_spec` dictionary
2. Handle the option in the directive's `run()` method
3. Add appropriate CSS classes or attributes to the output node
4. Document the new option
5. Add tests for the new option

### Working with CSS

1. Edit the sources in `style/` (`*.css` for hand-authored rules,
   `design.toml` for the generated utility families)
2. Run `python tools/generate_css.py` to rebuild (or `pre-commit run --all css`)
3. Compiled output goes to `sphinx_design/static/sphinx-design.min.css`
4. Test with different themes to ensure compatibility

## Reference Documentation

- [Docutils Repository](https://github.com/live-clones/docutils)
- [Docutils Documentation](https://docutils.sourceforge.io/)
- [Docutils Nodes](https://docutils.sourceforge.io/docs/ref/doctree.html)
- [Docutils release log](https://docutils.sourceforge.io/RELEASE-NOTES.html)
- [Sphinx Repository](https://github.com/sphinx-doc/sphinx)
- [Sphinx Extension Development](https://www.sphinx-doc.org/en/master/extdev/index.html)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.0/)
- [Baseline (web.dev)](https://web.dev/baseline)
