from collections.abc import Iterator, Sequence
import re
from typing import Any

from docutils import nodes
from docutils.parsers.rst import directives
from docutils.parsers.rst import roles as rst_roles
from docutils.parsers.rst.states import Inliner
from docutils.utils import unescape
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import ws_re
from sphinx.util.docutils import ReferenceRole, SphinxRole
from sphinx.util.logging import getLogger

from sphinx_design.config import WARNING_TYPE, SdConfig
from sphinx_design.shared import SEMANTIC_COLORS, SdDirective, make_choice, text_align

LOGGER = getLogger(__name__)

ROLE_NAME_BADGE_PREFIX = "bdg"
ROLE_NAME_LINK_PREFIX = "bdg-link"
ROLE_NAME_REF_PREFIX = "bdg-ref"
DIRECTIVE_NAME_BUTTON_LINK = "button-link"
DIRECTIVE_NAME_BUTTON_REF = "button-ref"

# TODO defining arbitrary classes for badges
# (maybe split text right of last `;`, then split that by comma)
# in particular for rounded-pill class etc


#: A single built-in badge role, as ``(name, role_class, color, outline)``.
BadgeRoleSpec = tuple[str, type["_TooltipRoleMixin"], "str | None", bool]


def _iter_badge_roles() -> Iterator[BadgeRoleSpec]:
    """Yield the ``(name, role_class, color, outline)`` of every built-in badge role.

    This is the single source of truth for the badge role family, used both to
    register the roles (:func:`setup_badges_and_buttons`) and to resolve an
    ``sd_custom_roles`` ``inherit`` target (:func:`setup_custom_roles`).

    .. note::

        The custom-role ``inherit`` mechanism is deliberately limited to this
        badge family in v1. Extending it to the icon roles (``icons.py``) or the
        button *roles* would mean yielding those here too, and giving their role
        constructors the same ``tooltip`` keyword the badge roles now accept.
    """
    yield ROLE_NAME_BADGE_PREFIX, BadgeRole, None, False
    yield ROLE_NAME_LINK_PREFIX, LinkBadgeRole, None, False
    yield ROLE_NAME_REF_PREFIX, XRefBadgeRole, None, False
    for color in SEMANTIC_COLORS:
        yield "-".join((ROLE_NAME_BADGE_PREFIX, color)), BadgeRole, color, False
        yield "-".join((ROLE_NAME_BADGE_PREFIX, color, "line")), BadgeRole, color, True
        yield "-".join((ROLE_NAME_LINK_PREFIX, color)), LinkBadgeRole, color, False
        yield (
            "-".join((ROLE_NAME_LINK_PREFIX, color, "line")),
            LinkBadgeRole,
            color,
            True,
        )
        yield "-".join((ROLE_NAME_REF_PREFIX, color)), XRefBadgeRole, color, False
        yield (
            "-".join((ROLE_NAME_REF_PREFIX, color, "line")),
            XRefBadgeRole,
            color,
            True,
        )


def setup_badges_and_buttons(app: Sphinx) -> None:
    """Setup the badge components."""
    for name, role_cls, color, outline in _iter_badge_roles():
        app.add_role(name, role_cls(color, outline=outline))

    app.add_node(
        sd_badge,
        html=(visit_sd_badge_html, depart_sd_badge_html),
        latex=(_visit_sd_badge_passthrough, _depart_sd_badge_passthrough),
        text=(_visit_sd_badge_passthrough, _depart_sd_badge_passthrough),
        man=(_visit_sd_badge_passthrough, _depart_sd_badge_passthrough),
        texinfo=(_visit_sd_badge_passthrough, _depart_sd_badge_passthrough),
    )

    app.add_directive(DIRECTIVE_NAME_BUTTON_LINK, ButtonLinkDirective)
    app.add_directive(DIRECTIVE_NAME_BUTTON_REF, ButtonRefDirective)
    app.add_post_transform(ButtonRefContentStash)
    app.add_post_transform(ButtonRefContentGraft)
    app.add_post_transform(BadgeRefTooltipStash)
    app.add_post_transform(BadgeRefTooltipGraft)


