---
kind: data_contracts
scope: tooling.spec_index
id: DATA-900
spec_title: "DATA-900: Spec Index — spec_index.json"
status: draft

# ---- 要求トレースグラフ（G_trace）用の情報 ----
trace:
  req: []        # このデータ契約に直接ひも付く REQ-xxx（ツール要件）があれば追記
  if: []         # この DATA を生成・更新する IF-xxx（例えば IF-1xx_indexer）があれば追記
  data: []       # 密接に関連する他の DATA-xxx（セクションスキーマなど）
  test: []       # 主にこの DATA を検証する TEST-xxx
  task: []       # この DATA を実装・整備する TASK-xxx

# ---- Data–Process グラフ（G_dp）用の情報 ----
dp:
  produces: []      # 通常は IF 側で使用。DATA 側では空のままでよい。
  produced_by: []   # この DATA を生成する IF-xxx（例: IF-1xx_spec_index_builder）を将来的に追記
  consumes: []      # この DATA が読み取る他 DATA は原則なし（index 自体は SSOT）
  inputs: []        # 外部入力（ファイル・サービス）があれば記載

# ---- ドキュメント依存グラフ（G_doc）用の情報 ----
doc:
  read_next:
    - DATA-901     # セクションスキーマの data_contract（spec_section_schema.yaml）
  see_also:
    - reference/iori_spec_guide.md
    - impl_notes/spec_command.md
---

# DATA-900: Spec Index — spec_index.json

## LLM_BRIEF

- role: このファイルは、`iori-spec` が管理する仕様群をノードとして一覧化した **spec カタログ（インデックス）のデータ契約**です。
- llm_action: `iori-spec index` コマンドや、それに相当する Python モジュールを **設計・実装・リファクタリングする際の「出力フォーマット仕様」**として、この data_contract を参照してください。spec_index.json を直接生成するのではなく、「ここに定義された構造に厳密に従うコード」を作ることが目的です。

## USAGE

- この data_contract を参照する主なユースケース
  - `iori-spec index` コマンドが、Markdown 仕様群から `spec_index.json` を生成する。
  - `iori-spec search` が、`spec_index.json` だけを読み込んで ID 候補を検索する。
  - `iori-spec impact` / `trace lint` が、`trace` / `dp` / `doc` 情報からグラフを構築する。
  - `iori-spec context` / `show` が、対象 ID と近傍ノードを決定するために利用する。
- 人間がこのドキュメントを読むタイミング
  - index 周りの実装を行うとき
  - 新しいフィールドを index に加えたいとき
  - 他ツール（VSCode 拡張・Web UI など）から `spec_index.json` を利用したいとき

## READ_NEXT

- `DATA-901: Spec Section Schema — spec_section_schema.yaml`
- `reference/iori_spec_guide.md`（ID 命名規則・ kind / scope など）
- `impl_notes/spec_command.md`（コマンド体系と index 利用箇所）

---

## 1. このドキュメントの役割

- 仕様書群（Markdown）の集合から、**機械が扱いやすいグラフノード一覧**を切り出すための「データ構造の SSOT」を定義する。
- `spec_index.json` のフィールド構造・意味・制約を明確化し、
  - 生成側（index コマンド / ビルドスクリプト）
  - 利用側（search / impact / context / lint / trace lint / 外部ツール）
  が同じ前提で実装できるようにする。
- 「仕様そのもの（requirements / interfaces ...）」ではなく、「仕様群のメタ情報」を扱う。

## 2. 範囲（Scope）と前提

- 範囲
  - `spec_index.json` 1 ファイルの JSON 形式を対象とする。
  - index に含めるノードは、**ID を持つ kind（requirements / architecture / interfaces / data_contracts / tests / dev_tasks / reference など）**を前提とする。
- 前提
  - 各 Markdown ファイルは `YAML front matter` に `kind / scope / id / spec_title / status / trace / dp / doc` を持つ。
  - ID は `REQ-xxx`, `IF-xxx`, `DATA-xxx`, `TEST-xxx`, `TASK-xxx` といったプレフィックス＋数値で一意に付与されている。
  - index そのものは純粋なデータであり、ここでは CLI 実装の詳細には踏み込まない（どのタイミング・コマンドで生成するかは IF 側で定義）。

## 3. 運用上の目安（LLM / SDD 観点）

