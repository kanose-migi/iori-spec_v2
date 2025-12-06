---
kind: interfaces
scope: tooling.cli
id: IF-900
spec_title: "IF-900: iori-spec CLI — Command-Line Interface"
status: draft

trace:
  req:
    - REQ-800      # iori-spec CLI — Core Tooling Requirements
  if:
    - IF-910       # spec_index_builder
    - IF-920       # lint_core
    - IF-930       # trace_lint
    - IF-940       # search_specs
    - IF-950       # impact_analyzer
    - IF-960       # context_builder
    - IF-970       # prompt_bundle_builder
  data:
    - DATA-900     # spec_index
    - DATA-901     # spec_section_schema
    - DATA-902     # lint_result
    - DATA-904     # search_result
    - DATA-905     # context_bundle
    - DATA-906     # impact_report
    - DATA-907     # prompt_bundle
    - DATA-910     # iori_spec_config
  test: []
  task: []

dp:
  produces: []
  produced_by:
    - IF-900
  consumes:
    - DATA-910     # config からパスやプリセットを取得
  inputs:
    - reference/iori_spec_config.yaml

doc:
  read_next:
    - requirements/REQ-800_tooling_cli.md
    - architecture/ARCH-900_tooling_core.md
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

# IF-900: iori-spec CLI — Command-Line Interface

## LLM_BRIEF

- role: この IF は、`iori-spec` CLI の **サブコマンド構成・オプション・入出力・Exit Code** を定義します。
- llm_action: あなた（LLM）は、`iori_spec.cli` や `iori_spec.commands.*` を実装するとき、
  この IF-900 を **「CLI レイヤの仕様」** として参照し、
  - ここで定義されたコマンド名・オプション名
  - `--format json` 時の DATA-9xx 対応
  - Exit Code ポリシー
  を守るようにコードを生成してください。  
  core レイヤ（IF-910〜970）や DATA-9xx の仕様は別ファイルを参照します。

## USAGE