#: Marker attribute set on the role instances this extension registers from
#: ``sd_custom_roles``. docutils' role registry (``roles._roles``) is
#: process-global and shared across Sphinx apps, so carrying "ownership" on the
#: stored role object itself lets every ``config-inited`` reconcile *our* roles
#: (refresh or unregister) without a side table that could drift from the
#: registry - e.g. across the many apps a test session builds.
_SD_CUSTOM_ROLE_ATTR = "_sd_custom_role"


def _role_name_taken(name: str) -> bool:
    """Return whether ``name`` already resolves to a role.

    docutils looks roles up case-insensitively, so the lower-cased name is
    compared against both the locally registered roles (``roles._roles``, the
    registry Sphinx's own ``add_role`` consults) *and* docutils' canonical
    built-in roles (``roles._role_registry``: ``code``/``math``/``strong``/
    ``emphasis``/``literal``/... ). Both are long-stable private attributes;
    docutils exposes no public query for either.
    """
    key = name.lower()
    return key in rst_roles._roles or key in rst_roles._role_registry


def setup_custom_roles(app: Sphinx, config: Config) -> None:
    """Register (and reconcile) the custom roles declared in ``sd_custom_roles``.

    Parallel to :func:`sphinx_design.shared.setup_custom_directives`: each entry
    inherits a built-in sphinx-design *badge* role (v1 scope; see
    :func:`_iter_badge_roles`), optionally baking in a default ``tooltip`` used
    whenever no per-instance ``; suffix`` overrides it.

    The entry shapes have already been validated on ``config-inited``
    (see ``sphinx_design.config``); here we additionally check ``inherit``
    against the known badge roles. Because it runs on every ``config-inited``
    against a process-global registry, the reconciliation policy is:

    * a name we registered before is **refreshed** (re-registered with override,
      picking up tooltip/inherit edits on an in-process rebuild);
    * a name we registered before but now absent from the config is
      **unregistered**, so it never leaks into a later build or sibling app;
    * a name clashing with a *foreign* role (another extension's, or a docutils
      built-in such as ``code``/``strong``) is skipped with a warning.
    """

    def _warn(msg: str) -> None:
        LOGGER.warning(f"sd_custom_roles: {msg}", type=WARNING_TYPE, subtype="config")

    specs = {
        name: (role_cls, color, outline)
        for name, role_cls, color, outline in _iter_badge_roles()
    }
    # extension point: to also inherit icon/button roles, yield them from
    # ``_iter_badge_roles`` (and give those constructors a ``tooltip`` keyword).

    # decide the roles to (re)register: a known ``inherit``, and a name that is
    # either already ours (refresh) or free (a foreign clash is skipped)
    desired: dict[str, tuple[str, dict[str, Any]]] = {}  # lower name -> (name, data)
    for name, data in SdConfig.from_sphinx(config).custom_roles.items():
        inherit = data["inherit"]
        if inherit not in specs:
            _warn(f"'{name}.inherit' is an unknown badge role: {inherit}")
            continue
        existing = rst_roles._roles.get(name.lower())
        if not getattr(existing, _SD_CUSTOM_ROLE_ATTR, False) and _role_name_taken(
            name
        ):
            _warn(f"'{name}' clashes with an existing role, skipping")
            continue
        desired[name.lower()] = (name, data)

    # unregister any of *our* previously-registered roles dropped from the config
    # (the registry is process-global, so this is what stops a stale role
    # resolving in a later in-process build or a sibling app)
    for key, role in list(rst_roles._roles.items()):
        if getattr(role, _SD_CUSTOM_ROLE_ATTR, False) and key not in desired:
            del rst_roles._roles[key]

    # (re)register, refreshing tooltip/inherit changes via ``override=True``
    for name, data in desired.values():
        role_cls, color, outline = specs[data["inherit"]]
        role = role_cls(color, outline=outline, tooltip=data.get("tooltip"))
        setattr(role, _SD_CUSTOM_ROLE_ATTR, True)
        app.add_role(name, role, override=True)


