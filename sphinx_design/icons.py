from collections.abc import Sequence
from functools import lru_cache
import json
import re
from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx.util.docutils import SphinxRole

from . import compiled
from ._compat import read_text
from .config import SdConfig, get_sd_config
from .shared import WARNING_TYPE, SdDirective

logger = logging.getLogger(__name__)


def setup_icons(app: Sphinx) -> None:
    app.add_role("octicon", OcticonRole())
    app.add_directive("_all-octicon", AllOcticons)
    # legacy v4/v5 class scheme (kept for backwards compatibility);
    # note: fa is deprecated in v5, fas is the default and fab is the other free option
    for style in ["fa", "fas", "fab", "far"]:
        app.add_role(style, FontawesomeRole(style))
    # v6 canonical class scheme (required by FA6+ setups without compatibility
    # aliases, e.g. Pro kits; the concise fas/fab/far roles remain supported)
    for style in ["fa-solid", "fa-brands", "fa-regular"]:
        app.add_role(style, FontawesomeRole(style))
    for style in ["regular", "outlined", "round", "sharp", "twotone"]:
        app.add_role("material-" + style, MaterialRole(style))
    app.connect("config-inited", add_fontawesome_pkg)
    app.connect("builder-inited", add_fontawesome_css)
    app.add_node(
        sd_icon,
        html=(visit_sd_icon_html, None),
        latex=(visit_sd_icon_skip, None),
        text=(visit_sd_icon_skip, None),
        man=(visit_sd_icon_skip, None),
        texinfo=(visit_sd_icon_skip, None),
    )
    app.add_node(
        fontawesome,
        html=(visit_fontawesome_html, depart_fontawesome_html),
        latex=(visit_fontawesome_latex, None),
        man=(visit_fontawesome_warning, None),
        text=(visit_fontawesome_warning, None),
        texinfo=(visit_fontawesome_warning, None),
    )


class sd_icon(nodes.inline, nodes.General):  # noqa: N801
    """Inline node for an SVG icon (octicon or material design).

    The rendered ``<svg>`` markup is carried in the ``svg`` attribute.

    The node deliberately has **no** ``Text`` children, so that ``astext()``
    returns an empty string. This keeps the SVG markup out of plain-text
    contexts derived via ``clean_astext`` (toctree labels, the search index,
    HTML page titles, ...), which would otherwise be polluted by the raw SVG
    when an icon role starts a section title.
    """


def create_icon_node(svg: str) -> sd_icon:
    """Create an inline icon node carrying the given SVG markup.

    :param svg: The rendered ``<svg>`` markup for the icon.
    :return: An :class:`sd_icon` node with no text children.
    """
    return sd_icon("", svg=svg)


def visit_sd_icon_html(self, node: nodes.Element) -> None:
    """Write the icon SVG markup directly into the HTML output."""
    self.body.append(node["svg"])
    raise nodes.SkipNode


def visit_sd_icon_skip(self, node: nodes.Element) -> None:
    """Skip the (decorative) icon for non-HTML builders."""
    raise nodes.SkipNode


@lru_cache(1)
def get_octicon_data() -> dict[str, Any]:
    """Load all octicon data."""
    content = read_text(compiled, "octicons.json")
    return json.loads(content)


def list_octicons() -> list[str]:
    """List available octicon names."""
    return list(get_octicon_data().keys())


HEIGHT_REGEX = re.compile(r"^(?P<value>\d+(\.\d+)?)(?P<unit>px|em|rem)$")


def get_octicon(
    name: str,
    height: str = "1em",
    classes: Sequence[str] = (),
    aria_label: str | None = None,
) -> str:
    """Return the HTML for an GitHub octicon SVG icon.

    :height: the height of the octicon, with suffix unit 'px', 'em' or 'rem'.
    """
    try:
        data = get_octicon_data()[name]
    except KeyError as exc:
        raise KeyError(f"Unrecognised octicon: {name}") from exc

    match = HEIGHT_REGEX.match(height)
    if not match:
        raise ValueError(
            f"Invalid height: '{height}', must be format <integer><px|em|rem>"
        )
    height_value = round(float(match.group("value")), 3)
    height_unit = match.group("unit")

    original_height = 16
    if "16" not in data["heights"]:
        original_height = int(next(iter(data["heights"].keys())))
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

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
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
        node = create_icon_node(svg)
        self.set_source_info(node)
        return [node], []


