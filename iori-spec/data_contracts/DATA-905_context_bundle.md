---
kind: data_contracts
scope: tooling.context
id: DATA-905
spec_title: "DATA-905: Context Bundle — Spec IDs → LLM Context Bundle (JSON)"
status: draft

trace:
  req: []        # 例: REQ-8xx_context_bundle などを後で紐付け
  if:
    - IF-960     # Context Builder — Spec IDs → LLM Context Bundle
  data:
    - DATA-900   # 入力: Spec Index Catalog
    - DATA-901   # 入力: Spec Section Schema
  test: []
  task: []

dp:
  produces:
    - DATA-905   # IF-960 が生成するコンテキストバンドル
  produced_by:
    - IF-960
  consumes:
    - DATA-900
    - DATA-901
  inputs:
    - iori_spec_config.yaml
    - Markdown specs (*.md)

doc:
  read_next:
    - DATA-900
    - DATA-901
    - interfaces/IF-960_context_builder.md
  see_also:
    - impl_notes/spec_command.md
---

# DATA-905: Context Bundle — Spec IDs → LLM Context Bundle (JSON)

## LLM_BRIEF

- role: このファイルは、`iori-spec context` コマンドや IF-960（Context Builder）が生成する  
  **「LLM に渡すためのコンテキストバンドル」のデータ構造**を定義する data_contract です。
- llm_action: あなた（LLM）は IF-960 を実装するとき、この data_contract を  
  **「context コマンドの JSON 出力／Python 戻り値のフォーマット」**として参照し、  
  ここで定義された構造を持つ `ContextBundle` オブジェクトを返すコードを書いてください。  
  `context_bundle.json` を直接手書きするのではなく、「常にこの構造に従う実装」を行うことが目的です。

## USAGE

- コマンド出力（CLI）
  - `iori-spec context REQ-201 IF-200 --depth 1 --max-tokens 2000 --format json`  
    → 標準出力に **ContextBundle（DATA-905 準拠の 1 オブジェクト）** を JSON として出す。
- Python ライブラリとして
  - `build_context(...) -> ContextBundle`  
    → 関数戻り値の構造が DATA-905 に準拠する。
- 他ツールからの利用
  - エディタ拡張・CI・独自スクリプトは、この data_contract に従って ContextBundle をパースし、  
    `items[].sections[]` をもとに LLM へのプロンプトを組み立てる。

## READ_NEXT

- IF-960: Context Builder — Spec IDs → LLM Context Bundle
- DATA-900: Spec Index Catalog — spec_index.json
- DATA-901: Spec Section Schema — spec_section_schema.yaml

---

## 1. このドキュメントの役割

- context 系の入出力を SSOT 化するために、
  - ContextBundle（トップレベル）
  - ContextItem（spec 単位の要素）
  - SectionSnippet（セクション単位の抜粋）
  の構造とフィールド意味を定義する。
- これにより、
  - IF-960 の実装
  - `iori-spec context` の CLI 出力
  - LLM 連携（プロンプト前処理）
  が同じ前提で ContextBundle を扱えるようにする。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- DATA-905 は **1 回の context 実行で得られる「コンテキストバンドル 1 つ」**のフォーマットを定義する。
- トップレベルは **1 つの JSON オブジェクト**（ContextBundle）とする。