def create_bdg_classes(color: str | None, outline: bool) -> list[str]:
    """Create the badge classes."""
    classes = [
        "sd-sphinx-override",
        "sd-badge",
    ]
    if color is None:
        return classes
    if outline:
        classes.extend([f"sd-outline-{color}", f"sd-text-{color}"])
    else:
        classes.extend([f"sd-bg-{color}", f"sd-bg-text-{color}"])
    return classes


_ESCAPE_RE = re.compile(r"\\(.)", re.DOTALL)


def _resolve_escapes(text: str) -> str:
    """Resolve backslash escapes (``\\x`` -> ``x``, so ``\\;`` -> ``;``)."""
    return _ESCAPE_RE.sub(r"\1", text)


def _last_unescaped_semicolon(text: str) -> int | None:
    """Return the index of the last ``;`` not escaped by a backslash, or ``None``.

    A ``;`` counts as escaped when it is preceded by an odd number of
    backslashes (so ``\\;`` is literal, but ``\\\\;`` is an escaped backslash
    followed by an unescaped ``;``).
    """
    index = len(text)
    while (index := text.rfind(";", 0, index)) != -1:
        before = text[:index]
        backslashes = len(before) - len(before.rstrip("\\"))
        if backslashes % 2 == 0:
            return index
    return None


def split_tooltip(text: str) -> tuple[str, str | None]:
    r"""Split a badge label into its text and an optional tooltip suffix.

    This is a small, parser-portable string grammar, mirroring the
    ``name;height;classes`` grammar of the icon roles::

        main                -> (main, None)
        main ; tooltip      -> (main, tooltip)

    The tooltip is the part after the **last unescaped** semicolon (``;``).
    A literal semicolon is written ``\;`` (a backslash escapes the following
    character); these escapes are resolved in both returned parts, and both
    parts are stripped of surrounding whitespace.

    There is no tooltip when the text contains no unescaped ``;``, or when the
    tooltip part is empty (e.g. a trailing ``;``); in that case the whole
    (escape-resolved, stripped) text is returned as ``main``.

    Note: the link/ref badge roles constrain this grammar further, accepting a
    tooltip suffix only after a complete explicit ``title <target>`` form,
    because ``;`` is a legal character in URLs and reference targets (see
    :class:`_TooltipRoleMixin`).

    :param text: the raw label text (using ``\;`` for a literal ``;``).
    :return: a ``(main, tooltip)`` tuple; ``tooltip`` is ``None`` when no
        non-empty tooltip suffix is present.
    """
    index = _last_unescaped_semicolon(text)
    if index is None:
        return _resolve_escapes(text.strip()), None
    tooltip = _resolve_escapes(text[index + 1 :].strip())
    if not tooltip:
        # a trailing (empty) tooltip is treated as no tooltip at all, leaving
        # the text - including that final ``;`` - as the label
        return _resolve_escapes(text.strip()), None
    return _resolve_escapes(text[:index].strip()), tooltip


class sd_badge(nodes.inline, nodes.General):  # noqa: N801
    """Inline node for a badge.

    Identical to a plain :class:`docutils.nodes.inline` (a ``<span>`` in HTML),
    except that when its ``tooltip`` attribute is set the HTML visitor emits a
    ``title`` attribute for a native tooltip.
    """


def visit_sd_badge_html(self: Any, node: nodes.Element) -> None:
    """Open the badge ``<span>``, adding a ``title`` when a tooltip is set."""
    if node.get("tooltip"):
        # ``starttag`` HTML-escapes attribute values (via ``attval``)
        self.body.append(self.starttag(node, "span", "", title=node["tooltip"]))
    else:
        # byte-identical to the default ``visit_inline`` for a badge: the badge
        # classes never match ``supported_inline_tags``, so ``inline`` also just
        # emits ``self.starttag(node, "span", "")``
        self.body.append(self.starttag(node, "span", ""))


