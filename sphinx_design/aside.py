"""A floated call-out box that the surrounding text flows around (see #97)."""

from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform

from .shared import (
    SdDirective,
    create_component,
    is_component,
    make_choice,
    margin_option,
)


def setup_aside(app: Sphinx) -> None:
    """Set up the aside component."""
    app.add_node(aside_main, html=(visit_aside_main, depart_aside_main))
    app.add_directive("aside", AsideDirective)
    app.add_post_transform(AsideHtmlTransform)


class aside_main(nodes.Element, nodes.General):  # noqa: N801
    """Outer node of an aside, rendered as a semantic ``<aside>`` in HTML."""


def visit_aside_main(self, node: nodes.Element) -> None:
    attributes = {}
    # titled asides are labelled by their title (see AsideHtmlTransform)
    labelledby = node.get("aria_labelledby")
    if labelledby:
        attributes["aria-labelledby"] = labelledby
    self.body.append(self.starttag(node, "aside", **attributes))


def depart_aside_main(self, node: nodes.Element) -> None:
    self.body.append("</aside>")


class AsideDirective(SdDirective):
    """A floated call-out box that the main text flows around.

    The directive produces a single container, holding an optional rubric title
    and a nested-parsed body::

        <container design_component="aside">
            <rubric>
                ...title nodes
            <container design_component="aside-body">
                ...content nodes

    This container renders as a ``<div>`` in every output, so non-HTML formats
    degrade to a plain titled block. For HTML, ``AsideHtmlTransform`` swaps the
    outer container for a semantic ``<aside>`` element.
    """

    optional_arguments = 1  # title of the aside
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "align": make_choice(["left", "right"]),
        "width": make_choice(["25%", "33%", "50%"]),
        "margin": margin_option,
        "name": directives.unchanged,
        "class": directives.class_option,
        "class-title": directives.class_option,
        "class-body": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        align = self.options.get("align", "right")
        # the width option keeps its ``%`` (e.g. ``33%``) for a friendly syntax,
        # but maps to a bare ``sd-aside-w-33`` class (styled in style/aside.css)
        width = self.options.get("width", "33%").rstrip("%")
        classes = [
            "sd-aside",
            f"sd-aside-{align}",
            f"sd-aside-w-{width}",
            *self.options.get("margin", ["sd-mb-3"]),
            *self.options.get("class", []),
        ]
        container = create_component("aside", classes)
        self.set_source_info(container)

        if self.arguments:
            textnodes, messages = self.state.inline_text(self.arguments[0], self.lineno)
            title_node = nodes.rubric(
                self.arguments[0],
                "",
                *textnodes,
                classes=["sd-aside-title", *self.options.get("class-title", [])],
            )
            container += title_node
            container += messages
            # where possible attach the target to the title node,
            # so that it can be used as the reference text
            self.add_name(title_node)
        else:
            self.add_name(container)

        body = create_component(
            "aside-body", ["sd-aside-body", *self.options.get("class-body", [])]
        )
        self.set_source_info(body)
        container += body
        self.state.nested_parse(self.content, self.content_offset, body)
        return [container]


class AsideHtmlTransform(SphinxPostTransform):
    """Swap the aside container for a semantic ``<aside>`` element (HTML only).

    The container built by :class:`AsideDirective` renders as a ``<div>`` in
    every writer; for HTML we replace it with an :class:`aside_main` node so the
    call-out is emitted as a semantic ``<aside>``. The children (title rubric and
    body) and any ``ids`` are carried across unchanged.

    For a titled aside the ``<aside>`` is given ``aria-labelledby`` pointing at
    its title, so assistive technology announces the region by its heading. The
    title is given a stable, deterministic id (``sd-aside-title-<n>``, numbered
    in document order like the tab ids) when it does not already carry one from
    ``:name:``. Untitled asides are left unlabelled (no invented label text).
    """

    default_priority = 199
    formats = ("html",)

    def run(self, **kwargs: Any) -> None:
        """Run the transform."""
        document: nodes.document = self.document
        for count, node in enumerate(
            list(document.findall(lambda n: is_component(n, "aside")))
        ):
            newnode = aside_main(classes=node["classes"])
            newnode["ids"] += node["ids"]
            # wire aria-labelledby to the title (titled asides only)
            title = next(
                (c for c in node.children if isinstance(c, nodes.rubric)), None
            )
            if title is not None:
                if not title["ids"]:
                    title["ids"].append(f"sd-aside-title-{count}")
                newnode["aria_labelledby"] = title["ids"][0]
            newnode += node.children
            node.replace_self(newnode)
