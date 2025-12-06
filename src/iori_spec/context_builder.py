# src/iori_spec/context_builder.py
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple

from .indexer import build_index, IndexResult, DocIndexEntry


def _merge_ranges(lines: Set[int], radius: int, max_line: int) -> List[Tuple[int, int]]:
    """行番号の集合から、radius 行ぶん前後を含むマージ済みの範囲リストを作る。"""
    if not lines:
        return []

    intervals: List[Tuple[int, int]] = []
    for ln in sorted(set(lines)):
        start = max(1, ln - radius)
        end = min(max_line, ln + radius)
        intervals.append((start, end))

    intervals.sort()
    merged: List[Tuple[int, int]] = []
    cur_start, cur_end = intervals[0]

    for start, end in intervals[1:]:
        if start <= cur_end + 1:
            # 重なっているのでマージ
            cur_end = max(cur_end, end)
        else:
            merged.append((cur_start, cur_end))
            cur_start, cur_end = start, end

    merged.append((cur_start, cur_end))
    return merged


def build_context_text(
    root: Path,
    target_ids: List[str],
    radius: int = 3,
    with_lines: bool = False,
    glob_pattern: str | None = None,
) -> str:
    """指定 ID 周辺のコンテキストをテキストとして構築する。

    - デフォルトでは行番号は付与しない（LLM 向け）
    - --with-lines オプション時などに行番号を付与
    """
    index: IndexResult = build_index(root, glob_pattern=glob_pattern)

    # doc_id → DocIndexEntry
    doc_map: Dict[str, DocIndexEntry] = {d.doc_id: d for d in index.docs}

    # id → IdIndexEntry の簡易 index
    id_map = {entry.id: entry for entry in index.ids}

    # doc_id ごとに、どの行・どの ID が対象かを集約
    doc_to_lines: Dict[str, Set[int]] = {}
    doc_to_ids: Dict[str, Set[str]] = {}

    for target in target_ids:
        entry = id_map.get(target)
        if entry is None:
            continue
        for occ in entry.occurrences:
            doc_to_lines.setdefault(occ.doc_id, set()).add(occ.line)
            doc_to_ids.setdefault(occ.doc_id, set()).add(target)

    if not doc_to_lines:
        return "No context found for given IDs."

    blocks: List[str] = []

    for doc_id in sorted(doc_to_lines.keys()):
        doc = doc_map.get(doc_id)
        if doc is None:
            continue

        path = doc.path
        text = path.read_text(encoding="utf-8")
        all_lines = text.splitlines()
        max_line = len(all_lines)

        ranges = _merge_ranges(doc_to_lines[doc_id], radius=radius, max_line=max_line)
        ids_here = ", ".join(sorted(doc_to_ids.get(doc_id, set())))

        for start, end in ranges:
            blocks.append(
                f"=== DOC: {doc_id} (kind={doc.kind or '-'}, scope={doc.scope or '-'})"
            )
            blocks.append(f"=== PATH: {path.as_posix()}")
            blocks.append(f"=== IDS: {ids_here}")
            blocks.append(f"=== LINES: {start}-{end}")
            blocks.append("")

            for ln in range(start, end + 1):
                line_text = all_lines[ln - 1]
                if with_lines:
                    blocks.append(f"{ln:4d}: {line_text}")
                else:
                    blocks.append(line_text)

            blocks.append("")

    return "\n".join(blocks)