def depart_sd_badge_html(self: Any, node: nodes.Element) -> None:
    """Close the badge ``<span>``."""
    self.body.append("</span>")


def _visit_sd_badge_passthrough(self: Any, node: nodes.Element) -> None:
    """Render badge children verbatim for non-HTML builders (no wrapper)."""


def _depart_sd_badge_passthrough(self: Any, node: nodes.Element) -> None:
    """Counterpart to :func:`_visit_sd_badge_passthrough`."""


_EXPLICIT_TARGET_RE = re.compile(r"^(.+?)\s*(?<!\\)<(.*?)>$", re.DOTALL)
"""The explicit ``title <target>`` reference form: docutils'/sphinx's
``explicit_title_re``, with backslash- (rather than NUL-) escape semantics,
for matching against backslash-restored role text."""

_RAW_ESCAPED_SEMICOLON_RE = re.compile(r"(?<!\x00)\\;")
"""A raw ``\\;`` escape sequence, as passed by MyST (which forwards role
content verbatim, without docutils' NUL-encoding of backslash escapes).
This never matches reStructuredText role text: there an escaped ``;``
arrives as ``\\x00;`` (no raw backslash), and a literal backslash is itself
NUL-prefixed (``\\x00\\``), which the lookbehind excludes."""


class _TooltipRoleMixin(SphinxRole):
    r"""Mixin that peels an optional ``; tooltip`` suffix off a role's text.

    The suffix uses the :func:`split_tooltip` grammar: the tooltip follows the
    last unescaped ``;`` (``\;`` is a literal ``;``). For roles with reference
    semantics (:attr:`tooltip_requires_explicit_target`), a ``;`` is only
    treated as a tooltip separator when the text before it is a complete
    explicit ``title <target>`` form - i.e. the ``;`` follows the closing
    ``>`` - because ``;`` is a legal character in URLs and reference targets;
    the bare form (where the whole text is the target) is never split.

    The parsed tooltip (or ``None``) is stored on :attr:`tooltip`, and the
    remaining text - with the suffix removed - is forwarded to the base role,
    so that ``ReferenceRole``'s title/target parsing still applies to it.

    The badge roles share this constructor (``color``/``outline``, plus an
    optional baked ``tooltip``), so that they - and any config-defined roles
    inheriting them (see :func:`setup_custom_roles`) - are built uniformly.
    """

    #: the tooltip parsed from the current role invocation, if any
    tooltip: str | None = None

    #: when true, only accept a tooltip suffix after an explicit
    #: ``title <target>`` form (set by the link/ref badge roles, whose bare
    #: form is a target in which ``;`` is a legal character)
    tooltip_requires_explicit_target: bool = False

    def __init__(
        self,
        color: str | None = None,
        *,
        outline: bool = False,
        tooltip: str | None = None,
    ) -> None:
        """Construct a badge role.

        :param color: the semantic colour, or ``None`` for the plain badge.
        :param outline: whether to use the outline (``-line``) variant.
        :param tooltip: a baked-in default tooltip, used when no per-instance
            ``; suffix`` overrides it (set by config-defined roles). An explicit
            suffix always wins. ``None`` for the built-in roles, keeping their
            output byte-identical.
        """
        super().__init__()
        self.color = color
        self.outline = outline
        #: the baked default tooltip (see the ``tooltip`` parameter)
        self.default_tooltip = tooltip

    def __call__(  # noqa: PLR0913
        self,
        name: str,
        rawtext: str,
        text: str,
        lineno: int,
        inliner: Inliner,
        options: dict[str, Any] | None = None,
        content: Sequence[str] = (),
    ) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Split off any tooltip, then defer to the base role."""
        # ``text`` differs by parser: docutils (rST) encodes a backslash escape
        # as a NUL marker (``\x00``) + the escaped char, while myst-parser
        # passes backslashes through verbatim. Restoring NULs to backslashes -
        # a 1:1, index-preserving replacement - yields the documented ``\;``
        # grammar form for both parsers.
        self.tooltip = None
        grammar = unescape(text, restore_backslashes=True)
        index = _last_unescaped_semicolon(grammar)
        while index is not None:
            if not self.tooltip_requires_explicit_target or _EXPLICIT_TARGET_RE.match(
                grammar[:index].rstrip()
            ):
                break
            # the ``;`` is part of a (bare or explicit) reference target,
            # where it is a legal character: try any earlier candidate
            index = _last_unescaped_semicolon(grammar[:index])
        if index is not None:
            tooltip = _resolve_escapes(grammar[index + 1 :].strip())
            if tooltip:
                self.tooltip = tooltip
                # slice the *original* text, so rST keeps its NUL-escaped form
                # and the base role unescapes / parses it exactly as usual
                text = text[:index].strip()
        # resolve raw (MyST-style) ``\;`` escapes in the forwarded text; a
        # no-op for rST, whose escapes are NUL-encoded and resolved downstream
        text = _RAW_ESCAPED_SEMICOLON_RE.sub(";", text)
        if self.tooltip is None:
            # no per-instance suffix: fall back to any baked default (``None``
            # for the built-in roles). A suffix, when present, always wins.
            self.tooltip = self.default_tooltip
        return super().__call__(name, rawtext, text, lineno, inliner, options, content)


class BadgeRole(_TooltipRoleMixin):
    """Role to display a badge."""

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        node = sd_badge(
            self.rawtext,
            self.text,
            classes=create_bdg_classes(self.color, self.outline),
        )
        if self.tooltip:
            node["tooltip"] = self.tooltip
        self.set_source_info(node)
        return [node], []


class LinkBadgeRole(_TooltipRoleMixin, ReferenceRole):
    """Role to display a badge with an external link."""

    # ``;`` is legal in URLs: tooltips only after ``text <target>``
    tooltip_requires_explicit_target = True

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        node = nodes.reference(
            self.rawtext,
            refuri=self.target,
            classes=create_bdg_classes(self.color, self.outline),
        )
        # TODO open in new tab
        self.set_source_info(node)
        if self.tooltip:
            # a reference renders ``reftitle`` as a native ``title`` attribute
            node["reftitle"] = self.tooltip
        node += nodes.inline(self.title, self.title)
        return [node], []


class XRefBadgeRole(_TooltipRoleMixin, ReferenceRole):
    """Role to display a badge with an internal link."""

    # ``;`` is legal in reference targets: tooltips only after ``text <target>``
    tooltip_requires_explicit_target = True

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Run the role."""
        options = {
            "classes": create_bdg_classes(self.color, self.outline),
            "reftarget": self.target,
            "refdoc": self.env.docname,
            "refdomain": "",
            "reftype": "any",
            "refexplicit": self.has_explicit_title,
            "refwarn": True,
        }
        node = addnodes.pending_xref(self.rawtext, **options)
        if self.tooltip:
            # ``reftitle`` cannot be set here: cross-reference resolution builds
            # a fresh reference and only copies "basic" attributes (ids/classes/
            # names) onto it, so an arbitrary attribute would be lost. Carry the
            # tooltip via a transient attribute that :class:`BadgeRefTooltipStash`
            # converts (before resolution) into the #281 marker-class mechanism.
            node["sd_tooltip"] = self.tooltip
        self.set_source_info(node)
        node += nodes.inline(self.title, self.title, classes=["xref", "any"])
        return [node], []


