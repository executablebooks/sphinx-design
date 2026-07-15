"""Central declarative configuration for sphinx-design.

All global configuration is declared on the :class:`SdConfig` dataclass:
every option is declared once, with its type, default, validator and help text.

Every value is plain, TOML-compatible, data
(``str``/``bool``/``int``/``list``/``dict`` of primitives),
so that the configuration could also be read from a TOML file,
or be understood by non-Python implementations.

The values are registered with Sphinx as flat, ``sd_`` prefixed,
configuration values (e.g. ``fontawesome_latex`` -> ``sd_fontawesome_latex``),
which remain the public interface.
Modules should read the validated configuration via :func:`get_sd_config`,
rather than accessing ``config.sd_*`` attributes directly.

The field validators mirror the approach of
https://github.com/python-attrs/attrs validators:
they take ``(inst, field, value)`` and raise on invalid values.
"""

from __future__ import annotations

import dataclasses as dc
from typing import TYPE_CHECKING, Any, Protocol

from sphinx.util.logging import getLogger

if TYPE_CHECKING:
    from collections.abc import Sequence

    from sphinx.application import Sphinx
    from sphinx.config import Config
    from sphinx.environment import BuildEnvironment

LOGGER = getLogger(__name__)

WARNING_TYPE = "design"
"""Type of warnings emitted by sphinx-design (i.e. ``design.<subtype>``)."""


class ValidatorType(Protocol):
    """Protocol for a dataclass field validator."""

    def __call__(
        self, inst: Any, field: dc.Field[Any], value: Any, suffix: str = ""
    ) -> None:
        """Validate the value of a dataclass field, raising if invalid.

        :param inst: The dataclass instance (or None if not yet created).
        :param field: The dataclass field.
        :param value: The value to validate.
        :param suffix: Suffix to append to the field name in error messages.
        :raises TypeError | ValueError: If the value is invalid.
        """


def validate_field(inst: Any, field: dc.Field[Any], value: Any) -> None:
    """Validate the field of a dataclass,
    according to a ``validator`` function set in the field metadata.

    :param inst: The dataclass instance (or None if not yet created).
    :param field: The dataclass field.
    :param value: The value to validate.
    :raises TypeError | ValueError: If the value is invalid.
    """
    if "validator" in field.metadata:
        field.metadata["validator"](inst, field, value)


def validate_fields(inst: Any) -> None:
    """Validate the fields of a dataclass instance,
    according to ``validator`` functions set in the field metadata.

    This function should be called in the ``__post_init__`` of the dataclass.

    :param inst: The dataclass instance.
    :raises TypeError | ValueError: If any value is invalid.
    """
    for field in dc.fields(inst):
        validate_field(inst, field, getattr(inst, field.name))


def instance_of(type_: type[Any] | tuple[type[Any], ...]) -> ValidatorType:
    """Create a validator that raises a ``TypeError``
    if the value is not an instance of the given type(s).

    :param type_: The type(s) to check for.
    """

    def _validator(
        inst: Any, field: dc.Field[Any], value: Any, suffix: str = ""
    ) -> None:
        if not isinstance(value, type_):
            raise TypeError(
                f"'{field.name}{suffix}' must be of type {type_!r} "
                f"(got {value!r} that is a {value.__class__!r})."
            )

    return _validator


def one_of(allowed: Sequence[Any]) -> ValidatorType:
    """Create a validator that raises a ``ValueError``
    if the value is not one of the allowed values.

    :param allowed: The allowed values.
    """
    allowed = tuple(allowed)

    def _validator(
        inst: Any, field: dc.Field[Any], value: Any, suffix: str = ""
    ) -> None:
        if value not in allowed:
            raise ValueError(
                f"'{field.name}{suffix}' must be one of {allowed!r} (got {value!r})."
            )

    return _validator


FONTAWESOME_LATEX_MODES = ("none", "fontawesome", "fontawesome5")
"""Allowed string values for the ``fontawesome_latex`` configuration."""


