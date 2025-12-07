---
kind: architecture
scope: tooling.cli
id: ARCH-900
spec_title: "ARCH-900: iori-spec Tooling Core — Python Package Architecture"
status: draft

trace:
  req:
    - REQ-800      # iori-spec CLI — Core Tooling Requirements
  if:
    - IF-910       # index
    - IF-920       # lint
    - IF-930       # trace
    - IF-940       # search
    - IF-950       # impact
    - IF-960       # context
    - IF-970       # prompt (拡張)
  data:
    - DATA-900     # spec_index
    - DATA-901     # spec_section_schema
    - DATA-904     # search_result
    - DATA-905     # context_bundle
    - DATA-906     # impact_report
    - DATA-907     # prompt_bundle
    - DATA-910     # iori_spec_config
  test: []
  task: []

dp:
  produces: []
  produced_by: []
  consumes:
    - DATA-910     # 設定を通じて挙動を切り替え
  inputs:
    - reference/iori_spec_config.yaml
    - reference/spec_section_schema.yaml

doc:
  read_next:
    - requirements/REQ-800_tooling_cli.md
    - data_contracts/DATA-910_iori_spec_config.md
    - interfaces/IF-910_spec_index_builder.md
    - interfaces/IF-920_lint_core.md
    - interfaces/IF-930_trace_lint.md
    - interfaces/IF-940_search_specs.md
    - interfaces/IF-950_impact_analyzer.md
    - interfaces/IF-960_context_builder.md
    - interfaces/IF-970_prompt_bundle_builder.md
  see_also:
    - dev-plan.md
    - reference/iori_spec_guide.md
---

# ARCH-900: iori-spec Tooling Core — Python Package Architecture

## LLM_BRIEF

- role: このドキュメントは、`iori-spec` の **Python 実装レベルの箱（パッケージ構成と依存関係）** を定義する
  アーキテクチャ仕様です。
- llm_action: あなた（LLM）は、`iori-spec` の CLI コマンドや IF 実装コードを生成するとき、
  この ARCH-900 を **「どのモジュールに何を書くか」「どのレイヤに依存してよいか」** を判断するための
  ガイドラインとして参照してください。  
  新しいコードは、このレイヤリングと依存方向を壊さないように配置します。

## USAGE

- 人間・LLM ともに、このファイルを参照する場面は次のとおり。
  - 新しく IF / DATA を実装するときに、  
    「`iori_spec.core` / `iori_spec.commands` / `iori_spec.cli` のどこに書くべきか」を判断したい。
  - 既存コードの修正時に、依存関係が逆流していないかを確認したい。
  - dev-plan（実装プラン）をコードレベルにマッピングしたい。
- 実装に迷ったときは：
  - まず REQ-800（要求） → 本 ARCH-900（箱の設計） → 対応する IF / DATA  
    の順で読む。

---

## READ_NEXT

- requirements/REQ-800_tooling_cli.md
- data_contracts/DATA-910_iori_spec_config.md
- interfaces/IF-910_spec_index_builder.md
- interfaces/IF-920_lint_core.md
- interfaces/IF-930_trace_lint.md
- interfaces/IF-940_search_specs.md
- interfaces/IF-950_impact_analyzer.md
- interfaces/IF-960_context_builder.md
- interfaces/IF-970_prompt_bundle_builder.md
- reference/iori_spec_guide.md

---

## 1. このドキュメントの役割

- iori-spec の Python 実装を「どのレイヤに何を書くか」「依存方向はどうするか」の観点で定義する。
- REQ-800 を満たすためのコマンド群（index/lint/search/impact/context/prompt）の箱組みを示し、IF / DATA 実装時の配置ガイドとする。
- 追加のコマンドやモジュールを導入する際に、既存レイヤとの整合性チェックリストとして使う。

---

## 2. 範囲（Scope）と前提

- 範囲: `iori_spec` Python パッケージ内のモジュール分割・依存関係・CLI サブコマンド構成。
- 前提:
  - 設定は DATA-910（iori_spec_config）経由で取得し、core レイヤから直接 YAML を読まない。
  - グラフ系データは DATA-900（spec_index）を SSOT とし、trace/dp/doc 情報はそこから構築する。
  - Section スキーマは DATA-901 を介して扱う。

