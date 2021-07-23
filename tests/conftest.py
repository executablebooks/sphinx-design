import os
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
from docutils import nodes
from sphinx.testing.path import path as sphinx_path
from sphinx.testing.util import SphinxTestApp

pytest_plugins = "sphinx.testing.fixtures"


class SphinxBuilder:
    def __init__(self, app: SphinxTestApp, src_path: Path):
        self.app = app
        self._src_path = src_path

    @property
    def src_path(self) -> Path:
        return self._src_path

    @property
    def out_path(self) -> Path:
        return Path(self.app.outdir)

    def build(self, assert_pass=True):
        self.app.build()
        if assert_pass:
            assert self.warnings == "", self.status
        return self

    @property
    def status(self):
        return self.app._status.getvalue()

    @property
    def warnings(self):
        return self.app._warning.getvalue()

    def get_doctree(
        self, docname: str, post_transforms: bool = False
    ) -> nodes.document:
        doctree = self.app.env.get_doctree(docname)
        if post_transforms:
            self.app.env.apply_post_transforms(doctree, docname)
        # make source path consistent for test comparisons
        doctree["source"] = (
            Path(doctree["source"]).relative_to(self.src_path).as_posix()
        )
        if doctree["source"].endswith(".rst"):
            doctree["source"] = doctree["source"][:-4]
        elif doctree["source"].endswith(".md"):
            doctree["source"] = doctree["source"][:-3]
        # remove mathjax classes added by myst parser
        if doctree.children and isinstance(doctree.children[0], nodes.section):
            doctree.children[0]["classes"] = []
        return doctree


@pytest.fixture()
def sphinx_builder(tmp_path: Path, make_app):
    def _create_project(
        buildername: str = "html", conf_kwargs: Optional[Dict[str, Any]] = None
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
            srcdir=sphinx_path(os.path.abspath(str(src_path))), buildername=buildername
        )
        return SphinxBuilder(app, src_path)

    yield _create_project
