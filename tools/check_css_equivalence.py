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

Any other difference is reported and makes the check fail. A rule-set (multiset)
match is necessary but *not sufficient*: it is blind to source order, and the
CSS cascade is order-sensitive. So a second, order-aware pass also runs and
fails on:

* **source-order inversions** -- any pair of rules whose relative order flips
  between base and new while they share a declared property, have intersecting
  selector specificity and sit in the same ``@media`` context (an equal-
  specificity, same-property, same-context flip changes which rule wins);
* **duplicate keys** -- a ``(context, selector)`` that occurs more than once in
  either artifact (the multiset pass silently merges these, so they are reported
  here instead of hidden); and
* **intra-rule duplicate-property reordering** -- a property declared twice in a
  rule whose surviving declaration order differs, allowing only the enumerated
  color-mix() fallback (which must stay *after* its static fallback) and the
  dropped ``-ms`` flexbox ``display`` value.

This is a verification tool, not a permanent CI gate: it is meant to be run
against the pre-migration commit while the stylesheet is otherwise quiet.

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


def _value_key(decl) -> str:
    """Normalised value (with importance) of a single declaration."""
    value = normalise_value(decl.value)
    if decl.important:
        value += " !important"
    return value


def _ordered_declarations(content: list) -> list[tuple[str, str]]:
    """Ordered ``(property, value)`` pairs of a rule, duplicates preserved."""
    decls = tinycss2.parse_declaration_list(
        content, skip_whitespace=True, skip_comments=True
    )
    return [(d.name, _value_key(d)) for d in decls if d.type == "declaration"]


# Selector specificity --------------------------------------------------------

_ID_RE = re.compile(r"#[-\w]+")
_ATTR_RE = re.compile(r"\[[^\]]*\]")
_CLASS_RE = re.compile(r"\.[-\w]+")
_PSEUDO_EL_RE = re.compile(r"::[-\w]+|:(?:before|after|first-line|first-letter)\b")
_PSEUDO_CLASS_RE = re.compile(r":[-\w]+(?:\([^)]*\))?")
_TYPE_RE = re.compile(r"[a-zA-Z][-\w]*")


def _specificity_of_simple(selector: str) -> tuple[int, int, int]:
    """Specificity ``(ids, classes/attrs/pseudo-classes, types/pseudo-elements)``.

    A deliberately small implementation: enough for the utility/component
    selectors in this stylesheet (classes, type names, ``:hover``/``:focus``
    pseudo-classes, ``::after`` pseudo-elements, ``*``). ``*`` contributes 0.
    """
    a = len(_ID_RE.findall(selector))
    selector = _ID_RE.sub(" ", selector)
    c = len(_PSEUDO_EL_RE.findall(selector))  # pseudo-elements count as type-level
    selector = _PSEUDO_EL_RE.sub(" ", selector)
    b = len(_ATTR_RE.findall(selector))
    selector = _ATTR_RE.sub(" ", selector)
    b += len(_CLASS_RE.findall(selector))
    selector = _CLASS_RE.sub(" ", selector)
    b += len(_PSEUDO_CLASS_RE.findall(selector))
    selector = _PSEUDO_CLASS_RE.sub(" ", selector)
    c += len(_TYPE_RE.findall(selector))  # leftover bare element names
    return (a, b, c)


def _split_selector_group(selector: str) -> list[str]:
    """Split a normalised selector group on top-level commas."""
    parts: list[str] = []
    depth = 0
    current: list[str] = []
    for char in selector:
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        if char == "," and depth == 0:
            parts.append("".join(current))
            current = []
        else:
            current.append(char)
    if current:
        parts.append("".join(current))
    return [p for p in parts if p]


def specificity_set(selector: str) -> frozenset[tuple[int, int, int]]:
    """Specificities of each branch of a (possibly grouped) selector.

    A grouped selector ``A, B`` behaves like independent rules, so its
    specificity is the *set* of its branches' specificities. Two rules can have
    an equal-specificity conflict on a shared element iff these sets intersect.
    """
    return frozenset(_specificity_of_simple(p) for p in _split_selector_group(selector))


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


# Ordered model (source-order / cascade checks) -------------------------------


@dataclass
class OrderedRule:
    context: str
    selector: str
    decls: list[tuple[str, str]]  # (property, value) in source order