---

## 3. 運用上の目安（LLM / SDD 観点）

- LLM には本書のレイヤ説明を前提知識として渡し、生成コードが依存方向を逆流させないようにする。
- コード変更時は、REQ-800 → ARCH-900 → 対応 IF / DATA の順に確認し、SpecIndex を更新したうえで lint/trace を回す。
- core レイヤの関数は CLI に閉じず、Python ライブラリとしても利用できる形を維持する。

---

## 1. アーキテクチャのゴール

1. 仕様セットごとに `iori-spec` CLI を導入しやすくすること。
2. index / lint / search / impact / context / prompt という **MUST コマンド**を、  
   共通の SpecIndex / Config / SectionSchema の上に素直に載せること。
3. LLM と協調しやすいように、
   - 単純で予測しやすいパッケージ構造
   - レイヤ間依存が明確で、逆流しない設計
   を保つこと。

このために、`iori-spec` の Python 実装を次の 3 レイヤに分ける。

- Foundation Layer: 低レベルユーティリティ・データ型
- Core Layer: IF 実装（index / lint / search / impact / context / prompt の本体）
- CLI Layer: CLI エントリポイントとサブコマンド定義

---

## 2. パッケージ構成（論理）

最小構成のパッケージツリー（論理的な姿。実際の `__init__.py` 等は実装時に調整）:

