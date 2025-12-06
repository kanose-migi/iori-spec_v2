from __future__ import annotations

import datetime
import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from .config_loader import IoriSpecConfig
from .section_schema import SectionSchema, heading_matches
from .spec_loader import SpecDocument, id_to_role, scan_specs


INDEX_VERSION = "0.1.0"


@dataclass
class SpecNode:
    id: str
    kind: str
    scope: str
    status: str
    spec_title: str
    role: str
    file: str

    llm_brief: Optional[str] = None
    summary: Optional[str] = None
    trace: Optional[Dict[str, List[str]]] = None
    dp: Optional[Dict[str, List[str]]] = None
    doc: Optional[Dict[str, List[str]]] = None
    hash: Optional[str] = None
    frontmatter_range: Optional[Dict[str, int]] = None


@dataclass
class SpecIndex:
    version: str
    generated_at: str
    root: str
    nodes: List[SpecNode] = field(default_factory=list)


def _rel_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _sanitize_id_list(value: object) -> Optional[List[str]]:
    if value is None:
        return None
    if not isinstance(value, list):
        return None
    items: List[str] = []
    for v in value:
        if isinstance(v, str) and v.strip():
            items.append(v.strip())
    return items or None


def _sanitize_mapping(value: object, allowed_keys: List[str]) -> Optional[Dict[str, List[str]]]:
    if not isinstance(value, dict):
        return None
    result: Dict[str, List[str]] = {}
    for key in allowed_keys:
        if key in value:
            lst = _sanitize_id_list(value.get(key))
            if lst:
                result[key] = lst
    return result or None


def _snippet(text: str, lines: int = 5) -> Optional[str]:
    if not text:
        return None
    parts = text.strip().splitlines()
    if not parts:
        return None
    return "\n".join(parts[:lines]).strip()


def _extract_section_snippet(doc: SpecDocument, schema: Optional[SectionSchema], target_ids: List[str]) -> Optional[str]:
    if schema is None or doc.kind is None:
        return None
    for rule in schema.rules_for_kind(doc.kind):
        if rule.id not in target_ids:
            continue
        for section in doc.sections:
            if heading_matches(rule, section.level, section.heading):
                return _snippet(section.body)
    return None


def _extract_llm_summary(doc: SpecDocument, schema: Optional[SectionSchema]) -> Tuple[Optional[str], Optional[str]]:
    llm_brief = _extract_section_snippet(doc, schema, ["llm_brief"])
    # Summary ルールは id に "summary" を含むものを対象にする（req_summary / if_summary / data_summary 等）
    summary = None
    if schema is not None and doc.kind is not None:
        for rule in schema.rules_for_kind(doc.kind):
            if "summary" not in rule.id:
                continue
            for section in doc.sections:
                if heading_matches(rule, section.level, section.heading):
                    summary = _snippet(section.body)
                    break
            if summary:
                break
    return llm_brief, summary


def build_spec_index(
    spec_root: Path,
    config: Optional[IoriSpecConfig] = None,
    section_schema: Optional[SectionSchema] = None,
    glob_pattern: Optional[str] = None,
    ignore_patterns: Optional[List[str]] = None,
) -> SpecIndex:
    spec_root = spec_root.resolve()
    docs: List[SpecDocument] = scan_specs(spec_root, glob_pattern=glob_pattern)

    valid_kinds = {k.id for k in config.vocab.kinds} if config else set()
    valid_scopes = {s.id for s in config.vocab.scopes} if config and config.vocab.scopes else set()

    nodes: List[SpecNode] = []
    ignore_patterns = ignore_patterns or []
    if config and config.paths.ignore_paths:
        for d in config.paths.ignore_paths:
            has_glob = any(ch in d for ch in "*?")
            if "/" in d:
                ignore_patterns.append(Path(d).name)
            if has_glob:
                ignore_patterns.append(d)
                ignore_patterns.append(f"**/{d}")
            else:
                ignore_patterns.append(d)
                ignore_patterns.append(f"**/{d}")
                if Path(d).suffix == "":
                    ignore_patterns.extend([f"{d}/**", f"**/{d}/**"])

    for doc in docs:
        rel = _rel_path(doc.path, spec_root)
        if any(Path(rel).match(pat) for pat in ignore_patterns):
            continue

        spec_id = doc.front_matter.get("id")
        kind = doc.kind
        scope = doc.scope
        status = doc.status
        spec_title = doc.spec_title

        if not spec_id or not kind or not scope or not status or not spec_title:
            continue
        if valid_kinds and kind not in valid_kinds:
            continue
        if valid_scopes and scope not in valid_scopes:
            continue

        llm_brief, summary = _extract_llm_summary(doc, section_schema)

        trace = _sanitize_mapping(doc.front_matter.get("trace"), ["req", "if", "data", "test", "task"])
        dp = _sanitize_mapping(doc.front_matter.get("dp"), ["produces", "produced_by", "consumes", "inputs"])
        doc_links = _sanitize_mapping(doc.front_matter.get("doc"), ["read_next", "see_also"])

        fm_range = None
        if doc.frontmatter_range is not None:
            fm_range = {"start": doc.frontmatter_range[0], "end": doc.frontmatter_range[1]}

        node = SpecNode(
            id=spec_id,
            kind=kind,
            scope=scope,
            status=status,
            spec_title=spec_title,
            role=id_to_role(spec_id),
            file=rel,
            llm_brief=llm_brief,
            summary=summary,
            trace=trace,
            dp=dp,
            doc=doc_links,
            hash=hashlib.sha256(doc.path.read_bytes()).hexdigest(),
            frontmatter_range=fm_range,
        )
        nodes.append(node)

    index = SpecIndex(
        version=INDEX_VERSION,
        generated_at=datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        root=spec_root.as_posix(),
        nodes=nodes,
    )
    return index


def spec_index_to_json(index: SpecIndex) -> str:
    payload = asdict(index)
    return json.dumps(payload, ensure_ascii=False, indent=2)


def save_spec_index(index: SpecIndex, output_path: Path) -> None:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(spec_index_to_json(index), encoding="utf-8")


def format_spec_index_text(index: SpecIndex) -> str:
    lines: List[str] = []
    lines.append(f"[iori-spec] spec_index version={index.version} root={index.root}")
    lines.append(f"[iori-spec] nodes: {len(index.nodes)}")
    lines.append("")

    role_counts: Dict[str, int] = {}
    kind_counts: Dict[str, int] = {}
    for node in index.nodes:
        role_counts[node.role] = role_counts.get(node.role, 0) + 1
        kind_counts[node.kind] = kind_counts.get(node.kind, 0) + 1

    lines.append("Roles:")
    for role in sorted(role_counts.keys()):
        lines.append(f"  - {role}: {role_counts[role]}")
    lines.append("")

    lines.append("Kinds:")
    for kind in sorted(kind_counts.keys()):
        lines.append(f"  - {kind}: {kind_counts[kind]}")
    lines.append("")

    lines.append("Nodes:")
    for node in sorted(index.nodes, key=lambda n: n.id):
        lines.append(
            f"  - {node.id} ({node.kind}/{node.scope}) status={node.status} file={node.file}"
        )

    return "\n".join(lines)
