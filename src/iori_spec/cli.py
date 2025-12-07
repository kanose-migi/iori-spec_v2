from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

from .config_loader import ConfigError, IoriSpecConfig, load_config
from .spec_loader import scan_specs, format_spec_summary
from .trace_analyzer import analyze_trace, format_trace_text, format_trace_json
from .context_builder import build_context_text
from .section_schema import load_section_schema
from .lint_core import lint_documents, format_lint_json, format_lint_text
from .spec_index_builder import (
    build_spec_index,
    format_spec_index_text,
    save_spec_index,
    spec_index_to_json,
)

try:
    _CLI_VERSION = pkg_version("iori-spec")
except PackageNotFoundError:
    _CLI_VERSION = "0.1.0"


def _prepare_paths(args: argparse.Namespace) -> tuple[Path | None, IoriSpecConfig | None, str | None, int]:
    """config / root を解決して (spec_root, config, glob_pattern, exit_code) を返す。"""
    project_root_hint = getattr(args, "project_root", None)
    config_path = getattr(args, "config", None)
    spec_root_override = getattr(args, "spec_root", None)

    try:
        cfg = load_config(config_path, root_hint=project_root_hint)
        spec_root = cfg.spec_root_path
        if spec_root_override:
            override_path = Path(spec_root_override)
            spec_root = override_path if override_path.is_absolute() else (cfg.project_root / override_path).resolve()
        return spec_root, cfg, cfg.paths.spec_glob, 0
    except FileNotFoundError as exc:
        # config が見つからない場合: 明示指定ならエラー、未指定ならフォールバック
        if config_path is not None:
            print(f"[iori-spec] 設定ファイルが見つかりません: {exc}", file=sys.stderr)
            return None, None, None, 2
        fallback_base = Path(project_root_hint).resolve() if project_root_hint else Path.cwd()
        fallback_root = Path(spec_root_override or "docs")
        if not fallback_root.is_absolute():
            fallback_root = (fallback_base / fallback_root).resolve()
        return fallback_root, None, None, 0
    except ConfigError as exc:
        print(f"[iori-spec] config error: {exc}", file=sys.stderr)
        return None, None, None, 2

def _cmd_scan(args: argparse.Namespace) -> int:
    """Step 0: 共通ローダの動作確認用サブコマンド。

    将来的には `index` / `trace` などに置き換え／分割される想定。
    """
    spec_root, cfg, glob_pattern, status = _prepare_paths(args)
    if status != 0 or spec_root is None:
        return status

    if not spec_root.exists():
        print(f"[iori-spec] root not found: {spec_root}", file=sys.stderr)
        return 1

    docs = scan_specs(spec_root, glob_pattern=glob_pattern)

    print(f"[iori-spec] scanned {len(docs)} spec files under {spec_root}")
    print()

    for doc in docs:
        print(format_spec_summary(doc))
        print("-" * 60)

    return 0

def _cmd_index(args: argparse.Namespace) -> int:
    """仕様書全体のインデックスを構築して出力する。

    - docs: 各ドキュメントごとの kind/scope/spec_title/ID数
    - ids : 各 ID の出現場所一覧
    """
    spec_root, cfg, glob_pattern, status = _prepare_paths(args)
    if status != 0 or spec_root is None:
        return status
    if not spec_root.exists():
        print(f"[iori-spec] root not found: {spec_root}", file=sys.stderr)
        return 1

    pattern = getattr(args, "glob", None) or glob_pattern
    schema = None
    if cfg and cfg.section_schema_path.exists():
        try:
            schema = load_section_schema(cfg.section_schema_path)
        except Exception as exc:
            print(f"[iori-spec] section schema load failed: {exc}", file=sys.stderr)

    index_obj = build_spec_index(
        spec_root=spec_root,
        config=cfg,
        section_schema=schema,
        glob_pattern=pattern,
        ignore_patterns=["**/artifacts/**", "**/.git/**"],
    )

    output_path = None
    if not getattr(args, "no_write", False):
        if args.output == "-":
            output_path = None  # stdout のみ
        elif args.output:
            output_path = Path(args.output)
            if not output_path.is_absolute():
                output_path = spec_root / output_path
        elif cfg is not None:
            output_path = cfg.artifacts_dir_path / "spec_index.json"
        else:
            output_path = (spec_root / "artifacts" / "spec_index.json").resolve()

        if output_path:
            save_spec_index(index_obj, output_path)
            if args.format == "text":
                print(f"[iori-spec] wrote spec index to {output_path}")

    if args.format == "json":
        print(spec_index_to_json(index_obj))
    else:
        print(format_spec_index_text(index_obj))

    return 0