```text
iori_spec/
  __init__.py

  config/
    __init__.py
    loader.py              # DATA-910: iori_spec_config.yaml ローダ
    models.py              # IoriSpecConfig / KindDef / ScopeDef 型

    core/
      __init__.py
      types.py               # SpecNode / SpecIndex / Graph などの共通型
    frontmatter.py         # front matter + 本文のパーサ
    section_schema.py      # DATA-901 ローダ／検証
    graph.py               # trace / dp / doc グラフ構築（G_trace / G_dp / G_doc）
    tokens.py              # ざっくりトークン見積もりユーティリティ

    indexer.py             # IF-910: spec_index_builder の実装
    linter.py              # IF-920: lint_core（構造・メタ）
    trace_linter.py        # IF-930: trace
    search.py              # IF-940: search_specs
    impact.py              # IF-950: impact_analyzer
    context_builder.py     # IF-960: context_builder
    prompt_builder.py      # IF-970: prompt_bundle_builder（拡張）

    commands/
      __init__.py
      index_cmd.py           # CLI サブコマンド: index
      lint_cmd.py            # CLI サブコマンド: lint
      trace_cmd.py           # CLI サブコマンド: trace
      search_cmd.py          # CLI サブコマンド: search
      impact_cmd.py          # CLI サブコマンド: impact
      context_cmd.py         # CLI サブコマンド: context
      prompt_cmd.py          # CLI サブコマンド: prompt（拡張）

  cli.py                   # `iori-spec` エントリ（argparse/typer/click など）

  # （将来）tests/
  #   test_index.py
  #   ...
````

依存方向は常に **上から下へのみ** とする：

- `core` → `config`（config を読む）
- `commands` → `core` / `config`
- `cli` → `commands`

---

## 3. レイヤ別の責務

### 3.1 config レイヤ（`iori_spec.config`）

責務:

- `DATA-910_iori_spec_config` に準拠した設定のロードと検証。
- 「どこに spec があるか」「どこに artifacts を出すか」「kind / scope / presets は何か」
  といった **プロジェクト全体の context** を一元的に提供。

主な公開 API:

- `load_config(root: Path | None = None) -> IoriSpecConfig`

  - `reference/iori_spec_config.yaml` を探し、読み込み、`IoriSpecConfig` を返す。
- `find_project_root(start: Path) -> Path`

  - `.git` / `iori_spec_config.yaml` を手掛かりに project root を推定（あれば）。

注意点:

- `core` / `commands` からは、必ずこのレイヤを通じて設定を取得する。
- 各 IF 実装内で `yaml.safe_load` を直接叩かない。

---

### 3.2 core レイヤ（`iori_spec.core`）

責務:

- SpecIndex / Lint / Search / Impact / Context / Prompt の **ビジネスロジック本体**。
- CLI とは独立しており、Python ライブラリとしても利用可能。

#### 3.2.1 共通型・ユーティリティ

- `types.py`

      - `SpecNode`

      - DATA-900 の `nodes[]` 要素に相当する型。
    - `SpecIndex`

      - DATA-900 全体を表す型。
    - その他、`LintIssue`, `SearchHit`, `ImpactEdge`, `ContextBundle`, `PromptBundle` など
      904 / 905 / 906 / 907 に対応する型（lint result 用 schema は将来定義）。
    - `frontmatter.py`

  - Markdown ファイルから `frontmatter: dict` と `body: str` を分離。
- `section_schema.py`

  - DATA-901（spec_section_schema）のロードと検証。
- `graph.py`

  - SpecIndex から G_trace / G_dp / G_doc を構築するユーティリティ。

#### 3.2.2 IF 実装モジュール

- `indexer.py`（IF-910）

  - 入力:

    - `IoriSpecConfig`
    - ファイルシステムから読み出した Markdown
  - 出力:

    - `SpecIndex`（必要なら JSON シリアライズ可能な dict に変換）
    - `linter.py`（IF-920）

      - 入力:

        - Markdown specs + `SpecSectionSchema`
      - 出力:

        - `LintResult`（スキーマは将来 DATA-9xx として定義予定）
    - `trace_linter.py`（IF-930）

      - 入力:

        - `SpecIndex`
      - 出力:

        - `LintResult`（スキーマは将来 DATA-9xx として定義予定、rule_id で trace 系と判別）
- `search.py`（IF-940）

  - 入力:

    - `SpecIndex`
    - 検索クエリ / フィルタ条件
  - 出力:

    - `List[SearchHit]`（DATA-904）
- `impact.py`（IF-950）

  - 入力:

    - `SpecIndex`
    - `changed_ids` / `mode` / `max_distance` 等
  - 出力:

    - `ImpactReport`（DATA-906）
- `context_builder.py`（IF-960）

  - 入力:

    - `SpecIndex`
    - `SpecSectionSchema`
    - seed_ids / roles / max_tokens など
  - 出力:

    - `ContextBundle`（DATA-905）
- `prompt_builder.py`（IF-970）

  - 入力:

    - `ContextBundle`
    - preset / language / extra_instruction
  - 出力:

    - `PromptBundle` (DATA-907)

依存ルール:

- これらの IF 実装は、**相互に強く依存しない**。

  - 例：`impact` は `indexer` に依存せず、`SpecIndex` 型だけに依存する。
- 共同で使う構造は `types.py` / `graph.py` / `section_schema.py` などに切り出す。

---

### 3.3 commands レイヤ（`iori_spec.commands`）

責務:

- CLI サブコマンドから core レイヤの API を呼び出す **薄いアダプタ**。
- 引数のパース結果を core の引数にマッピングし、

  - エラーを適切な例外／exit code に変換
  - DATA-9xx 準拠の JSON / human-readable なテーブルなどに整形して出力する。

各ファイルの役割:

- `index_cmd.py`

  - `cli.py` から `index` サブコマンドとして登録。
  - 内部では `config.load_config()` と `core.indexer.build_spec_index()` を呼び出す。
- `lint_cmd.py`

  - `core.linter.run_lint()` を呼び出し、`--format` に応じて出力整形。
- `trace_lint_cmd.py`

  - `core.trace_linter.run_trace()` を呼び出し（実装名は trace_lint でも可）。
- `search_cmd.py`

  - 入力クエリを受け取り、`core.search.search_specs()` を呼び出し。
- `impact_cmd.py`

  - `core.impact.analyze_impact()` を呼び出し。
- `context_cmd.py`

  - `core.context_builder.build_context_bundle()` を呼び出し。
- `prompt_cmd.py`

  - `core.prompt_builder.build_prompt_bundle()` を呼び出し。

依存ルール:

- `commands` は `core` と `config` のみ参照可。
- `commands` 同士での依存は原則避ける（共通処理は別モジュールに切り出す）。

---

### 3.4 CLI エントリ（`iori_spec.cli`）

責務:

- 引数パーサの初期化とサブコマンド登録。
- 実際の処理は `iori_spec.commands.*` に委譲。

典型的な入口:

```python
def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return dispatch(args)  # 各 commands.* に委譲
```

---

## 4. データフローと IF / DATA の関係

### 4.1 共通パイプラインの鳥瞰図

概念的なデータフロー（MVP）:

```text
Markdown specs
    │
    │  (frontmatter / sections)
    ▼
