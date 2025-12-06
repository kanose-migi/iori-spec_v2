from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List, Optional

from .config_loader import IoriSpecConfig
from .section_schema import SectionSchema, heading_matches
from .spec_loader import ID_PATTERN, SpecDocument, scan_specs


ALLOWED_STATUS = {"draft", "review", "stable", "deprecated"}


@dataclass
class LintIssue:
    rule_id: str
    severity: str  # "error" | "warning" | "info"
    file: str
    line: Optional[int]
    message: str
    hint: Optional[str] = None
    extra: Optional[dict] = None


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def lint_documents(
    spec_root: Path,
    config: IoriSpecConfig,
    section_schema: Optional[SectionSchema],
    glob_pattern: Optional[str] = None,
    ignore_patterns: Optional[List[str]] = None,
    enable_frontmatter: bool = True,
    enable_sections: bool = True,
    enable_ids: bool = True,
) -> List[LintIssue]:
    spec_root = spec_root.resolve()
    ignore_patterns = list(ignore_patterns or [])
    if config and config.paths.ignore_paths:
        for d in config.paths.ignore_paths:
            # ファイル/ディレクトリ/ワイルドカードに柔軟対応
            has_glob = any(ch in d for ch in "*?")
            # スラッシュを含む場合は basename でもマッチさせる
            if "/" in d:
                ignore_patterns.append(Path(d).name)
            if has_glob:
                ignore_patterns.append(d)
                ignore_patterns.append(f"**/{d}")
            else:
                ignore_patterns.append(d)
                ignore_patterns.append(f"**/{d}")
                # ディレクトリ名の場合は配下も含める
                if Path(d).suffix == "":
                    ignore_patterns.extend([f"{d}/**", f"**/{d}/**"])
    issues: List[LintIssue] = []

    docs: List[SpecDocument] = scan_specs(spec_root, glob_pattern=glob_pattern)

    valid_kinds = {k.id for k in config.vocab.kinds} if config else set()
    valid_scopes = {s.id for s in config.vocab.scopes} if config and config.vocab.scopes else set()

    for doc in docs:
        rel = _rel(doc.path, spec_root)
        if any(Path(rel).match(pat) for pat in ignore_patterns):
            continue

        # frontmatter warnings from loader
        if enable_frontmatter and doc.front_matter_errors:
            for err in doc.front_matter_errors:
                issues.append(
                    LintIssue(
                        rule_id="FM-000",
                        severity="error",
                        file=rel,
                        line=1,
                        message=err,
                    )
                )

        fm = doc.front_matter

        if enable_frontmatter:
            required_keys = ["kind", "scope", "id", "spec_title", "status"]
            for key in required_keys:
                if not fm.get(key):
                    issues.append(
                        LintIssue(
                            rule_id="FM-001",
                            severity="error",
                            file=rel,
                            line=doc.frontmatter_range[0] if doc.frontmatter_range else None,
                            message=f"front matter に必須キー {key} がありません。",
                            hint="kind/scope/id/spec_title/status を設定してください。",
                        )
                    )

            if doc.kind and valid_kinds and doc.kind not in valid_kinds:
                issues.append(
                    LintIssue(
                        rule_id="FM-002",
                        severity="error",
                        file=rel,
                        line=doc.frontmatter_range[0] if doc.frontmatter_range else None,
                        message=f"kind '{doc.kind}' は config の定義に含まれていません。",
                        hint=f"有効な kind: {', '.join(sorted(valid_kinds))}",
                    )
                )

            if doc.scope and valid_scopes and doc.scope not in valid_scopes:
                issues.append(
                    LintIssue(
                        rule_id="FM-002",
                        severity="error",
                        file=rel,
                        line=doc.frontmatter_range[0] if doc.frontmatter_range else None,
                        message=f"scope '{doc.scope}' は config の定義に含まれていません。",
                        hint=f"有効な scope: {', '.join(sorted(valid_scopes))}",
                    )
                )

            if doc.status and doc.status not in ALLOWED_STATUS:
                issues.append(
                    LintIssue(
                        rule_id="FM-003",
                        severity="error",
                        file=rel,
                        line=doc.frontmatter_range[0] if doc.frontmatter_range else None,
                        message=f"status '{doc.status}' は許可された値ではありません。",
                        hint=f"許可: {', '.join(sorted(ALLOWED_STATUS))}",
                    )
                )

        if enable_sections and section_schema and doc.kind:
            rules = section_schema.rules_for_kind(doc.kind)
            # required check
            for rule in rules:
                matched_sections = [
                    s for s in doc.sections if heading_matches(rule, s.level, s.heading)
                ]
                if rule.required and not matched_sections:
                    issues.append(
                        LintIssue(
                            rule_id="SEC-001",
                            severity="error",
                            file=rel,
                            line=None,
                            message=f"必須セクション '{rule.heading.text}' がありません。",
                            hint=f"{doc.kind} では {rule.heading.text} が必要です。",
                            extra={"section_id": rule.id},
                        )
                    )
                if not rule.multiple and len(matched_sections) > 1:
                    issues.append(
                        LintIssue(
                            rule_id="SEC-002",
                            severity="warning",
                            file=rel,
                            line=matched_sections[1].start_line,
                            message=f"セクション '{rule.heading.text}' が複数回出現しています。",
                            extra={"section_id": rule.id, "count": len(matched_sections)},
                        )
                    )

        if enable_ids:
            spec_id = fm.get("id")
            if spec_id:
                if not ID_PATTERN.fullmatch(spec_id):
                    issues.append(
                        LintIssue(
                            rule_id="ID-001",
                            severity="error",
                            file=rel,
                            line=doc.frontmatter_range[0] if doc.frontmatter_range else None,
                            message=f"id '{spec_id}' の形式が不正です。",
                            hint="REQ-|IF-|DATA-|TEST-|TASK-|ARCH-|NFR-|REF-|STEER- で始まる数字3桁以上にしてください。",
                        )
                    )

    return issues


def format_lint_text(issues: List[LintIssue]) -> str:
    lines: List[str] = []
    errors = [i for i in issues if i.severity == "error"]
    warns = [i for i in issues if i.severity == "warning"]
    infos = [i for i in issues if i.severity == "info"]
    lines.append(f"[iori-spec] lint issues: {len(issues)} (errors={len(errors)}, warnings={len(warns)}, info={len(infos)})")
    lines.append("")
    for i in issues:
        loc = i.file if i.line is None else f"{i.file}:{i.line}"
        lines.append(f"[{i.severity.upper()}] {i.rule_id} :: {loc}")
        lines.append(f"  - {i.message}")
        if i.hint:
            lines.append(f"  - hint: {i.hint}")
        lines.append("")
    return "\n".join(lines).rstrip()


def format_lint_json(issues: List[LintIssue]) -> str:
    payload = [asdict(i) for i in issues]
    return json.dumps(payload, ensure_ascii=False, indent=2)
