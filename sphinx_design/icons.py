import json
import re
from functools import lru_cache
from typing import Any, Dict, List, Optional, Sequence, Tuple

try:
    import importlib.resources as resources
except ImportError:
    # python < 3.7
    import importlib_resources as resources  # type: ignore[no-redef]

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util.docutils import SphinxDirective, SphinxRole

from . import compiled

OCTICON_VERSION = "0.0.0-dd899ea"

OCTICON_CSS = """\
.octicon {
  display: inline-block;
  vertical-align: text-top;
  fill: currentColor;
}"""


def setup_icons(app: Sphinx) -> None:
    app.add_role("octicon", OcticonRole())
    app.add_directive("_all-octicon", AllOcticons)
    for style in ["fa", "fas", "fab", "far"]:
        # note: fa is deprecated in v5, fas is the default and fab is the other free option
        app.add_role(style, FontawesomeRole(style))
    app.add_config_value("sd_fontawesome_latex", False, "env")
    app.connect("config-inited", add_fontawesome_pkg)
    app.add_node(
        fontawesome,
        html=(visit_fontawesome_html, depart_fontawesome_html),
        latex=(visit_fontawesome_latex, None),
        text=(None, None),
        man=(None, None),
        texinfo=(None, None),
    )


@lru_cache(1)
def get_octicon_data() -> Dict[str, Any]:
    """Load all octicon data."""
    content = resources.read_text(compiled, "octicons.json")
    return json.loads(content)


def list_octicons() -> List[str]:
    """List available octicon names."""
    return list(get_octicon_data().keys())


HEIGHT_REGEX = re.compile(r"^(?P<value>\d+(\.\d+)?)(?P<unit>px|em|rem)$")


def get_octicon(
    name: str,
    height: str = "1em",
    classes: Sequence[str] = (),
    aria_label: Optional[str] = None,
) -> str:
    """Return the HTML for an GitHub octicon SVG icon.

    :height: the height of the octicon, with suffix unit 'px', 'em' or 'rem'.
    """
    try:
        data = get_octicon_data()[name]
    except KeyError:
        raise KeyError(f"Unrecognised octicon: {name}")

    match = HEIGHT_REGEX.match(height)
    if not match:
        raise ValueError(
            f"Invalid height: '{height}', must be format <integer><px|em|rem>"
        )
    height_value = round(float(match.group("value")), 3)
    height_unit = match.group("unit")

    original_height = 16
    if "16" not in data["heights"]:
        original_height = int(list(data["heights"].keys())[0])
    elif "24" in data["heights"]:
        if height_unit == "px":
            if height_value >= 24:
                original_height = 24
        elif height_value >= 1.5:
            original_height = 24
    original_width = data["heights"][str(original_height)]["width"]
    width_value = round(original_width * height_value / original_height, 3)
    content = data["heights"][str(original_height)]["path"]
    options = {
        "version": "1.1",
        "width": f"{width_value}{height_unit}",
        "height": f"{height_value}{height_unit}",
        "class": " ".join(("sd-octicon", f"sd-octicon-{name}", *classes)),
    }

    options["viewBox"] = f"0 0 {original_width} {original_height}"

    if aria_label is not None:
        options["aria-label"] = aria_label
        options["role"] = "img"
    else:
        options["aria-hidden"] = "true"

    opt_string = " ".join(f'{k}="{v}"' for k, v in options.items())
    return f"<svg {opt_string}>{content}</svg>"


class OcticonRole(SphinxRole):
    """Role to display a GitHub octicon SVG.

    Additional classes can be added to the element after a semicolon.
    """

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        values = self.text.split(";") if ";" in self.text else [self.text]
        icon = values[0]
        height = "1em" if len(values) < 2 else values[1]
        classes = "" if len(values) < 3 else values[2]
        icon = icon.strip()
        try:
            svg = get_octicon(icon, height=height, classes=classes.split())
        except Exception as exc:
            msg = self.inliner.reporter.error(
                f"Invalid octicon content: {exc}",
                line=self.lineno,
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        node = nodes.raw("", nodes.Text(svg), format="html")
        self.set_source_info(node)
        return [node], []


class AllOcticons(SphinxDirective):
    """Directive to generate all octicon icons.

    Primarily for self documentation.
    """

    option_spec = {
        "class": directives.class_option,
    }

    def run(self) -> List[nodes.Node]:
        """Run the directive."""
        classes = self.options.get("class", [])
        list_node = nodes.bullet_list()
        for icon in list_octicons():
            item_node = nodes.list_item()
            item_node.extend(
                (
                    nodes.literal(icon, icon),
                    nodes.Text(": "),
                    nodes.raw(
                        "",
                        nodes.Text(get_octicon(icon, classes=classes)),
                        format="html",
                    ),
                )
            )
            list_node += item_node
        return [list_node]


class fontawesome(nodes.Element, nodes.General):
    """Node for rendering fontawesome icon."""


class FontawesomeRole(SphinxRole):
    """Role to display a Fontawesome icon.

    Additional classes can be added to the element after a semicolon.
    """

    def __init__(self, style: str) -> None:
        super().__init__()
        self.style = style

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        icon, classes = self.text.split(";", 1) if ";" in self.text else [self.text, ""]
        icon = icon.strip()
        node = fontawesome(
            icon=icon, classes=[self.style, f"fa-{icon}"] + classes.split()
        )
        self.set_source_info(node)
        return [node], []


def visit_fontawesome_html(self, node):
    self.body.append(self.starttag(node, "span", ""))


def depart_fontawesome_html(self, node):
    self.body.append("</span>")


def add_fontawesome_pkg(app, config):
    if app.config.sd_fontawesome_latex:
        app.add_latex_package("fontawesome")


def visit_fontawesome_latex(self, node):
    if self.config.sd_fontawesome_latex:
        self.body.append(f"\\faicon{{{node['icon_name']}}}")
    raise nodes.SkipNode