def validate_fontawesome_latex(
    inst: Any, field: dc.Field[Any], value: Any, suffix: str = ""
) -> None:
    """Validate the ``fontawesome_latex`` value.

    Accepts a ``bool`` (``True``/``False`` are kept for backwards
    compatibility, and normalized by :attr:`SdConfig.fontawesome_latex_mode`),
    or one of :data:`FONTAWESOME_LATEX_MODES`.

    :param inst: The dataclass instance (or None if not yet created).
    :param field: The dataclass field.
    :param value: The value to validate.
    :param suffix: Suffix to append to the field name in error messages.
    :raises TypeError | ValueError: If the value is invalid.
    """
    if isinstance(value, bool):
        return
    if not isinstance(value, str):
        raise TypeError(
            f"'{field.name}{suffix}' must be a bool or str "
            f"(got {value!r} that is a {value.__class__!r})."
        )
    if value not in FONTAWESOME_LATEX_MODES:
        raise ValueError(
            f"'{field.name}{suffix}' must be a bool or one of "
            f"{FONTAWESOME_LATEX_MODES!r} (got {value!r})."
        )


def validate_custom_directive(field: dc.Field[Any], name: Any, data: Any) -> None:
    """Validate the shape of a single custom directive (name -> data) entry.

    Note, whether ``data["inherit"]`` refers to a known sphinx-design directive,
    and whether the option names are known for that directive,
    can only be checked at registration time
    (see ``sphinx_design.shared.setup_custom_directives``).

    :param field: The dataclass field the entry belongs to.
    :param name: The name of the new directive.
    :param data: The directive data, expected shape
        ``{inherit: str, argument: str, options: {str: str}}``.
    :raises TypeError | ValueError: If the entry is invalid.
    """
    if not isinstance(name, str):
        raise TypeError(f"key must be a string: {name!r}")
    if not isinstance(data, dict):
        raise TypeError(f"{name!r} value must be a dictionary")
    if "inherit" not in data:
        raise ValueError(f"{name!r} value must have an 'inherit' key")
    if not isinstance(data["inherit"], str):
        raise TypeError(f"'{name}.inherit' value must be a string")
    if "argument" in data and not isinstance(data["argument"], str):
        raise TypeError(f"'{name}.argument' value must be a string")
    if "options" in data:
        if not isinstance(data["options"], dict):
            raise TypeError(f"'{name}.options' value must be a dictionary")
        for key, value in data["options"].items():
            if not isinstance(key, str):
                raise TypeError(f"'{name}.options' key must be a string: {key!r}")
            if not isinstance(value, str):
                raise TypeError(f"'{name}.options.{key}' value must be a string")


def validate_custom_directives(
    inst: Any, field: dc.Field[Any], value: Any, suffix: str = ""
) -> None:
    """Validate the custom directives mapping, raising on the first invalid entry.

    :param inst: The dataclass instance (or None if not yet created).
    :param field: The dataclass field.
    :param value: The value to validate.
    :param suffix: Suffix to append to the field name in error messages.
    :raises TypeError | ValueError: If the value is invalid.
    """
    if not isinstance(value, dict):
        raise TypeError(f"'{field.name}{suffix}' must be a dictionary (got {value!r})")
    for name, data in value.items():
        validate_custom_directive(field, name, data)


@dc.dataclass
class SdConfig:
    """Global configuration for sphinx-design (all values TOML-compatible).

    In the sphinx configuration, these option names are prepended with ``sd_``.
    """

    custom_directives: dict[str, Any] = dc.field(
        default_factory=dict,
        metadata={
            "validator": validate_custom_directives,
            "entry_validator": validate_custom_directive,
            "help": "Custom directives, inheriting from sphinx-design ones",
            "doc_type": "dict[str, dict]",
        },
    )
    fontawesome_source: str = dc.field(
        default="none",
        metadata={
            "validator": one_of(("none", "cdn")),
            "help": "How sphinx-design loads the FontAwesome CSS: "
            '"none" (default, provided by you/your theme) or "cdn"',
        },
    )
    fontawesome_cdn_url: str = dc.field(
        default="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css",
        metadata={
            "validator": instance_of(str),
            "help": 'FontAwesome CSS URL to add when sd_fontawesome_source="cdn"',
        },
    )
    fontawesome_version: str = dc.field(
        default="as-named",
        metadata={
            "validator": one_of(("as-named", "4", "5", "6")),
            "help": "FontAwesome class scheme emitted by the icon roles: "
            '"as-named" (default, role name emitted verbatim), "4", "5" or "6"',
        },
    )
    fontawesome_latex: bool | str = dc.field(
        default=False,
        metadata={
            "validator": validate_fontawesome_latex,
            "types": (bool, str),
            "help": "Render fontawesome icons in LaTeX output: "
            'False/"none", True/"fontawesome", or "fontawesome5"',
            "doc_type": "bool | str",
        },
    )
    tabs_storage_prefix: str = dc.field(
        default="sphinx-design-tab-id-",
        metadata={
            "validator": instance_of(str),
            "help": (
                "localStorage key prefix for persisting synced tab selections "
                "(an empty string disables persistence)"
            ),
        },
    )

    def __post_init__(self) -> None:
        validate_fields(self)

    @property
    def fontawesome_latex_mode(self) -> str:
        """The normalized LaTeX fontawesome mode.

        Maps the backwards-compatible boolean values to their string
        equivalents (``True`` -> ``"fontawesome"``, ``False`` -> ``"none"``),
        so downstream code only has to handle :data:`FONTAWESOME_LATEX_MODES`.

        :return: One of :data:`FONTAWESOME_LATEX_MODES`.
        """
        value = self.fontawesome_latex
        if value is True:
            return "fontawesome"
        if value is False:
            return "none"
        return value

    @classmethod
    def from_sphinx(cls, config: Config) -> SdConfig:
        """Create a validated instance from the flat ``sd_`` prefixed
        Sphinx configuration values.

        Note, the values are expected to have already been sanitized by
        the ``config-inited`` event (which replaces invalid values with defaults),
        otherwise this may raise.

        :param config: The Sphinx configuration.
        :raises TypeError | ValueError: If any value is invalid.
        """
        return cls(**{f.name: getattr(config, f"sd_{f.name}") for f in dc.fields(cls)})


