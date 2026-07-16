"""The ``steps`` and ``step`` directives, for numbered procedures.

The doctree is a real ordered list (``enumerated_list`` of ``list_item``), so
assistive technology announces the step numbering and non-HTML builders degrade
to a proper numbered list. The visible circular markers and connecting rail are
drawn purely with CSS (``style/steps.css``): the marker text is
``counter(list-item)``, the built-in list counter, so it always reflects the
document order (including the ``start`` offset) without baking any number into
the doctree -- translations or re-ordering can never desynchronise it.
"""

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.logging import getLogger

from .shared import (
    SEMANTIC_COLORS,
    WARNING_TYPE,
    SdDirective,
    create_component,
    is_component,
    is_ignorable_child,
    make_choice,
)

LOGGER = getLogger(__name__)

DIRECTIVE_NAME_STEPS = "steps"
DIRECTIVE_NAME_STEP = "step"


def setup_steps(app: Sphinx) -> None:
    """Set up the steps components."""
    app.add_directive(DIRECTIVE_NAME_STEPS, StepsDirective)
    app.add_directive(DIRECTIVE_NAME_STEP, StepDirective)


class StepsDirective(SdDirective):
    """A container for a numbered sequence of :rst:dir:`step` items.

    The container is an ``enumerated_list`` (rendered ``<ol>``), so the
    numbering is semantic; the ``start`` option maps to the list's native
    ``start`` attribute, which the CSS marker reads via ``counter(list-item)``.
    """

    has_content = True
    option_spec = {
        "start": directives.nonnegative_int,
        "color": make_choice(SEMANTIC_COLORS),
        "class": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        self.assert_has_content()
        classes = ["sd-steps"]
        if color := self.options.get("color"):
            classes.append(f"sd-steps-{color}")
        classes += self.options.get("class", [])
        # a real ordered list: assistive tech gets the numbering, and non-HTML
        # builders degrade to a numbered list. ``suffix``/``enumtype`` mirror
        # what the rst parser sets on an ordinary ``#.`` list.
        steps = nodes.enumerated_list(
            "",
            design_component="steps",
            classes=classes,
            enumtype="arabic",
            prefix="",
            suffix=".",
        )
        start = self.options.get("start", 1)
        if start != 1:
            # native <ol start="N"> drives both the (hidden) list marker and the
            # CSS counter(list-item) used for the visible marker
            steps["start"] = start
        self.set_source_info(steps)
        self.state.nested_parse(self.content, self.content_offset, steps)
        # each child must be a ``step``; an ``enumerated_list`` can only hold
        # ``list_item`` children, so drop (rather than keep) anything else
        valid_children: list[nodes.Node] = []
        for item in steps.children:
            if is_ignorable_child(item):
                continue
            if not is_component(item, "step"):
                LOGGER.warning(
                    f"All children of a 'steps' should be 'step' [{WARNING_TYPE}.steps]",
                    location=item,
                    type=WARNING_TYPE,
                    subtype="steps",
                )
                continue
            valid_children.append(item)
        steps.children = valid_children
        return [steps]


class StepDirective(SdDirective):
    """A single step within a :rst:dir:`steps` container.

    Generates a ``list_item`` holding an optional title (a ``rubric``, as for
    tab labels and dropdown titles) followed by a ``step-content`` container::

        <list_item design_component="step">
            <rubric classes="sd-step-title">
                ...title nodes
            <container design_component="step-content">
                ...content nodes
    """

    optional_arguments = 1  # the (optional) step title
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "class": directives.class_option,
        "class-title": directives.class_option,
        "class-content": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        if not is_component(self.state_machine.node, "steps"):
            LOGGER.warning(
                f"The parent of a 'step' should be a 'steps' [{WARNING_TYPE}.steps]",
                location=(self.env.docname, self.lineno),
                type=WARNING_TYPE,
                subtype="steps",
            )
        step = nodes.list_item(
            "",
            design_component="step",
            classes=["sd-step", *self.options.get("class", [])],
        )
        self.set_source_info(step)
        if self.arguments:
            textnodes, messages = self.state.inline_text(self.arguments[0], self.lineno)
            title_node = nodes.rubric(
                self.arguments[0],
                "",
                *textnodes,
                classes=["sd-step-title", *self.options.get("class-title", [])],
            )
            step += title_node
            step += messages
        content = create_component(
            "step-content",
            classes=["sd-step-content", *self.options.get("class-content", [])],
        )
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, content)
        step += content
        return [step]
