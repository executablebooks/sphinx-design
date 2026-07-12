from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import ws_re
from sphinx.util.docutils import ReferenceRole, SphinxRole

from sphinx_design.shared import SEMANTIC_COLORS, SdDirective, make_choice, text_align

ROLE_NAME_BADGE_PREFIX = "bdg"
ROLE_NAME_LINK_PREFIX = "bdg-link"
ROLE_NAME_REF_PREFIX = "bdg-ref"
DIRECTIVE_NAME_BUTTON_LINK = "button-link"
DIRECTIVE_NAME_BUTTON_REF = "button-ref"

# TODO defining arbitrary classes for badges
# (maybe split text right of last `;`, then split that by comma)
# in particular for rounded-pill class etc


def setup_badges_and_buttons(app: Sphinx) -> None:
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

    app.add_directive(DIRECTIVE_NAME_BUTTON_LINK, ButtonLinkDirective)
    app.add_directive(DIRECTIVE_NAME_BUTTON_REF, ButtonRefDirective)
    app.add_post_transform(ButtonRefContentStash)
    app.add_post_transform(ButtonRefContentGraft)


def create_bdg_classes(color: str | None, outline: bool) -> list[str]:
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

    def __init__(self, color: str | None = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        node = nodes.inline(
            self.rawtext,
            self.text,
            classes=create_bdg_classes(self.color, self.outline),
        )
        self.set_source_info(node)
        return [node], []


class LinkBadgeRole(ReferenceRole):
    """Role to display a badge with an external link."""

    def __init__(self, color: str | None = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        node = nodes.reference(
            self.rawtext,
            refuri=self.target,
            classes=create_bdg_classes(self.color, self.outline),
        )
        # TODO open in new tab
        self.set_source_info(node)
        # if self.target != self.title:
        #     node["reftitle"] = self.target
        node += nodes.inline(self.title, self.title)
        return [node], []


class XRefBadgeRole(ReferenceRole):
    """Role to display a badge with an internal link."""

    def __init__(self, color: str | None = None, *, outline: bool = False) -> None:
        super().__init__()
        self.color = color
        self.outline = outline

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        options = {
            "classes": create_bdg_classes(self.color, self.outline),
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


class _ButtonDirective(SdDirective):
    """A base button directive."""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "color": make_choice(SEMANTIC_COLORS),
        "outline": directives.flag,
        "align": text_align,
        # expand to fit parent width
        "expand": directives.flag,
        # make parent also clickable
        "click-parent": directives.flag,
        "tooltip": directives.unchanged_required,
        "shadow": directives.flag,
        # ref button only
        "ref-type": make_choice(["any", "ref", "doc", "myst"]),
        "class": directives.class_option,
    }

    @staticmethod
    def get_target(argument: str) -> str:
        """Normalise the directive argument into a reference target."""
        raise NotImplementedError

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        raise NotImplementedError

    def run_with_defaults(self) -> list[nodes.Node]:
        rawtext = self.arguments[0]
        target = self.get_target(rawtext)
        classes = ["sd-sphinx-override", "sd-btn", "sd-text-wrap"]
        if "color" in self.options:
            if "outline" in self.options:
                classes.append(f"sd-btn-outline-{self.options['color']}")
            else:
                classes.append(f"sd-btn-{self.options['color']}")
        if "click-parent" in self.options:
            classes.append("sd-stretched-link")
        if "shadow" in self.options:
            classes.append("sd-shadow-sm")
        if "class" in self.options:
            classes.extend(self.options["class"])
        node = self.create_ref_node(rawtext, target, bool(self.content), classes)
        # TODO open in new tab
        self.set_source_info(node)
        if "tooltip" in self.options:
            node["reftitle"] = self.options["tooltip"]  # TODO escape HTML

        if self.content:
            textnodes, _ = self.state.inline_text(
                "\n".join(self.content), self.lineno + self.content_offset
            )
            # make link text translatable -
            # target gettext to the content lines, not the outer directive
            translatable = nodes.inline("", "", *textnodes, translatable=True)
            self.set_source_info(translatable)
            translatable.line += self.content_offset
            # the translatable inline is a placeholder that sphinx unwraps
            # after translation (RemoveTranslatableInline); keep a plain outer
            # inline so the reference always retains an element child
            # (an unresolved xref otherwise crashes on replacement)
            content = nodes.inline("", "", translatable)
        else:
            content = nodes.inline(target, target)
        node.append(content)

        if "expand" in self.options:
            grid_container = nodes.inline(classes=["sd-d-grid"])
            self.set_source_info(grid_container)
            grid_container += node
            node = grid_container

        # `visit_reference` requires that a reference be inside a `TextElement` parent
        container = nodes.paragraph(
            classes=self.options.get("align", []), translatable=False
        )
        self.set_source_info(container)
        container += node

        return [container]


class ButtonLinkDirective(_ButtonDirective):
    """A button directive with an external link."""

    @staticmethod
    def get_target(argument: str) -> str:
        """Return the URI, with all whitespace removed (as for a normal link)."""
        return directives.uri(argument)

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        return nodes.reference(
            rawtext,
            refuri=target,
            classes=classes,
        )


class ButtonRefDirective(_ButtonDirective):
    """A button directive with an internal link."""

    @staticmethod
    def get_target(argument: str) -> str:
        """Return the reference target, collapsing internal whitespace.

        This mirrors :class:`~sphinx.roles.XRefRole`'s whitespace
        normalisation, so that multi-word labels (e.g. those generated by
        ``sphinx.ext.autosectionlabel`` from section titles) are preserved and
        resolve correctly, rather than being stripped of all whitespace.
        """
        return ws_re.sub(" ", argument).strip()

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        ref_type = self.options.get("ref-type", "any")
        if ref_type == "ref":
            # match sphinx's :ref: role, which is ``XRefRole(lowercase=True)``:
            # std-domain labels are stored lowercased, so lowercase the target
            # too. ``doc``/``myst`` targets are case-sensitive, and the ``any``
            # resolver lowercases internally where needed
            target = target.lower()
        options = {
            "classes": classes,
            "reftarget": target,
            "refdoc": self.env.docname,
            "refdomain": "std" if ref_type in {"ref", "doc"} else "",
            "reftype": ref_type,
            "refexplicit": explicit_title,
            "refwarn": True,
        }
        return addnodes.pending_xref(rawtext, **options)


_BUTTON_REF_STASH_ATTR = "sd_button_ref_content"
"""Name of the (transient) python attribute on the ``document`` object,
mapping marker class names to stashed ``button-ref`` content nodes."""

_BUTTON_REF_MARKER_PREFIX = "sd-button-ref-content-"
"""Prefix of the transient marker classes used to correlate a ``button-ref``
``pending_xref`` with its resolved node; never present in final output."""


class ButtonRefContentStash(SphinxPostTransform):
    """Stash the rich content of each ``button-ref`` cross-reference.

    Sphinx's standard-domain resolvers rebuild an explicit-title ``ref``/``doc``
    cross-reference from ``node.astext()``, which flattens any nested inline
    markup (emphasis, icons, ...) down to plain text (see issue #228). Since
    ``button-ref`` allows arbitrary parsed content, we stash a copy of that
    content before any resolver runs, tagging the ``pending_xref`` with a
    unique marker class. Whatever node the xref is replaced with inherits the
    marker (docutils ``replace_self`` copies ids/classes onto the
    replacement), letting :class:`ButtonRefContentGraft` restore the content
    afterwards, without relying on any non-public resolver API.
    """

    # must run before every cross-reference resolver: the built-in
    # ``ReferencesResolver`` runs at priority 10, and myst-parser's resolver
    # (which handles ``ref-type: myst`` buttons) at priority 9
    default_priority = 8

    def run(self, **kwargs: Any) -> None:
        """Tag and stash every ``button-ref`` pending cross-reference."""
        stash: dict[str, nodes.Element] = {}
        for index, node in enumerate(self.document.findall(addnodes.pending_xref)):
            if "sd-btn" not in node.get("classes", ()):
                continue
            if not node.get("refexplicit"):
                # the directive had no content: the resolver-generated text
                # (e.g. the target's section title) is the desired button text
                continue
            if next(iter(node[0].findall(addnodes.pending_xref)), None) is not None:
                # the button content itself contains a cross-reference: a
                # stashed copy would re-insert an unresolved ``pending_xref``
                # after every resolver has run, crashing the writer. Fall back
                # to the pre-existing behaviour (the std domain flattens the
                # content to plain text) - a link nested inside a button link
                # would be invalid HTML anyway
                continue
            marker = f"{_BUTTON_REF_MARKER_PREFIX}{index}"
            node["classes"].append(marker)
            stash[marker] = node[0].deepcopy()
        # a plain (transient) python attribute: unlike a node attribute it can
        # never leak into pickled doctrees or (XML) serialisations
        setattr(self.document, _BUTTON_REF_STASH_ATTR, stash)


class ButtonRefContentGraft(SphinxPostTransform):
    """Restore stashed ``button-ref`` content onto resolved references.

    Counterpart to :class:`ButtonRefContentStash`: locate the node that
    inherited each marker class from its ``pending_xref``, strip the marker,
    and, for resolved references, replace the (possibly text-flattened)
    resolver-built content with the stashed rich content, so that
    ``button-ref`` renders its content identically to ``button-link``.
    """

    # run just after the built-in ``ReferencesResolver`` (priority 10)
    default_priority = 11

    def run(self, **kwargs: Any) -> None:
        """Graft stashed content onto each marked node."""
        stash: dict[str, nodes.Element] = getattr(
            self.document, _BUTTON_REF_STASH_ATTR, {}
        )
        if not stash:
            return
        for element in list(self.document.findall(nodes.Element)):
            classes = element.get("classes", [])
            for marker in [cls for cls in classes if cls in stash]:
                classes.remove(marker)
                if isinstance(element, nodes.reference):
                    # a resolver replaced the xref with a reference, possibly
                    # rebuilding its content from plain text (the std domain
                    # does, for explicit-title ref/doc targets): restore the
                    # stashed rich content (a no-op in effect for resolvers
                    # that already preserved the original content node)
                    element.children = []
                    element.append(stash[marker].deepcopy())
                # otherwise the xref was unresolved, and the built-in resolver
                # substituted the original (still rich) content node itself,
                # which inherited the marker: stripping the marker is enough.
                # If an (external) resolver produced a node that did not
                # inherit the marker at all, nothing is found here and the
                # graft is a no-op: such resolvers build on the passed
                # contnode, which was never flattened by the std domain.
        setattr(self.document, _BUTTON_REF_STASH_ATTR, {})
