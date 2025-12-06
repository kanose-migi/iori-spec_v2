# src/iori_spec/spec_loader.py
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import re

import yaml

# 仕様IDのパターン（必要に応じて追加）
ID_PATTERN = re.compile(
    r"\b(?P<id>(REQ|NFR|IF|DATA|TEST|TASK|ARCH|REF|STEER)-\d{3,})\b"
)

ROLE_MAP = {
    "REQ": "req",
    "NFR": "req",
    "IF": "if",
    "DATA": "data",
    "TEST": "test",
    "TASK": "task",
    "ARCH": "arch",
    "REF": "ref",
    "STEER": "steering",
}

HEADING_PATTERN = re.compile(r"^(?P<marks>#+)\s+(?P<text>.+?)\s*$")


@dataclass
class SpecIdOccurrence:
    """1つのIDが、どのファイルのどの行に現れたかを表す。"""

    id: str            # 例: "REQ-001"
    role: str          # 例: "req" / "if" / "data" / "test" / "task" / "arch" / "other"
    file: Path         # ファイルパス（絶対 or 相対）
    line_no: int       # 1-origin
    line_text: str     # 行の内容（トリム前）


@dataclass
class SpecSection:
    """Markdown 見出し1つ分のブロック情報。"""

    heading: str
    level: int
    start_line: int
    end_line: int
    body: str


@dataclass
class SpecDocument:
    """仕様ファイル1つ分のメタ情報とID出現情報。"""

    path: Path                             # ファイルパス
    kind: Optional[str]                    # front matter の kind（なければ None）
    scope: Optional[str]                   # front matter の scope（なければ None）
    status: Optional[str]                  # front matter の status（なければ None）
    spec_title: Optional[str]              # 見出し or front matter の title
    front_matter: Dict[str, Any] = field(default_factory=dict)
    front_matter_errors: List[str] = field(default_factory=list)
    frontmatter_range: Optional[Tuple[int, int]] = None
    sections: List[SpecSection] = field(default_factory=list)
    ids: List[SpecIdOccurrence] = field(default_factory=list)


def id_to_role(id_: str) -> str:
    prefix = id_.split("-", 1)[0]
    return ROLE_MAP.get(prefix, "other")


def _split_front_matter(text: str) -> Tuple[Dict[str, Any], str, List[str], int, Optional[int]]:
    """YAML front matter（先頭の --- ... ---）を分離して dict にする。

    front matter がない場合は ({}, text, [], 1, None) を返す。
    body_start_line は本文の開始行番号（1-origin）。fm_end_line は front matter の終了行。
    """
    lines = text.splitlines(keepends=True)
    if not lines or not lines[0].lstrip().startswith("---"):
        return {}, text, [], 1, None

    fm_lines: List[str] = []
    fm_errors: List[str] = []
    closing_idx: Optional[int] = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.lstrip().startswith("---"):
            closing_idx = idx
            break
        fm_lines.append(line)

    if closing_idx is None:
        # 閉じタグが見つからない場合は front matter 無しとして扱う
        return {}, text, ["front matter の終端 '---' が見つかりません。"], 1, None

    body_lines = lines[closing_idx + 1:]
    fm_text = "".join(fm_lines)
    body_text = "".join(body_lines) if body_lines else ""
    body_start_line = closing_idx + 2  # 0-index → 1-origin
    fm_end_line = closing_idx + 1      # front matter 終了行（1-origin）

    if not fm_text.strip():
        return {}, body_text, [], body_start_line, fm_end_line

    # 目視漏れ防止: 値にコロンが含まれていて無引用なら警告を入れる
    for i, raw in enumerate(fm_lines, start=2):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            continue
        key, _, val = stripped.partition(":")
        if not key.strip():
            continue
        val = val.lstrip()
        # コメント（# 以降）は無視して値部だけを確認する
        val_no_comment = val.split("#", 1)[0].strip()
        if val_no_comment and not val_no_comment.startswith(('"', "'")) and ":" in val_no_comment:
            fm_errors.append(
                f"front matter 行{i}: 値にコロンが含まれています。引用符で囲ってください: {stripped}"
            )

    try:
        fm_dict = yaml.safe_load(fm_text) or {}
        if not isinstance(fm_dict, dict):
            fm_errors.append("front matter は YAML オブジェクトである必要があります。")
            fm_dict = {}
    except Exception as exc:
        fm_errors.append(f"front matter の YAML パースに失敗しました: {exc}")
        fm_dict = {}

    return fm_dict, body_text, fm_errors, body_start_line, fm_end_line