def _cmd_trace(args: argparse.Namespace) -> int:
    """トレーサビリティチェック."""
    spec_root, cfg, glob_pattern, status = _prepare_paths(args)
    if status != 0 or spec_root is None:
        return status
    if not spec_root.exists():
        print(f"[iori-spec] root not found: {spec_root}", file=sys.stderr)
        return 1

    trace_map: Path | None = None
    if args.trace_map is not None:
        trace_map = Path(args.trace_map)

    pattern = getattr(args, "glob", None) or glob_pattern
    ignore_paths = cfg.paths.ignore_paths if cfg else None
    result = analyze_trace(spec_root, trace_map, glob_pattern=pattern, ignore_paths=ignore_paths)

    if args.format == "json":
        print(format_trace_json(result))
    else:
        print(format_trace_text(result))

    # error があれば 1 を返す
    has_error = any(i.severity == "error" for i in result.issues)
    return 1 if has_error else 0

def _cmd_context(args: argparse.Namespace) -> int:
    """指定 ID 周辺のテキストコンテキストを抽出して表示する。"""
    spec_root, cfg, glob_pattern, status = _prepare_paths(args)
    if status != 0 or spec_root is None:
        return status
    if not spec_root.exists():
        print(f"[iori-spec] root not found: {spec_root}", file=sys.stderr)
        return 1

    if not args.ids:
        print("[iori-spec] no IDs given.", file=sys.stderr)
        return 1

    pattern = getattr(args, "glob", None) or glob_pattern
    text = build_context_text(
        root=spec_root,
        target_ids=args.ids,
        radius=args.radius,
        with_lines=args.with_lines,
        glob_pattern=pattern,
    )
    print(text)
    return 0