class _ButtonDirective(SdDirective):
    """A base button directive."""

    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    has_content = True
    option_spec = {
        "color": make_choice(SEMANTIC_COLORS),
        "outline": directives.flag,
        "align": text_align,
        # expand to fit parent width
        "expand": directives.flag,
        # make parent also clickable
        "click-parent": directives.flag,
        "tooltip": directives.unchanged_required,
        "shadow": directives.flag,
        # ref button only
        "ref-type": make_choice(["any", "ref", "doc", "myst"]),
        "class": directives.class_option,
    }

    @staticmethod
    def get_target(argument: str) -> str:
        """Normalise the directive argument into a reference target."""
        raise NotImplementedError

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        raise NotImplementedError

    def run_with_defaults(self) -> list[nodes.Node]:
        rawtext = self.arguments[0]
        target = self.get_target(rawtext)
        classes = ["sd-sphinx-override", "sd-btn", "sd-text-wrap"]
        if "color" in self.options:
            if "outline" in self.options:
                classes.append(f"sd-btn-outline-{self.options['color']}")
            else:
                classes.append(f"sd-btn-{self.options['color']}")
        if "click-parent" in self.options:
            classes.append("sd-stretched-link")
        if "shadow" in self.options:
            classes.append("sd-shadow-sm")
        if "class" in self.options:
            classes.extend(self.options["class"])
        node = self.create_ref_node(rawtext, target, bool(self.content), classes)
        # TODO open in new tab
        self.set_source_info(node)
        if "tooltip" in self.options:
            # ``reftitle`` is rendered as the HTML ``title`` attribute, whose
            # value the writer HTML-escapes (via ``starttag``/``attval``)
            node["reftitle"] = self.options["tooltip"]

        if self.content:
            textnodes, _ = self.state.inline_text(
                "\n".join(self.content), self.lineno + self.content_offset
            )
            # make link text translatable -
            # target gettext to the content lines, not the outer directive
            translatable = nodes.inline("", "", *textnodes, translatable=True)
            self.set_source_info(translatable)
            translatable.line += self.content_offset
            # the translatable inline is a placeholder that sphinx unwraps
            # after translation (RemoveTranslatableInline); keep a plain outer
            # inline so the reference always retains an element child
            # (an unresolved xref otherwise crashes on replacement)
            content = nodes.inline("", "", translatable)
        else:
            content = nodes.inline(target, target)
        node.append(content)

        if "expand" in self.options:
            grid_container = nodes.inline(classes=["sd-d-grid"])
            self.set_source_info(grid_container)
            grid_container += node
            node = grid_container

        # `visit_reference` requires that a reference be inside a `TextElement` parent
        container = nodes.paragraph(
            classes=self.options.get("align", []), translatable=False
        )
        self.set_source_info(container)
        container += node

        return [container]


