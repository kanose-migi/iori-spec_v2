---
kind: data_contracts
scope: tooling.config
id: DATA-910
spec_title: "DATA-910: iori_spec_config — Project-wide Config (YAML)"
status: draft

trace:
  req: []        # 例: REQ-8xx_tooling_cli などを後で紐付け
  if:
    - IF-910     # Spec Index Builder — spec_index.json
    - IF-920     # Lint Core — Frontmatter / Sections Lint
    - IF-960     # Context Builder — Spec IDs → ContextBundle
    - IF-970     # Prompt Bundle Builder — ContextBundle → PromptBundle
  data:
    - DATA-900   # Spec Index Catalog（出力パスなどで参照され得る）
    - DATA-901   # Spec Section Schema（パス指定）
    - DATA-905   # Context Bundle（prompt 設定と連携）
    - DATA-907   # Prompt Bundle（preset / language と連携）
  test: []
  task: []

dp:
  produces:
    - DATA-910   # iori_spec_config.yaml の論理スキーマ
  produced_by: []
  consumes: []
  inputs:
    - reference/iori_spec_config.yaml

doc:
  read_next:
    - DATA-900_spec_index.md
    - DATA-901_iori_spec_section_schema_guide.md
    - interfaces/IF-910_spec_index_builder.md
    - interfaces/IF-920_lint_core.md
    - interfaces/IF-960_context_builder.md
    - interfaces/IF-970_prompt_bundle_builder.md
  see_also:
    - reference/iori_spec_guide.md
---

# DATA-910: iori_spec_config — Project-wide Config (YAML)

## LLM_BRIEF

- role: このファイルは、`reference/iori_spec_config.yaml` の **構造と意味** を定義する
  data_contract です。  
- llm_action: あなた（LLM）は、`IF-910 / IF-920 / IF-960 / IF-970` などを実装するとき、
  この data_contract を **「設定ファイルのスキーマ」** として参照し、
  Python で `IoriSpecConfig` 的なデータクラス／型を定義して読み書きしてください。  
  YAML ファイルそのものを書き換えるのではなく、「ここで定義された構造に従うコード」を書くことが目的です。
- この config は、`paths.*` および `vocab.kinds` を通じて  
  **spec_root と kind↔ディレクトリ対応（標準ディレクトリ構成）の SSOT** となります。  
  README_SPEC.md や iori_spec_guide.md は、この定義を人間向けに説明するビューとして振る舞います。

## USAGE

- 実際の設定ファイルの想定パス：
  - `reference/iori_spec_config.yaml`
- 利用例：
  - `iori-spec index` / `lint` / `context` / `prompt` などのコマンドが、
    - どのディレクトリを spec とみなすか
    - artifacts をどこに出力するか
    - 許可される kind / scope は何か
    - prompt preset は何か
    をこの config から取得する。

---

## READ_NEXT

- DATA-900_spec_index.md
- DATA-901_iori_spec_section_schema_guide.md
- interfaces/IF-910_spec_index_builder.md
- interfaces/IF-920_lint_core.md
- interfaces/IF-960_context_builder.md
- interfaces/IF-970_prompt_bundle_builder.md
- reference/iori_spec_guide.md

---

## 1. このドキュメントの役割

- iori-spec ツール全体で共有される **プロジェクト単位の設定情報** を SSOT 化する。
- 具体的には、以下のような値のスキーマを定義する：
  - spec をどこから読み込むか（root / glob / ignore）
  - artifacts（`spec_index.json` 等）をどこへ出力するか
  - 有効な `kind` / `scope` 一覧
  - section schema のパス
  - LLM prompt 向けの preset / language 設定（MVP では任意・軽量でよい）
- あわせて、以下を明示する：
  - **標準ディレクトリ種別（`steering/`, `requirements/`, `architecture/` など）とその役割**は、
    `vocab.kinds` と `paths.spec_root` によって機械可読に定義される。
  - README_SPEC.md（そのプロジェクト固有の「地図」）や reference/iori_spec_guide.md（iori-spec 共通の「書き方ガイド」）は、  
    この config に記述された情報を前提とする「ビュー」であり、パスやディレクトリ構成の SSOT そのものではない。

- IF-910 / IF-920 / IF-960 / IF-970 は、この data_contract に従って  
  `iori_spec_config.yaml` をパースし、挙動を切り替える。

---

## 2. 範囲（Scope）と前提

- 範囲: `reference/iori_spec_config.yaml` という 1 ファイルの構造と意味を定義する。
- 前提: iori-spec の各 IF（index/lint/context/prompt）は、この config を経由して paths/kinds/scopes/presets を参照する。

---

## 3. 運用上の目安（LLM / SDD 観点）

