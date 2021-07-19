import json
from functools import lru_cache
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    import importlib.resources as resources
except ImportError:
    # python < 3.7
    import importlib_resources as resources  # type: ignore[no-redef]

from docutils import nodes
from sphinx.util.docutils import SphinxRole

from . import compiled

OPTICON_VERSION = "0.0.0-dd899ea"

OPTICON_CSS = """\
.octicon {
  display: inline-block;
  vertical-align: text-top;
  fill: currentColor;
}"""


def setup_icons(app):
    app.add_role("opticon-16", OpticonRole(16))
    app.add_role("opticon-24", OpticonRole(24))
    for style in ["fa", "fas", "fab"]:
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
def get_opticon_data() -> Dict[str, Any]:
    """Load all octicon data."""
    content = resources.read_text(compiled, "opticons.json")
    return json.loads(content)


def list_opticons() -> List[str]:
    """List available octicon names."""
    return list(get_opticon_data().keys())


def get_opticon(
    name: str,
    classes: Optional[str] = None,
    width: Optional[Union[int, float]] = None,
    height: Optional[Union[int, float]] = None,
    aria_label: Optional[str] = None,
    size: int = 16,
) -> str:
    """Return the HTML for an GitHub octicon SVG icon."""
    assert size in [16, 24], "size must be 16 or 24"
    try:
        data = get_opticon_data()[name]
    except KeyError:
        raise KeyError(f"Unrecognised opticon: {name}")

    content = data["heights"][str(size)]["path"]
    options = {
        "version": "1.1",
        "width": data["heights"][str(size)]["width"],
        "height": int(size),
        "class": f"sd-octicon sd-octicon-{name}",
    }

    if width is not None or height is not None:
        if width is None and height is not None:
            width = round((int(height) * options["width"]) / options["height"], 2)
        if height is None and width is not None:
            height = round((int(width) * options["height"]) / options["width"], 2)
        options["width"] = width
        options["height"] = height

    options["viewBox"] = f'0 0 {options["width"]} {options["height"]}'

    if classes is not None:
        options["class"] += " " + classes.strip()

    if aria_label is not None:
        options["aria-label"] = aria_label
        options["role"] = "img"
    else:
        options["aria-hidden"] = "true"

    opt_string = " ".join(f'{k}="{v}"' for k, v in options.items())
    return f"<svg {opt_string}>{content}</svg>"


class OpticonRole(SphinxRole):
    """Role to display a GitHub opticon SVG."""

    def __init__(self, size: int) -> None:
        super().__init__()
        self.size = size

    def run(self) -> Tuple[List[nodes.Node], List[nodes.system_message]]:
        """Run the role."""
        icon, classes = self.text.split(";", 1) if ";" in self.text else [self.text, ""]
        icon = icon.strip()
        try:
            svg = get_opticon(icon, size=self.size, classes=classes)
        except KeyError:
            msg = self.inliner.reporter.error(
                f"Unknown opticon name: {self.content}", line=self.lineno
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        node = nodes.raw("", nodes.Text(svg), format="html")
        self.set_source_info(node)
        return [node], []


class fontawesome(nodes.Element, nodes.General):
    """Node for rendering fontawesome icon."""


class FontawesomeRole(SphinxRole):
    """Role to display a Fontawesome icon."""

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
