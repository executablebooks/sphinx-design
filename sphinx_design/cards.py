import re
from typing import List, NamedTuple, Optional, Tuple

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective

from .shared import create_component, make_option, text_align

DIRECTIVE_NAME_CARD = "card"
REGEX_HEADER = re.compile(r"^\^{3,}\s*$")
REGEX_FOOTER = re.compile(r"^\+{3,}\s*$")


def setup_cards(app: Sphinx):
    """Setup the card components."""
    app.add_directive(DIRECTIVE_NAME_CARD, CardDirective)


class CardContent(NamedTuple):
    """Split card into header (optional), body, footer (optional).

    (offset, content)
    """

    body: Tuple[int, StringList]
    header: Optional[Tuple[int, StringList]] = None
    footer: Optional[Tuple[int, StringList]] = None


class CardDirective(SphinxDirective):
    """A card component."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1  # card title
    final_argument_whitespace = True
    option_spec = {
        # TODO adaptive width/ width based on content
        "width": make_option(["auto", "25", "50", "75", "100"]),
        "align": make_option(["left", "center", "right"]),
        "text-align": text_align,
        "img-top": directives.uri,
        "img-bottom": directives.uri,
        "no-shadow": directives.flag,
        "class-card": directives.class_option,
        "class-header": directives.class_option,
        "class-body": directives.class_option,
        "class-title": directives.class_option,
        "class-footer": directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        self.assert_has_content()
        return [self.create_card(self, self.arguments, self.options)]

    @classmethod
    def create_card(
        cls, inst: SphinxDirective, arguments: Optional[list], options: dict
    ) -> nodes.Node:
        """Run the directive."""
        card_classes = ["sd-card", "sd-sphinx-override"]
        if "width" in options:
            card_classes += [f'sd-w-{options["width"]}']
        if "align" in options:
            align_class = {
                "center": "sd-mx-auto",
                "left": "sd-mr-auto",
                "right": "sd-ml-auto",
            }[options["align"]]
            card_classes += [align_class]
        if "no-shadow" in options:
            card_classes += ["sd-shadow"]
        card = create_component(
            "card",
            card_classes
            + options.get("text-align", [])
            + options.get("class-card", []),
        )
        inst.set_source_info(card)

        if "img-top" in options:
            image_top = nodes.image(
                "",
                uri=options["img-top"],
                alt="card-img-top",
                classes=["sd-card-img-top"],
            )
            card.append(image_top)

        components = cls.split_content(inst.content, inst.content_offset)

        if components.header:
            card.append(
                cls._create_component(
                    inst, "header", options, components.header[0], components.header[1]
                )
            )

        body = cls._create_component(
            inst, "body", options, components.body[0], components.body[1]
        )
        if arguments:
            title = create_component(
                "card-title",
                ["sd-card-title", "sd-font-weight-bold"]
                + options.get("class-title", []),
            )
            textnodes, _ = inst.state.inline_text(arguments[0], inst.lineno)
            title.extend(textnodes)
            body.insert(0, title)
        card.append(body)

        if components.footer:
            card.append(
                cls._create_component(
                    inst, "footer", options, components.footer[0], components.footer[1]
                )
            )

        if "img-bottom" in options:
            image_bottom = nodes.image(
                "",
                uri=options["img-bottom"],
                alt="card-img-bottom",
                classes=["sd-card-img-bottom"],
            )
            card.append(image_bottom)

        return card

    @staticmethod
    def split_content(content: StringList, offset: int) -> CardContent:
        """Split the content into header, body and footer."""
        header_index, footer_index, header, footer = None, None, None, None
        body_offset = offset
        for index, line in enumerate(content):
            # match the first occurrence of a header regex
            if (header_index is None) and REGEX_HEADER.match(line):
                header_index = index
            # match the final occurrence of a footer regex
            if REGEX_FOOTER.match(line):
                footer_index = index
        if header_index is not None:
            header = (offset, content[:header_index])
            body_offset += header_index + 1
        if footer_index is not None:
            footer = (offset + footer_index + 1, content[footer_index + 1 :])
        body = (
            body_offset,
            content[
                (header_index + 1 if header_index is not None else None) : footer_index
            ],
        )
        return CardContent(body, header, footer)

    @classmethod
    def _create_component(
        cls,
        inst: SphinxDirective,
        name: str,
        options: dict,
        offset: int,
        content: StringList,
    ) -> nodes.container:
        """Create the header, body, or footer."""
        component = create_component(
            f"card-{name}", [f"sd-card-{name}"] + options.get(f"class-{name}", [])
        )
        inst.set_source_info(component)  # TODO set proper lines
        inst.state.nested_parse(content, offset, component)
        cls.add_card_child_classes(component)
        return component

    @staticmethod
    def add_card_child_classes(node):
        """Add classes to specific child nodes."""
        for para in node.traverse(nodes.paragraph):
            para["classes"] = ([] if "classes" not in para else para["classes"]) + [
                "sd-card-text"
            ]
        # for title in node.traverse(nodes.title):
        #     title["classes"] = ([] if "classes" not in title else title["classes"]) + [
        #         "sd-card-title"
        #     ]