- config を変更した場合は SpecIndex を再生成し、lint/trace-lint を実行して整合性を保つ。
- 追加した kind/scope は section_schema やテンプレート側にも追記し、SSOT をずらさない。
- preset/system テキストなどの詳細は IF-970 側で管理し、config には「キーと基本情報」を置く。

---

## 4. Summary

- `iori_spec_config.yaml` は、仕様ツール全体の **パス・kind/scope・プリセット** を機械可読に定義する SSOT である。
- IF-910/920/960/970 などすべてのコマンドは、この設定を経由して入出力先や許容値を決定する。
- 人間向けの地図（README_SPEC 等）は補助であり、正式な値の定義は常に本 config に従う。

---

## 5. Schema

- トップレベルは `version` / `project` / `paths` / `vocab` / `prompt`（任意）の 1 オブジェクト。
- `paths.*` には spec_root / spec_glob / artifacts_dir / section_schema_path / ignore_paths を持たせる。
- `vocab.kinds` / `vocab.scopes` は kind/scope の許容リストであり、IF-920 の lint や SpecIndex のフィルタに利用される。
- 詳細なキー構造は以下のセクション「2. 全体構造」「3. フィールド定義」で規定する。

---

## 2. 全体構造（トップレベル）

`reference/iori_spec_config.yaml` のトップレベル構造は、以下のような 1 オブジェクトとする：

```yaml
version: 1
project:
  name: "goro-dict"
  description: "数字列 → 日本語語呂合わせ辞書の仕様セット"
paths:
  spec_root: "docs"
  spec_glob: "docs/**/*.md"
  artifacts_dir: "artifacts"
  section_schema_path: "reference/spec_section_schema.yaml"
  ignore_paths:
    - "impl_notes"
vocab:
  kinds:
    - id: "requirements"
      label: "Requirements"
      dir: "requirements"
    - id: "interfaces"
      label: "Interfaces"
      dir: "interfaces"
  scopes:
    - id: "client.query_engine"
      label: "Client: Query Engine"
    - id: "build_system"
      label: "Build System"
prompt:
  default_language: "ja"
  presets:
    default.codegen:
      description: "仕様からコードを生成するプリセット"
      language: "ja"
    default.review:
      description: "仕様・コードレビュー用プリセット"
      language: "ja"
````

> ここに示す値はあくまで例であり、実プロジェクトでは内容を書き換えてよい。
> データ構造（キー・型）は本 data_contract に従う必要がある。

---

## 3. フィールド定義

### 3.1 version

| フィールド     | 型   | 必須  | 説明                                 |
| --------- | --- | --- | ---------------------------------- |
| `version` | int | Yes | config スキーマのバージョン番号。現時点では `1` を想定。 |

- 将来、スキーマを後方互換性を壊す形で変更する場合に備えたバージョン識別子。
- 実装側は、未知バージョンの場合に警告を出したり、サポート対象外として扱うことができる。

---

### 3.2 project セクション

```yaml
project:
  name: "goro-dict"
  description: "..."
```

| フィールド                 | 型      | 必須  | 説明              |
| --------------------- | ------ | --- | --------------- |
| `project.name`        | string | Yes | プロジェクト名（短い識別名）。 |
| `project.description` | string | No  | プロジェクトの説明テキスト。  |

- ツールの挙動には直接は関係しないが、

  - ログ出力
  - LLM プロンプトの meta 情報
    などに使うことを想定。

---

### 3.3 paths セクション

```yaml
paths:
  spec_root: "docs"
  spec_glob: "docs/**/*.md"
  artifacts_dir: "artifacts"
  section_schema_path: "reference/spec_section_schema.yaml"
  ignore_paths:
    - "impl_notes"
```

| フィールド                       | 型      | 必須  | 説明                                                |
| --------------------------- | ------ | --- | ------------------------------------------------- |
| `paths.spec_root`           | string | Yes | 仕様書のルートディレクトリ（リポジトリ root からの相対パス）。                |
| `paths.spec_glob`           | string | No  | 仕様書を列挙するための glob パターン。未指定時は `spec_root` 配下すべてを対象。 |
| `paths.artifacts_dir`       | string | Yes | `spec_index.json` など artifacts を出力するディレクトリ。       |
| `paths.section_schema_path` | string | Yes | `spec_section_schema.yaml`（DATA-901）のパス。          |
| `paths.ignore_paths`        | string[] | No  | lint / index などの走査対象から除外するパス（ファイルまたはディレクトリ、`spec_root` 相対、glob 可）。 |

- IF-910（index）は、

  - `spec_root` / `spec_glob` を使って Markdown を列挙し、
  - `artifacts_dir` に `spec_index.json`（DATA-900）を出力し、
  - `section_schema_path` を使って DATA-901 を読み込む。
  - `ignore_paths` に指定されたパス（例: `impl_notes/`）は index 対象から除外する。
- IF-920 / IF-960 なども `section_schema_path` を利用する。
- `ignore_paths` は lint / index など共通のスキャン処理で使用し、`spec_root` 相対のディレクトリ名または glob を受け付ける。
- プロジェクト固有の README_SPEC.md では、`spec_root` を前提としたパス（例: `spec_root/requirements/`）を地図として説明し、
  物理パスの正式な定義は常に本 config に従うことを推奨する。

---

### 3.4 vocab セクション

```yaml
vocab:
  kinds:
    - id: "requirements"
      label: "Requirements"
      dir: "requirements"
    - id: "interfaces"
      label: "Interfaces"
      dir: "interfaces"
  scopes:
    - id: "client.query_engine"
      label: "Client: Query Engine"
    - id: "build_system"
      label: "Build System"
