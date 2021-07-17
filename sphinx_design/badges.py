from typing import List, Optional, Tuple

from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.util.docutils import ReferenceRole, SphinxRole

from sphinx_design.shared import SEMANTIC_COLORS

ROLE_NAME_BADGE_PREFIX = "bdg"
ROLE_NAME_LINK_PREFIX = "bdg-link"
ROLE_NAME_REF_PREFIX = "bdg-ref"

# TODO defining arbitrary classes (split text right of last `;`, then split that by comma)


def setup_badges(app: Sphinx):
    """Setup the badge components."""
    app.add_role(ROLE_NAME_BADGE_PREFIX, BadgeRole())
    app.add_role(ROLE_NAME_LINK_PREFIX, LinkBadgeRole())
    app.add_role(ROLE_NAME_REF_PREFIX, XRefBadgeRole())
    for color in SEMANTIC_COLORS:
        app.add_role("-".join((ROLE_NAME_BADGE_PREFIX, color)), BadgeRole(color))
        app.add_role(
            "-".join((ROLE_NAME_BADGE_PREFIX, color, "line")),
            BadgeRole(color, outline=True),
        )
        app.add_role("-".join((ROLE_NAME_LINK_PREFIX, color)), LinkBadgeRole(color))
        app.add_role(
            "-".join((ROLE_NAME_LINK_PREFIX, color, "line")),
            LinkBadgeRole(color, outline=True),
        )
        app.add_role("-".join((ROLE_NAME_REF_PREFIX, color)), XRefBadgeRole(color))
        app.add_role(
            "-".join((ROLE_NAME_REF_PREFIX, color, "line")),
            XRefBadgeRole(color, outline=True),
        )


def create_classes(color: Optional[str], outline: bool) -> List[str]:
    """Create the badge classes."""
    classes = [
        "sd-sphinx-override",
        "sd-badge",
    ]
    if color is None:
        return classes
    if outline:
        classes.extend([f"sd-outline-{color}", f"sd-text-{color}"])
    else:
        classes.extend([f"sd-bg-{color}", f"sd-bg-text-{color}"])
    return classes


class BadgeRole(SphinxRole):
    """Role to display a badge."""

    def __init__(self, color: Optional[str] = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        node = nodes.inline(
            self.rawtext, self.text, classes=create_classes(self.color, self.outline)
        )
        self.set_source_info(node)
        return [node], []


class LinkBadgeRole(ReferenceRole):
    """Role to display a badge with an external link."""

    def __init__(self, color: Optional[str] = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        node = nodes.reference(
            self.rawtext,
            refuri=self.target,
            classes=create_classes(self.color, self.outline),
        )
        self.set_source_info(node)
        # if self.target != self.title:
        #     node["reftitle"] = self.target
        node += nodes.inline(self.title, self.title)
        return [node], []


class XRefBadgeRole(ReferenceRole):
    """Role to display a badge with an internal link."""

    def __init__(self, color: Optional[str] = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        options = {
            "classes": create_classes(self.color, self.outline),
            "reftarget": self.target,
            "refdoc": self.env.docname,
            "refdomain": "",
            "reftype": "any",
            "refexplicit": self.has_explicit_title,
            "refwarn": True,
        }
        node = addnodes.pending_xref(self.rawtext, **options)
        self.set_source_info(node)
        node += nodes.inline(self.title, self.title, classes=["xref", "any"])
        return [node], []