```jsonc
{
  "seed_ids": ["REQ-201"],
  "strategy": "default",
  "depth": 1,
  "roles": ["req", "if", "data", "test"],
  "max_tokens": 2000,
  "approx_tokens_total": 1480,
  "items": [
    { /* ContextItem */ }
  ]
}
````

### 2.2 前提

- ContextBundle は、以下を前提として組み立てられる：

  - SpecIndex（DATA-900）
  - SectionSchema（DATA-901）
- トークン数は近似値で構わない（文字数や単語数からの変換など）。

---

## 3. 運用上の目安（LLM / SDD 観点）

- LLM に渡す際は、seed と近傍を必要最小限に絞り、ContextBundle 全体は渡しすぎない。
- impact などから得た近傍 ID と合わせて使う場合は、`roles` / `depth` を明示的に管理する。
- `approx_tokens_total` を用いてトークン上限を超えないように組み立てる。

---

## 4. Summary

- **ContextBundle** は「どの ID（seed_ids）を起点に」「どの戦略・条件で」
  「どの spec のどのセクションを」「どれくらいのトークン量で」LLM に渡すかを表現する。
- 構造は：

  - `ContextBundle` … 全体のメタ情報＋ `items[]`
  - `ContextItem` … spec 1 件分の情報＋ `sections[]`
  - `SectionSnippet` … 見出し 1 つ分の本文抜粋
    という 3 層で構成される。

---

## 5. Schema

### 5.1 ContextBundle（トップレベル）

#### 5.1.1 フィールド一覧

| フィールド                 | 型               | 必須  | 説明                                                            |
| --------------------- | --------------- | --- | ------------------------------------------------------------- |
| `seed_ids`            | string[]        | Yes | 入力として与えられた種 ID の一覧（例: `["REQ-201"]`）。                         |
| `strategy`            | string          | Yes | 使用した戦略名（例: `"default"`）。                                      |
| `depth`               | int             | Yes | グラフ探索に用いた最大距離（0 が自己のみ）。                                       |
| `roles`               | string[] \| null | No  | 探索対象とした role の一覧（例: `["req", "if", "data"]`）。指定なしの場合は `null`。 |
| `max_tokens`          | int \| null      | No  | コンテキストの概算トークン上限。未指定時は `null`。                                 |
| `approx_tokens_total` | int             | Yes | `items[].sections[].approx_tokens` の合計値。                      |
| `items`               | ContextItem[]   | Yes | 抽出された spec ごとのコンテキスト要素の配列。                                    |

#### 5.1.2 フィールド詳細

- `seed_ids`

  - CLI 引数で指定された ID を、そのまま配列で残す。
  - 不明な ID が含まれていた場合は、IF-960 側のポリシー（エラー／警告／無視）に従いつつ、
    必要であれば `items` とは別に `unknown_ids` のようなフィールドで補足してもよい（拡張は `extra` 等で扱う）。
- `strategy`

  - 例：

    - `"default"` … REQ を中心に近傍 IF / DATA / TEST を集める標準戦略
    - `"req-focused"` … REQ のみを優先する戦略
  - 将来複数戦略を実装する場合でも、ContextBundle スキーマは共通とする前提。
- `depth`

  - seed から trace/doc エッジを辿る hop 数上限。
  - `0` … seed 自身のみ
  - `1` … seed と、そこから 1 hop の近傍
- `roles`

  - `["req", "if", "data", "test", "task"]` など。
  - `null` の場合、「特に role で絞り込んでいない」と解釈する。
- `max_tokens`

  - LLM に渡すコンテキスト全体の近似トークン上限。
  - `null` の場合、トークン上限を考慮しない。
- `approx_tokens_total`

  - items 配下の SectionSnippet の `approx_tokens` 合計。
  - LLM に渡した際のトークン上限チェックや UI 表示などに利用できる。
- `items`

  - 実際にコンテキストとして採用された spec 群。
  - 配列順序は IF-960 側で定義した優先度（distance, role, rule_id 等）に従って安定的にソートされる。

---

### 5.2 ContextItem（spec 単位の要素）

#### 5.2.1 構造（一覧）

| フィールド      | 型                | 必須  | 説明                                                                 |
| ---------- | ---------------- | --- | ------------------------------------------------------------------ |
| `id`       | string           | Yes | SpecNode の ID（例: `"REQ-201"`）。                                     |
| `file`     | string           | Yes | SpecNode のファイルパス（リポジトリ root からの相対パス）。                              |
| `kind`     | string           | Yes | SpecNode の kind。                                                   |
| `scope`    | string           | Yes | SpecNode の scope。                                                  |
| `role`     | string           | Yes | SpecNode の role（例: `"req"`, `"if"`, `"data"`, `"test"`, `"task"`）。 |
| `distance` | int              | Yes | seed からの hop 数（0 が seed 自身）。                                       |
| `sections` | SectionSnippet[] | Yes | この spec から抽出したセクションの配列。                                            |

#### 5.2.2 フィールド詳細

- `id`

  - SpecIndex の `nodes[].id` と一致する値。
- `file`

  - SpecIndex の `nodes[].file` と一致する相対パス。
- `kind` / `scope` / `role`

  - SpecIndex に記録された値をそのまま利用する。
- `distance`

  - Graph Layer で計算した最短距離（BFS のレベル番号など）。
  - `0` … seed_ids に含まれるノード
  - `1` … seed から 1 hop のノード
- `sections`

  - SectionSchema（DATA-901）の `tool_source: true` なルールに基づいて抽出された見出し単位の抜粋群。

---

### 5.3 SectionSnippet（セクションの抜粋）

#### 5.3.1 構造（一覧）

| フィールド           | 型      | 必須  | 説明                                                                  |
| --------------- | ------ | --- | ------------------------------------------------------------------- |
| `rule_id`       | string | Yes | SectionSchema 上の rule ID または論理名（例: `"llm_brief"`, `"req_summary"`）。 |
| `heading`       | string | Yes | 実際の見出しテキスト（例: `"## LLM_BRIEF"`）。                                    |
| `level`         | int    | Yes | 見出しレベル（例: `2` は `##`）。                                              |
| `body`          | string | Yes | 見出し直後から、次の同レベル以上の見出し直前までの Markdown テキスト。                            |
| `approx_tokens` | int    | Yes | このセクション本文の概算トークン数。                                                  |