```

#### 3.4.1 kinds

| フィールド           | 型         | 必須  | 説明                                   |
| --------------- | --------- | --- | ------------------------------------ |
| `vocab.kinds`   | KindDef[] | Yes | 有効な kind の一覧。                        |
| `KindDef.id`    | string    | Yes | kind の内部 ID（例: `"requirements"`）。    |
| `KindDef.label` | string    | No  | 人間向けラベル。                             |
| `KindDef.dir`   | string    | No  | 主に配置されるディレクトリ名（例: `"requirements"`）。 |

- front matter の `kind` に書ける値は、この `KindDef.id` に制限される想定。
- `dir` は、`kind` とディレクトリ構造を紐付けるために使える（必須ではない）。
- iori-spec は「標準」としていくつかの kind / dir を推奨するが、
  プロジェクトごとに追加・削除してもよい（後述 3.4.3 参照）。

#### 3.4.2 scopes

| フィールド            | 型          | 必須  | 説明                                        |
| ---------------- | ---------- | --- | ----------------------------------------- |
| `vocab.scopes`   | ScopeDef[] | No  | 有効な scope の一覧。                            |
| `ScopeDef.id`    | string     | Yes | scope の内部 ID（例: `"client.query_engine"`）。 |
| `ScopeDef.label` | string     | No  | 人間向けラベル。                                  |

- front matter の `scope` に書ける値をここで制限したい場合に使う。
- `vocab.scopes` が未指定の場合、scope は自由文字列として扱ってもよい（IF-920 の lint ルール次第）。

#### 3.4.3 iori-spec 標準の kinds / ディレクトリ

iori-spec は、仕様セットを整理するための **標準ディレクトリ種別と意味** を定義する。
代表的な例（推奨セット）は次のとおり。

```yaml
vocab:
  kinds:
    - id: "steering"
      label: "Steering (Why / Where)"
      dir: "steering"
    - id: "requirements"
      label: "Requirements (What)"
      dir: "requirements"
    - id: "architecture"
      label: "Architecture (How, at system level)"
      dir: "architecture"
    - id: "data_contracts"
      label: "Data Contracts"
      dir: "data_contracts"
    - id: "interfaces"
      label: "Interfaces / Modules"
      dir: "interfaces"
    - id: "tests"
      label: "Test Specs"
      dir: "tests"
    - id: "dev_tasks"
      label: "Dev Tasks / Work Items"
      dir: "dev_tasks"
    - id: "impl_notes"
      label: "Implementation Notes"
      dir: "impl_notes"
```

- これらの `id` / `dir` 組み合わせは **iori-spec としての標準レイアウト** であり、
  iori_spec_guide.md ではそれぞれの役割（「steering はビジョン・方針」「requirements は REQ-xxx」といった意味）が説明される。
- 各プロジェクトは、この標準セットをベースにして：

  - 一部の kind を採用しない
  - 独自の kind を追加する
    といった拡張をしてもよい。
- README_SPEC.md 側では、この標準セットのうち「このプロジェクトで使うもの」を
  `spec_root/steering/`, `spec_root/requirements/` のように説明するだけに留め、
  **kind↔dir の正式な対応や意味の定義は iori-spec 側（本 DATA-910 および iori_spec_guide.md）を参照する** ことを推奨する。

---

### 3.5 prompt セクション（任意）

```yaml
prompt:
  default_language: "ja"
  presets:
    default.codegen:
      description: "仕様からコードを生成するプリセット"
      language: "ja"
    default.review:
      description: "仕様・コードレビュー用プリセット"
      language: "ja"
