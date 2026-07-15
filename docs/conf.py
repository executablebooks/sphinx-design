"""Configuration file for the Sphinx documentation builder."""

import dataclasses as dc
import os

from sphinx_design.config import SdConfig

project = "Sphinx Design"
copyright = "2021, Executable Book Project"
author = "Executable Book Project"

extensions = [
    "myst_parser",
    "sphinx_design",
    "sphinx.ext.extlinks",
    # SVG images must be converted for the LaTeX/PDF build
    "sphinx.ext.imgconverter",
]

# suppresses the warning for builders with no fontawesome support (e.g. man)
suppress_warnings = ["design.fa-build"]
sd_fontawesome_latex = "fontawesome5"
# pdflatex errors on emoji (e.g. in the changelog); xelatex only warns for
# missing glyphs. makeindex replaces xindy, which CI TeX images lack.
latex_engine = "xelatex"
latex_use_xindy = False
sd_custom_directives = {
    "dropdown-syntax": {
        "inherit": "dropdown",
        "argument": "Syntax",
        "options": {
            "color": "primary",
            "icon": "code",
        },
    }
}

extlinks = {
    "pr": ("https://github.com/executablebooks/sphinx-design/pull/%s", "PR #%s"),
    "issue": (
        "https://github.com/executablebooks/sphinx-design/issues/%s",
        "#%s",
    ),
    "user": ("https://github.com/%s", "@%s"),
}

html_theme = os.environ.get("SPHINX_THEME", "alabaster")
html_title = f"Sphinx Design ({html_theme.replace('_', '-')})"

html_static_path = ["_static"]
html_logo = "_static/logo_wide.svg"
html_favicon = "_static/logo_square.svg"

if html_theme not in ("sphinx_book_theme", "pydata_sphinx_theme"):
    # let sphinx-design load FontAwesome from the CDN, rather than
    # hand-editing html_css_files (the sphinx_book/pydata themes bundle it)
    sd_fontawesome_source = "cdn"
if html_theme == "alabaster":
    html_logo = ""
    html_theme_options = {
        "logo": "logo_wide.svg",
        "logo_name": False,
        "description": "(alabaster theme)",
        "github_button": False,
        "github_type": "star",
        "github_banner": False,
        "github_user": "executablebooks",
        "github_repo": "sphinx-design",
    }
if html_theme == "sphinx_book_theme":
    html_theme_options = {
        "repository_url": "https://github.com/executablebooks/sphinx-design",
        "use_repository_button": True,
        "use_edit_page_button": True,
        "use_issues_button": True,
        "repository_branch": "main",
        "path_to_docs": "docs",
        "home_page_in_toc": False,
    }
if html_theme == "furo":
    # FontAwesome is loaded via sd_fontawesome_source="cdn" (set above)
    html_css_files = ["furo.css"]
    html_theme_options = {
        "sidebar_hide_name": True,
    }
if html_theme == "sphinx_rtd_theme":
    html_theme_options = {
        "logo_only": True,
    }
if html_theme == "sphinx_immaterial":
    extensions.append("sphinx_immaterial")
    html_css_files = ["sphinx_immaterial.css"]
    sd_fontawesome_source = "none"  # immaterial provides its own icon fonts
    html_theme_options = {
        "icon": {
            "repo": "fontawesome/brands/github",
        },
        "site_url": "https://sphinx-design.readthedocs.io/",
        "repo_url": "https://github.com/executablebooks/sphinx-design",
        "repo_name": "Sphinx-Design",
        "palette": [
            {
                "media": "(prefers-color-scheme: light)",
                "scheme": "default",
                "primary": "blue",
                "accent": "light-blue",
                "toggle": {
                    "icon": "material/weather-night",
                    "name": "Switch to dark mode",
                },
            },
            {
                "media": "(prefers-color-scheme: dark)",
                "scheme": "slate",
                "primary": "blue",
                "accent": "yellow",
                "toggle": {
                    "icon": "material/weather-sunny",
                    "name": "Switch to light mode",
                },
            },
        ],
    }

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
myst_enable_extensions = [
    "attrs_inline",
    "colon_fence",
    "deflist",
    "substitution",
    "html_image",
]


def _sd_config_options_table() -> str:
    """Generate a Markdown table of all sphinx-design configuration options,
    from the ``SdConfig`` dataclass fields.
    """
    rows = [
        "| Name | Type | Default | Description |",
        "| ---- | ---- | ------- | ----------- |",
    ]
    for field in dc.fields(SdConfig):
        default = (
            field.default_factory()
            if field.default_factory is not dc.MISSING
            else field.default
        )
        type_str = field.metadata.get("doc_type", field.type)
        rows.append(
            f"| `sd_{field.name}` | `{type_str}` | `{default!r}` "
            f"| {field.metadata.get('help', '')} |"
        )
    return "\n".join(rows)


myst_substitutions = {
    "sd_config_options": _sd_config_options_table(),
    "loremipsum": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
    "Sed iaculis arcu vitae odio gravida congue. Donec porttitor ac risus et condimentum. "
    "Phasellus bibendum ac risus a sollicitudin. "
    "Proin pulvinar risus ac mauris aliquet fermentum et varius nisi. "
    "Etiam sit amet metus ac ipsum placerat congue semper non diam. "
    "Nunc luctus tincidunt ipsum id eleifend. Ut sed faucibus ipsum. "
    "Aliquam maximus dictum posuere. Nunc vitae libero nec enim tempus euismod. "
    "Aliquam sed lectus ac nisl sollicitudin ultricies id at neque. "
    "Aliquam fringilla odio vitae lorem ornare, sit amet scelerisque orci fringilla. "
    "Nam sed arcu dignissim, ultrices quam sit amet, commodo ipsum. "
    "Etiam quis nunc at ligula tincidunt eleifend.",
}
