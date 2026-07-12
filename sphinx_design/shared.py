"""Shared constants and functions."""

from __future__ import annotations

from collections.abc import Sequence
from typing import final

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

from .config import WARNING_TYPE, SdConfig, get_sd_config

LOGGER = getLogger(__name__)

__all__ = (
    "SEMANTIC_COLORS",
    "SKIP_CHILD_TYPES",
    "WARNING_TYPE",
    "PassthroughTextElement",
    "SdDirective",
    "create_component",
    "is_component",
    "is_ignorable_child",
    "make_choice",
    "margin_option",
    "padding_option",
    "setup_custom_directives",
    "text_align",
)

SEMANTIC_COLORS = (
    "primary",
    "secondary",
    "success",
    "info",
    "warning",
    "danger",
    "light",
    "muted",
    "dark",
    "white",
    "black",
)


def setup_custom_directives(
    app: Sphinx, config: Config, directive_map: dict[str, SdDirective]
) -> None:
    """Register the custom directives declared in ``sd_custom_directives``.

    The shape of each entry has already been validated on ``config-inited``
    (see ``sphinx_design.config``);
    here we additionally check the values against the known directives.
    """

    def _warn(msg: str) -> None:
        LOGGER.warning(
            f"sd_custom_directives: {msg}", type=WARNING_TYPE, subtype="config"
        )

    for name, data in SdConfig.from_sphinx(config).custom_directives.items():
        if data["inherit"] not in directive_map:
            _warn(f"'{name}.inherit' is an unknown directive key: {data['inherit']}")
            continue
        directive_cls = directive_map[data["inherit"]]
        for key in data.get("options", {}):
            if key not in directive_cls.option_spec:
                _warn(f"'{name}.options' unknown key {key!r}")
        app.add_directive(name, directive_cls, override=True)


class SdDirective(SphinxDirective):
    """Base class for all sphinx-design directives.

    Having a base class allows for shared functionality to be implemented in one place.
    Namely, we allow for default options to be configured, per directive name.

    This class should be sub-classed by all directives in the sphinx-design extension.
    """

    # TODO perhaps ideally there would be separate sphinx extension,
    # that generalises the concept of default directive options (that does not require subclassing)
    # but for now I couldn't think of a trivial way to achieve this.

    @final
    def run(self) -> list[nodes.Node]:
        """Run the directive.

        This method should not be overridden, instead override `run_with_defaults`.
        """
        if data := get_sd_config(self.env).custom_directives.get(self.name):
            if (not self.arguments) and (argument := data.get("argument")):  # type: ignore[has-type]
                self.arguments = [str(argument)]
            for key, value in data.get("options", {}).items():
                if key not in self.options and key in self.option_spec:
                    try:
                        self.options[key] = self.option_spec[key](str(value))
                    except Exception as exc:
                        LOGGER.warning(
                            f"Invalid default option {key!r} for {self.name!r}: {exc}",
                            type=WARNING_TYPE,
                            subtype="directive",
                            location=(self.env.docname, self.lineno),
                        )
        return self.run_with_defaults()

    def run_with_defaults(self) -> list[nodes.Node]:
        """Run the directive, after default options have been set.

        This method should be overridden by subclasses.
        """
        raise NotImplementedError


def create_component(
    name: str,
    classes: Sequence[str] = (),
    *,
    rawtext: str = "",
    children: Sequence[nodes.Node] = (),
    **attributes,
) -> nodes.container:
    """Create a container node for a design component."""
    node = nodes.container(
        rawtext, is_div=True, design_component=name, classes=list(classes), **attributes
    )
    node.extend(children)
    return node


def is_component(node: nodes.Node, name: str):
    """Check if a node is a certain design component."""
    try:
        return node.get("design_component") == name
    except AttributeError:
        return False


#: Node types that are structurally inert inside component containers.
SKIP_CHILD_TYPES = (nodes.comment, nodes.target, nodes.system_message)


def is_ignorable_child(node: nodes.Node) -> bool:
    """Check if a node can be silently ignored when validating component children."""
    return isinstance(node, SKIP_CHILD_TYPES)


def make_choice(choices: Sequence[str]):
    """Create a choice validator."""
    return lambda argument: directives.choice(argument, choices)


def _margin_or_padding_option(
    argument: str | None,
    class_prefix: str,
    allowed: Sequence[str],
) -> list[str]:
    """Validate the margin/padding is one (all) or four (top bottom left right) integers,
    between 0 and 5 or 'auto'.
    """
    if argument is None:
        raise ValueError("argument required but none supplied")
    values = argument.split()
    for value in values:
        if value not in allowed:
            raise ValueError(f"{value} is not in: {allowed}")
    if len(values) == 1:
        return [f"{class_prefix}-{values[0]}"]
    if len(values) == 4:
        return [
            f"{class_prefix}{side}-{value}"
            for side, value in zip(["t", "b", "l", "r"], values, strict=False)
        ]
    raise ValueError(
        "argument must be one (all) or four (top bottom left right) integers"
    )


def margin_option(argument: str | None) -> list[str]:
    """Validate the margin is one (all) or four (top bottom left right) integers,
    between 0 and 5 or 'auto'.
    """
    return _margin_or_padding_option(
        argument, "sd-m", ("auto", "0", "1", "2", "3", "4", "5")
    )


def padding_option(argument: str | None) -> list[str]:
    """Validate the padding is one (all) or four (top bottom left right) integers,
    between 0 and 5.
    """
    return _margin_or_padding_option(argument, "sd-p", ("0", "1", "2", "3", "4", "5"))


def text_align(argument: str | None) -> list[str]:
    """Validate the text align is left, right, center or justify."""
    value = directives.choice(argument, ["left", "right", "center", "justify"])
    return [f"sd-text-{value}"]


class PassthroughTextElement(nodes.TextElement):
    """A text element which will not render anything.

    This is required for reference node to render correctly outside of paragraphs.
    Since sphinx expects them to be within a ``TextElement``:
    https://github.com/sphinx-doc/sphinx/blob/068f802df90ea790f89319094e407c4d5f6c26ff/sphinx/writers/html5.py#L224
    """