class ButtonLinkDirective(_ButtonDirective):
    """A button directive with an external link."""

    @staticmethod
    def get_target(argument: str) -> str:
        """Return the URI, with all whitespace removed (as for a normal link)."""
        return directives.uri(argument)

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        return nodes.reference(
            rawtext,
            refuri=target,
            classes=classes,
        )


class ButtonRefDirective(_ButtonDirective):
    """A button directive with an internal link."""

    @staticmethod
    def get_target(argument: str) -> str:
        """Return the reference target, collapsing internal whitespace.

        This mirrors :class:`~sphinx.roles.XRefRole`'s whitespace
        normalisation, so that multi-word labels (e.g. those generated by
        ``sphinx.ext.autosectionlabel`` from section titles) are preserved and
        resolve correctly, rather than being stripped of all whitespace.
        """
        return ws_re.sub(" ", argument).strip()

    def create_ref_node(
        self, rawtext: str, target: str, explicit_title: bool, classes: list[str]
    ) -> nodes.Node:
        """Create the reference node."""
        ref_type = self.options.get("ref-type", "any")
        if ref_type == "ref":
            # match sphinx's :ref: role, which is ``XRefRole(lowercase=True)``:
            # std-domain labels are stored lowercased, so lowercase the target
            # too. ``doc``/``myst`` targets are case-sensitive, and the ``any``
            # resolver lowercases internally where needed
            target = target.lower()
        options = {
            "classes": classes,
            "reftarget": target,
            "refdoc": self.env.docname,
            "refdomain": "std" if ref_type in {"ref", "doc"} else "",
            "reftype": ref_type,
            "refexplicit": explicit_title,
            "refwarn": True,
        }
        return addnodes.pending_xref(rawtext, **options)


_BUTTON_REF_STASH_ATTR = "sd_button_ref_content"
"""Name of the (transient) python attribute on the ``document`` object,
mapping marker class names to stashed ``button-ref`` content nodes."""