- エントリポイントは常に次の形をとる：

  ```bash
  iori-spec [GLOBAL_OPTIONS] <command> [COMMAND_OPTIONS]
  ````

- 主なサブコマンド：

  - `index`      … SpecIndex（DATA-900）の生成
  - `lint`       … 構造・メタ情報 lint（DATA-902）
  - `trace-lint` … トレーサビリティ lint（DATA-902）
  - `search`     … SpecIndex ベースの検索（DATA-904）
  - `impact`     … 影響範囲の列挙（DATA-906）
  - `context`    … 局所コンテキスト（DATA-905）
  - `prompt`     … PromptBundle の生成（DATA-907, 拡張）

## READ_NEXT

- REQ-800: iori-spec CLI — Core Tooling Requirements
- ARCH-900: iori-spec Tooling Core — Python Package Architecture
- 対応する IF-910〜970 / DATA-9xx 群

---

## 1. このドキュメントの役割

- `iori-spec` CLI の **外部インターフェイス**（コマンド名・オプション・入出力フォーマット・Exit Code）を定義する。
- 実装レベルでは：

  - `iori_spec.cli.main()` がこの仕様どおりの CLI を提供すること。
  - `iori_spec.commands.*` が core レイヤ（IF-910〜970）の関数をラップすること。
- REQ-800 / ARCH-900 と IF-910〜970 / DATA-9xx の橋渡しをする。

---

## 2. 範囲（Scope）と前提

- 対象: `iori-spec` CLI のサブコマンドと共通オプション、Exit Code ポリシー。
- 前提: 各サブコマンドは対応する IF-910?970 / DATA-9xx を実装済みで、`reference/iori_spec_config.yaml` を経由してパスや kind/scope を解決する。

---

## 3. 運用上の目安（LLM / SDD 観点）

- 定期ジョブでは config の `paths.ignore_dirs` を尊重して index/lint 系を実行する。
- `--format json` を利用する場合、標準出力は機械読取用、ログは標準エラーに分離する。
- Exit Code 0/1/2 は品質ゲートや CI 判定に用いることを想定する。

---

## 4. Summary

- `iori-spec` の CLI エントリポイントとして、index/lint/trace-lint/search/impact/context/prompt を提供する。
- すべてのコマンドが DATA-910 を起点に環境を解決し、DATA-9xx を入出力として扱う。

---

## 5. Inputs

- `reference/iori_spec_config.yaml`（DATA-910）
- `artifacts/spec_index.json`（DATA-900、必要に応じて）
- その他 DATA-9xx（lint/search/impact/context/prompt で利用する中間データ）

---

## 6. Outputs

- 各コマンドの標準出力（`--format` に応じて DATA-9xx 相当）
- Exit Code（0: 正常、1: 仕様上のエラー、2: 実行時エラー）

---

## 7. CLI 全体構造

### 7.1 コマンド一覧

- `index`      … SpecIndex（DATA-900）をビルドする必須コマンド。
- `lint`       … frontmatter / sections / ids の lint（DATA-902）。
- `trace-lint` … trace グラフベースの lint（DATA-902）。
- `search`     … SpecIndex に対する検索（DATA-904）。
- `impact`     … trace / dp / doc グラフに基づく影響範囲列挙（DATA-906）。
- `context`    … LLM 向け ContextBundle（DATA-905）の生成。
- `prompt`     … ContextBundle から PromptBundle（DATA-907）を生成する拡張コマンド。

### 7.2 グローバルオプション

すべてのサブコマンドが共通で受け取るオプション：

- `--config PATH`

  - 説明: `reference/iori_spec_config.yaml` のパスを明示的に指定。
  - 省略時: カレントディレクトリから上位へ探索し、最初に見つかったものを使用。
- `--root PATH`

  - 説明: プロジェクト root を強制指定。config や paths の解決に利用。
  - 省略時: `--config` の位置、またはカレントディレクトリから推定。
- `--format FORMAT`

  - 説明: 出力形式の指定。
  - 候補: `json` / `table` / `markdown`
  - デフォルト: サブコマンドごとに人間向けの形式（`table` or `markdown`）。
- `--verbose`, `-v`

  - 説明: ログレベルを上げて debug 情報を表示。
- `--quiet`, `-q`

  - 説明: 最低限のメッセージのみを表示（JSON 出力時などに便利）。
- `--version`

  - 説明: `iori-spec` CLI のバージョンを表示して終了。
- `--help`

  - 説明: 全体またはサブコマンドのヘルプを表示して終了。

### 7.3 Exit Code ポリシー

- `0`:

  - 正常終了。
    lint / trace-lint では「指定された fail-level 以上の問題がない」状態を含む。
- `1`:

  - 処理系エラー（内部エラー・予期しない例外など）。
- `2`:

  - CLI 使用方法エラー / config ロードエラーなどの usage エラー。
- `3`:

  - lint / trace-lint で **重大な問題** が見つかった場合（fail-level 以上）。

> 実装では `3` 番の意味を「lint 的なドメインエラー」として扱い、
> CI からは `== 0` or `== 3` を見て判断できるようにする。

---

## 8. グローバル構文

構文定義（擬似 BNF）：

```text
iori-spec
  := "iori-spec" GLOBAL_OPTIONS? COMMAND COMMAND_OPTIONS?

GLOBAL_OPTIONS
  := ("--config" PATH)?
     ("--root" PATH)?
     ("--format" FORMAT)?
     ("--verbose" | "--quiet")*
     ("--version")?
     ("--help")?

COMMAND
  := "index"
   | "lint"
   | "trace-lint"
   | "search"
   | "impact"
   | "context"
   | "prompt"
