from collections.abc import Callable
import os
from pathlib import Path
from typing import Any

import pytest

from sphinx_design.testing import SphinxBuilder
from sphinx_design.testing import normalize_doctree_xml as _normalize_doctree_xml

# re-exported for tests that do ``from .conftest import SphinxBuilder``
__all__ = ["SphinxBuilder"]

pytest_plugins = "sphinx.testing.fixtures"


@pytest.fixture(params=[pytest.param("html", id="html")])
def sphinx_builder(
    tmp_path: Path, make_app, monkeypatch, request: pytest.FixtureRequest
):
    def _create_project(
        buildername: str = request.param, conf_kwargs: dict[str, Any] | None = None
    ):
        src_path = tmp_path / "srcdir"
        src_path.mkdir()
        conf_kwargs = conf_kwargs or {
            "extensions": ["myst_parser", "sphinx_design"],
            "myst_enable_extensions": ["colon_fence"],
        }
        content = "\n".join(
            [f"{key} = {value!r}" for key, value in conf_kwargs.items()]
        )
        src_path.joinpath("conf.py").write_text(content, encoding="utf8")
        app = make_app(
            srcdir=Path(os.path.abspath(str(src_path))),  # noqa: PTH100
            buildername=buildername,
        )
        return SphinxBuilder(app, src_path)

    yield _create_project


@pytest.fixture
def normalize_doctree_xml() -> Callable[..., str]:
    """Return the public doctree-XML normalizer.

    Thin wrapper around :func:`sphinx_design.testing.normalize_doctree_xml`,
    kept so existing tests keep working; see that module for details.
    """
    return _normalize_doctree_xml