- LLM 観点
  - LLM に「仕様の全体像を把握させる」のではなく、`search` や `impact` で **近傍の数十ノードに絞り込むためのメタ情報**として利用する。
  - LLM に `spec_index.json` 全体を渡すのは避け、ID のフィルタリングやグラフ探索ロジックは基本的にツール側で行う。
- SDD 観点
  - index にフィールドを追加する場合は、
    - 先にこの data_contract（DATA-900）を更新する。
    - その後で `index` 実装と利用側コマンド（search / impact / context / lint / trace lint）のコードを更新する。
  - 既存フィールドの semantics を変える場合は、「バージョン番号の更新」または「別バージョンの DATA-xxx を追加」する形を検討する。

---

## 4. Summary

- `spec_index.json` は、`iori-spec` リポジトリ内の ID 付き仕様ファイルをすべてノードとして列挙する **インデックスファイル**である。
- 各ノードは、
  - `id / kind / scope / status / spec_title / role / file`
  - `trace`（REQ / IF / DATA / TEST / TASK の論理関係）
  - `dp`（IF⇄DATA のビルド依存関係）
  - `doc`（一緒に読むとよい ID 等）
  といった情報を持つ。
- `search` / `impact` / `context` / `lint` / `trace lint` など、ほぼすべてのツールはこのインデックスを出発点とする。

---

## 5. Schema

### 5.1 トップレベル構造

`spec_index.json` は次の形をとる。

```jsonc
{
  "version": "0.1.0",              // index スキーマのバージョン
  "generated_at": "2025-12-04T12:34:56Z",  // ISO 8601 形式
  "root": ".",                     // index の生成対象としたルートディレクトリ（相対パス）
  "nodes": [                       // 仕様ノードの配列
    {
      /* SpecNode オブジェクト */
    }
  ]
}
````

| フィールド          | 型          | 必須  | 説明                                      |
| -------------- | ---------- | --- | --------------------------------------- |
| `version`      | string     | Yes | index スキーマのバージョン。互換性を判定するために利用。         |
| `generated_at` | string     | Yes | index 生成日時（UTC / ISO 8601 推奨）。          |
| `root`         | string     | Yes | index を生成したときのルートディレクトリのパス（ツール内部の相対パス）。 |
| `nodes`        | SpecNode[] | Yes | 仕様ファイル 1 件につき 1 要素となるノード配列。             |

### 5.2 SpecNode オブジェクト

```jsonc
{
  "id": "IF-200",
  "kind": "interfaces",
  "scope": "client.query_engine",
  "status": "review",
  "spec_title": "Query Engine — digits→segments",

  "role": "if",
  "file": "interfaces/IF-200_query_engine.md",

  "llm_brief": "この IF は digits を segments に分割するクエリエンジンの中核仕様です…",
  "summary": "ユーザーが入力した 0〜9 の数字列を…",

  "trace": { /* TraceInfo */ },
  "dp": { /* DPInfo */ },
  "doc": { /* DocLinks */ },

  "hash": "c0ffee...", 
  "frontmatter_range": { "start": 1, "end": 24 }
}
```

| フィールド          | 型                | 必須  | 説明                                                                                                                               |
| ------------------- | ----------------- | ----- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `id`                | string            | Yes   | 仕様 ID（例: `REQ-201`, `IF-200`, `DATA-101`）。|
| `kind`              | string            | Yes   | 仕様の種別（例: `requirements`, `architecture`, `interfaces`, `data_contracts`, `tests`, `dev_tasks`, `reference`, `impl_notes`）。|
| `scope`             | string            | Yes   | 対象領域・モジュール名（例: `client.query_engine`, `build_system`, `tooling.*`）。|
| `status`            | string            | Yes   | 仕様の成熟度（例: `draft`, `review`, `stable`, `deprecated`）。|
| `spec_title`        | string            | Yes   | 人間・LLM 向け仕様タイトル。front matter の `spec_title` と一致させる。|
| `role`              | string            | Yes   | ID プレフィックスから導く論理ロール（`"req" \| "if" \| "data" \| "test" \| "task" \| "ref" \| "doc" \| "impl" \| "unknown"`）。 |
| `file`              | string            | Yes   | リポジトリルートからの相対パス（例: `requirements/REQ-201_digits_segments.md`）。|
| `llm_brief`         | string \| null    | No    | `## LLM_BRIEF` セクション先頭の数行を抜粋したもの。存在しない場合は `null`。|
| `summary`           | string \| null    | No    | kind ごとの Summary セクション（例: `## 4. Summary`）から抜粋した要約。|
| `trace`             | TraceInfo \| null | No    | トレースグラフ用の情報。後述。|
| `dp`                | DPInfo \| null    | No    | Data–Process グラフ用の情報。後述。|
| `doc`               | DocLinks \| null  | No    | ドキュメント依存グラフ用の情報。後述。|
| `hash`              | string \| null    | No    | ノードに対応するファイルの内容ハッシュ（変更検出用）。|
| `frontmatter_range` | object \| null    | No    | front matter の行範囲（1-origin）。`{"start": 1, "end": 15}` 等。|