```

- 各 COMMAND の OPTIONS は後述。

---

## 9. コマンド仕様

### 9.1 `index` コマンド

#### 9.1.1 目的

- SpecIndex（DATA-900）を生成し、`DATA-910.paths.artifacts_dir` 配下に
  `spec_index.json` を書き出す。

#### 9.1.2 シグネチャ

```bash
iori-spec index [--format json|table|markdown] [--no-write]
```

- `--no-write`

  - 説明: `spec_index.json` をファイルに書き出さず、標準出力のみに出す。
  - デフォルト: false（書き出しあり）。

#### 9.1.3 入出力

- 入力:

  - `reference/iori_spec_config.yaml`（DATA-910）
  - config が指す `paths.spec_root` / `paths.spec_glob` 配下の Markdown specs
  - `paths.section_schema_path`（DATA-901）
- 出力:

  - `artifacts/spec_index.json`（DATA-900）
  - `--format json` 指定時:

    - 標準出力に DATA-900 準拠の JSON 1 オブジェクト。
  - `--format table` / `markdown` 指定時:

    - 人間向けサマリ（件数など）を標準出力。

#### 9.1.4 Exit Code

- `0`: 正常に SpecIndex を生成。
- `1`: ファイル I/O などの内部エラー。
- `2`: config が見つからない / 破損している。
- `3`: 使用しない（lint 専用）。

---

### 9.2 `lint` コマンド

#### 9.2.1 目的

- frontmatter / sections / ids などの **構造・メタ情報** を lint し、
  DATA-902 として Issue リストを返す。

#### 9.2.2 シグネチャ

```bash
iori-spec lint [--format json|table|markdown] [--fail-level LEVEL]
```

- `--fail-level LEVEL`

  - 説明: Exit Code=3 とみなす最小 severity。
  - 候補: `error` / `warning` / `info`
  - デフォルト: `error`

#### 9.2.3 入出力

- 入力:

  - config（DATA-910）
  - section schema（DATA-901）
  - spec_root / spec_glob 配下の Markdown specs
- 出力:

  - DATA-902_lint_result
  - `--format json` 指定時:

    - DATA-902 準拠の JSON。
  - `--format table` / `markdown`:

    - filename / id / rule / severity / message を含む一覧。

#### 9.2.4 Exit Code

- `0`: fail-level 以上の Issue なし。
- `3`: fail-level 以上の Issue を 1 件以上検出。
- `1` / `2`: index と同様。

---

### 9.3 `trace-lint` コマンド

#### 9.3.1 目的

- SpecIndex（DATA-900）から G_trace を構築し、
  REQ ↔ IF / DATA / TEST のトレーサビリティ健全性を lint する。

#### 9.3.2 シグネチャ

```bash
iori-spec trace-lint [--format json|table|markdown] [--fail-level LEVEL]
```

- `--fail-level` の意味は `lint` と同様。

#### 9.3.3 入出力

- 入力:

  - `artifacts/spec_index.json`（DATA-900）

    - なければ `index` 相当の処理で一時的に構築してもよい。
- 出力:

  - DATA-902_lint_result（rule_id で trace 系ルールと判別可能）。

#### 9.3.4 Exit Code

- `0`: fail-level 以上のトレーサビリティ問題なし。
- `3`: fail-level 以上の問題を検出。
- `1` / `2`: index と同様。

---

### 9.4 `search` コマンド

#### 9.4.1 目的

- SpecIndex（DATA-900）に対して、ID / spec_title / scope を中心に
  シンプルな全文検索を行う。

#### 9.4.2 シグネチャ

```bash
iori-spec search <query> [--kinds K1,K2,...] [--roles R1,R2,...] [--scopes S1,S2,...] [--limit N] [--format json|table|markdown]
```

- `<query>`

  - 説明: 検索キーワード。スペース区切りで AND 検索（MVP）。
- `--kinds`

  - 説明: `requirements,interfaces,data_contracts,...` のカンマ区切り。
- `--roles`

  - 説明: `req,if,data,test,task` のカンマ区切り。
- `--scopes`

  - 説明: `client.query_engine,build_system,...` など scope ID のカンマ区切り。
- `--limit`

  - 説明: 最大ヒット件数。デフォルト: 20。

#### 9.4.3 入出力

- 入力:

  - SpecIndex（DATA-900）
- 出力:

  - DATA-904_search_result（SearchHit[]）
  - JSON モードでは厳密に DATA-904 準拠。

#### 9.4.4 Exit Code

- `0`: 正常終了（ヒットが 0 件でも 0）。
- `1` / `2`: エラー時。
- `3`: 使用しない。

---

### 9.5 `impact` コマンド

#### 9.5.1 目的

- 指定 ID 群を起点とし、trace / dp / doc グラフ上の影響範囲を列挙する。

#### 9.5.2 シグネチャ

```bash
iori-spec impact <ID...> [--mode forward|backward|both] [--max-distance N] [--roles R1,R2,...] [--format json|table|markdown]
```

- `<ID...>`

  - 説明: impact の起点とする spec ID 群（例: `REQ-201 IF-200`）。
- `--mode`

  - デフォルト: `both`
- `--max-distance`

  - 説明: BFS の距離上限。デフォルト: 2。
- `--roles`

  - 説明: 辿る対象の role をフィルタ（例: `--roles if,data`）。

#### 9.5.3 入出力

- 入力:

  - SpecIndex（DATA-900）
- 出力:

  - DATA-906_impact_report
  - JSON モードでは DATA-906 準拠。

#### 9.5.4 Exit Code

- `0`: 正常に ImpactReport を生成。
- `1` / `2`: エラー時。
- `3`: 使用しない。

---

### 9.6 `context` コマンド

#### 9.6.1 目的

- seed ID 群とその近傍から、LLM に渡しやすい ContextBundle（DATA-905）を生成する。

#### 9.6.2 シグネチャ

```bash
iori-spec context <ID...> [--radius N] [--roles R1,R2,...] [--max-tokens T] [--format json|markdown]
```

- `<ID...>`

  - 説明: seed となる spec ID 群。
- `--radius`

  - 説明: trace / dp / doc グラフ上で何ステップ先まで含めるか。
  - デフォルト: 1。
- `--roles`

  - 説明: コンテキストとして含める role（例: `req,if,data,test`）。
- `--max-tokens`

  - 説明: ContextBundle の本⽂総量の目安。ざっくりとこれを超えないように努力する。
- `--format`

  - 説明: `json`（DATA-905） or `markdown`（human 読み用）。

#### 9.6.3 入出力

- 入力:

  - SpecIndex（DATA-900）
  - SectionSchema（DATA-901）
  - config（DATA-910）
- 出力:

  - DATA-905_context_bundle
  - `--format markdown` の場合は、ContextBundle を元に生成した Markdown 1 本。

#### 9.6.4 Exit Code

- `0`: 正常に ContextBundle を生成。
- `1` / `2`: エラー時。
- `3`: 使用しない。

---

### 9.7 `prompt` コマンド（拡張）

#### 9.7.1 目的

- ContextBundle（DATA-905）から PromptBundle（DATA-907）を生成し、
  LLM にそのまま渡せる構造にする。

#### 9.7.2 シグネチャ

基本形（パイプ経由）:

```bash
iori-spec context IF-200 --radius 1 --format json \
  | iori-spec prompt --preset default.codegen --format json
