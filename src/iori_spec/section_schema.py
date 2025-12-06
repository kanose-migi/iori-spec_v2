from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .config_loader import ConfigError


@dataclass
class HeadingSpec:
    level: int
    text: str
    match: str = "exact"  # "exact" | "prefix"


@dataclass
class SectionRule:
    id: str
    kinds: List[str]
    heading: HeadingSpec
    required: bool
    multiple: bool
    tool_source: bool
    order: int
    short_desc: Optional[str] = None
    body_hint: Optional[str] = None
    llm_hint: Optional[str] = None
    notes: Optional[str] = None


@dataclass
class SectionSchemaOptions:
    allow_extra_sections: bool = True
    default_tool_source: bool = False


@dataclass
class SectionSchema:
    version: str
    rules: List[SectionRule] = field(default_factory=list)
    options: SectionSchemaOptions = field(default_factory=SectionSchemaOptions)

    def rules_for_kind(self, kind: str) -> List[SectionRule]:
        """kind に適用されるルールを order 順に返す。"""
        matched: List[SectionRule] = []
        for rule in self.rules:
            if "*" in rule.kinds or kind in rule.kinds:
                matched.append(rule)
        return sorted(matched, key=lambda r: r.order)

    def tool_source_rules(self, kind: str) -> List[SectionRule]:
        return [r for r in self.rules_for_kind(kind) if r.tool_source]


def _expect_dict(obj: Any, context: str) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        raise ConfigError(f"{context} はオブジェクト(dict)である必要があります。")
    return obj


def _parse_heading(raw: Any) -> HeadingSpec:
    heading = _expect_dict(raw, "heading")
    level = heading.get("level")
    text = heading.get("text")
    match = heading.get("match", "exact")
    if not isinstance(level, int):
        raise ConfigError("heading.level は整数である必要があります。")
    if not isinstance(text, str):
        raise ConfigError("heading.text は文字列である必要があります。")
    if match not in ("exact", "prefix"):
        raise ConfigError("heading.match は 'exact' または 'prefix' を指定してください。")
    return HeadingSpec(level=level, text=text, match=match)


def _parse_rule(raw: Any) -> SectionRule:
    rule_dict = _expect_dict(raw, "rules[]")
    rule_id = rule_dict.get("id")
    if not isinstance(rule_id, str) or not rule_id:
        raise ConfigError("rules[].id は非空文字列である必要があります。")

    kinds = rule_dict.get("kinds")
    if not isinstance(kinds, list) or not kinds:
        raise ConfigError(f"rules[{rule_id}].kinds は 1 件以上の配列である必要があります。")
    kinds_list = []
    for k in kinds:
        if not isinstance(k, str):
            raise ConfigError(f"rules[{rule_id}].kinds は文字列の配列である必要があります。")
        kinds_list.append(k)

    heading = _parse_heading(rule_dict.get("heading"))

    def _expect_bool(key: str) -> bool:
        val = rule_dict.get(key)
        if not isinstance(val, bool):
            raise ConfigError(f"rules[{rule_id}].{key} は bool である必要があります。")
        return val

    required = _expect_bool("required")
    multiple = _expect_bool("multiple")
    tool_source = _expect_bool("tool_source")
    order = rule_dict.get("order")
    if not isinstance(order, int):
        raise ConfigError(f"rules[{rule_id}].order は整数である必要があります。")

    return SectionRule(
        id=rule_id,
        kinds=kinds_list,
        heading=heading,
        required=required,
        multiple=multiple,
        tool_source=tool_source,
        order=order,
        short_desc=rule_dict.get("short_desc"),
        body_hint=rule_dict.get("body_hint"),
        llm_hint=rule_dict.get("llm_hint"),
        notes=rule_dict.get("notes"),
    )


def _parse_options(raw: Any) -> SectionSchemaOptions:
    if raw is None:
        return SectionSchemaOptions()
    opts = _expect_dict(raw, "options")
    allow_extra = opts.get("allow_extra_sections", True)
    default_tool_src = opts.get("default_tool_source", False)
    if not isinstance(allow_extra, bool):
        raise ConfigError("options.allow_extra_sections は bool である必要があります。")
    if not isinstance(default_tool_src, bool):
        raise ConfigError("options.default_tool_source は bool である必要があります。")
    return SectionSchemaOptions(
        allow_extra_sections=allow_extra,
        default_tool_source=default_tool_src,
    )


def load_section_schema(path: Path) -> SectionSchema:
    if not path.is_file():
        raise FileNotFoundError(f"spec_section_schema.yaml が見つかりません: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    root = _expect_dict(raw, "root")

    version = root.get("version")
    if version is None:
        raise ConfigError("version が spec_section_schema.yaml に存在しません。")

    rules_raw = root.get("rules", [])
    if not isinstance(rules_raw, list) or not rules_raw:
        raise ConfigError("rules は 1 件以上の配列である必要があります。")
    rules = [_parse_rule(r) for r in rules_raw]

    options = _parse_options(root.get("options"))

    return SectionSchema(version=str(version), rules=rules, options=options)


def heading_matches(rule: SectionRule, level: int, text: str) -> bool:
    if level != rule.heading.level:
        return False
    if rule.heading.match == "exact":
        return text == rule.heading.text
    return text.startswith(rule.heading.text)
