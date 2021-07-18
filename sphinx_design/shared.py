"""Shared constants and functions."""

from typing import List, Optional, Sequence

from docutils import nodes
from docutils.parsers.rst import directives

WARNING_TYPE = "design"

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
)


def create_component(name: str, classes: List[str]) -> nodes.container:
    """Create a container node for a design component."""
    return nodes.container("", is_div=True, design_component=name, classes=classes)


def is_component(node: nodes.Node, name: str):
    """Check if a node is a certain design component."""
    return node.get("design_component") == name


def make_choice(choices: Sequence[str]):
    """Create a choice validator."""
    return lambda argument: directives.choice(argument, choices)


def _margin_or_padding_option(argument: Optional[str], class_prefix: str) -> List[str]:
    """Validate the margin/padding is one (all) or four (top bottom left right) integers,
    between 0 and 5.
    """
    if argument is None:
        raise ValueError("argument required but none supplied")
    values = argument.split()
    try:
        int_values = [int(value) for value in values]
    except Exception:
        raise ValueError("argument must be space separated list of integers")
    for value in int_values:
        if not 0 <= value <= 5:
            raise ValueError("argument must be integers in range 0 to 5")
    if len(values) == 1:
        return [f"{class_prefix}-{values[0]}"]
    if len(values) == 4:
        return [
            f"{class_prefix}{side}-{value}"
            for side, value in zip(["t", "b", "l", "r"], int_values)
        ]
    raise ValueError(
        "argument must be one (all) or four (top bottom left right) integers"
    )


def margin_option(argument: Optional[str]) -> List[str]:
    """Validate the margin is one (all) or four (top bottom left right) integers,
    between 0 and 5.
    """
    return _margin_or_padding_option(argument, "sd-m")


def padding_option(argument: Optional[str]) -> List[str]:
    """Validate the padding is one (all) or four (top bottom left right) integers,
    between 0 and 5.
    """
    return _margin_or_padding_option(argument, "sd-p")


def text_align(argument: Optional[str]) -> List[str]:
    """Validate the text align is left, right, center or justify."""
    value = directives.choice(argument, ["left", "right", "center", "justify"])
    return [f"sd-text-{value}"]
