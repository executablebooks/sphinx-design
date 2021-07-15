"""A sphinx extension for implementing Material Design system web components,
for building beautiful, responsive, mobile-friendly sites.
"""
from typing import TYPE_CHECKING

__version__ = "0.0.1"

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def setup(app: "Sphinx") -> dict:
    from .extension import setup_extension

    setup_extension(app)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