```

| フィールド                     | 型                   | 必須 | 説明                                |
| ------------------------- | ------------------- | -- | --------------------------------- |
| `prompt.default_language` | string \| null       | No | プロンプトのデフォルト言語（例: `"ja"`, `"en"`）。 |
| `prompt.presets`          | map<string, Preset> | No | preset 名 → 設定のマップ。                |

Preset の構造（最低限）：

| フィールド                | 型      | 必須 | 説明            |
| -------------------- | ------ | -- | ------------- |
| `Preset.description` | string | No | プリセットの説明。     |
| `Preset.language`    | string | No | このプリセットの標準言語。 |

- IF-970（Prompt Bundle Builder）は、

  - `preset` 引数で与えられたキー（例: `"default.codegen"`）を、
  - `prompt.presets` のキーと突き合わせて動作を切り替えることができる。
- MVP では、`system` / `user` のテンプレート本文はコード側に持たせ、

  - config には「どのプリセットが存在するか」と「言語のデフォルト」を置く程度でもよい。
- 将来的に、テンプレート本文を `iori_spec_config.yaml` 側に移したい場合は、

  - `Preset.system_template`
  - `Preset.user_template`
    などを optional フィールドとして DATA-910 に追加する。

---

## 4. 型まとめ（擬似スキーマ）

参考として、Python 的な型イメージを示す。

```python
from dataclasses import dataclass
from typing import Dict, List, Optional


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
    # 将来拡張:
    # system_template: Optional[str] = None
    # user_template: Optional[str] = None


@dataclass
class PromptConfig:
    default_language: Optional[str] = None
    presets: Dict[str, PromptPresetDef] = None


@dataclass
class VocabConfig:
    kinds: List[KindDef]
    scopes: Optional[List[ScopeDef]] = None


@dataclass
class PathsConfig:
    spec_root: str
    artifacts_dir: str
    spec_glob: Optional[str] = None
    section_schema_path: str = "reference/spec_section_schema.yaml"
    ignore_paths: List[str] = []


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
    prompt: Optional[PromptConfig] = None
```

---

## 5. Constraints（制約）

- `version` は必ず存在し、現行実装がサポートする値（例: `1`）でなければならない。
- `paths.spec_root` / `paths.artifacts_dir` / `paths.section_schema_path` は必須。
- `vocab.kinds` は 1 要素以上を含む配列であること。
- `prompt` セクションは省略可能だが、存在する場合はここで定義した構造に従う。
- 余計なトップレベルキーがあってもよいが、

  - IF / DATA 群が参照するのは基本的に本 data_contract で定義されたキーのみとする。

---

## 6. IF との関係

- **IF-910_spec_index_builder**

  - `paths.spec_root` / `paths.spec_glob` / `paths.artifacts_dir` / `paths.section_schema_path` を使用。
- **IF-920_lint_core**

  - `paths.section_schema_path` と `vocab.kinds` / `vocab.scopes` を使用。
- **IF-960_context_builder**

  - `paths.section_schema_path`（DATA-901）や、将来的には scope 単位の設定を参照し得る。
- **IF-970_prompt_bundle_builder**

  - `prompt.default_language` / `prompt.presets` を利用して、
    PromptBundle（DATA-907）の言語や挙動を切り替える。

---

## 7. 今後の拡張（メモ）

- `paths` 配下に、テスト用 / draft 用などの追加パス設定を設ける案。
- `vocab` 配下に、role や ID プレフィックス（`REQ-`, `IF-` など）の定義を追加する案。
- `prompt.presets` に、model 名 / 温度 / max_tokens など LLM 呼び出しパラメータを持たせる案。
  → その場合は provider-specific な IF（例: IF-975_provider_prompt_adapter）と連携する。

---

## 8. SSOT と他ドキュメントとの関係

- **物理レイアウトの SSOT**

  - `paths.*` と `vocab.kinds[].dir` は、
    「どのディレクトリにどの kind の spec が置かれるか」の **唯一の機械可読な定義** である。
  - ツール実装は、README_SPEC.md や iori_spec_guide.md ではなく
    **常に本 config を参照してパスを解決する** こと。

- **README_SPEC.md（プロジェクト地図）**

  - 各プロジェクト固有の「Repository Map（概要）」を提供するが、
    ディレクトリ種別や kind↔dir 対応の正式な定義は行わない。
  - 代わりに、「正式な定義は `reference/iori_spec_config.yaml`（DATA-910）を参照」と明記する。

- **reference/iori_spec_guide.md（iori-spec 共通ガイド）**

  - iori-spec フレームワークとしての

    - kind の意味（`steering`, `requirements`, など）
    - 1ファイル1ID 原則
    - trace / IF / DATA の付け方
      を説明するテキストガイドであり、
      物理パス自体は DATA-910 / `iori_spec_config.yaml` に委ねる。

- この 3 者を分離することで：

  - パスやディレクトリ構成の SSOT は 1 箇所（本 DATA-910 + YAML 実体）にまとまり、
  - 人間向けの説明やプロジェクト固有の地図は、ビューとして柔軟に更新できる。



