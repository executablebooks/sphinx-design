"""The ``accordion`` directive: a group of mutually-exclusive dropdowns.

An accordion is a thin wrapper around a set of :mod:`~sphinx_design.dropdown`
directives. It assigns every *direct* child dropdown a shared, document-unique
``name``, which the HTML writer stamps onto the underlying ``<details>``
elements. Browsers that support the native ``name`` attribute on ``<details>``
then make the group mutually exclusive: opening one item automatically closes
the others -- with **no JavaScript**.

This degrades gracefully: engines that predate ``<details name>`` simply ignore
the attribute and render each item as an independent, individually collapsible
dropdown (see ``docs/accordions.md`` for the browser-support note).
"""

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.logging import getLogger

from .shared import (
    WARNING_TYPE,
    SdDirective,
    create_component,
    is_component,
    is_ignorable_child,
)

LOGGER = getLogger(__name__)


def setup_accordion(app: Sphinx) -> None:
    app.add_directive("accordion", AccordionDirective)


class AccordionDirective(SdDirective):
    """A container of ``dropdown`` items behaving as one exclusive group.

    Opening one item collapses the others, via a shared native
    ``<details name="...">`` attribute (no JavaScript). The directive:

    - parses its content, which should be a sequence of ``dropdown`` directives;
    - warns (subtype ``design.accordion``) about any non-dropdown child, while
      silently keeping structurally inert nodes (comments, targets, ...);
    - stamps every direct child dropdown with a shared ``details_name``, so the
      HTML transform can emit the grouping ``name`` attribute; and
    - enforces at most one initially-``open`` item (warning and keeping the
      first, since an exclusive group can only have one member open at a time).

    Nested dropdowns (inside an item's *body*) are deliberately left untouched:
    only *direct* children join the group.
    """

    has_content = True
    option_spec = {
        "flush": directives.flag,  # edge-to-edge styling (no outer borders)
        "class": directives.class_option,
    }

    def _group_name(self) -> str:
        """Build a document-unique, build-stable group name.

        The name is derived from the current docname (kept unique even in
        single-page/concatenated builds, where accordions from different
        source documents share one HTML page) plus a per-document serial
        counter. It is fully deterministic -- no randomness -- so rebuilds of
        unchanged content produce byte-identical output.
        """
        slug = nodes.make_id(self.env.docname) or "doc"
        serial = self.env.new_serialno("sd-accordion")
        return f"sd-accordion-{slug}-{serial}"

    def run_with_defaults(self) -> list[nodes.Node]:
        self.assert_has_content()

        classes = ["sd-accordion"]
        if "flush" in self.options:
            classes.append("sd-accordion-flush")
        classes.extend(self.options.get("class", []))

        accordion = create_component("accordion", classes=classes)
        self.set_source_info(accordion)
        self.state.nested_parse(self.content, self.content_offset, accordion)

        group_name = self._group_name()
        valid_children: list[nodes.Node] = []
        has_open = False
        for child in accordion.children:
            if is_ignorable_child(child):
                # comments and system messages can be dropped, but hyperlink
                # targets must be kept so references to them still resolve
                if isinstance(child, nodes.target):
                    valid_children.append(child)
                continue
            if not is_component(child, "dropdown"):
                LOGGER.warning(
                    f"All children of an 'accordion' "
                    f"should be 'dropdown' [{WARNING_TYPE}.accordion]",
                    location=child,
                    type=WARNING_TYPE,
                    subtype="accordion",
                )
                continue  # skip invalid children rather than breaking
            # only *direct* child dropdowns join the group; nested dropdowns
            # keep their own independent open/close behaviour
            child["details_name"] = group_name
            if child.get("opened"):
                if has_open:
                    # an exclusive group can only have one member open at a time
                    LOGGER.warning(
                        f"Multiple open 'dropdown' items in an 'accordion'; "
                        f"keeping only the first open [{WARNING_TYPE}.accordion]",
                        location=child,
                        type=WARNING_TYPE,
                        subtype="accordion",
                    )
                    child["opened"] = False
                else:
                    has_open = True
            valid_children.append(child)

        accordion.children = valid_children
        return [accordion]
