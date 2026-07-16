from __future__ import annotations

import re
from typing import TYPE_CHECKING, NamedTuple

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.util import ws_re
from sphinx.util.logging import getLogger

from .config import get_sd_config
from .shared import (
    WARNING_TYPE,
    PassthroughTextElement,
    SdDirective,
    create_component,
    is_component,
    is_ignorable_child,
    make_choice,
    margin_option,
    text_align,
)

if TYPE_CHECKING:
    from docutils.statemachine import StringList
    from sphinx.util.docutils import SphinxDirective

LOGGER = getLogger(__name__)

DIRECTIVE_NAME_CARD = "card"
DIRECTIVE_NAME_CARD_HEADER = "card-header"
DIRECTIVE_NAME_CARD_FOOTER = "card-footer"
DIRECTIVE_NAME_CAROUSEL = "card-carousel"

#: Node attribute marking a container as a "card content" parse context,
#: so that the ``card-header``/``card-footer`` sub-directives can detect
#: that they are being parsed inside a card (mirrors the ``tab-item`` parent
#: check). It is only ever set on transient/parse containers, and removed
#: before those containers reach the output, so it never leaks into a doctree.
CARD_CONTEXT_KEY = "sd_card_context"

#: Documentation anchor for the legacy-separator deprecation notice.
LEGACY_MIGRATION_URL = (
    "https://sphinx-design.readthedocs.io/en/latest/cards.html#legacy-separator-syntax"
)


def setup_cards(app: Sphinx) -> None:
    """Setup the card components."""
    app.add_directive(DIRECTIVE_NAME_CARD, CardDirective)
    app.add_directive(DIRECTIVE_NAME_CARD_HEADER, CardHeaderDirective)
    app.add_directive(DIRECTIVE_NAME_CARD_FOOTER, CardFooterDirective)
    app.add_directive(DIRECTIVE_NAME_CAROUSEL, CardCarouselDirective)


def is_card_context(node: nodes.Node) -> bool:
    """Check if a node marks a "card content" parse context.

    :param node: The (parse-parent) node to check.
    :return: True if the node is a card content container.
    """
    try:
        return bool(node.get(CARD_CONTEXT_KEY))
    except AttributeError:
        return False


