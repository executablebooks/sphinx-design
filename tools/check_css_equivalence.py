#!/usr/bin/env python3
"""Prove that two compiled stylesheets are rule-set equivalent.

Used to verify the Sass -> plain-CSS migration: it parses a *base* artifact and
the *new* artifact with ``tinycss2``, normalises whitespace/serialisation and
flattens ``@media`` blocks, then diffs the two as sets of ``(context, selector)
-> declarations`` rules. The only differences it tolerates are the intentional,
enumerated ones:

* **dropped vendor prefixes** -- ``-ms-*`` flexbox, ``-moz-``/``-webkit-``
  animation, box-sizing and user-select duplicates that no longer serve any
  browser in the support policy; and
* **runtime ``color-mix()``** -- the added ``--sd-color-<name>-highlight:
  color-mix(...)`` declaration that lets user colour overrides propagate to
  hover/focus shades (the static fallback beside it is unchanged).

Any other difference is reported and makes the check fail. This is a
verification tool, not a permanent CI gate: it is meant to be run against the
pre-migration commit while the stylesheet is otherwise quiet.

Usage::

    python tools/check_css_equivalence.py BASE.css NEW.css

``tinycss2`` is only needed for this dev/CI tool (see the ``testing`` extra); the
runtime package and the generator have no third-party dependency.
"""

from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
import re
import warnings

warnings.simplefilter("ignore")  # tinycss2 deprecation chatter is not relevant here

import tinycss2  # noqa: E402

# Enumerated intentional differences ------------------------------------------

# Vendor-prefixed declarations that are deliberately dropped. A removed
# declaration is allowlisted if its property is one of these, or if it is a
# ``display`` declaration whose value is one of the dropped flexbox values.
DROPPED_PREFIX_PROPS = {
    "-ms-flex",
    "-ms-flex-direction",
    "-ms-flex-wrap",
    "-moz-user-select",
    "-ms-user-select",
    "-webkit-user-select",
    "-moz-animation",
    "-webkit-animation",
    "-moz-box-sizing",
    "-webkit-box-sizing",
}
DROPPED_DISPLAY_VALUES = {"-ms-flexbox", "-ms-inline-flexbox"}


# CSS normalisation -----------------------------------------------------------


