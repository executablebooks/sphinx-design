# Brief 02: Central declarative configuration (`SdConfig` dataclass)

**Type**: refactor (foundation for other briefs) | **Size**: medium
**Principle**: every config value must be TOML-representable data.

## Goal

Consolidate all `sd_*` configuration into a single typed dataclass, modelled
on myst-parser's `MdParserConfig` (`myst_parser/config/main.py`) and its
`dc_validators.py` pattern, so that:

1. Every option is declared once, with type, default, validator, and help
   text (field metadata) — enabling an auto-generated config docs table.
2. All values are plain data (str/bool/int/list/dict of primitives). String
   enums instead of Python objects. No callables. This keeps the door open to
   reading configuration from a TOML file later, and to non-Python
   implementations understanding it.

## Current state

Only two config values exist, registered ad-hoc:

- `sd_custom_directives` (dict) — `sphinx_design/extension.py:58`, validated
  imperatively in `setup_custom_directives` (`sphinx_design/shared.py:34-76`)
  with hand-rolled warnings. The *shape* is already declarative (dict of
  `{inherit: str, argument: str, options: {str: str}}`) — keep it.
- `sd_fontawesome_latex` (bool) — `sphinx_design/icons.py:37`.

Several briefs add options: `sd_card_legacy_separators` (bool, brief 16),
`sd_tabs_storage_prefix` (str, brief 11), `sd_fontawesome` /
`sd_fontawesome_latex_package` (str enums, brief 13).

## What to do

1. Create `sphinx_design/config.py`:

   ```python
   @dataclass
   class SdConfig:
       """Global configuration for sphinx-design (all values TOML-compatible)."""

       custom_directives: dict[str, Any] = dc.field(
           default_factory=dict,
           metadata={"validator": validate_custom_directives,
                     "help": "Custom directives inheriting from sphinx-design ones"},
       )
       fontawesome_latex: bool = dc.field(
           default=False, metadata={"help": "Render fontawesome icons in LaTeX"}
       )
       # future fields land here (briefs 11, 13, 16)
   ```

   Port the validator approach from myst-parser's
   `myst_parser/config/dc_validators.py` (type-check from the field's
   annotation, per-field custom validators, warning callback rather than
   raising). Move the body of `setup_custom_directives`'s validation into
   `validate_custom_directives`.

2. Registration: keep the existing flat Sphinx confvals (`sd_<field>`) for
   backwards compatibility — iterate `dataclasses.fields(SdConfig)` to
   `app.add_config_value(f"sd_{f.name}", f.default, "env", ...)`, then on
   `config-inited` build a validated `SdConfig` instance and stash it as
   `app.env.sd_config` (typed accessor helper `get_sd_config(env)` — do NOT
   scatter `getattr(config, "sd_...")` around modules).

3. Migrate the two existing options; emit warnings through the existing
   `WARNING_TYPE = "design"` / subtype `config` convention
   (`sphinx_design/shared.py:17`).

4. Docs: add a `configuration` section that renders the table from the
   dataclass (myst-parser does this with a small Sphinx directive reading
   field metadata — `myst_parser/sphinx_ext/directives.py`; a simpler
   hand-rolled table generator in `docs/conf.py` is acceptable).

5. Tests: `tests/test_misc.py` — invalid types for each field produce a
   `design.config` warning and fall back to the default; valid TOML round-trip
   sanity check: `tomllib.loads(tomli_w/`hand-written string`)` for a config
   containing every field → `SdConfig(**data)` validates. (Use `tomllib` from
   stdlib; only needed in tests.)

## Constraints

- No behavioural change for existing users: `sd_custom_directives` and
  `sd_fontawesome_latex` keep their names, defaults, and semantics.
- Do not add a `sd_config`-style single-dict confval yet; flat `sd_*` values
  remain the public interface for now.

## Acceptance criteria

- All config declared in one dataclass; `extension.py` / `icons.py` read via
  the typed accessor.
- Existing test suite passes unchanged (except any regression re-runs).
- New validation tests pass; docs list every option with type/default/help.
