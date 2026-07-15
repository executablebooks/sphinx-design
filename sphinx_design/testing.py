"""Semi-public testing helpers for sphinx-design and downstream extensions.

These utilities are used by sphinx-design's own test suite and are exposed so
that downstream extensions (such as ``sphinx-design-elements``) can reuse them
in their own doctree regression tests, rather than re-implementing them.

Support policy
--------------

This is a *semi-public* testing API:

- The **signatures** of the public helpers are covered by the project's
  deprecation policy (they will not be removed or changed without a
  deprecation period).
- The **exact output** of :func:`normalize_doctree_xml` is **not** guaranteed
  to be stable across docutils versions. It exists purely to paper over
  docutils' changing serialization of boolean attributes for regression
  testing, and may change as docutils changes.

The module has zero runtime dependencies beyond docutils and the standard
library (in particular it does **not** import ``pytest``, and imports
``sphinx.testing`` only for type checking), so it can be imported with only
``sphinx_design`` installed -- no test extras required.
"""

from __future__ import annotations

from collections.abc import Sequence
from io import StringIO
from pathlib import Path
import re
from typing import TYPE_CHECKING, cast

from docutils import __version_info__ as _docutils_version_info
from docutils import nodes

if TYPE_CHECKING:
    from sphinx.testing.util import SphinxTestApp

__all__ = ("SphinxBuilder", "normalize_doctree_xml")

#: Whether the installed docutils serializes boolean attributes as ``"1"``/
#: ``"0"`` (docutils >= 0.22) rather than ``"True"``/``"False"``.
_DOCUTILS_0_22_PLUS = _docutils_version_info >= (0, 22)

#: Node attributes whose values are booleans, and therefore need normalizing
#: back to the ``"True"``/``"False"`` serialization for stable regression
#: fixtures. Downstream extensions with custom nodes can extend this via the
#: ``extra_attributes`` argument of :func:`normalize_doctree_xml`.
_BOOL_ATTRIBUTES: tuple[str, ...] = (
    "checked",
    "force",
    "has_title",
    "internal",
    "is_div",
    "linenos",
    "opened",
    "refexplicit",
    "refwarn",
    "selected",
    "translatable",
    "translated",
)


def normalize_doctree_xml(text: str, extra_attributes: Sequence[str] = ()) -> str:
    """Normalize docutils XML output for cross-version compatibility.

    In docutils 0.22+, boolean node attributes are serialized as ``"1"``/
    ``"0"`` instead of ``"True"``/``"False"``. This function normalizes the
    newer serialization back to the older one, so that a single set of
    regression fixtures works across docutils versions.

    On docutils < 0.22 the input is returned unchanged (no-op).

    Only known boolean attributes are rewritten (see :data:`_BOOL_ATTRIBUTES`),
    so non-boolean ``"1"``/``"0"`` values -- such as text content or numeric
    attributes -- are left untouched. Note the match is a textual heuristic:
    element *text content* that exactly mimics a known attribute assignment
    (e.g. a literal containing ``force="1"``) would also be rewritten.

    :param text: The pretty-printed doctree XML (e.g. from
        ``document.pformat()``).
    :param extra_attributes: Additional boolean attribute names to normalize,
        for downstream extensions that define custom nodes.
    :return: The normalized XML text.
    """
    if not _DOCUTILS_0_22_PLUS:
        return text
    # Normalize the new format (1/0) to the old format (True/False).
    # Only replace when it is clearly a boolean attribute value, i.e.
    # ``attribute="1"`` or ``attribute="0"`` for a known boolean attribute.
    attributes = (*_BOOL_ATTRIBUTES, *extra_attributes)
    pattern = "|".join(re.escape(attr) for attr in attributes)
    text = re.sub(rf' ({pattern})="1"', r' \1="True"', text)
    text = re.sub(rf' ({pattern})="0"', r' \1="False"', text)
    return text


class SphinxBuilder:
    """Wrapper around a :class:`~sphinx.testing.util.SphinxTestApp`.

    Provides convenience access to the source/output paths, build status and
    warnings, and a normalized doctree for regression testing.
    """

    def __init__(self, app: SphinxTestApp, src_path: Path):
        self.app = app
        self._src_path = src_path

    @property
    def src_path(self) -> Path:
        """The source directory of the Sphinx project."""
        return self._src_path

    @property
    def out_path(self) -> Path:
        """The output directory of the Sphinx project."""
        return Path(self.app.outdir)

    def build(self, assert_pass: bool = True) -> SphinxBuilder:
        """Build the project.

        :param assert_pass: If true, assert that the build emitted no warnings.
        :return: This builder, for chaining.
        """
        self.app.build()
        if assert_pass:
            assert self.warnings == "", self.status
        return self

    @property
    def status(self) -> str:
        """The build status messages."""
        # the public SphinxTestApp.status property only exists on sphinx>=7.3;
        # fall back to the private stream on the sphinx 7.2 floor
        stream: StringIO | None = getattr(self.app, "status", None)
        if stream is None:
            stream = cast("StringIO", self.app._status)
        return stream.getvalue()

    @property
    def warnings(self) -> str:
        """The build warning messages."""
        # see ``status`` regarding the sphinx 7.2 floor
        stream: StringIO | None = getattr(self.app, "warning", None)
        if stream is None:
            stream = cast("StringIO", self.app._warning)
        return stream.getvalue()

    def get_doctree(
        self, docname: str, post_transforms: bool = False
    ) -> nodes.document:
        """Get the doctree for a document, with source paths made relative.

        :param docname: The document name.
        :param post_transforms: If true, apply post-transforms to the doctree.
        :return: The (possibly transformed) doctree.
        """
        doctree = self.app.env.get_doctree(docname)
        if post_transforms:
            self.app.env.apply_post_transforms(doctree, docname)
        # make source path consistent for test comparisons
        for node in doctree.findall(include_self=True):
            if not (hasattr(node, "get") and node.get("source")):
                continue
            node["source"] = Path(node["source"]).relative_to(self.src_path).as_posix()
            if node["source"].endswith(".rst"):
                node["source"] = node["source"][:-4]
            elif node["source"].endswith(".md"):
                node["source"] = node["source"][:-3]
        # remove mathjax classes added by myst parser
        if doctree.children and isinstance(doctree.children[0], nodes.section):
            doctree.children[0]["classes"] = []
        return doctree