class CardDirective(SdDirective):
    """A card component."""

    has_content = True
    required_arguments = 0
    optional_arguments = 1  # card title
    final_argument_whitespace = True
    option_spec = {
        "width": make_choice(["auto", "25%", "50%", "75%", "100%"]),
        "margin": margin_option,
        "text-align": text_align,
        "img-top": directives.uri,
        "img-bottom": directives.uri,
        "img-background": directives.uri,
        "img-alt": directives.unchanged,
        "link": directives.unchanged_required,
        "link-type": make_choice(["url", "any", "ref", "doc"]),
        "link-alt": directives.unchanged,
        "shadow": make_choice(["none", "sm", "md", "lg"]),
        # inline one-liner slots (compose with the body content);
        # mutually exclusive with the card-header/card-footer sub-directives
        "header": directives.unchanged,
        "footer": directives.unchanged,
        "class-card": directives.class_option,
        "class-header": directives.class_option,
        "class-body": directives.class_option,
        "class-title": directives.class_option,
        "class-footer": directives.class_option,
        "class-img-top": directives.class_option,
        "class-img-bottom": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        return [self.create_card(self, self.arguments, self.options)]

    @classmethod
    def create_card(  # noqa: PLR0915
        cls, inst: SphinxDirective, arguments: list | None, options: dict
    ) -> nodes.Node:
        """Run the directive."""
        # TODO better degradation for latex
        card_classes = ["sd-card", "sd-sphinx-override"]
        if "width" in options:
            card_classes += [f"sd-w-{options['width'].rstrip('%')}"]
        card_classes += options.get("margin", ["sd-mb-3"])
        card_classes += [f"sd-shadow-{options.get('shadow', 'sm')}"]
        if "link" in options:
            card_classes += ["sd-card-hover"]
        card = create_component(
            "card",
            card_classes
            + options.get("text-align", [])
            + options.get("class-card", []),
        )
        inst.set_source_info(card)

        img_alt = options.get("img-alt") or ""

        container = card
        if "img-background" in options:
            card.append(
                nodes.image(
                    uri=options["img-background"],
                    classes=["sd-card-img"],
                    alt=img_alt,
                )
            )
            overlay = create_component("card-overlay", ["sd-card-img-overlay"])
            inst.set_source_info(overlay)
            card += overlay
            container = overlay

        if "img-top" in options:
            image_top = nodes.image(
                "",
                uri=options["img-top"],
                alt=img_alt,
                classes=["sd-card-img-top", *options.get("class-img-top", [])],
            )
            container.append(image_top)

        # parse the content into the header/body/footer slots
        # (using the card-header/card-footer directives, or -- if enabled and
        # present -- the legacy ^^^/+++ separators)
        header, body_children, footer = cls.parse_content(inst, options)

        # inline one-liner :header:/:footer: options
        header = cls._slot_from_option(inst, options, "header", header)
        footer = cls._slot_from_option(inst, options, "footer", footer)

        if header is not None:
            container.append(header)

        body = create_component(
            "card-body", ["sd-card-body", *options.get("class-body", [])]
        )
        inst.set_source_info(body)
        body.extend(body_children)
        cls.add_card_child_classes(body)
        if arguments:
            title = create_component(
                "card-title",
                [
                    "sd-card-title",
                    "sd-font-weight-bold",
                    *options.get("class-title", []),
                ],
            )
            textnodes, _ = inst.state.inline_text(arguments[0], inst.lineno)
            title_container = PassthroughTextElement()
            title_container.extend(textnodes)
            inst.set_source_info(title_container)
            title.append(title_container)
            body.insert(0, title)
        container.append(body)

        if footer is not None:
            container.append(footer)

        if "img-bottom" in options:
            image_bottom = nodes.image(
                "",
                uri=options["img-bottom"],
                alt=img_alt,
                classes=["sd-card-img-bottom", *options.get("class-img-bottom", [])],
            )
            container.append(image_bottom)

        if "link" in options:
            link_container = PassthroughTextElement()
            _classes = ["sd-stretched-link", "sd-hide-link-text"]
            link_type = options.get("link-type", "url")
            # the raw (un-normalised) target, kept for user-visible fallback text
            link_raw = options["link"]
            link_target = cls.get_link_target(link_raw, link_type)
            _rawtext = options.get("link-alt") or link_raw
            if link_type == "url":
                link = nodes.reference(
                    _rawtext,
                    "",
                    nodes.inline(_rawtext, _rawtext),
                    refuri=link_target,
                    classes=_classes,
                )
            else:
                ref_options = {
                    # TODO the presence of classes raises an error if the link cannot be found
                    "classes": _classes,
                    "reftarget": link_target,
                    "refdoc": inst.env.docname,
                    "refdomain": "" if link_type == "any" else "std",
                    "reftype": link_type,
                    "refexplicit": "link-alt" in options,
                    "refwarn": True,
                }
                link = addnodes.pending_xref(
                    _rawtext, nodes.inline(_rawtext, _rawtext), **ref_options
                )
            inst.set_source_info(link)
            link_container += link
            container.append(link_container)

        return card

    @staticmethod
    def get_link_target(target: str, link_type: str) -> str:
        """Normalise a ``link`` option value into a reference target.

        The ``link`` option is captured verbatim (``unchanged_required``) so
        that whitespace in reference targets is preserved; how it is normalised
        then depends on ``link-type``:

        - ``url`` (the default): all whitespace is removed, exactly as
          :func:`docutils.parsers.rst.directives.uri` did before -- URLs cannot
          contain unescaped whitespace.
        - ``ref``: internal whitespace runs are collapsed to single spaces and
          the target is lowercased, mirroring Sphinx's ``:ref:`` role
          (``XRefRole(lowercase=True)``); std-domain labels are stored
          lowercased, so a multi-word, Title-Case heading (e.g. one generated
          by ``sphinx.ext.autosectionlabel``) can be pasted verbatim.
        - ``doc`` / ``any``: internal whitespace runs are collapsed, but case is
          preserved (docnames are case-sensitive; the ``any`` resolver
          lowercases internally where needed).

        :param target: The raw ``link`` option value.
        :param link_type: The ``link-type`` option
            (``url``/``ref``/``doc``/``any``).
        :return: The normalised reference target.
        """
        if link_type == "url":
            return directives.uri(target)
        target = ws_re.sub(" ", target).strip()
        if link_type == "ref":
            return target.lower()
        return target

    @classmethod
    def parse_content(
        cls, inst: SphinxDirective, options: dict
    ) -> tuple[nodes.container | None, list[nodes.Node], nodes.container | None]:
        """Parse the card content into ``(header, body_children, footer)``.

        The primary (parser-portable) syntax uses the ``card-header`` and
        ``card-footer`` sub-directives, which are hoisted out of the parsed
        content into their slots. If the legacy ``^^^``/``+++`` separators are
        enabled (``sd_card_legacy_separators``) *and* present in the raw
        content, the deprecated separator splitter is used instead.

        :param inst: The (card or grid-item-card) directive instance.
        :param options: The directive options.
        :return: The header slot (or None), the ordered body children, and the
            footer slot (or None).
        """
        config = get_sd_config(inst.env)
        if config.card_legacy_separators and _has_legacy_separators(inst.content):
            return cls._parse_legacy(inst, options)
        return cls._parse_slots(inst, options)

    @classmethod
    def _parse_slots(
        cls, inst: SphinxDirective, options: dict
    ) -> tuple[nodes.container | None, list[nodes.Node], nodes.container | None]:
        """Parse the content once, hoisting card-header/card-footer directives.

        The whole content is parsed into a transient container marked as a card
        context; its children are then partitioned into the header slot, the
        footer slot, and the (ordered) body children. Because docutils tracks
        source lines throughout this single parse, error attribution is correct
        for free.
        """
        temp = create_component("card-content")
        temp[CARD_CONTEXT_KEY] = True
        inst.set_source_info(temp)
        inst.state.nested_parse(inst.content, inst.content_offset, temp)
        header: nodes.container | None = None
        footer: nodes.container | None = None
        body_children: list[nodes.Node] = []
        for child in temp.children:
            if is_component(child, "card-header"):
                header = cls._merge_slot(header, child, "header")
            elif is_component(child, "card-footer"):
                footer = cls._merge_slot(footer, child, "footer")
            else:
                body_children.append(child)
        # compose the card-level class-header/class-footer options onto the slots
        _apply_slot_classes(header, options.get("class-header", []))
        _apply_slot_classes(footer, options.get("class-footer", []))
        return header, body_children, footer

    @classmethod
    def _merge_slot(
        cls,
        existing: nodes.container | None,
        new: nodes.container,
        name: str,
    ) -> nodes.container:
        """Return the slot to use, warning and merging if one already exists.

        Multiple ``card-header``/``card-footer`` directives in a single card is
        a user error; rather than dropping content we merge the later slot's
        children into the first, and warn.
        """
        if existing is None:
            return new
        LOGGER.warning(
            f"Card has multiple 'card-{name}' directives; "
            f"merging them into one [{WARNING_TYPE}.card]",
            location=new,
            type=WARNING_TYPE,
            subtype="card",
        )
        existing.extend(new.children)
        return existing

    @classmethod
    def _slot_from_option(
        cls,
        inst: SphinxDirective,
        options: dict,
        name: str,
        slot: nodes.container | None,
    ) -> nodes.container | None:
        """Build a header/footer slot from the inline ``:header:``/``:footer:``
        option, or warn (slot wins) if a slot was already supplied.

        :param inst: The directive instance.
        :param options: The directive options.
        :param name: The slot name (``header`` or ``footer``).
        :param slot: The slot already produced from the content (or None).
        :return: The slot to use.
        """
        raw = options.get(name)
        if not raw:
            return slot
        if slot is not None:
            LOGGER.warning(
                f"Card ':{name}:' option ignored: a 'card-{name}' directive "
                f"(or '^^^'/'+++' separator) is also present, which takes "
                f"precedence [{WARNING_TYPE}.card]",
                location=(inst.env.docname, inst.lineno),
                type=WARNING_TYPE,
                subtype="card",
            )
            return slot
        option_slot = create_component(
            f"card-{name}", [f"sd-card-{name}", *options.get(f"class-{name}", [])]
        )
        inst.set_source_info(option_slot)
        textnodes, _ = inst.state.inline_text(raw, inst.lineno)
        para = nodes.paragraph("", "", *textnodes, classes=["sd-card-text"])
        inst.set_source_info(para)
        option_slot.append(para)
        return option_slot

    @staticmethod
    def add_card_child_classes(node: nodes.Element) -> None:
        """Add classes to specific child nodes."""
        # only stamp direct child paragraphs of the component (see #40),
        # not paragraphs nested inside admonitions, lists, nested cards, etc.
        for para in node.children:
            if isinstance(para, nodes.paragraph):
                para["classes"] = [*para.get("classes", []), "sd-card-text"]
        # for title in node.findall(nodes.title):
        #     title["classes"] = ([] if "classes" not in title else title["classes"]) + [
        #         "sd-card-title"
        #     ]

    # ------------------------------------------------------------------
    # Legacy ^^^/+++ separator handling.
    #
    # This whole section supports the deprecated separator syntax, kept behind
    # the ``sd_card_legacy_separators`` config flag (default on). It is
    # scheduled to become opt-in at v1.0 and be removed at v2.0; the block can
    # then be deleted wholesale, leaving the directive-based ``_parse_slots``
    # path to stand alone.
    # ------------------------------------------------------------------

    @classmethod
    def _parse_legacy(
        cls, inst: SphinxDirective, options: dict
    ) -> tuple[nodes.container | None, list[nodes.Node], nodes.container | None]:
        """Split the content on the legacy ``^^^``/``+++`` separators.

        A single deprecation notice is emitted per document. If card-header/
        card-footer directives are *also* present (mixed syntax), they win: a
        ``design.card`` warning is emitted and they are hoisted into the slots,
        overriding the separator-derived ones.
        """
        # once-per-document deprecation notice (``temp_data`` is cleared before
        # each document is read, giving us document-scoped de-duplication)
        if not inst.env.temp_data.get("sd_card_legacy_warned"):
            inst.env.temp_data["sd_card_legacy_warned"] = True
            LOGGER.warning(
                "The '^^^'/'+++' card header/footer separators are deprecated; "
                "use the 'card-header'/'card-footer' directives instead "
                f"(see {LEGACY_MIGRATION_URL}; silence with "
                'suppress_warnings=["design.card_legacy"] or disable with '
                f"sd_card_legacy_separators=False) [{WARNING_TYPE}.card_legacy]",
                location=(inst.env.docname, inst.lineno),
                type=WARNING_TYPE,
                subtype="card_legacy",
            )

        components = cls.split_content(inst.content, inst.content_offset)
        header = (
            cls._create_slot(inst, "header", options, *components.header)
            if components.header
            else None
        )
        body_children = cls._parse_body_chunk(inst, *components.body)
        footer = (
            cls._create_slot(inst, "footer", options, *components.footer)
            if components.footer
            else None
        )
        # sub-directives take precedence over separators when both are used
        return cls._reconcile_mixed(inst, options, header, body_children, footer)

    @classmethod
    def _reconcile_mixed(
        cls,
        inst: SphinxDirective,
        options: dict,
        header: nodes.container | None,
        body_children: list[nodes.Node],
        footer: nodes.container | None,
    ) -> tuple[nodes.container | None, list[nodes.Node], nodes.container | None]:
        """Hoist any card-header/card-footer directives nested in the legacy
        chunks (mixed syntax), so the directives take precedence.

        The directives may be nested in *any* legacy chunk -- the body, or even
        inside a separator-derived header/footer slot (which would otherwise
        double the ``sd-card-*`` wrapper). A single ``design.card`` warning is
        emitted, the directives are removed from wherever they were parsed, and
        their children are merged into the matching slot (creating the slot if
        the separators did not).
        """
        # extract nested directive slots from every parsed location
        dir_headers: list[nodes.container] = []
        dir_footers: list[nodes.container] = []
        header = cls._extract_nested_slots(header, dir_headers, dir_footers)
        body_children = cls._extract_nested_slots_list(
            body_children, dir_headers, dir_footers
        )
        footer = cls._extract_nested_slots(footer, dir_headers, dir_footers)

        if not (dir_headers or dir_footers):
            return header, body_children, footer

        LOGGER.warning(
            "Card mixes '^^^'/'+++' separators with card-header/card-footer "
            "directives; the directives take precedence. If a '^^^'/'+++' line "
            "is incidental body content (e.g. inside a code block), disable the "
            f"legacy separators with sd_card_legacy_separators=False "
            f"[{WARNING_TYPE}.card]",
            location=(dir_headers or dir_footers)[0],
            type=WARNING_TYPE,
            subtype="card",
        )
        for node in dir_headers:
            header = cls._merge_directive_slot(inst, options, "header", header, node)
        for node in dir_footers:
            footer = cls._merge_directive_slot(inst, options, "footer", footer, node)
        return header, body_children, footer

    @staticmethod
    def _extract_nested_slots(
        slot: nodes.container | None,
        dir_headers: list[nodes.container],
        dir_footers: list[nodes.container],
    ) -> nodes.container | None:
        """Pull any nested card-header/card-footer directive components out of a
        separator-derived slot, collecting them for later merging.
        """
        if slot is None:
            return None
        slot.children = CardDirective._extract_nested_slots_list(
            list(slot.children), dir_headers, dir_footers
        )
        return slot

    @staticmethod
    def _extract_nested_slots_list(
        children: list[nodes.Node],
        dir_headers: list[nodes.container],
        dir_footers: list[nodes.container],
    ) -> list[nodes.Node]:
        """Partition a child list, collecting card-header/card-footer directive
        components and returning the remaining (non-slot) children.
        """
        kept: list[nodes.Node] = []
        for node in children:
            if is_component(node, "card-header"):
                dir_headers.append(node)
            elif is_component(node, "card-footer"):
                dir_footers.append(node)
            else:
                kept.append(node)
        return kept

    @classmethod
    def _merge_directive_slot(
        cls,
        inst: SphinxDirective,
        options: dict,
        name: str,
        slot: nodes.container | None,
        directive_slot: nodes.container,
    ) -> nodes.container:
        """Merge a mixed-syntax directive slot into the separator slot.

        If the separators produced no slot of this type, the directive's own
        container becomes the slot (with the card-level ``class-*`` option
        composed on); otherwise the directive's children are merged into the
        existing slot, dropping the directive's wrapper (no doubled wrappers).
        """
        if slot is None:
            _apply_slot_classes(directive_slot, options.get(f"class-{name}", []))
            return directive_slot
        slot.extend(directive_slot.children)
        return slot

    @staticmethod
    def split_content(content: StringList, offset: int) -> CardContent:
        """Split the content into header, body and footer.

        .. deprecated::
            Part of the legacy ``^^^``/``+++`` separator syntax.
        """
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
    def _create_slot(
        cls,
        inst: SphinxDirective,
        name: str,
        options: dict,
        offset: int,
        content: StringList,
    ) -> nodes.container:
        """Create a header or footer slot from a legacy content chunk."""
        slot = create_component(
            f"card-{name}", [f"sd-card-{name}", *options.get(f"class-{name}", [])]
        )
        inst.set_source_info(slot)
        # parse into a discarded, marked temp container (so any nested
        # card-header/card-footer directives detect the card context), then
        # move the children onto the slot -- the marker never touches `slot`,
        # and this is exception-safe (no marker to clean up on `slot` itself)
        slot.extend(cls._parse_body_chunk(inst, offset, content))
        cls.add_card_child_classes(slot)
        return slot

    #: Back-compatible alias for the pre-``card-header``/``card-footer`` name.
    #: Retained for one release for downstream extensions (e.g.
    #: sphinx-design-elements) that call it; prefer :meth:`_create_slot`.
    # TODO(2.0) remove this alias
    _create_component = _create_slot

    @classmethod
    def _parse_body_chunk(
        cls, inst: SphinxDirective, offset: int, content: StringList
    ) -> list[nodes.Node]:
        """Parse a legacy content chunk into its (unstamped) child nodes.

        Parsing happens inside a transient container marked as a card context
        (so nested card-header/card-footer directives detect the card), which
        is then discarded -- the marker never reaches the output.
        """
        temp = create_component("card-content")
        temp[CARD_CONTEXT_KEY] = True
        inst.set_source_info(temp)
        inst.state.nested_parse(content, offset, temp)
        return list(temp.children)


class CardContent(NamedTuple):
    """Split card into header (optional), body, footer (optional).

    (offset, content)

    .. deprecated::
        Part of the legacy ``^^^``/``+++`` separator syntax.
    """

    body: tuple[int, StringList]
    header: tuple[int, StringList] | None = None
    footer: tuple[int, StringList] | None = None


#: Legacy card header separator (``^^^``); part of the deprecated syntax.
REGEX_HEADER = re.compile(r"^\^{3,}\s*$")
#: Legacy card footer separator (``+++``); part of the deprecated syntax.
REGEX_FOOTER = re.compile(r"^\+{3,}\s*$")


def _has_legacy_separators(content: StringList) -> bool:
    """Check the raw content for any legacy ``^^^``/``+++`` separator line."""
    return any(REGEX_HEADER.match(line) or REGEX_FOOTER.match(line) for line in content)


def _apply_slot_classes(slot: nodes.container | None, extra: list[str]) -> None:
    """Compose the card-level ``class-header``/``class-footer`` options onto a
    directive-produced slot, keeping the base ``sd-card-*`` class first and
    dropping any duplicates (order-preserving).
    """
    if slot is None or not extra:
        return
    seen = set(slot["classes"])
    additions: list[str] = []
    for cls_name in extra:
        if cls_name not in seen:
            seen.add(cls_name)
            additions.append(cls_name)
    slot["classes"][1:1] = additions


class _CardSlotDirective(SdDirective):
    """Base class for the ``card-header`` and ``card-footer`` sub-directives."""

    has_content = True
    option_spec = {"class": directives.class_option}

    #: The slot name (``header`` or ``footer``), set by subclasses.
    slot_name: str = ""

    def run_with_defaults(self) -> list[nodes.Node]:
        self.assert_has_content()
        if not is_card_context(self.state_machine.node):
            LOGGER.warning(
                f"The parent of a 'card-{self.slot_name}' should be a 'card' "
                f"or 'grid-item-card' [{WARNING_TYPE}.card]",
                location=(self.env.docname, self.lineno),
                type=WARNING_TYPE,
                subtype="card",
            )
        slot = create_component(
            f"card-{self.slot_name}",
            [f"sd-card-{self.slot_name}", *self.options.get("class", [])],
        )
        self.set_source_info(slot)
        self.state.nested_parse(self.content, self.content_offset, slot)
        CardDirective.add_card_child_classes(slot)
        return [slot]


class CardHeaderDirective(_CardSlotDirective):
    """The header of a card (rendered in the header slot regardless of
    position within the card body).
    """

    slot_name = "header"


class CardFooterDirective(_CardSlotDirective):
    """The footer of a card (rendered in the footer slot regardless of
    position within the card body).
    """

    slot_name = "footer"


class CardCarouselDirective(SdDirective):
    """A component, which is a container for cards in a single scrollable row."""

    has_content = True
    required_arguments = 1  # columns
    optional_arguments = 0
    option_spec = {
        "class": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        self.assert_has_content()
        try:
            cols = make_choice([str(i) for i in range(1, 13)])(
                self.arguments[0].strip()
            )
        except ValueError as exc:
            raise self.error(f"Invalid directive argument: {exc}") from exc
        container = create_component(
            "card-carousel",
            [
                "sd-sphinx-override",
                "sd-cards-carousel",
                f"sd-card-cols-{cols}",
                *self.options.get("class", []),
            ],
        )
        self.set_source_info(container)
        self.state.nested_parse(self.content, self.content_offset, container)
        for item in container.children:
            if is_ignorable_child(item):
                continue
            if not is_component(item, "card"):
                LOGGER.warning(
                    "All children of a 'card-carousel' "
                    f"should be 'card' [{WARNING_TYPE}.card]",
                    location=item,
                    type=WARNING_TYPE,
                    subtype="card",
                )
                break
        return [container]
