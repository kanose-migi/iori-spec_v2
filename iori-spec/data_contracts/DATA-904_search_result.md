---
kind: data_contracts
scope: tooling.search
id: DATA-904
spec_title: "DATA-904: Search Result — SearchHit List (JSON)"
status: draft

trace:
  req: []        # 例: REQ-8xx_search_specs などを後で紐付け
  if:
    - IF-940     # Search Specs — spec_index.json → ID Candidates
  data:
    - DATA-900   # 入力: Spec Index Catalog（検索対象）
  test: []
  task: []

dp:
  produces:
    - DATA-904   # IF-940 が生成する search_result
  produced_by:
    - IF-940
  consumes:
    - DATA-900
  inputs:
    - iori_spec_config.yaml
    - Markdown specs (*.md)

doc:
  read_next:
    - DATA-900
    - interfaces/IF-940_search_specs.md
  see_also:
    - DATA-902_lint_result.md
    - DATA-905_context_bundle.md
    - impl_notes/spec_command.md
---

# DATA-904: Search Result — SearchHit List (JSON)

## LLM_BRIEF

- role: このファイルは、`iori-spec search` コマンドや IF-940（Search Specs）が生成する  
  **「検索結果（SearchHit の一覧）」のデータ構造**を定義する data_contract です。
- llm_action: あなた（LLM）は IF-940 を実装するとき、この data_contract を  
  **「search コマンドの JSON 出力／Python 戻り値のフォーマット」**として参照し、  
  ここで定義されたフィールドを持つ `SearchHit` の配列を返すコードを書いてください。  
  `search_result.json` を直接手書きするのではなく、「常にこの構造に従う実装」を行うことが目的です。

## USAGE

- コマンド出力（CLI）
  - `iori-spec search "digits segments" --format json`  
    → 標準出力に **SearchHit の配列（DATA-904 準拠）** を JSON として出す。
  - `iori-spec search "REQ-201" --kind requirements --format json`  
    → 同様に、フィルタ済みの SearchHit[] を JSON 出力。
- Python ライブラリとして
  - `search_specs(...) -> list[SearchHit]`  
    → 関数戻り値の構造が DATA-904 に準拠する。
- 他ツールからの利用
  - エディタ拡張・CI・独自スクリプトは、この data_contract に従って SearchHit[] をパースし、  
    ID / title / scope / score をもとに spec ナビゲーションやジャンプを提供する。

## READ_NEXT

- IF-940: Search Specs — spec_index.json → ID Candidates
- DATA-900: Spec Index Catalog — spec_index.json

---

## 1. このドキュメントの役割

- search 系の入出力を SSOT 化するために、
  - SearchHit（1 件の検索結果）
  - SearchHit[]（1 回の search 実行結果）
  の構造とフィールド意味を定義する。
- これにより、
  - IF-940 の実装
  - `iori-spec search` の CLI 出力
  - 検索結果を扱う周辺ツール（エディタ、スクリプト）
  が同じ前提で SearchHit を扱えるようになる。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- DATA-904 は **1 回の search 実行で得られる SearchHit の配列**のフォーマットを定義する。
- トップレベルは **JSON 配列**とする。