def _cmd_lint(args: argparse.Namespace) -> int:
    """frontmatter / sections / ids の lint を実行する。"""
    spec_root, cfg, glob_pattern, status = _prepare_paths(args)
    if status != 0 or spec_root is None:
        return status
    if cfg is None:
        print("[iori-spec] lint には --config が必要です。", file=sys.stderr)
        return 2
    if not spec_root.exists():
        print(f"[iori-spec] root not found: {spec_root}", file=sys.stderr)
        return 1

    try:
        section_schema = load_section_schema(cfg.section_schema_path)
    except Exception as exc:
        print(f"[iori-spec] section schema load failed: {exc}", file=sys.stderr)
        return 2

    pattern = getattr(args, "glob", None) or glob_pattern

    # どれか一つでも指定されていればその指定を採用、なければ全カテゴリ有効化
    specified = any([args.frontmatter, args.sections, args.ids])
    enable_frontmatter = args.frontmatter or not specified
    enable_sections = args.sections or not specified
    enable_ids = args.ids or not specified

    issues = lint_documents(
        spec_root=spec_root,
        config=cfg,
        section_schema=section_schema,
        glob_pattern=pattern,
        ignore_patterns=["**/artifacts/**", "**/.git/**"],
        enable_frontmatter=enable_frontmatter,
        enable_sections=enable_sections,
        enable_ids=enable_ids,
    )

    if args.format == "json":
        print(format_lint_json(issues))
    else:
        print(format_lint_text(issues))

    severity_rank = {"error": 3, "warning": 2, "info": 1}
    threshold = severity_rank.get(args.fail_level, 3)
    has_fail = any(severity_rank.get(i.severity, 0) >= threshold for i in issues)
    return 3 if has_fail else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="iori-spec",
        description="Static analysis toolkit for specs (Step 0: loader & scanner).",
    )
    parser.add_argument(
        "--config",
        help="Path to iori_spec_config.yaml (default: search from cwd upward)",
    )
    parser.add_argument(
        "--root",
        dest="project_root",
        help="Project root to resolve config/paths (default: current working directory)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity for debugging (placeholder).",
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="count",
        default=0,
        help="Reduce output verbosity (placeholder).",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {_CLI_VERSION}",
        help="Show version and exit.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan コマンド（Step 0 用）
    p_scan = subparsers.add_parser(
        "scan",
        help="Scan markdown specs under a root directory and show a summary.",
    )
    p_scan.add_argument(
        "spec_root",
        nargs="?",
        default=None,
        help="(Optional) override spec root when config is absent.",
    )
    p_scan.set_defaults(func=_cmd_scan)

    # index コマンド
    p_index = subparsers.add_parser(
        "index",
        help="Build index of specs and IDs under a root directory.",
    )
    p_index.add_argument(
        "spec_root",
        nargs="?",
        default=None,
        help="(Optional) override spec root when config is absent.",
    )
    p_index.add_argument(
        "--glob",
        help="Optional glob pattern to collect specs (overrides config.paths.spec_glob).",
    )
    p_index.add_argument(
        "--output",
        "-o",
        help="Path to output spec_index.json (default: config.artifacts_dir/spec_index.json). Use '-' for stdout only.",
    )
    p_index.add_argument(
        "--no-write",
        action="store_true",
        help="Do not write spec_index.json to file.",
    )
    p_index.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json; default: text)",
    )
    p_index.set_defaults(func=_cmd_index)

    # trace コマンド
    p_trace = subparsers.add_parser(
        "trace",
        help="Check traceability between REQ/IF/DATA/TEST and the traceability map.",
    )
    p_trace.add_argument(
        "spec_root",
        nargs="?",
        default=None,
        help="(Optional) override spec root when config is absent.",
    )
    p_trace.add_argument(
        "--trace-map",
        dest="trace_map",
        help="Path to traceability map markdown "
             "(default: requirements/traceability_map.md under root).",
    )
    p_trace.add_argument(
        "--glob",
        help="Optional glob pattern to collect specs (overrides config.paths.spec_glob).",
    )
    p_trace.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json; default: text)",
    )
    p_trace.set_defaults(func=_cmd_trace)

    # context コマンド
    p_context = subparsers.add_parser(
        "context",
        help="Extract textual context around given IDs.",
    )
    p_context.add_argument(
        "spec_root",
        nargs="?",
        default=None,
        help="(Optional) override spec root when config is absent.",
    )
    p_context.add_argument(
        "--radius",
        type=int,
        default=3,
        help="Lines of context before/after each match (default: 3)",
    )
    p_context.add_argument(
        "--with-lines",
        action="store_true",
        help="Include line numbers in output (for human review).",
    )
    p_context.add_argument(
        "--glob",
        help="Optional glob pattern to collect specs (overrides config.paths.spec_glob).",
    )
    p_context.add_argument(
        "ids",
        nargs="+",
        help="IDs to extract context for (e.g., REQ-001 IF-100).",
    )
    p_context.set_defaults(func=_cmd_context)

    # lint コマンド
    p_lint = subparsers.add_parser(
        "lint",
        help="Lint specs (frontmatter / sections / ids).",
    )
    p_lint.add_argument(
        "spec_root",
        nargs="?",
        default=None,
        help="(Optional) override spec root when config is absent.",
    )
    p_lint.add_argument(
        "--glob",
        help="Optional glob pattern to collect specs (overrides config.paths.spec_glob).",
    )
    p_lint.add_argument(
        "--frontmatter",
        action="store_true",
        help="Enable frontmatter lint only (if specified with others, combine).",
    )
    p_lint.add_argument(
        "--sections",
        action="store_true",
        help="Enable sections lint.",
    )
    p_lint.add_argument(
        "--ids",
        action="store_true",
        help="Enable ids lint.",
    )
    p_lint.add_argument(
        "--fail-level",
        choices=["error", "warning", "info"],
        default="error",
        help="Exit with code 3 if issues at this severity or higher exist (default: error).",
    )
    p_lint.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (text or json; default: text)",
    )
    p_lint.set_defaults(func=_cmd_lint)

    # 今後ここに:
    # - labels
    # などのサブコマンドを追加していく
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())