#### 5.3.2 フィールド詳細

- `rule_id`

  - SectionSchema 側で定義された「セクション種別」を識別するための ID／名前。
  - 例：

    - `llm_brief`
    - `summary`
    - `acceptance_criteria`
- `heading`

  - 実際の Markdown 見出しテキスト全体。
    例：`"## LLM_BRIEF"`、`"### 4.1. Inputs"`.
- `level`

  - heading のレベル番号。
  - `#` → 1, `##` → 2, `###` → 3, …
- `body`

  - 抜粋対象の本文部分（Markdown のままでよい）。
  - LLM に渡す際は、この `body` を連結してプロンプトに組み込む想定。
- `approx_tokens`

  - トークン数のラフな近似値（文字数や単語数からの変換でよい）。
  - ContextBundle 全体の `approx_tokens_total` 集計に利用する。

---

## 6. 例

簡易な ContextBundle の例：

```jsonc
{
  "seed_ids": ["REQ-201"],
  "strategy": "default",
  "depth": 1,
  "roles": ["req", "if", "data", "test"],
  "max_tokens": 2000,
  "approx_tokens_total": 480,
  "items": [
    {
      "id": "REQ-201",
      "file": "requirements/REQ-201_digits_segments.md",
      "kind": "requirements",
      "scope": "client.query_engine",
      "role": "req",
      "distance": 0,
      "sections": [
        {
          "rule_id": "llm_brief",
          "heading": "## LLM_BRIEF",
          "level": 2,
          "body": "この REQ は digits セグメント化の振る舞いを定義する…",
          "approx_tokens": 120
        },
        {
          "rule_id": "req_summary",
          "heading": "## 4. Summary",
          "level": 2,
          "body": "- ユーザーは 0–9 の数字列を入力する\n- システムは…",
          "approx_tokens": 200
        }
      ]
    }
  ]
}
```

---

## 7. Constraints（制約）

- トップレベルは常に **1 オブジェクト**（配列ではない）。
- `items` は配列であり、空の場合は `[]` となる。
- `approx_tokens_total` は `items[].sections[].approx_tokens` の合計と整合していることが望ましい。
- `distance` は非負整数（0 以上）。
- `approx_tokens` / `approx_tokens_total` も非負整数。

---

## 8. IF-960 との関係

- IF-960（Context Builder）は、この DATA-905 を

  - Python 戻り値の型
  - CLI `--format json` の出力フォーマット
    として採用する。
- IF-960 側では、Graph Layer / Section Layer / Bundle Layer の処理結果を
  この ContextBundle スキーマにマッピングして返す実装を行う。

---

## 9. 今後の拡張（メモ）

- ContextBundle に `extra` フィールドを追加し、

  - 実行時メタ情報（生成日時、index のバージョンなど）
  - seed_ids のうち不明だった ID 一覧
    を格納する案もあり（後方互換を意識して optional な object とする）。
- LLM への直接入力を意識した「フラットな Markdown 表現」の data_contract（例: DATA-906_prompt_bundle）を別途定義し、
  ContextBundle → PromptBundle の変換用 IF を設計することも検討対象。



