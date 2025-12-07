# src/iori_spec/trace_analyzer.py
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import json

from .indexer import IndexResult, DocIndexEntry, IdIndexEntry, build_index
from .spec_loader import ID_PATTERN


@dataclass
class TraceRow:
    """Traceability Map の1行分。"""
    line_no: int
    raw_line: str
    ids: List[str]


@dataclass
class TraceIssue:
    """トレーサビリティに関する問題1件。"""
    issue_type: str        # "missing_trace_for_req" など
    severity: str          # "error" | "warn"
    id: str                # REQ-xxx / IF-xxx / DATA-xxx / TEST-xxx / "(none)"
    message: str
    doc_id: Optional[str] = None
    lines: Optional[List[int]] = None   # 該当行（あれば）


@dataclass
class TraceResult:
    root: Path
    index: IndexResult
    trace_doc: Optional[DocIndexEntry]
    rows: List[TraceRow]
    issues: List[TraceIssue]


# ---------- ヘルパ ----------

def _find_trace_doc(result: IndexResult, explicit_path: Optional[Path]) -> Optional[DocIndexEntry]:
    """IndexResult から Traceability Map 用のドキュメントを特定する."""
    # 明示指定があればそれを優先
    if explicit_path is not None:
        target = explicit_path if explicit_path.is_absolute() else (result.root / explicit_path)
        for doc in result.docs:
            if doc.path.resolve() == target.resolve():
                return doc
        return None

    # デフォルト: root/artifacts/traceability_map.md
    default = result.root / "artifacts" / "traceability_map.md"
    for doc in result.docs:
        if doc.path.resolve() == default.resolve():
            return doc

    # パス or doc_id に "traceability" を含むものを候補に
    for doc in result.docs:
        if "traceability" in doc.doc_id.lower() or "traceability" in str(doc.path).lower():
            return doc

    return None


def _parse_trace_rows(trace_doc: DocIndexEntry) -> Tuple[List[TraceRow], Dict[str, List[int]]]:
    """traceability_map.md から TraceRow と ID→行番号のマップを抽出."""
    text = trace_doc.path.read_text(encoding="utf-8")
    rows: List[TraceRow] = []
    id_to_lines: Dict[str, List[int]] = {}

    for i, line in enumerate(text.splitlines(), start=1):
        if not any(prefix in line for prefix in ("REQ-", "IF-", "DATA-", "TEST-")):
            continue

        ids = [m.group("id") for m in ID_PATTERN.finditer(line)]
        if not ids:
            continue

        rows.append(TraceRow(line_no=i, raw_line=line, ids=ids))
        for id_ in ids:
            id_to_lines.setdefault(id_, []).append(i)

    return rows, id_to_lines


def _ids_in_specs_excluding_trace(result: IndexResult, trace_doc_id: str, prefix: str) -> List[str]:
    """Traceability Map 以外のドキュメントで使われている ID を prefix ごとに取得."""
    ids: List[str] = []
    for entry in result.ids:
        if entry.prefix != prefix:
            continue
        if any(occ.doc_id != trace_doc_id for occ in entry.occurrences):
            ids.append(entry.id)
    return sorted(set(ids))


def _find_id_entry(result: IndexResult, id_: str) -> Optional[IdIndexEntry]:
    for entry in result.ids:
        if entry.id == id_:
            return entry
    return None


# ---------- 解析本体 ----------

