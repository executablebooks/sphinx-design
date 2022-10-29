"""Helpers for cross compatibility across dependency versions."""
from importlib import resources
from typing import Callable, Iterable

from docutils.nodes import Element


def findall(node: Element) -> Callable[..., Iterable[Element]]:
    """Iterate through"""
    # findall replaces traverse in docutils v0.18
    # note a difference is that findall is an iterator
    return getattr(node, "findall", node.traverse)


def read_text(module: resources.Package, filename: str) -> str:
    has_files = hasattr(resources, "files")
    if has_files:
        return resources.files(module).joinpath(filename).read_text()
    return resources.read_text(module, filename)