class AllOcticons(SdDirective):
    """Directive to generate all octicon icons.

    Primarily for self documentation.
    """

    option_spec = {
        "class": directives.class_option,
    }

    def run_with_defaults(self) -> list[nodes.Node]:
        classes = self.options.get("class", [])
        table = nodes.table()
        group = nodes.tgroup(cols=2)
        table += group
        group.extend(
            (
                nodes.colspec(colwidth=1),
                nodes.colspec(colwidth=1),
            )
        )
        body = nodes.tbody()
        group += body
        for icon in list_octicons():
            row = nodes.row()
            body += row
            cell = nodes.entry()
            row += cell
            cell += nodes.literal(icon, icon)
            cell = nodes.entry()
            row += cell
            cell += create_icon_node(get_octicon(icon, classes=classes))
        return [table]


class fontawesome(nodes.Element, nodes.General):  # noqa: N801
    """Node for rendering fontawesome icon."""


#: Map a fontawesome role name (also the node's leading CSS class, under the
#: default ``as-named`` scheme) to the semantic icon style. ``fa`` (v4) and
#: ``fas`` are solid, ``fab`` brands, ``far`` regular; the v6 role names are
#: explicit. Used both to translate role names between FontAwesome class
#: schemes (``sd_fontawesome_version``) and for the ``fontawesome5`` LaTeX
#: package's style conventions.
FA_ROLE_STYLES = {
    "fa": "solid",
    "fas": "solid",
    "fab": "brands",
    "far": "regular",
    "fa-solid": "solid",
    "fa-brands": "brands",
    "fa-regular": "regular",
}

#: Map a semantic icon style to the leading CSS class emitted for each
#: FontAwesome version (``sd_fontawesome_version``). v4 has no style prefixes
#: (all distinctions collapse to ``fa``), v5 uses ``fas``/``fab``/``far``,
#: v6 uses ``fa-solid``/``fa-brands``/``fa-regular``.
FA_VERSION_CLASSES = {
    "solid": {"4": "fa", "5": "fas", "6": "fa-solid"},
    "brands": {"4": "fa", "5": "fab", "6": "fa-brands"},
    "regular": {"4": "fa", "5": "far", "6": "fa-regular"},
}


class FontawesomeRole(SphinxRole):
    """Role to display a Fontawesome icon.

    Additional classes can be added to the element after a semicolon.
    """

    def __init__(self, style: str) -> None:
        super().__init__()
        self.style = style

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        icon, classes = self.text.split(";", 1) if ";" in self.text else [self.text, ""]
        icon = icon.strip()
        # the role name selects the icon style; the emitted leading class is
        # the role name itself ("as-named", backward-compatible default), or
        # its translation into the configured FontAwesome version's scheme
        version = get_sd_config(self.env).fontawesome_version
        if version == "as-named":
            leading_class = self.style
        else:
            leading_class = FA_VERSION_CLASSES[FA_ROLE_STYLES[self.style]][version]
        node = fontawesome(
            icon=icon,
            # the semantic style travels on the node, so non-HTML renderers
            # (LaTeX) stay independent of the configured HTML class scheme
            icon_style=FA_ROLE_STYLES[self.style],
            classes=[leading_class, f"fa-{icon}", *classes.split()],
        )
        self.set_source_info(node)
        return [node], []


def visit_fontawesome_html(self, node):
    self.body.append(self.starttag(node, "span", ""))


def depart_fontawesome_html(self, node):
    self.body.append("</span>")


def add_fontawesome_css(app: Sphinx) -> None:
    """Add the FontAwesome CDN CSS to HTML builds, if so configured."""
    if app.builder.format != "html":
        return
    config = get_sd_config(app.env)
    if config.fontawesome_source == "cdn":
        app.add_css_file(config.fontawesome_cdn_url)


def add_fontawesome_pkg(app, config):
    """Load the LaTeX fontawesome package matching ``sd_fontawesome_latex``."""
    mode = SdConfig.from_sphinx(config).fontawesome_latex_mode
    if mode == "fontawesome":
        app.add_latex_package("fontawesome")
    elif mode == "fontawesome5":
        app.add_latex_package("fontawesome5")


