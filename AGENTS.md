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
package.json            # Node.js config for SASS compilation

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

style/                  # SASS source files
├── index.scss          # Main SCSS entry point
├── _variables.scss     # SCSS variables
├── _grids.scss         # Grid styles
├── _cards.scss         # Card styles
├── _tabs.scss          # Tab styles
├── _dropdown.scss      # Dropdown styles
└── ...                 # Other component styles

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

# Compile SASS to CSS
npm run css
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

Compiled CSS and JS are stored in `sphinx_design/compiled/`:

- CSS is compiled from SASS sources in `style/`
- JavaScript for tab functionality

### Styling

The extension uses SASS for styling:

1. SASS source files are in `style/`
2. Compiled using `npm run css` (requires Node.js)
3. Output goes to `sphinx_design/compiled/style.min.css`
4. CSS is automatically copied to build output during Sphinx builds

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
5. Add SASS styles in `style/_my_component.scss`
6. Import the SASS file in `style/index.scss`
7. Document in `docs/`
8. Add tests in `tests/`

### Adding a New Directive Option

1. Add the option to the directive's `option_spec` dictionary
2. Handle the option in the directive's `run()` method
3. Add appropriate CSS classes or attributes to the output node
4. Document the new option
5. Add tests for the new option

### Working with SASS

1. Edit SASS files in `style/`
2. Run `npm run css` to compile (or `pre-commit run --all css`)
3. Compiled output goes to `sphinx_design/compiled/style.min.css`
4. Test with different themes to ensure compatibility

## Reference Documentation

- [Docutils Repository](https://github.com/live-clones/docutils)
- [Docutils Documentation](https://docutils.sourceforge.io/)
- [Docutils Nodes](https://docutils.sourceforge.io/docs/ref/doctree.html)
- [Docutils release log](https://docutils.sourceforge.io/RELEASE-NOTES.html)
- [Sphinx Repository](https://github.com/sphinx-doc/sphinx)
- [Sphinx Extension Development](https://www.sphinx-doc.org/en/master/extdev/index.html)
- [Bootstrap Documentation](https://getbootstrap.com/docs/5.0/)
- [SASS Documentation](https://sass-lang.com/documentation)