_BUTTON_REF_MARKER_PREFIX = "sd-button-ref-content-"
"""Prefix of the transient marker classes used to correlate a ``button-ref``
``pending_xref`` with its resolved node; never present in final output."""


class ButtonRefContentStash(SphinxPostTransform):
    """Stash the rich content of each ``button-ref`` cross-reference.

    Sphinx's standard-domain resolvers rebuild an explicit-title ``ref``/``doc``
    cross-reference from ``node.astext()``, which flattens any nested inline
    markup (emphasis, icons, ...) down to plain text (see issue #228). Since
    ``button-ref`` allows arbitrary parsed content, we stash a copy of that
    content before any resolver runs, tagging the ``pending_xref`` with a
    unique marker class. Whatever node the xref is replaced with inherits the
    marker (docutils ``replace_self`` copies ids/classes onto the
    replacement), letting :class:`ButtonRefContentGraft` restore the content
    afterwards, without relying on any non-public resolver API.
    """

    # must run before every cross-reference resolver: the built-in
    # ``ReferencesResolver`` runs at priority 10, and myst-parser's resolver
    # (which handles ``ref-type: myst`` buttons) at priority 9
    default_priority = 8

    def run(self, **kwargs: Any) -> None:
        """Tag and stash every ``button-ref`` pending cross-reference."""
        stash: dict[str, nodes.Element] = {}
        for index, node in enumerate(self.document.findall(addnodes.pending_xref)):
            if "sd-btn" not in node.get("classes", ()):
                continue
            if not node.get("refexplicit"):
                # the directive had no content: the resolver-generated text
                # (e.g. the target's section title) is the desired button text
                continue
            if next(iter(node[0].findall(addnodes.pending_xref)), None) is not None:
                # the button content itself contains a cross-reference: a
                # stashed copy would re-insert an unresolved ``pending_xref``
                # after every resolver has run, crashing the writer. Fall back
                # to the pre-existing behaviour (the std domain flattens the
                # content to plain text) - a link nested inside a button link
                # would be invalid HTML anyway
                continue
            marker = f"{_BUTTON_REF_MARKER_PREFIX}{index}"
            node["classes"].append(marker)
            stash[marker] = node[0].deepcopy()
        # a plain (transient) python attribute: unlike a node attribute it can
        # never leak into pickled doctrees or (XML) serialisations
        setattr(self.document, _BUTTON_REF_STASH_ATTR, stash)


class ButtonRefContentGraft(SphinxPostTransform):
    """Restore stashed ``button-ref`` content onto resolved references.

    Counterpart to :class:`ButtonRefContentStash`: locate the node that
    inherited each marker class from its ``pending_xref``, strip the marker,
    and, for resolved references, replace the (possibly text-flattened)
    resolver-built content with the stashed rich content, so that
    ``button-ref`` renders its content identically to ``button-link``.
    """

    # run just after the built-in ``ReferencesResolver`` (priority 10)
    default_priority = 11

    def run(self, **kwargs: Any) -> None:
        """Graft stashed content onto each marked node."""
        stash: dict[str, nodes.Element] = getattr(
            self.document, _BUTTON_REF_STASH_ATTR, {}
        )
        if not stash:
            return
        for element in list(self.document.findall(nodes.Element)):
            classes = element.get("classes", [])
            for marker in [cls for cls in classes if cls in stash]:
                classes.remove(marker)
                if isinstance(element, nodes.reference):
                    # a resolver replaced the xref with a reference, possibly
                    # rebuilding its content from plain text (the std domain
                    # does, for explicit-title ref/doc targets): restore the
                    # stashed rich content (a no-op in effect for resolvers
                    # that already preserved the original content node)
                    element.children = []
                    element.append(stash[marker].deepcopy())
                # otherwise the xref was unresolved, and the built-in resolver
                # substituted the original (still rich) content node itself,
                # which inherited the marker: stripping the marker is enough.
                # If an (external) resolver produced a node that did not
                # inherit the marker at all, nothing is found here and the
                # graft is a no-op: such resolvers build on the passed
                # contnode, which was never flattened by the std domain.
        setattr(self.document, _BUTTON_REF_STASH_ATTR, {})


