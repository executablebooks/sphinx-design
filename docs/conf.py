"""Configuration file for the Sphinx documentation builder."""

import os

project = "Sphinx Design"
copyright = "2021, Executable Book Project"
author = "Executable Book Project"

extensions = ["myst_parser", "sphinx_design", "sphinx.ext.extlinks"]

suppress_warnings = ["design.fa-build"]
sd_fontawesome_latex = True
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
    "user": ("https://github.com/%s", "@%s"),
}

html_theme = os.environ.get("SPHINX_THEME", "pydata_sphinx_theme")
html_title = f"Sphinx Design ({html_theme.replace('_', '-')})"

html_static_path = ["_static"]
html_logo = "_static/logo_wide.svg"
html_favicon = "_static/logo_square.svg"

if html_theme not in ("sphinx_book_theme", "pydata_sphinx_theme"):
    html_css_files = [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css"
    ]
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
    html_css_files = [
        "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/fontawesome.min.css",
        "furo.css",
    ]
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

myst_substitutions = {
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
    "Etiam quis nunc at ligula tincidunt eleifend."
}