SpecIndex (DATA-900)  ←── IF-910 (indexer)
    │
    ├─→ IF-920 (linter) ──→ LintResult（スキーマは将来 DATA-9xx として定義予定）
    ├─→ IF-930 (trace_linter) ──→ LintResult（スキーマは将来 DATA-9xx として定義予定）
    ├─→ IF-940 (search) ──→ SearchHit[] (DATA-904)
    ├─→ IF-950 (impact) ──→ ImpactReport (DATA-906)
    └─→ IF-960 (context_builder)
             │
             └─→ ContextBundle (DATA-905)
                      │
                      └─→ IF-970 (prompt_builder)
                               └─→ PromptBundle (DATA-907)
```

- すべての矢印は core レイヤ内の関数呼び出しに対応する。
- commands レイヤは、これらの関数を CLI から呼べるようラップする。

---

## 5. エラーハンドリングとログ

### 5.1 エラー設計

`iori_spec.core` 内では、次のような独自例外を用意する：

- `ConfigError`
- `SpecIndexError`
- `LintError`
- `SearchError`
- `ImpactError`
- `ContextError`
- `PromptError`

commands レイヤでは、これらを捕捉して Exit Code にマッピングする：

- Config 系 / 引数エラー → `exit code 2`（usage error）
- lint / trace-lint での「重大な問題検出」 → `exit code >0`（REQ-800 の RNF と整合）
- 予期しない例外 → `exit code 1`（スタックトレースを表示するモードをオプションで用意してもよい）

### 5.2 ログ

- core レイヤでは `logging.getLogger("iori_spec")` を利用し、

  - debug / info / warning / error を適宜出す。
- CLI では `--verbose` / `--quiet` でログレベルを切り替えられるようにする。

---

## 6. 拡張とテスト

### 6.1 新コマンド追加のパス

新しい CLI コマンド（例: `show`, `scaffold`）を追加する場合のパターン：

1. REQ:

   - REQ-800 に要件を追記するか、RE-8xx 番台で新しい REQ を切る。
2. IF / DATA:

   - `interfaces/IF-9xx_new_command.md`
   - `data_contracts/DATA-9xx_new_command_result.md`（必要なら）
3. Architecture:

   - ここ ARCH-900 に「どのモジュールに追加するか」を追記する。
4. 実装:

   - `iori_spec.core.<something>.py` に IF を実装。
   - `iori_spec.commands.<new>_cmd.py` に CLI アダプタ。
   - `cli.py` にサブコマンド登録。

### 6.2 テスト戦略（概要）

- `tests/` ディレクトリで core レイヤのユニットテストを優先実装。
- CLI レイヤは、pytest + `CliRunner` 的な仕組みで最低限のスモークテストを行う。

---

## 7. 非機能ガイドライン（実装指針）

1. **シンプルな依存**

   - 「core → config」の一方向依存。逆向きは禁止。
2. **シリアライズフレンドリ**

   - DATA-9xx に対応する型は、`dict` / `list` への変換を簡単に行えるようにする。
3. **LLM フレンドリ**

   - モジュール名・関数名は役割が一目で分かるようにする（`build_*` / `run_*` / `load_*` など）。
4. **エントリポイントの安定**

   - core 関数のシグネチャは、IF 仕様で定めたものから大きく逸脱しないようにする。