```

単体利用（ID 指定、内部で context を呼ぶ拡張形）:

```bash
iori-spec prompt <ID...> [--radius N] [--roles R1,R2,...] [--max-tokens T] \
  --preset NAME [--language LANG] [--format json|markdown]
```

- `--preset NAME`

  - 説明: DATA-910.prompt.presets で定義されたプリセット名。
- `--language LANG`

  - 説明: `"ja"` / `"en"` など。未指定時は config の default_language。
- `--format`

  - 説明: `json`（DATA-907） or `markdown`（system / user / context_markdown を整形して表示）。

#### 9.7.3 入出力

- 入力:

  - 標準入力（ContextBundle の JSON）
    または `<ID...>` から `context` 相当の処理を内部呼び出し。
- 出力:

  - DATA-907_prompt_bundle（`--format json`）。
  - `--format markdown` の場合は、人間がそのまま LLM に貼れる形のプロンプト。

#### 9.7.4 Exit Code

- `0`: 正常に PromptBundle を生成。
- `1` / `2`: エラー時。
- `3`: 使用しない（lint ではないため）。

---

## 10. JSON 出力と DATA-9xx の対応

各コマンドと DATA-9xx の対応表：

| コマンド         | `--format json` 出力 | DATA ID  |
| ------------ | ------------------ | -------- |
| `index`      | SpecIndex          | DATA-900 |
| `lint`       | LintResult         | DATA-902 |
| `trace-lint` | LintResult         | DATA-902 |
| `search`     | SearchHit[]        | DATA-904 |
| `impact`     | ImpactReport       | DATA-906 |
| `context`    | ContextBundle      | DATA-905 |
| `prompt`     | PromptBundle       | DATA-907 |

- すべての JSON 出力は「1 つのトップレベル値」（オブジェクト or 配列）とする。
- 追加メタ情報が必要な場合は、対応する DATA-9xx 側にフィールドを拡張してから
  CLI 実装を追従させる。

---

## 11. エラーとメッセージ

- CLI レイヤは、core レイヤの例外を捕捉し、
  Exit Code と人間向けメッセージに変換する。
- JSON モードでは、可能な限りエラーメッセージも JSON で返す設計にしてよいが、
  MVP では人間向けメッセージのみでもよい（追って data_contract 化を検討）。

---

## 12. 将来拡張に関するメモ

- `show` / `scaffold` / `graph` などの新コマンドを追加する場合、本 IF-900 に
  サブコマンド定義を追記すること。
- Exit Code のバリエーションを増やす場合も、本 IF を更新し、
  REQ-800 / ARCH-900 の非機能要件と矛盾しないようにする。



