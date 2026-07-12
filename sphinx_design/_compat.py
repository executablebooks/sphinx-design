"""Helpers for cross compatibility across dependency versions."""

from importlib import resources


def read_text(module: resources.Package, filename: str) -> str:
    return resources.files(module).joinpath(filename).read_text()
