from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml


class ConfigError(Exception):
    """設定ファイルの読み込み・検証エラー。"""


@dataclass
class KindDef:
    id: str
    label: Optional[str] = None
    dir: Optional[str] = None


@dataclass
class ScopeDef:
    id: str
    label: Optional[str] = None


@dataclass
class PromptPresetDef:
    description: Optional[str] = None
    language: Optional[str] = None


@dataclass
class PromptConfig:
    default_language: Optional[str] = None
    presets: Dict[str, PromptPresetDef] = field(default_factory=dict)


@dataclass
class VocabConfig:
    kinds: List[KindDef]
    scopes: List[ScopeDef] = field(default_factory=list)


@dataclass
class PathsConfig:
    spec_root: str
    artifacts_dir: str
    section_schema_path: str
    spec_glob: Optional[str] = None
    ignore_paths: List[str] = field(default_factory=list)


@dataclass
class ProjectConfig:
    name: str
    description: Optional[str] = None


@dataclass
class IoriSpecConfig:
    version: int
    project: ProjectConfig
    paths: PathsConfig
    vocab: VocabConfig
    prompt: Optional[PromptConfig]
    project_root: Path

    spec_root_path: Path = field(init=False)
    artifacts_dir_path: Path = field(init=False)
    section_schema_path: Path = field(init=False)

    def __post_init__(self) -> None:
        self.spec_root_path = _resolve_path(self.project_root, Path(self.paths.spec_root))
        self.artifacts_dir_path = _resolve_path(self.project_root, Path(self.paths.artifacts_dir))
        self.section_schema_path = _resolve_path(
            self.project_root, Path(self.paths.section_schema_path)
        )


def _resolve_path(base: Path, candidate: Path) -> Path:
    return candidate if candidate.is_absolute() else (base / candidate).resolve()


def _find_project_root(start: Path) -> Path:
    """`.git` または `pyproject.toml` を手掛かりにプロジェクトルートを推定する。"""
    for current in [start] + list(start.parents):
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            return current
    return start.resolve()


def find_config_path(start: Path) -> Optional[Path]:
    """カレント（または start）から親方向に設定ファイルを探索する。"""
    candidates = [
        Path("iori_spec_config.yaml"),
        Path("reference") / "iori_spec_config.yaml",
        Path("docs") / "reference" / "iori_spec_config.yaml",
    ]

    for current in [start] + list(start.parents):
        for rel in candidates:
            candidate = (current / rel).resolve()
            if candidate.is_file():
                return candidate
    return None


def _expect_dict(obj: Any, context: str) -> Dict[str, Any]:
    if not isinstance(obj, dict):
        raise ConfigError(f"{context} はオブジェクト(dict)である必要があります。")
    return obj


def _parse_kinds(raw_kinds: Any) -> List[KindDef]:
    kinds_list: List[KindDef] = []
    for entry in raw_kinds or []:
        entry_dict = _expect_dict(entry, "vocab.kinds[]")
        kind_id = entry_dict.get("id")
        if not isinstance(kind_id, str) or not kind_id:
            raise ConfigError("vocab.kinds[].id は非空文字列である必要があります。")
        kinds_list.append(
            KindDef(
                id=kind_id,
                label=entry_dict.get("label"),
                dir=entry_dict.get("dir"),
            )
        )
    if not kinds_list:
        raise ConfigError("vocab.kinds は 1 件以上の要素を持つ必要があります。")
    return kinds_list


def _parse_scopes(raw_scopes: Any) -> List[ScopeDef]:
    scopes: List[ScopeDef] = []
    for entry in raw_scopes or []:
        entry_dict = _expect_dict(entry, "vocab.scopes[]")
        scope_id = entry_dict.get("id")
        if not isinstance(scope_id, str) or not scope_id:
            raise ConfigError("vocab.scopes[].id は非空文字列である必要があります。")
        scopes.append(
            ScopeDef(
                id=scope_id,
                label=entry_dict.get("label"),
            )
        )
    return scopes