```jsonc
[
  { /* SearchHit */ },
  { /* SearchHit */ }
]
````

### 2.2 前提

- 検索対象は SpecIndex（DATA-900）のノード情報であり、

  - `nodes[].id`
  - `nodes[].file`
  - `nodes[].kind`
  - `nodes[].scope`
  - `nodes[].role`
  - `nodes[].spec_title`
  - `nodes[].llm_brief` / `summary`（あれば）
    などのフィールドを利用して SearchHit を構築する。
- スコアリングは IF-940 に定義された方針に従う（ID 完全一致を最優先、等）。

---

## 3. 運用上の目安（LLM / SDD 観点）

- LLM には search_result 全体ではなく、必要なヒットのみを抜粋して渡す（大量に渡さない）。
- search → impact / context といった後続コマンドへの入力として、SearchHit.id をそのまま利用する。
- スコアリングやフィルタ条件は IF-940 側で管理し、この data_contract は結果形式だけに責務を限定する。

---

## 4. Summary

- search_result.json は **SearchHit の配列**として表現される。
- 各 SearchHit は少なくとも：

  - `id` / `file` / `kind` / `scope` / `role`
  - `spec_title`
  - `score`
    を含み、任意で
  - `snippet`（概要テキスト）
  - `matched_fields`（どのフィールドがマッチしたか）
    を持つことができる。

---

## 5. Schema

### 5.1 トップレベル

search 結果ファイル（もしくは CLI の `--format json` 出力）は、以下の形式をとる：

```jsonc
[
  {
    "id": "REQ-201",
    "file": "requirements/REQ-201_digits_segments.md",
    "kind": "requirements",
    "scope": "client.query_engine",
    "role": "req",
    "spec_title": "REQ-201: digits segmentation rules",
    "score": 1.0,
    "snippet": "0–9 の数字列をセグメント分割するための要件を定義する…",
    "matched_fields": ["id", "spec_title"]
  }
]
```

- トップレベルは **SearchHit オブジェクトの配列**。
- ヒットが 0 件の場合は `[]`（空配列）となる。

---

### 5.2 SearchHit オブジェクト

#### 5.2.1 構造（一覧）

| フィールド            | 型               | 必須  | 説明                                                                 |
| ---------------- | --------------- | --- | ------------------------------------------------------------------ |
| `id`             | string          | Yes | SpecNode の ID（例: `"REQ-201"`）。                                     |
| `file`           | string          | Yes | SpecNode のファイルパス（リポジトリ root からの相対）。                                |
| `kind`           | string          | Yes | SpecNode の kind。                                                   |
| `scope`          | string          | Yes | SpecNode の scope。                                                  |
| `role`           | string          | Yes | SpecNode の role（`"req"`, `"if"`, `"data"`, `"test"`, `"task"` など）。 |
| `spec_title`     | string          | Yes | 仕様タイトル。                                                            |
| `score`          | number          | Yes | 検索スコア（0 以上の相対値を推奨）。                                                |
| `snippet`        | string \| null   | No  | `llm_brief` や `summary` から抜粋した短いテキスト。なければ `null`。                  |
| `matched_fields` | string[] \| null | No  | マッチに寄与したフィールド名（例: `["id","spec_title"]`）。なければ `null`。              |

#### 5.2.2 フィールド詳細

- `id`

  - SpecIndex の `nodes[].id` と一致する値。
  - 例：`"REQ-201"`, `"IF-200"`, `"DATA-101"`, `"TEST-300"`。
- `file`

  - SpecIndex の `nodes[].file` と一致する相対パス。
  - エディタやブラウザで spec ファイルを開く際のキーとして利用。
- `kind`

  - SpecIndex の `nodes[].kind` をそのまま格納。
  - 例：`"requirements"`, `"interfaces"`, `"data_contracts"`, `"architecture"`, `"steering"`, `"test"` 等。
- `scope`

  - SpecIndex の `nodes[].scope` をそのまま格納。
  - 例：`"client.query_engine"`, `"build_system"`, `"tooling.index"`。
- `role`

  - SpecIndex の `nodes[].role` をそのまま格納。
  - 例：`"req"`, `"if"`, `"data"`, `"test"`, `"task"`, `"note"` 等。
- `spec_title`

  - 仕様の人間向けタイトル。
  - 例：`"IF-200: Query Engine — digits → Segmented Candidates"`。
- `score`

  - 検索の関連度スコア。
  - 範囲・スケールは実装に委ねるが、0 以上の実数値とすることを推奨。
  - ソートは `score` の降順（高いほど関連度が高い）で行う。
- `snippet`

  - ユーザーに結果を一覧表示する際の説明として利用しやすい短いテキスト。
  - 通常は、SpecIndex に格納された `llm_brief` や `summary` に由来する。
  - スニペットが用意できない場合は `null` でよい。
- `matched_fields`

  - 検索時にマッチングに寄与したフィールド名の配列。
  - 例：

    - `["id"]`
    - `["spec_title", "scope"]`
  - UI で「どこがヒットしたか」をハイライトする用途などを想定。
  - 管理コストを下げるため、MVP では `null` や空配列でも構わない（あとから段階的に充実させる形でもよい）。

---

## 6. 例

### 6.1 単純な ID 検索の例

```jsonc
[
  {
    "id": "REQ-201",
    "file": "requirements/REQ-201_digits_segments.md",
    "kind": "requirements",
    "scope": "client.query_engine",
    "role": "req",
    "spec_title": "REQ-201: digits segmentation rules",
    "score": 1.0,
    "snippet": "digits セグメント分割の要件を定義する REQ です…",
    "matched_fields": ["id"]
  }
]
```

### 6.2 複数ヒットの例

```jsonc
[
  {
    "id": "REQ-201",
    "file": "requirements/REQ-201_digits_segments.md",
    "kind": "requirements",
    "scope": "client.query_engine",
    "role": "req",
    "spec_title": "REQ-201: digits segmentation rules",
    "score": 0.95,
    "snippet": "0–9 の数字列をセグメント分割するための要件…",
    "matched_fields": ["spec_title", "scope"]
  },
  {
    "id": "IF-200",
    "file": "interfaces/IF-200_query_engine.md",
    "kind": "interfaces",
    "scope": "client.query_engine",
    "role": "if",
    "spec_title": "IF-200: Query Engine — digits → Segmented Candidates",
    "score": 0.80,
    "snippet": "digits をセグメント単位に分割し、候補 entry を返す…",
    "matched_fields": ["spec_title"]
  }
]
```

---

## 7. Constraints（制約）

- トップレベルは常に **JSON 配列**。
- 各要素は SearchHit オブジェクトであり、`id` / `file` / `kind` / `scope` / `role` / `spec_title` / `score` の各フィールドを必須で持つ。
- `score` は 0 以上の数値であることが望ましい（負の値は使用しない）。
- `matched_fields` を利用する場合、その要素は SearchHit の実際のフィールド名と一致している必要がある。

---

## 8. IF-940 との関係

- IF-940（Search Specs）は、この DATA-904 を

  - Python 戻り値（`list[SearchHit]`）の型
  - CLI `--format json` の出力フォーマット
    として採用する。
- IF-940 側では、SpecIndex から検索した結果を
  この SearchHit スキーマにマッピングして返す実装を行う。

---

## 9. 今後の拡張（メモ）

- SearchHit に `extra` フィールド（任意の object）を追加し、

  - スコアの内訳（id マッチ / title マッチなど）
  - role / kind ごとの優先度
    などを格納する案もある（後方互換性に配慮して optional に追加）。
- フィルタ条件（kinds / scopes / roles / limit）の情報を
  別のトップレベルオブジェクトに持たせたい場合は、
  `DATA-904` のバージョンアップとして `{"query": {...}, "hits": [SearchHit...]}` の形に拡張する可能性もある。
  その場合は `version` フィールドや後方互換の扱いを IF / CLI 側で明示する。