def _collapse(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _strip_leading_zeros(text: str) -> str:
    # 0.5 -> .5, -0.5 -> -.5, but leave 10.5 and bare 0 untouched
    return re.sub(r"(?<![\w.])0(?=\.\d)", "", text)


def normalise_selector(prelude: list) -> str:
    sel = _collapse(tinycss2.serialize(prelude))
    sel = re.sub(r"\s*([>~+,])\s*", r"\1", sel)  # tidy combinators/lists
    return sel


def normalise_prelude(prelude: list) -> str:
    text = _collapse(tinycss2.serialize(prelude))
    text = re.sub(r"\s*([:,])\s*", r"\1", text)  # (min-width: 5px) -> (min-width:5px)
    return text


def normalise_value(value_nodes: list) -> str:
    text = _collapse(tinycss2.serialize(value_nodes))
    text = re.sub(r"\s*,\s*", ",", text)
    return _strip_leading_zeros(text)


def declaration_key(decl) -> str:
    key = f"{decl.name}:{normalise_value(decl.value)}"
    if decl.important:
        key += " !important"
    return key


def _declarations(content: list) -> Counter:
    decls = tinycss2.parse_declaration_list(
        content, skip_whitespace=True, skip_comments=True
    )
    return Counter(declaration_key(d) for d in decls if d.type == "declaration")


# Rule-set model --------------------------------------------------------------


@dataclass
class RuleSet:
    """A flattened stylesheet: ``(context, selector) -> declaration multiset``."""

    rules: dict[tuple[str, str], Counter] = field(default_factory=dict)
    keyframes: dict[str, str] = field(default_factory=dict)

    def _add(self, context: str, selector: str, decls: Counter) -> None:
        self.rules.setdefault((context, selector), Counter()).update(decls)


def _keyframe_body(content: list) -> str:
    frames = []
    for frame in tinycss2.parse_rule_list(
        content, skip_whitespace=True, skip_comments=True
    ):
        if frame.type != "qualified-rule":
            continue
        stops = _collapse(tinycss2.serialize(frame.prelude))
        stops = re.sub(r"\s*,\s*", ",", stops)
        body = ";".join(sorted(_declarations(frame.content).elements()))
        frames.append(f"{stops}{{{body}}}")
    return " ".join(frames)


def parse(css: str) -> RuleSet:
    rule_set = RuleSet()
    for node in tinycss2.parse_stylesheet(
        css, skip_whitespace=True, skip_comments=True
    ):
        if node.type == "qualified-rule":
            rule_set._add(
                "", normalise_selector(node.prelude), _declarations(node.content)
            )
        elif node.type == "at-rule":
            keyword = (node.lower_at_keyword or node.at_keyword or "").lstrip("-")
            # normalise -webkit-keyframes / -moz-keyframes to keyframes
            keyword = re.sub(r"^(webkit|moz|o|ms)keyframes$", "keyframes", keyword)
            if keyword == "keyframes":
                name = _collapse(tinycss2.serialize(node.prelude))
                rule_set.keyframes[name] = _keyframe_body(node.content)
            elif node.content is not None:
                context = f"@{node.at_keyword} {normalise_prelude(node.prelude)}"
                for nested in tinycss2.parse_rule_list(
                    node.content, skip_whitespace=True, skip_comments=True
                ):
                    if nested.type == "qualified-rule":
                        rule_set._add(
                            context,
                            normalise_selector(nested.prelude),
                            _declarations(nested.content),
                        )
    return rule_set


# Diffing + classification ----------------------------------------------------


@dataclass
class Diff:
    dropped_prefixes: list[str] = field(default_factory=list)
    color_mix: list[str] = field(default_factory=list)
    unexpected: list[str] = field(default_factory=list)


def _classify_removed(context: str, selector: str, decl: str, diff: Diff) -> None:
    prop, _, value = decl.partition(":")
    prop = prop.strip()
    value = value.replace(" !important", "").strip()
    where = f"{context} {selector}".strip()
    if prop in DROPPED_PREFIX_PROPS or (
        prop == "display" and value in DROPPED_DISPLAY_VALUES
    ):
        diff.dropped_prefixes.append(f"{where} {{ {decl} }}")
    else:
        diff.unexpected.append(f"REMOVED  {where} {{ {decl} }}")


def _classify_added(context: str, selector: str, decl: str, diff: Diff) -> None:
    prop, _, value = decl.partition(":")
    prop = prop.strip()
    value = value.strip()
    where = f"{context} {selector}".strip()
    if re.fullmatch(r"--sd-color-[a-z]+-highlight", prop) and value.startswith(
        "color-mix("
    ):
        diff.color_mix.append(f"{where} {{ {decl} }}")
    else:
        diff.unexpected.append(f"ADDED    {where} {{ {decl} }}")


def diff_stylesheets(base: RuleSet, new: RuleSet) -> Diff:
    diff = Diff()

    base_keys = set(base.rules)
    new_keys = set(new.rules)
    for context, selector in sorted(new_keys - base_keys):
        diff.unexpected.append(f"ADDED RULE    {context} {selector}".strip())
    for context, selector in sorted(base_keys - new_keys):
        diff.unexpected.append(f"REMOVED RULE  {context} {selector}".strip())

    for key in sorted(base_keys & new_keys):
        context, selector = key
        base_decls = base.rules[key]
        new_decls = new.rules[key]
        for decl in sorted((base_decls - new_decls).elements()):
            _classify_removed(context, selector, decl, diff)
        for decl in sorted((new_decls - base_decls).elements()):
            _classify_added(context, selector, decl, diff)

    # keyframes must match exactly (name + normalised body)
    for name in sorted(set(new.keyframes) - set(base.keyframes)):
        diff.unexpected.append(f"ADDED @keyframes {name}")
    for name in sorted(set(base.keyframes) - set(new.keyframes)):
        diff.unexpected.append(f"REMOVED @keyframes {name}")
    for name in sorted(set(base.keyframes) & set(new.keyframes)):
        if base.keyframes[name] != new.keyframes[name]:
            diff.unexpected.append(
                f"CHANGED @keyframes {name}\n"
                f"    base: {base.keyframes[name]}\n"
                f"    new:  {new.keyframes[name]}"
            )

    return diff


def render_report(
    base_label: str, new_label: str, base: RuleSet, new: RuleSet, diff: Diff
) -> str:
    lines: list[str] = []
    lines.append("sphinx-design CSS rule-set equivalence check")
    lines.append("=" * 60)
    lines.append(f"base: {base_label}")
    lines.append(f"new:  {new_label}")
    lines.append(
        f"base rules: {len(base.rules)} + {len(base.keyframes)} keyframes; "
        f"new rules: {len(new.rules)} + {len(new.keyframes)} keyframes"
    )
    lines.append("")

    lines.append(f"(a) DROPPED VENDOR PREFIXES ({len(diff.dropped_prefixes)}):")
    lines.extend(f"    - {item}" for item in diff.dropped_prefixes)
    lines.append("")

    lines.append(f"(b) ADDED RUNTIME color-mix() HIGHLIGHTS ({len(diff.color_mix)}):")
    lines.extend(f"    + {item}" for item in diff.color_mix)
    lines.append("")

    if diff.unexpected:
        lines.append(f"(c) UNEXPECTED DIFFERENCES ({len(diff.unexpected)}):")
        lines.extend(f"    ! {item}" for item in diff.unexpected)
    else:
        lines.append("(c) UNEXPECTED DIFFERENCES: none")
    lines.append("")
    lines.append(
        "RESULT: "
        + (
            "PASS - only intentional, allowlisted differences"
            if not diff.unexpected
            else "FAIL - unexpected differences found"
        )
    )
    return "\n".join(lines)


def check(
    base_css: str, new_css: str, base_label: str, new_label: str
) -> tuple[bool, str]:
    base = parse(base_css)
    new = parse(new_css)
    diff = diff_stylesheets(base, new)
    report = render_report(base_label, new_label, base, new, diff)
    return (not diff.unexpected), report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check CSS rule-set equivalence.")
    parser.add_argument("base", type=Path, help="baseline (pre-migration) CSS file")
    parser.add_argument("new", type=Path, help="new CSS file")
    args = parser.parse_args(argv)

    ok, report = check(
        args.base.read_text(encoding="utf8"),
        args.new.read_text(encoding="utf8"),
        str(args.base),
        str(args.new),
    )
    print(report)  # noqa: T201  -- this is a CLI reporting tool
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
