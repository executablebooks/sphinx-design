from typing import List, Optional

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective
from sphinx.util.logging import getLogger

from sphinx_design.card import CardDirective

from .shared import (
    WARNING_TYPE,
    create_component,
    is_component,
    make_option,
    margin_option,
    padding_option,
)

LOGGER = getLogger(__name__)


DIRECTIVE_NAME_GRID = "grid"
DIRECTIVE_NAME_GRID_ITEM = "grid-item"
DIRECTIVE_NAME_GRID_ITEM_CARD = "grid-card-item"


def setup_grid(app: Sphinx):
    """Setup the card components."""
    app.add_directive(DIRECTIVE_NAME_GRID, GridDirective)
    app.add_directive(DIRECTIVE_NAME_GRID_ITEM, GridItemDirective)
    app.add_directive(DIRECTIVE_NAME_GRID_ITEM_CARD, GridItemCardDirective)
    # TODO check all grid items have grid parents (or auto wrap in grid?)


def _number_columns_option(
    argument: Optional[str], allow_auto: bool, prefix: str
) -> List[str]:
    """Validate the number of columns (out of 12).

    One or four integers (for "xs sm md lg") between 1 and 12.
    """
    if argument is None:
        return []
    values = argument.split()
    validate_error_msg = (
        "argument must be empty, 1 or 4 values: xs sm md lg, "
        "and each should be either 'auto' or an integer from 1 to 12"
    )
    if len(values) == 1:
        values = [values[0], values[0], values[0], values[0]]
    if len(values) != 4:
        raise ValueError(validate_error_msg)
    for value in values:
        if allow_auto and value == "auto":
            continue
        try:
            int_value = int(value)
        except Exception:
            raise ValueError(validate_error_msg)
        if not 0 < int_value < 13:
            raise ValueError(validate_error_msg)
    return [
        f"{prefix}-{size}-{value}"
        for size, value in zip(["xs", "sm", "md", "lg"], values)
    ]


def grid_columns_option(argument: Optional[str]) -> List[str]:
    """Validate the number of columns (out of 12) a grid row will have.

    One or four integers (for "xs sm md lg") between 1 and 12.
    """
    return ["mui-row-cols-1"] + _number_columns_option(argument, False, "mui-row-cols")


def item_columns_option(argument: Optional[str]) -> List[str]:
    """Validate the number of columns (out of 12) a grid-item will take up.

    One or four integers (for "xs sm md lg") between 1 and 12.
    """
    return _number_columns_option(argument, True, "mui-col")


class GridDirective(SphinxDirective):
    """A grid component, which is a container for grid items (i.e. columns)."""

    has_content = True
    option_spec = {
        "columns": grid_columns_option,
        # TODO gutters
        "margin": margin_option,
        "padding": padding_option,
        "class": directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Run the directive."""
        self.assert_has_content()
        container = create_component(
            "grid",
            ["mui-container", "mui-sphinx-override"]
            + self.options.get("margin", [])
            + self.options.get("padding", ["mui-pb-4"])
            + self.options.get("class", []),
        )
        self.set_source_info(container)
        row = create_component(
            "grid-row", ["mui-row"] + self.options.get("columns", [])
        )
        self.set_source_info(row)
        container += row
        self.state.nested_parse(self.content, self.content_offset, row)
        # each item in a row should be a column
        for item in row.children:
            if not is_component(item, "grid-column"):
                LOGGER.warning(
                    f"All children of a '{DIRECTIVE_NAME_GRID}' "
                    f"should be '{DIRECTIVE_NAME_GRID_ITEM}' [{WARNING_TYPE}.grid]",
                    location=item,
                    type=WARNING_TYPE,
                    subtype="grid",
                )
                break
        return [container]


class GridItemDirective(SphinxDirective):
    """An item within a grid row.

    Can "occupy" 1 to 12 columns.
    """

    has_content = True
    option_spec = {
        "columns": item_columns_option,
        "margin": margin_option,
        "padding": padding_option,
        "class": directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Run the directive."""
        self.assert_has_content()
        column = create_component(
            "grid-column",
            [
                "mui-col",
                "mui-d-flex",  # TODO is this necessary or should be configurable?
            ]
            + self.options.get("columns", [])
            + self.options.get("margin", [])
            + self.options.get("padding", [])
            + self.options.get("class", []),
        )
        self.set_source_info(column)
        self.state.nested_parse(self.content, self.content_offset, column)
        return [column]


class GridItemCardDirective(SphinxDirective):
    """An item within a grid row, with an internal card."""

    has_content = True
    option_spec = {
        "columns": item_columns_option,
        "margin": margin_option,
        "padding": padding_option,
        "text-align": make_option(["left", "right", "center"]),
        "img-top": directives.uri,
        "img-bottom": directives.uri,
        "no-shadow": directives.flag,
        "class-grid": directives.class_option,
        "class-card": directives.class_option,
        "class-body": directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Run the directive."""
        self.assert_has_content()
        column = create_component(
            "grid-column",
            [
                "mui-col",
                "mui-d-flex",  # TODO is this necessary or should be configurable?
            ]
            + self.options.get("columns", [])
            + self.options.get("margin", [])
            + self.options.get("padding", [])
            + self.options.get("class-grid", []),
        )
        card_options = {
            key: value
            for key, value in self.options.items()
            if key
            in [
                "text-align",
                "img-top",
                "img-bottom",
                "no-shadow",
                "class-card",
                "class-body",
            ]
        }
        card_options["width"] = "100"
        card = CardDirective.create_card(self, card_options)
        column += card
        return [column]