def _extract_title(body_text: str, front_matter: Dict[str, Any]) -> Optional[str]:
    """タイトルを front matter または Markdown 見出しから推定する。"""
    if isinstance(front_matter.get("spec_title"), str):
        return front_matter["spec_title"]

    for line in body_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped.lstrip("#").strip()
        if stripped.startswith("## "):
            return stripped.lstrip("#").strip()
    return None


def _extract_sections(body_text: str, body_start_line: int) -> List[SpecSection]:
    """Markdown 本文を見出しごとに分割して返す。"""
    sections: List[SpecSection] = []
    lines = body_text.splitlines()
    current: Optional[SpecSection] = None
    buffer: List[str] = []

    def _flush(end_line: int) -> None:
        nonlocal current, buffer
        if current is None:
            return
        current.end_line = end_line
        current.body = "\n".join(buffer).rstrip("\n")
        sections.append(current)
        current = None
        buffer = []

    for idx, line in enumerate(lines):
        absolute_line = body_start_line + idx
        m = HEADING_PATTERN.match(line)
        if m:
            _flush(absolute_line - 1)
            level = len(m.group("marks"))
            heading_text = m.group("text").strip()
            current = SpecSection(
                heading=heading_text,
                level=level,
                start_line=absolute_line,
                end_line=absolute_line,
                body="",
            )
            buffer = []
        else:
            buffer.append(line)

    # 最終セクションの flush
    _flush(body_start_line + len(lines) - 1)

    return sections


def _extract_ids(path: Path, text: str) -> List[SpecIdOccurrence]:
    """Markdown テキストから仕様ID出現をすべて抽出する。"""
    occurrences: List[SpecIdOccurrence] = []
    for i, line in enumerate(text.splitlines(), start=1):
        for m in ID_PATTERN.finditer(line):
            full_id = m.group("id")
            occurrences.append(
                SpecIdOccurrence(
                    id=full_id,
                    role=id_to_role(full_id),
                    file=path,
                    line_no=i,
                    line_text=line.rstrip("\n"),
                )
            )
    return occurrences


def load_spec_document(path: Path) -> SpecDocument:
    """1つの Markdown 仕様ファイルを読み込んで SpecDocument に変換する。"""
    text = path.read_text(encoding="utf-8")
    front_matter, body, fm_errors, body_start_line, fm_end_line = _split_front_matter(text)

    kind = front_matter.get("kind")
    scope = front_matter.get("scope")
    status = front_matter.get("status")
    spec_title = _extract_title(body, front_matter)
    ids = _extract_ids(path, text)
    sections = _extract_sections(body, body_start_line)

    return SpecDocument(
        path=path,
        kind=kind,
        scope=scope,
        status=status,
        spec_title=spec_title,
        front_matter=front_matter,
        front_matter_errors=fm_errors,
        frontmatter_range=(1, fm_end_line) if fm_end_line is not None else None,
        sections=sections,
        ids=ids,
    )


def scan_specs(root: Path, glob_pattern: Optional[str] = None) -> List[SpecDocument]:
    """ルートディレクトリ以下の .md ファイルを再帰的に走査して SpecDocument を返す。

    glob_pattern を指定した場合はそのパターンに従う（例: docs/**/*.md）。
    """
    root = root.resolve()
    paths: List[Path] = []
    if glob_pattern:
        for p in Path().glob(glob_pattern):
            if p.suffix.lower() == ".md":
                paths.append(p.resolve())
    else:
        paths.extend(p.resolve() for p in root.rglob("*.md"))

    docs: List[SpecDocument] = []
    for path in sorted(set(paths)):
        if path.is_file():
            docs.append(load_spec_document(path))
    return docs


def format_spec_summary(doc: SpecDocument) -> str:
    """デバッグ用に SpecDocument の簡易サマリを文字列にする。"""
    rel = doc.path
    kind = doc.kind or "-"
    scope = doc.scope or "-"
    status = doc.status or "-"
    spec_title = doc.spec_title or "(no title)"
    id_counts: Dict[str, int] = {}
    for occ in doc.ids:
        id_counts[occ.id] = id_counts.get(occ.id, 0) + 1

    ids_preview = ", ".join(sorted(id_counts.keys())) or "(no IDs)"
    lines = [
        f"path   : {rel}",
        f"kind   : {kind}",
        f"scope  : {scope}",
        f"status : {status}",
        f"title  : {spec_title}",
        f"sections: {len(doc.sections)}",
        f"ids    : {ids_preview}",
    ]
    return "\n".join(lines)
