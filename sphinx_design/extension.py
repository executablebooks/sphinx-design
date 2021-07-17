import hashlib
from pathlib import Path

try:
    import importlib.resources as resources
except ImportError:
    # python < 3.7
    import importlib_resources as resources  # type: ignore[no-redef]

from docutils import nodes
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from . import compiled as css_module
from .badges import setup_badges
from .cards import setup_cards
from .grids import setup_grids


def setup_extension(app: Sphinx):
    """Set up the sphinx extension."""
    app.connect("builder-inited", update_css)
    app.connect("env-updated", update_css_links)
    # we override container html visitors, to stop the default behaviour
    # of adding the `container` class to all nodes.container
    app.add_node(
        nodes.container, override=True, html=(visit_container, depart_container)
    )
    setup_badges(app)
    setup_cards(app)
    setup_grids(app)


def update_css(app: Sphinx):
    """Copy the CSS to the build directory."""
    # reset changed identifier
    app.env.sphinx_design_css_changed = False
    # setup up new static path in output dir
    static_path = (Path(app.outdir) / "_sphinx_design_static").absolute()
    static_existed = static_path.exists()
    static_path.mkdir(exist_ok=True)
    app.config.html_static_path.append(str(static_path))
    # Read the css content and hash it
    content = resources.read_text(css_module, "style.min.css")
    hash = hashlib.md5(content.encode("utf8")).hexdigest()
    # Write the css file
    css_path = static_path / f"design-style.{hash}.min.css"
    app.add_css_file(css_path.name)
    if css_path.exists():
        return
    if static_existed:
        app.env.sphinx_design_css_changed = True
    for path in static_path.glob("*.css"):
        path.unlink()
    css_path.write_text(content, encoding="utf8")


def update_css_links(app: Sphinx, env: BuildEnvironment):
    """If CSS has changed, all files must be re-written, to include the correct stylesheets."""
    if env.sphinx_design_css_changed:
        return list(env.all_docs.keys())


def visit_container(self, node: nodes.Node):
    classes = "docutils container"
    if node.get("is_div", False):
        # we don't want the CSS for container for these nodes
        classes = "docutils"
    self.body.append(self.starttag(node, "div", CLASS=classes))


def depart_container(self, node: nodes.Node):
    self.body.append("</div>\n")
