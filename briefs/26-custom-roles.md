# Brief 26: Config-defined custom roles (`sd_custom_roles`)

**Type**: feature | **Size**: small-medium | **Closes**: — (follow-up to #81/#286;
generalizes the `sd_custom_directives` pattern from #194).
**Depends on**: brief 02 (SdConfig — merged #274) and the badge tooltip
machinery (merged #286).

## Motivation

#286 added per-instance badge tooltips via the `; tooltip` role-text suffix.
That is the only *per-instance* mechanism docutils roles permit (roles take a
single text argument; MyST `attrs_inline` has no rst equivalent). But the
dominant use case for badge tooltips is **repeated semantics** — status
badges like "stable"/"beta"/"deprecated" whose tooltip is the same at every
use site. For those, retyping the suffix is noise, and a config-defined role
is strictly cleaner: zero new syntax, defined once, TOML-representable,
parser-portable by construction (it is just a role name).

This mirrors `sd_custom_directives` (shipped in 0.6), which does exactly this
for directives.

## Design

New `SdConfig` field (flat confval `sd_custom_roles`), TOML-compatible:

```python
sd_custom_roles = {
    "bdg-stable": {
        "inherit": "bdg-success",
        "tooltip": "A released, supported version",
    },
    "bdg-beta": {"inherit": "bdg-warning", "tooltip": "Interface may change"},
}
```

- Key = the new role name to register. Value keys:
  - `inherit` (required): an existing sphinx-design **badge** role name
    (`bdg`, `bdg-<color>`, `bdg-*-line`, `bdg-link-*`, `bdg-ref-*`). v1 scope
    is the badge family only — note the extension point for icon/button roles
    in a code comment, but do not implement.
  - `tooltip` (optional str): baked tooltip. A per-instance `; suffix`
    (per #286's grammar) **overrides** the baked value; document this
    precedence.
- Validator mirrors `validate_custom_directive` (config.py): dict of dicts,
  primitives only, unknown keys rejected, `inherit` must name a known badge
  role, role-name syntax validated (no clash with an existing role — warn and
  skip on clash, same policy as custom directives).
- Registration at `config-inited`, parallel to `setup_custom_directives`
  (extension.py): construct the inherited role class instance with the baked
  tooltip. The #286 role classes take constructor args (color/outline) —
  extend constructors with `tooltip: str | None = None` used as the default
  when no suffix is present, rather than subclass gymnastics.

## Docs

- New subsection under badges: "Custom badge roles" — present this as the
  **primary** pattern for repeated status badges, with the `; tooltip` suffix
  as the one-off escape hatch (adjust #286's tooltip docs accordingly).
- Cross-link from the `sd_custom_directives` docs (same concept, roles).
- Config-options table picks the field up automatically.

## Tests

- Config validation cases (+ the mechanical `test_misc.py` meta-test syncs
  every SdConfig field requires: `INVALID_CONFIG_VALUES`, TOML round-trip).
- Registration: custom role usable in rst + myst; renders identically to the
  inherited role plus the baked tooltip; suffix-overrides-baked precedence;
  clash with an existing role name warns and skips; unknown `inherit` warns.
- No-tooltip custom role = byte-identical output to the inherited role.
- Standard matrix + pinned rails (7.2.6 / 7.4.7 / 8.2.3, pin-and-print).

## Acceptance criteria

- `sd_custom_roles` fully TOML-representable and validated; docs updated with
  the primary/escape-hatch framing; zero behaviour change for anyone not
  setting the option.