def _field_default(field: dc.Field[Any]) -> Any:
    """Return the default value for a dataclass field."""
    if field.default_factory is not dc.MISSING:
        return field.default_factory()
    return field.default


def setup_sd_config(app: Sphinx) -> None:
    """Set up the sphinx-design configuration handling.

    Each field of :class:`SdConfig` is registered as a flat ``sd_<name>``
    Sphinx configuration value (the public, backwards-compatible, interface).

    :param app: The Sphinx application object.
    """
    for field in dc.fields(SdConfig):
        app.add_config_value(
            f"sd_{field.name}",
            _field_default(field),
            "env",
            types=field.metadata.get("types", ()),
        )
    # low priority, so that the values are validated
    # before any other `config-inited` listener reads them
    app.connect("config-inited", _validate_config_values, priority=400)
    app.connect("builder-inited", _attach_env_config)


def get_sd_config(env: BuildEnvironment) -> SdConfig:
    """Get the validated sphinx-design configuration for a build environment.

    :param env: The Sphinx build environment.
    """
    try:
        return env.sd_config  # type: ignore[attr-defined]
    except AttributeError:
        sd_config = SdConfig.from_sphinx(env.config)
        env.sd_config = sd_config  # type: ignore[attr-defined]
        return sd_config


def _validate_config_values(app: Sphinx, config: Config) -> None:
    """Validate the flat ``sd_`` prefixed configuration values
    (on the ``config-inited`` event).

    Invalid values are replaced by the field default, with a warning,
    so that :class:`SdConfig` instances can subsequently always be created.
    For mapping fields with an ``entry_validator``,
    only the invalid entries are discarded.
    """

    def _warn(msg: str) -> None:
        LOGGER.warning(msg, type=WARNING_TYPE, subtype="config")

    for field in dc.fields(SdConfig):
        name = f"sd_{field.name}"
        value = getattr(config, name)
        if entry_validator := field.metadata.get("entry_validator"):
            # validate mapping values per entry, discarding invalid entries,
            # so that one invalid entry does not invalidate the whole mapping
            if not isinstance(value, dict):
                _warn(f"{name}: must be a dictionary")
                value = _field_default(field)
            else:
                valid = {}
                for key, entry in value.items():
                    try:
                        entry_validator(field, key, entry)
                    except (TypeError, ValueError) as exc:
                        _warn(f"{name}: {exc}")
                    else:
                        valid[key] = entry
                value = valid
        else:
            try:
                validate_field(None, field, value)
            except (TypeError, ValueError) as exc:
                value = _field_default(field)
                _warn(f"{name}: {exc} Reverting to default: {value!r}")
        setattr(config, name, value)


def _attach_env_config(app: Sphinx) -> None:
    """Attach the validated configuration to the build environment
    (on the ``builder-inited`` event).

    This is re-created on every build,
    so that changes to the configuration are always picked up.
    """
    app.env.sd_config = SdConfig.from_sphinx(app.config)  # type: ignore[attr-defined]