def parse_ordered(css: str) -> list[OrderedRule]:
    """Flatten a stylesheet to a source-ordered list of rules.

    Unlike :func:`parse`, duplicate ``(context, selector)`` keys are *preserved*
    (not merged) and declaration order within a rule is kept, so the cascade
    passes can reason about last-wins semantics. ``@keyframes`` are skipped
    (their ordering carries no cascade meaning).
    """
    rules: list[OrderedRule] = []

    def emit(context: str, node) -> None:
        rules.append(
            OrderedRule(
                context,
                normalise_selector(node.prelude),
                _ordered_declarations(node.content),
            )
        )

    for node in tinycss2.parse_stylesheet(
        css, skip_whitespace=True, skip_comments=True
    ):
        if node.type == "qualified-rule":
            emit("", node)
        elif node.type == "at-rule":
            keyword = (node.lower_at_keyword or node.at_keyword or "").lstrip("-")
            keyword = re.sub(r"^(webkit|moz|o|ms)keyframes$", "keyframes", keyword)
            if keyword == "keyframes" or node.content is None:
                continue
            context = f"@{node.at_keyword} {normalise_prelude(node.prelude)}"
            for nested in tinycss2.parse_rule_list(
                node.content, skip_whitespace=True, skip_comments=True
            ):
                if nested.type == "qualified-rule":
                    emit(context, nested)
    return rules


def _is_color_mix_add(prop: str, value: str) -> bool:
    """The enumerated intentional addition: the runtime color-mix() highlight."""
    return bool(
        re.fullmatch(r"--sd-color-[a-z]+-highlight", prop)
    ) and value.startswith("color-mix(")


def _is_dropped_prefix_value(prop: str, value: str) -> bool:
    """A value-level dropped prefix that formed an intra-rule duplicate in base.

    Only ``display: -ms-flexbox`` / ``-ms-inline-flexbox`` qualify: the other
    dropped prefixes (``-ms-flex`` etc.) live under *distinct* property names and
    so never duplicate a property within a single rule.
    """
    return (
        prop == "display" and value.replace(" !important", "") in DROPPED_DISPLAY_VALUES
    )


@dataclass
class OrderDiff:
    duplicate_keys: list[str] = field(default_factory=list)
    inversions: list[str] = field(default_factory=list)
    intra_rule: list[str] = field(default_factory=list)


Key = tuple[str, str]  # (context, selector)


def _first_positions(rules: list[OrderedRule]) -> dict[Key, int]:
    pos: dict[Key, int] = {}
    for i, rule in enumerate(rules):
        pos.setdefault((rule.context, rule.selector), i)
    return pos


def _duplicate_keys(base: list[OrderedRule], new: list[OrderedRule]) -> list[str]:
    """(b) ``(context, selector)`` keys that occur more than once in either side."""
    out: list[str] = []
    for label, rules in (("base", base), ("new", new)):
        counts = Counter((r.context, r.selector) for r in rules)
        for (context, selector), count in sorted(counts.items()):
            if count > 1:
                out.append(f"{label}: {count}x  {f'{context} {selector}'.strip()}")
    return out


def _inversions(base: list[OrderedRule], new: list[OrderedRule]) -> list[str]:
    """(a) order flips between rule pairs sharing a property + specificity + context."""
    pos_base, pos_new = _first_positions(base), _first_positions(new)
    props: dict[Key, set[str]] = {}
    spec: dict[Key, frozenset[tuple[int, int, int]]] = {}
    for rule in (*base, *new):
        key = (rule.context, rule.selector)
        props.setdefault(key, set()).update(p for p, _ in rule.decls)
        spec[key] = specificity_set(rule.selector)

    # group common keys by @media context so only same-context pairs are compared
    by_context: dict[str, list[Key]] = {}
    for key in set(pos_base) & set(pos_new):
        by_context.setdefault(key[0], []).append(key)

    out: list[str] = []
    for context, keys in by_context.items():
        for i, k1 in enumerate(keys):
            for k2 in keys[i + 1 :]:
                flipped = (pos_base[k1] < pos_base[k2]) != (pos_new[k1] < pos_new[k2])
                shared = props[k1] & props[k2]  # (i) shared property
                if not (flipped and shared and (spec[k1] & spec[k2])):  # (ii) spec
                    continue
                lo, hi = (k1, k2) if pos_base[k1] < pos_base[k2] else (k2, k1)
                out.append(
                    f"ctx={context!r}  base order [{lo[1]}] before [{hi[1]}], "
                    f"new order flipped (shared: {', '.join(sorted(shared))})"
                )
    return out


def _mix_precedes_fallback(prop: str, seq: list[str]) -> bool:
    """True if a color-mix() value appears with no static fallback before it."""
    return any(
        _is_color_mix_add(prop, value)
        and not any(not _is_color_mix_add(prop, seq[k]) for k in range(i))
        for i, value in enumerate(seq)
    )


