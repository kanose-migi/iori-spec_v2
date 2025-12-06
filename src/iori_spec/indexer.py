from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import json

from .spec_loader import SpecDocument, SpecIdOccurrence, scan_specs


def _id_prefix(id_: str) -> str:
    """ID から種別プレフィックスを判定する。

    - "REQ-001" -> "REQ"
    - "IF-201"  -> "IF"
    - "DATA-101" -> "DATA"
    - "TEST-001" -> "TEST"
    """
    if id_.startswith("REQ-"):
        return "REQ"
    if id_.startswith("IF-"):
        return "IF"
    if id_.startswith("DATA-"):
        return "DATA"
    if id_.startswith("TEST-"):
        return "TEST"
    return "OTHER"


@dataclass
class DocIndexEntry:
    """1ドキュメント分のインデックス情報。"""

    doc_id: str           # 例: "requirements/functional"
    path: Path            # 実ファイルパス
    kind: str | None
    scope: str | None
    spec_title: str | None
    id_counts: Dict[str, int]  # {"REQ": 10, "IF": 2, ...}


@dataclass
class IdOccurrenceSummary:
    """ID の 1 出現箇所を要約したもの。"""

    doc_id: str
    line: int


@dataclass
class IdIndexEntry:
    """1つの ID に対する出現リスト。"""

    id: str
    prefix: str
    occurrences: List[IdOccurrenceSummary]


@dataclass
class IndexResult:
    """index コマンドの結果全体。"""

    root: Path
    docs: List[DocIndexEntry]
    ids: List[IdIndexEntry]


def build_index(root: Path, glob_pattern: str | None = None) -> IndexResult:
    """root 以下の .md を走査して IndexResult を構築する。"""
    root = root.resolve()
    docs = scan_specs(root, glob_pattern=glob_pattern)

    doc_entries: List[DocIndexEntry] = []
    # ID -> occurrences
    id_occ_map: Dict[str, List[IdOccurrenceSummary]] = {}

    for doc in docs:
        # 例: root=docs, path=docs/requirements/functional.md
        #   -> rel = "requirements/functional.md"
        rel = doc.path.relative_to(root)
        # doc_id は拡張子なしの相対パスにしておく
        doc_id = str(rel.with_suffix("")).replace("\\", "/")

        # メタタイトル: spec_title があればそれを優先、なければ doc.title
        spec_title = None
        if doc.front_matter is not None:
            spec_title = doc.front_matter.get("spec_title")
        if spec_title is None:
            spec_title = doc.spec_title

        # ドキュメント内の ID をカウント
        id_counts: Dict[str, int] = {}
        for occ in doc.ids:
            prefix = _id_prefix(occ.id)
            id_counts[prefix] = id_counts.get(prefix, 0) + 1

            # グローバルな ID インデックスにも追加
            id_occ_map.setdefault(occ.id, []).append(
                IdOccurrenceSummary(
                    doc_id=doc_id,
                    line=occ.line_no,
                )
            )

        doc_entries.append(
            DocIndexEntry(
                doc_id=doc_id,
                path=doc.path,
                kind=doc.kind,
                scope=doc.scope,
                spec_title=spec_title,
                id_counts=id_counts,
            )
        )

    # ID 側の一覧を作成
    id_entries: List[IdIndexEntry] = []
    for id_ in sorted(id_occ_map.keys()):
        prefix = _id_prefix(id_)
        id_entries.append(
            IdIndexEntry(
                id=id_,
                prefix=prefix,
                occurrences=id_occ_map[id_],
            )
        )

    return IndexResult(root=root, docs=doc_entries, ids=id_entries)


# ---------- フォーマッタ ----------

def format_index_text(result: IndexResult) -> str:
    """人間向けのテキスト出力。"""
    lines: List[str] = []

    lines.append(f"[iori-spec] index for root: {result.root}")
    lines.append(f"[iori-spec] docs: {len(result.docs)}  ids: {len(result.ids)}")
    lines.append("")

    # プレフィックス別 ID 数
    total_prefix_counts: Dict[str, int] = {}
    for entry in result.ids:
        total_prefix_counts[entry.prefix] = total_prefix_counts.get(entry.prefix, 0) + 1

    if total_prefix_counts:
        lines.append("ID counts by prefix:")
        for prefix in sorted(total_prefix_counts.keys()):
            lines.append(f"  - {prefix}: {total_prefix_counts[prefix]}")
        lines.append("")

    lines.append("Docs:")
    for doc in sorted(result.docs, key=lambda d: d.doc_id):
        kc = ", ".join(
            f"{k}={v}" for k, v in sorted(doc.id_counts.items())
        ) or "none"
        lines.append(
            f"  - [{doc.doc_id}] kind={doc.kind or '-'} scope={doc.scope or '-'} "
            f"ids({kc})"
        )
    lines.append("")

    lines.append("IDs:")
    for id_entry in result.ids:
        occ = id_entry.occurrences[0]
        lines.append(
            f"  - {id_entry.id} ({id_entry.prefix}) "
            f"first: {occ.doc_id}:{occ.line} (total {len(id_entry.occurrences)} occurrences)"
        )

    return "\n".join(lines)


def format_index_json(result: IndexResult) -> str:
    """LLM / ツール向けのコンパクトな JSON 出力。"""

    def _doc_to_dict(doc: DocIndexEntry) -> dict:
        return {
            "doc_id": doc.doc_id,
            "path": doc.path.as_posix(),
            "kind": doc.kind,
            "scope": doc.scope,
            "spec_title": doc.spec_title,
            "id_counts": doc.id_counts,
        }

    def _id_to_dict(entry: IdIndexEntry) -> dict:
        by_doc: dict[str, list[int]] = {}
        for occ in entry.occurrences:
            by_doc.setdefault(occ.doc_id, []).append(occ.line)

        return {
            "id": entry.id,
            "prefix": entry.prefix,
            "occurrences_by_doc": [
                {"doc_id": doc_id, "lines": sorted(lines), "count":len(lines)}
                for doc_id, lines in sorted(by_doc.items())
            ],
        }

    payload = {
        "kind": "index",                 # ← これは index 用 JSON ですよ、の明示
        "version": "0.1",                # ← 将来スキーマ変えるとき用のフック
        "root": result.root.as_posix(),
        "docs": [_doc_to_dict(d) for d in sorted(result.docs, key=lambda d: d.doc_id)],
        "ids": [_id_to_dict(e) for e in result.ids],
    }

    # 可読性優先。トークンを極限までケチりたくなったら indent=None にするオプションを
    # 後で増やすイメージ。
    return json.dumps(payload, ensure_ascii=False, indent=2)