def analyze_trace(
    root: Path,
    trace_map_path: Optional[Path] = None,
    glob_pattern: str | None = None,
    ignore_paths: List[str] | None = None,
) -> TraceResult:
    """トレーサビリティチェックのメイン関数."""
    index = build_index(root, glob_pattern=glob_pattern, ignore_paths=ignore_paths)
    trace_doc = _find_trace_doc(index, trace_map_path)
    issues: List[TraceIssue] = []
    rows: List[TraceRow] = []
    id_to_lines: Dict[str, List[int]] = {}

    if trace_doc is None:
        issues.append(
            TraceIssue(
                issue_type="trace_map_not_found",
                severity="error",
                id="(none)",
                message=(
                    "Traceability Map document not found. "
                    "Tried default 'artifacts/traceability_map.md' and files containing 'traceability'."
                ),
            )
        )
        return TraceResult(root=root, index=index, trace_doc=None, rows=[], issues=issues)

    rows, id_to_lines = _parse_trace_rows(trace_doc)
    trace_doc_id = trace_doc.doc_id

    # Traceability Map 内に登場する ID
    ids_in_trace = set(id_to_lines.keys())
    req_in_trace = {i for i in ids_in_trace if i.startswith("REQ-")}
    if_in_trace = {i for i in ids_in_trace if i.startswith("IF-")}
    data_in_trace = {i for i in ids_in_trace if i.startswith("DATA-")}
    test_in_trace = {i for i in ids_in_trace if i.startswith("TEST-")}

    # Traceability Map 以外の spec に登場する ID
    req_in_specs = set(_ids_in_specs_excluding_trace(index, trace_doc_id, "REQ"))
    if_in_specs = set(_ids_in_specs_excluding_trace(index, trace_doc_id, "IF"))
    data_in_specs = set(_ids_in_specs_excluding_trace(index, trace_doc_id, "DATA"))
    test_in_specs = set(_ids_in_specs_excluding_trace(index, trace_doc_id, "TEST"))

    # 1. REQ: spec にあるのに trace に無いもの → error
    for req in sorted(req_in_specs):
        if req not in req_in_trace:
            entry = _find_id_entry(index, req)
            doc_id = None
            line = None
            if entry is not None:
                for occ in entry.occurrences:
                    if occ.doc_id != trace_doc_id:
                        doc_id = occ.doc_id
                        line = occ.line
                        break
            issues.append(
                TraceIssue(
                    issue_type="missing_trace_for_req",
                    severity="error",
                    id=req,
                    message=f"{req} is defined in specs but not present in traceability map.",
                    doc_id=doc_id,
                    lines=[line] if line is not None else None,
                )
            )

    # 2. IF/DATA/TEST: spec にあるのに trace に無いもの → warning
    for prefix, specs_set, trace_set, issue_type in [
        ("IF", if_in_specs, if_in_trace, "unmapped_if"),
        ("DATA", data_in_specs, data_in_trace, "unmapped_data"),
        ("TEST", test_in_specs, test_in_trace, "unmapped_test"),
    ]:
        for id_ in sorted(specs_set):
            if id_ not in trace_set:
                entry = _find_id_entry(index, id_)
                doc_id = None
                line = None
                if entry is not None:
                    for occ in entry.occurrences:
                        if occ.doc_id != trace_doc_id:
                            doc_id = occ.doc_id
                            line = occ.line
                            break
                issues.append(
                    TraceIssue(
                        issue_type=issue_type,
                        severity="warn",
                        id=id_,
                        message=f"{id_} is used in specs but not present in traceability map.",
                        doc_id=doc_id,
                        lines=[line] if line is not None else None,
                    )
                )

    # 3. Traceability Map のみに出てくる ID → warning
    def _only_in_trace(trace_set: set[str], specs_set: set[str], issue_type: str) -> None:
        for id_ in sorted(trace_set):
            if id_ not in specs_set:
                issues.append(
                    TraceIssue(
                        issue_type=issue_type,
                        severity="warn",
                        id=id_,
                        message=f"{id_} appears only in traceability map and nowhere else.",
                        doc_id=trace_doc_id,
                        lines=id_to_lines.get(id_),
                    )
                )

    _only_in_trace(req_in_trace, req_in_specs, "req_only_in_trace")
    _only_in_trace(if_in_trace, if_in_specs, "if_only_in_trace")
    _only_in_trace(data_in_trace, data_in_specs, "data_only_in_trace")
    _only_in_trace(test_in_trace, test_in_specs, "test_only_in_trace")

    return TraceResult(root=root, index=index, trace_doc=trace_doc, rows=rows, issues=issues)


# ---------- フォーマット ----------

def format_trace_text(result: TraceResult) -> str:
    """人間向けのテキスト出力."""
    if result.trace_doc is None:
        # trace_map_not_found だけのケース
        if result.issues:
            return "\n".join([i.message for i in result.issues])
        return "Traceability map not found."

    lines: List[str] = []
    lines.append(f"[iori-spec] root           : {result.root.as_posix()}")
    lines.append(f"[iori-spec] traceability   : {result.trace_doc.path.as_posix()}")
    lines.append(f"[iori-spec] docs           : {len(result.index.docs)}")
    lines.append(f"[iori-spec] trace rows     : {len(result.rows)}")
    lines.append("")

    if not result.issues:
        lines.append("No traceability issues found. ✅")
        return "\n".join(lines)

    errors = [i for i in result.issues if i.severity == "error"]
    warns = [i for i in result.issues if i.severity == "warn"]

    lines.append(f"Traceability issues: {len(result.issues)} (errors={len(errors)}, warnings={len(warns)})")
    lines.append("")

    for issue in result.issues:
        loc = "(n/a)"
        if issue.doc_id is not None:
            # doc_id → path 解決
            doc = next((d for d in result.index.docs if d.doc_id == issue.doc_id), None)
            if doc is not None:
                if issue.lines:
                    loc = f"{doc.path.as_posix()}:{issue.lines[0]}"
                else:
                    loc = doc.path.as_posix()
            else:
                loc = issue.doc_id

        lines.append(f"[{issue.severity.upper()}] {issue.issue_type} :: {issue.id}")
        lines.append(f"  - where : {loc}")
        lines.append(f"  - detail: {issue.message}")
        lines.append("")

    return "\n".join(lines)


def format_trace_json(result: TraceResult) -> str:
    """LLM / ツール向けの JSON 出力."""

    def _issue_to_dict(i: TraceIssue) -> dict:
        return {
            "issue_type": i.issue_type,
            "severity": i.severity,
            "id": i.id,
            "message": i.message,
            "doc_id": i.doc_id,
            "lines": i.lines,
        }

    payload = {
        "kind": "trace",
        "version": "0.1",
        "root": result.root.as_posix(),
        "trace_doc": (
            {
                "doc_id": result.trace_doc.doc_id,
                "path": result.trace_doc.path.as_posix(),
                "kind": result.trace_doc.kind,
                "scope": result.trace_doc.scope,
            }
            if result.trace_doc is not None
            else None
        ),
        "issues": [_issue_to_dict(i) for i in result.issues],
    }

    return json.dumps(payload, ensure_ascii=False, indent=2)