def _parse_prompt(raw_prompt: Any) -> Optional[PromptConfig]:
    if raw_prompt is None:
        return None
    prompt_dict = _expect_dict(raw_prompt, "prompt")
    default_lang = prompt_dict.get("default_language")
    if default_lang is not None and not isinstance(default_lang, str):
        raise ConfigError("prompt.default_language は文字列である必要があります。")

    presets_raw = prompt_dict.get("presets", {})
    if presets_raw is None:
        presets_raw = {}
    presets_dict = _expect_dict(presets_raw, "prompt.presets")

    presets: Dict[str, PromptPresetDef] = {}
    for key, value in presets_dict.items():
        value_dict = _expect_dict(value, f"prompt.presets.{key}")
        presets[key] = PromptPresetDef(
            description=value_dict.get("description"),
            language=value_dict.get("language"),
        )

    return PromptConfig(default_language=default_lang, presets=presets)


def _parse_paths(raw_paths: Any) -> PathsConfig:
    paths_dict = _expect_dict(raw_paths, "paths")
    try:
        spec_root = paths_dict["spec_root"]
        artifacts_dir = paths_dict["artifacts_dir"]
        section_schema_path = paths_dict["section_schema_path"]
    except KeyError as exc:
        raise ConfigError(f"paths セクションに必須キー {exc} がありません。") from exc

    for key, value in [
        ("paths.spec_root", spec_root),
        ("paths.artifacts_dir", artifacts_dir),
        ("paths.section_schema_path", section_schema_path),
    ]:
        if not isinstance(value, str) or not value:
            raise ConfigError(f"{key} は非空文字列である必要があります。")

    spec_glob = paths_dict.get("spec_glob")
    if spec_glob is not None and not isinstance(spec_glob, str):
        raise ConfigError("paths.spec_glob は文字列または未指定にしてください。")

    ignore_paths_raw = paths_dict.get("ignore_paths", [])
    ignore_paths: List[str] = []
    if ignore_paths_raw is None:
        ignore_paths_raw = []
    if not isinstance(ignore_paths_raw, list):
        raise ConfigError("paths.ignore_paths は文字列の配列である必要があります。")
    for d in ignore_paths_raw:
        if not isinstance(d, str) or not d.strip():
            raise ConfigError("paths.ignore_paths は非空文字列の配列である必要があります。")
        ignore_paths.append(d.strip())

    return PathsConfig(
        spec_root=spec_root,
        artifacts_dir=artifacts_dir,
        section_schema_path=section_schema_path,
        spec_glob=spec_glob,
        ignore_paths=ignore_paths,
    )


def load_config(
    config_path: str | Path | None = None,
    root_hint: str | Path | None = None,
) -> IoriSpecConfig:
    """iori_spec_config.yaml をロードし、検証済みオブジェクトとして返す。"""

    start_dir = Path(root_hint).resolve() if root_hint is not None else Path.cwd()

    resolved_config: Optional[Path] = None
    if config_path is not None:
        candidate = Path(config_path)
        resolved_config = (start_dir / candidate).resolve() if not candidate.is_absolute() else candidate
        if not resolved_config.is_file():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {resolved_config}")
    else:
        resolved_config = find_config_path(start_dir)
        if resolved_config is None:
            raise FileNotFoundError("iori_spec_config.yaml が見つかりませんでした。--config で指定してください。")

    raw = yaml.safe_load(resolved_config.read_text(encoding="utf-8")) or {}
    root_obj = _expect_dict(raw, "config root")

    version = root_obj.get("version")
    if not isinstance(version, int):
        raise ConfigError("version は整数である必要があります。")

    project_raw = root_obj.get("project", {})
    project_dict = _expect_dict(project_raw, "project")
    project_name = project_dict.get("name")
    if not isinstance(project_name, str) or not project_name:
        raise ConfigError("project.name は非空文字列である必要があります。")
    project = ProjectConfig(
        name=project_name,
        description=project_dict.get("description"),
    )

    paths = _parse_paths(root_obj.get("paths"))
    vocab_raw = _expect_dict(root_obj.get("vocab", {}), "vocab")
    vocab = VocabConfig(
        kinds=_parse_kinds(vocab_raw.get("kinds")),
        scopes=_parse_scopes(vocab_raw.get("scopes")),
    )
    prompt = _parse_prompt(root_obj.get("prompt"))

    project_root = _find_project_root(resolved_config.parent)

    return IoriSpecConfig(
        version=version,
        project=project,
        paths=paths,
        vocab=vocab,
        prompt=prompt,
        project_root=project_root,
    )