### 5.3 TraceInfo

```jsonc
"trace": {
  "req": ["REQ-201", "REQ-202"],
  "if": [],
  "data": ["DATA-101"],
  "test": ["TEST-201"],
  "task": ["TASK-301"]
}
```

| フィールド  | 型        | 必須 | 説明                                |
| ------ | -------- | -- | --------------------------------- |
| `req`  | string[] | No | このノードが論理的に紐づく要求（REQ-xxx）の一覧。      |
| `if`   | string[] | No | 関係する IF-xxx（派生 / ラッパ / 下位 IF など）。 |
| `data` | string[] | No | 密接に関わる DATA-xxx。                  |
| `test` | string[] | No | 主にこのノードを検証する TEST-xxx。            |
| `task` | string[] | No | 実装タスク（TASK-xxx）の一覧。               |

### 5.4 DPInfo（Data–Process 情報）

```jsonc
"dp": {
  "produces": ["DATA-101"],
  "produced_by": [],
  "consumes": ["DATA-020", "DATA-014"],
  "inputs": []
}
```

| フィールド         | 型        | 必須 | 説明                                     |
| ------------- | -------- | -- | -------------------------------------- |
| `produces`    | string[] | No | この IF が生成する DATA-xxx。通常は IF ノード側で設定。   |
| `produced_by` | string[] | No | この DATA を生成する IF-xxx。通常は DATA ノード側で設定。 |
| `consumes`    | string[] | No | この IF が入力として利用する DATA-xxx。             |
| `inputs`      | string[] | No | より広義の入力（ログファイル、外部 API など）があれば列挙。       |

### 5.5 DocLinks

```jsonc
"doc": {
  "read_next": ["IF-210", "DATA-130"],
  "see_also": ["reference/iori_spec_guide.md"]
}
```

| フィールド       | 型        | 必須 | 説明                                     |
| ----------- | -------- | -- | -------------------------------------- |
| `read_next` | string[] | No | 「この spec を読んだあとに次に読むとよい ID」の一覧。ID ベース。 |
| `see_also`  | string[] | No | 参考 URL やパスなど、ID 以外の関連リソース。             |

---

## 6. Constraints（任意）

- 一意性

  - `nodes[].id` は index 内で重複してはならない。
  - `nodes[].file` も index 内で一意であることが望ましい。
- 整合性

  - 各ノードの `role` は `id` のプレフィックスから決定される（例: `REQ-` → `req`）。
  - `trace.*` / `dp.*` / `doc.read_next` に記載される ID は、原則として同じ index 内に存在している必要がある（存在しない場合、lint で警告・エラー）。
- バージョニング

  - `version` フィールドは、スキーマを後方互換性を壊す変更が入った場合に更新する。
  - 後方互換な追加（オプションフィールドの追加等）は `0.x` の minor version として扱ってよい。

---

## 7. 利用箇所の概要（任意）

- コマンド

  - `iori-spec index` … この data_contract に沿って `spec_index.json` を生成する。
  - `iori-spec search` … `nodes` を検索して ID 候補の一覧を返す。
  - `iori-spec impact` … `trace` / `dp` / `doc` 情報から影響範囲を計算する。
  - `iori-spec context` / `show` … seed ID と近傍 ID を決定するために利用する。
  - `iori-spec lint` / `trace lint` … index をもとに構造健全性・トレーサビリティ健全性を検査する。
- 将来的な利用

  - VSCode 拡張・Web UI などが `spec_index.json` を読み取り、
    仕様のナビゲーション・可視化ツールとして利用することを想定する。



