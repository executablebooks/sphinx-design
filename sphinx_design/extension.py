from contextlib import contextmanager
from functools import partial
from pathlib import Path

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.transforms import SphinxTransform

from .article_info import setup_article_info
from .badges_buttons import setup_badges_and_buttons
from .cards import setup_cards
from .config import get_sd_config, setup_sd_config
from .dropdown import setup_dropdown
from .grids import setup_grids
from .icons import setup_icons
from .shared import (
    PassthroughTextElement,
    SdDirective,
    create_component,
    setup_custom_directives,
)
from .tabs import setup_tabs

STATIC_DIR = Path(__file__).parent / "static"


def setup_extension(app: Sphinx) -> None:
    """Set up the sphinx extension."""
    setup_sd_config(app)
    app.connect("builder-inited", add_static_assets)
    # we override container html visitors, to stop the default behaviour
    # of adding the `container` class to all nodes.container
    app.add_node(
        nodes.container, override=True, html=(visit_container, depart_container)
    )
    app.add_node(
        PassthroughTextElement,
        html=(visit_depart_null, visit_depart_null),
        latex=(visit_depart_null, visit_depart_null),
        text=(visit_depart_null, visit_depart_null),
        man=(visit_depart_null, visit_depart_null),
        texinfo=(visit_depart_null, visit_depart_null),
    )
    with capture_directives(app) as directive_map:
        app.add_directive("div", Div, override=True)
        app.add_transform(AddFirstTitleCss)
        setup_badges_and_buttons(app)
        setup_cards(app)
        setup_grids(app)
        setup_dropdown(app)
        setup_icons(app)
        setup_tabs(app)
        setup_article_info(app)

    app.connect(
        "config-inited", partial(setup_custom_directives, directive_map=directive_map)
    )


@contextmanager
def capture_directives(app: Sphinx):
    """Capture the directives that are registered by the extension."""
    directive_map = {}
    add_directive = app.add_directive

    def _add_directive(name, directive, **kwargs):
        directive_map[name] = directive
        add_directive(name, directive, **kwargs)

    app.add_directive = _add_directive  # type: ignore[assignment,method-assign]
    yield directive_map
    app.add_directive = add_directive  # type: ignore[method-assign]


def add_static_assets(app: Sphinx) -> None:
    """Register the extension's static assets (HTML-format builders only)."""
    if app.builder.format != "html":
        return
    app.config.html_static_path.append(str(STATIC_DIR))
    app.add_css_file("sphinx-design.min.css")
    # deliver the (configurable) tab-storage key prefix declaratively,
    # as a data attribute on the script tag (read by design-tabs.js at startup)
    sd_config = get_sd_config(app.env)
    js_attributes: dict[str, str] = {
        "data-sd-tabs-storage-prefix": sd_config.tabs_storage_prefix
    }
    # the ignore is because mypy checks the unpacked values against the
    # explicit ``priority: int`` parameter, but they only ever land in
    # ``**kwargs`` (the HTML attributes)
    app.add_js_file("design-tabs.js", **js_attributes)  # type: ignore[arg-type]


def visit_container(self, node: nodes.Node):
    classes = "docutils container"
    attrs = {}
    if node.get("is_div", False):
        # we don't want the CSS for container for these nodes
        classes = "docutils"
    if "style" in node:
        attrs["style"] = node["style"]
    self.body.append(self.starttag(node, "div", CLASS=classes, **attrs))


def depart_container(self, node: nodes.Node):
    self.body.append("</div>\n")


def visit_depart_null(self, node: nodes.Element) -> None:
    """visit/depart passthrough"""


class Div(SdDirective):
    """Same as the ``container`` directive,
    but does not add the ``container`` class in HTML outputs,
    which can interfere with Bootstrap CSS.
    """

    optional_arguments = 1  # css classes
    final_argument_whitespace = True
    option_spec = {"style": directives.unchanged, "name": directives.unchanged}
    has_content = True

    def run_with_defaults(self) -> list[nodes.Node]:
        try:
            if self.arguments:
                classes = directives.class_option(self.arguments[0])
            else:
                classes = []
        except ValueError as exc:
            raise self.error(
                f'Invalid class attribute value for "{self.name}" directive: "{self.arguments[0]}".'
            ) from exc
        node = create_component("div", rawtext="\n".join(self.content), classes=classes)
        if "style" in self.options:
            node["style"] = self.options["style"]
        self.set_source_info(node)
        self.add_name(node)
        if self.content:
            self.state.nested_parse(self.content, self.content_offset, node)
        return [node]


class AddFirstTitleCss(SphinxTransform):
    """Add a CSS class to to the first sections title."""

    default_priority = 699  # priority main

    def apply(self):
        hide = False
        for docinfo in self.document.findall(nodes.docinfo):
            for name in docinfo.findall(nodes.field_name):
                if name.astext() == "sd_hide_title":
                    hide = True
                    break
            break
        if not hide:
            return
        for section in self.document.findall(nodes.section):
            if isinstance(section.children[0], nodes.title):
                if "classes" in section.children[0]:
                    section.children[0]["classes"].append("sd-d-none")
                else:
                    section.children[0]["classes"] = ["sd-d-none"]
            break