def _intra_rule_disorder(base: list[OrderedRule], new: list[OrderedRule]) -> list[str]:
    """(c) duplicate-property rules whose surviving declaration order changed."""
    base_by_key = {(r.context, r.selector): r for r in base}
    new_by_key = {(r.context, r.selector): r for r in new}
    out: list[str] = []
    for key in sorted(set(base_by_key) & set(new_by_key)):
        b_decls, n_decls = base_by_key[key].decls, new_by_key[key].decls
        duplicated = {p for p, c in Counter(p for p, _ in b_decls).items() if c > 1}
        duplicated |= {p for p, c in Counter(p for p, _ in n_decls).items() if c > 1}
        for prop in sorted(duplicated):
            b_seq = [v for p, v in b_decls if p == prop]
            n_seq = [v for p, v in n_decls if p == prop]
            # compare surviving declarations only: strip the enumerated dropped
            # -ms display prefix (base-only) and color-mix() addition (new-only)
            base_kept = [v for v in b_seq if not _is_dropped_prefix_value(prop, v)]
            new_kept = [v for v in n_seq if not _is_color_mix_add(prop, v)]
            if base_kept != new_kept or _mix_precedes_fallback(prop, n_seq):
                where = f"{key[0]} {key[1]}".strip()
                out.append(f"{where} {{{prop}}}: base {b_seq} -> new {n_seq}")
    return out


def order_diff(base_css: str, new_css: str) -> OrderDiff:
    """Second-pass, order-aware comparison of two stylesheets.

    Fails on (a) source-order inversions between rule pairs that share a declared
    property, have intersecting selector specificity and sit in the same @media
    context; (b) any ``(context, selector)`` key that occurs more than once in
    either artifact; and (c) any intra-rule duplicate property whose surviving
    declaration order differs -- allowing only the enumerated color-mix() fallback
    addition (which must sit *after* its static fallback) and the dropped ``-ms``
    flexbox ``display`` value.
    """
    base = parse_ordered(base_css)
    new = parse_ordered(new_css)
    return OrderDiff(
        duplicate_keys=_duplicate_keys(base, new),
        inversions=_inversions(base, new),
        intra_rule=_intra_rule_disorder(base, new),
    )


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
    labels: tuple[str, str],
    base: RuleSet,
    new: RuleSet,
    diff: Diff,
    order: OrderDiff,
) -> str:
    base_label, new_label = labels
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

    lines.append("--- MULTISET PASS (rule-set equivalence) ---")
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

    lines.append("--- ORDER PASS (cascade / source order) ---")
    lines.append("")

    if order.duplicate_keys:
        lines.append(
            f"(d) DUPLICATE (context,selector) KEYS ({len(order.duplicate_keys)}):"
        )
        lines.extend(f"    ! {item}" for item in order.duplicate_keys)
    else:
        lines.append("(d) DUPLICATE (context,selector) KEYS: none")
    lines.append("")

    if order.inversions:
        lines.append(
            "(e) SOURCE-ORDER INVERSIONS "
            f"(shared-prop, equal-specificity, same @media) ({len(order.inversions)}):"
        )
        lines.extend(f"    ! {item}" for item in order.inversions)
    else:
        lines.append(
            "(e) SOURCE-ORDER INVERSIONS "
            "(shared-prop, equal-specificity, same @media): none"
        )
    lines.append("")

    if order.intra_rule:
        lines.append(
            f"(f) INTRA-RULE DUPLICATE-PROPERTY ORDER ({len(order.intra_rule)}):"
        )
        lines.extend(f"    ! {item}" for item in order.intra_rule)
    else:
        lines.append("(f) INTRA-RULE DUPLICATE-PROPERTY ORDER: none")
    lines.append("")

    order_ok = not (order.duplicate_keys or order.inversions or order.intra_rule)
    ok = not diff.unexpected and order_ok
    lines.append(
        "RESULT: "
        + (
            "PASS - only intentional, allowlisted differences; source order faithful"
            if ok
            else "FAIL - "
            + ", ".join(
                filter(
                    None,
                    [
                        "unexpected rule-set differences" if diff.unexpected else "",
                        "source-order regressions" if not order_ok else "",
                    ],
                )
            )
        )
    )
    return "\n".join(lines)


def check(
    base_css: str, new_css: str, base_label: str, new_label: str
) -> tuple[bool, str]:
    base = parse(base_css)
    new = parse(new_css)
    diff = diff_stylesheets(base, new)
    order = order_diff(base_css, new_css)
    report = render_report((base_label, new_label), base, new, diff, order)
    order_ok = not (order.duplicate_keys or order.inversions or order.intra_rule)
    return (not diff.unexpected and order_ok), report


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