def visit_fontawesome_latex(self, node):
    """Add latex fontawesome icon, if configured, else warn."""
    mode = get_sd_config(self.builder.env).fontawesome_latex_mode
    if mode == "fontawesome5":
        # the fontawesome5 package resolves brand icons by name, and takes the
        # style as an optional argument (default solid); see its manual
        # prefer the semantic style stored on the node; fall back to deriving
        # it from the leading class (doctrees pickled before it existed)
        style = node.get("icon_style") or FA_ROLE_STYLES.get(
            node["classes"][0], "solid"
        )
        if style == "regular":
            self.body.append(f"\\faIcon[regular]{{{node['icon']}}}")
        else:
            self.body.append(f"\\faIcon{{{node['icon']}}}")
    elif mode == "fontawesome":
        self.body.append(f"\\faicon{{{node['icon']}}}")
    else:
        logger.warning(
            "Fontawesome icons not included in LaTeX output, "
            "consider 'sd_fontawesome_latex=\"fontawesome5\"' "
            f"[{WARNING_TYPE}.fa-build]",
            location=node,
            type=WARNING_TYPE,
            subtype="fa-build",
            once=True,
        )
    raise nodes.SkipNode


def visit_fontawesome_warning(self, node: nodes.Element) -> None:
    """Warn that fontawesome is not supported for this builder."""
    logger.warning(
        "Fontawesome icons not supported for builder: "
        f"{self.builder.name} [{WARNING_TYPE}.fa-build]",
        location=node,
        type=WARNING_TYPE,
        subtype="fa-build",
        once=True,
    )
    raise nodes.SkipNode


@lru_cache(1)
def get_material_icon_data(style: str) -> dict[str, Any]:
    """Load all octicon data."""
    content = read_text(compiled, f"material_{style}.json")
    return json.loads(content)


def get_material_icon(
    style: str,
    name: str,
    height: str = "1em",
    classes: Sequence[str] = (),
    aria_label: str | None = None,
) -> str:
    """Return the HTML for an Google material icon SVG icon.

    :height: the height of the material icon, with suffix unit 'px', 'em' or 'rem'.
    """
    try:
        data = get_material_icon_data(style)[name]
    except KeyError as exc:
        raise KeyError(f"Unrecognised material-{style} icon: {name}") from exc

    match = HEIGHT_REGEX.match(height)
    if not match:
        raise ValueError(
            f"Invalid height: '{height}', must be format <integer><px|em|rem>"
        )
    height_value = round(float(match.group("value")), 3)
    height_unit = match.group("unit")

    original_height = 20
    if "20" not in data["heights"]:
        original_height = int(next(iter(data["heights"].keys())))
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
        "version": "4.0.0.63c5cb3",
        "width": f"{width_value}{height_unit}",
        "height": f"{height_value}{height_unit}",
        "class": " ".join(("sd-material-icon", f"sd-material-icon-{name}", *classes)),
    }

    options["viewBox"] = f"0 0 {original_width} {original_height}"

    if aria_label is not None:
        options["aria-label"] = aria_label
        options["role"] = "img"
    else:
        options["aria-hidden"] = "true"

    opt_string = " ".join(f'{k}="{v}"' for k, v in options.items())
    return f"<svg {opt_string}>{content}</svg>"


class MaterialRole(SphinxRole):
    """Role to display a Material-* icon.

    Additional classes can be added to the element after a semicolon.
    """

    def __init__(self, style: str) -> None:
        super().__init__()
        self.style = style

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        values = self.text.split(";") if ";" in self.text else [self.text]
        icon = values[0]
        height = "1em" if len(values) < 2 else values[1]
        classes = "" if len(values) < 3 else values[2]
        icon = icon.strip()
        try:
            svg = get_material_icon(
                self.style, icon, height=height, classes=classes.split()
            )
        except Exception as exc:
            msg = self.inliner.reporter.error(
                f"Invalid material-{self.style} icon content: {type(exc)} {exc}",
                line=self.lineno,
            )
            prb = self.inliner.problematic(self.rawtext, self.rawtext, msg)
            return [prb], [msg]
        node = create_icon_node(svg)
        self.set_source_info(node)
        return [node], []