_BADGE_REF_TOOLTIP_STASH_ATTR = "sd_badge_ref_tooltip"
"""Name of the (transient) python attribute on the ``document`` object,
mapping marker class names to stashed ``bdg-ref`` tooltip strings."""

_BADGE_REF_TOOLTIP_MARKER_PREFIX = "sd-badge-ref-tooltip-"
"""Prefix of the transient marker classes used to correlate a ``bdg-ref``
``pending_xref`` with its resolved reference; never present in final output."""


class BadgeRefTooltipStash(SphinxPostTransform):
    """Stash each ``bdg-ref`` tooltip before cross-reference resolution.

    An arbitrary node attribute (such as the ``sd_tooltip`` set by
    :class:`XRefBadgeRole`) does not survive cross-reference resolution: the
    resolver builds a fresh reference and docutils' ``update_basic_atts`` only
    copies the "basic" attributes (ids/classes/names). Mirroring the #281
    machinery, we therefore move the tooltip into a document-level stash keyed
    by a unique marker *class* appended to the ``pending_xref`` - classes
    *are* copied onto the resolved node - and drop the transient attribute so
    nothing leaks into the (pre-resolution) doctree.
    """

    # must run before every cross-reference resolver (built-in
    # ``ReferencesResolver`` is priority 10; myst-parser's is priority 9)
    default_priority = 5

    def run(self, **kwargs: Any) -> None:
        """Tag and stash every ``bdg-ref`` tooltip."""
        stash: dict[str, str] = {}
        for index, node in enumerate(self.document.findall(addnodes.pending_xref)):
            if "sd_tooltip" not in node:
                continue
            marker = f"{_BADGE_REF_TOOLTIP_MARKER_PREFIX}{index}"
            node["classes"].append(marker)
            stash[marker] = node["sd_tooltip"]
            # the attribute has served its purpose; remove it so it can never
            # leak into a pickled doctree or (XML) serialisation
            del node["sd_tooltip"]
        # a plain (transient) python attribute, as for #281
        setattr(self.document, _BADGE_REF_TOOLTIP_STASH_ATTR, stash)


class BadgeRefTooltipGraft(SphinxPostTransform):
    """Apply stashed ``bdg-ref`` tooltips as ``reftitle`` after resolution.

    Counterpart to :class:`BadgeRefTooltipStash`: find the node that inherited
    each marker class from its ``pending_xref``, strip the marker, and, for a
    resolved reference, set ``reftitle`` (rendered as the HTML ``title``) to the
    stashed tooltip. A ``bdg-ref`` without a tooltip has no stash entry, so an
    auto-generated ``reftitle`` (e.g. a section title) is left untouched.
    """

    # run after the built-in ``ReferencesResolver`` (priority 10) and the #281
    # graft (priority 11); ordering relative to the latter is immaterial (they
    # act on disjoint marker sets and attributes), but running after resolution
    # is essential, so the marker has reached the resolved reference
    default_priority = 12

    def run(self, **kwargs: Any) -> None:
        """Move each stashed tooltip onto its resolved reference."""
        stash: dict[str, str] = getattr(
            self.document, _BADGE_REF_TOOLTIP_STASH_ATTR, {}
        )
        if not stash:
            return
        for element in list(self.document.findall(nodes.Element)):
            classes = element.get("classes", [])
            for marker in [cls for cls in classes if cls in stash]:
                classes.remove(marker)
                if isinstance(element, nodes.reference):
                    # the tooltip overrides any auto-generated reftitle
                    element["reftitle"] = stash[marker]
                # an unresolved xref leaves the (non-reference) content node
                # carrying the marker: stripping it is enough (no link, so no
                # tooltip target)
        setattr(self.document, _BADGE_REF_TOOLTIP_STASH_ATTR, {})
