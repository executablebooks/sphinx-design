"""Configuration file for the Sphinx documentation builder."""
import os

project = "Sphinx Design"
copyright = "2021, Executable Book Project"
author = "Executable Book Project"

extensions = ["myst_parser", "sphinx_design"]

html_theme = os.environ.get("SPHINX_THEME", "alabaster")
html_title = f"Sphinx Design ({html_theme})"

exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
myst_enable_extensions = ["colon_fence", "substitution"]

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
