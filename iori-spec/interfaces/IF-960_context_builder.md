---
kind: interfaces
scope: tooling.context
id: IF-960
spec_title: "IF-960: Context Builder — Spec IDs → LLM Context Bundle"
status: draft

trace:
  req: []        # 例: REQ-8xx_context_builder などを後で紐付け
  if:
    - IF-910     # Spec Index Builder — SpecIndex を前提とする
    - IF-920     # Lint Core — 構造が整った spec 群を前提とできる
    - IF-930     # Trace Lint — trace の健全性が前提として望ましい
  data:
    - DATA-900   # Spec Index Catalog（ノード情報・trace・doc リンク）
    - DATA-901   # Spec Section Schema（tool_source セクション定義）
  test: []
  task: []

dp:
  produces: []      # コンテキストバンドルは通常 HTTP/CLI レスポンスとして消費される（永続 DATA は別途検討）
  produced_by: []
  consumes:
    - DATA-900
    - DATA-901
  inputs:
    - iori_spec_config.yaml   # role / kind / scope 定義（優先度のヒントとして利用してもよい）

doc:
  read_next:
    - DATA-900
    - DATA-901
    - interfaces/IF-910_spec_index_builder.md
    - reference/iori_spec_guide.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-960: Context Builder — Spec IDs → LLM Context Bundle

## LLM_BRIEF

- role: この IF は、`spec_index.json`（DATA-900）と `spec_section_schema.yaml`（DATA-901）を入力として、  
  1つ以上の **種 ID（seed_ids）** から「LLM に渡すべき最小限かつ十分なコンテキスト」を組み立てる **コンテキストビルダー**の振る舞いを定義します。
- llm_action: あなた（LLM）はこの IF と DATA-900 / DATA-901 を読み、`iori-spec context` コマンドの中核となる **Python モジュール（context コア）** を設計・実装してください。  
  仕様そのものを直接要約するのではなく、「どの spec / セクションを選び、どの順番で LLM に渡すか」を決めるコードを書くことが目的です。

## USAGE

- ユースケース（CLI 層から見た想定）

  - 指定 ID の周辺だけを見たい場合  
    `iori-spec context REQ-201 IF-200 --format markdown`

  - 役割を絞って近傍を見たい場合  
    `iori-spec context REQ-201 --roles req,if,data --depth 1 --format json`

  - トークン制約を意識した LLM 用コンテキスト生成  
    `iori-spec context REQ-201 --max-tokens 2000 --strategy default`

- ユースケース（Python モジュールとしての関数イメージ）

  ```python
  build_context(
      index: SpecIndex,
      section_schema: SectionSchema,
      seed_ids: list[str],
      *,
      depth: int = 1,
      roles: list[str] | None = None,
      max_tokens: int | None = None,
      strategy: str = "default",
  ) -> ContextBundle
  ````

- `SpecIndex` … DATA-900 準拠
- `SectionSchema` … DATA-901 準拠（内部表現）
- `ContextBundle` … 本 IF で定義する構造（後述）

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- DATA-901: Spec Section Schema — spec_section_schema.yaml
- IF-910: Spec Index Builder — Markdown Specs → spec_index.json
- reference/iori_spec_guide.md（ID / role / kind / scope の意味）

---

## 1. このドキュメントの役割

- 「巨大仕様でも、LLM からは常に“小さい仕様”に見える状態」を実現するための中核機能として、
  **ID → 近傍 spec の集合 → 抜粋セクション →（任意で）マージ済み Markdown** までのパイプラインの振る舞いを定義する。
- 具体的には：

  - どの入力を受け取り（seed_ids, depth, roles, max_tokens など）
  - SpecIndex（DATA-900）と SectionSchema（DATA-901）から
  - どのようなルールで spec / セクションを選び
  - どの順番で返すか（ContextBundle の形式）
    を仕様として明示する。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- 本 IF が扱うのは **コンテキストの「選択・構造化」** であり、
  個々のセクション本文の「要約」そのものは範囲外とする（必要なら別 IF / 別フェーズ）。

- 対象となるデータ：

  - SpecIndex（DATA-900）

    - `nodes[].(id, kind, scope, role, file, trace, doc, llm_brief, summary)`
  - SpecSectionSchema（DATA-901）

    - `rules[].(heading, required, multiple, tool_source, order)`
    - `options.default_tool_source` 等

- コンテキスト対象セクションは、原則として `tool_source: true` な見出しに限定する。

### 2.2 前提

- SpecIndex / SectionSchema は lint（IF-920 / IF-930）済みであることが望ましいが、
  一部の不整合があっても可能な範囲で動作を継続する実装が望ましい。
- トークン数の見積りは近似でよく、
  単語数や文字数からのラフな換算（「1 トークン ≒ 3〜4 文字」など）を用いてもよい。

---

## 3. 運用上の目安（LLM / SDD 観点）

- 入力 SpecIndex（DATA-900）は `paths.ignore_dirs` を適用した最新を使用する。
- context 生成時は `spec_section_schema` の `tool_source=true` のセクションを優先し、出力サイズが大きくなりすぎないよう max_tokens を意識する。
- `--format json` 出力（DATA-905 相当）は LLM 連携の中間形式として安定再現性を重視する。

---

## 4. Summary

- SpecIndex を起点に seed ID と近傍 ID を決定し、セクションスキーマに従って本文を抽出・整形した ContextBundle（DATA-905）を生成する。
- 探索範囲（radius/roles/docリンク）と抽出ルールを切り替え可能にする。

---

## 5. Inputs

- `artifacts/spec_index.json`（DATA-900）
- `spec_section_schema.yaml`（DATA-901）
- seed_ids, radius/depth, roles, include_doc_links, max_tokens などのパラメータ

---

## 6. Outputs

- ContextBundle（DATA-905、json/markdown）
- Exit Code（生成可否で判断）

---

## 7. ContextBuilder の役割

ContextBuilder は、以下の 3 層の仕事を行う。

1. **Graph Layer（ID → 近傍 ID 集合）**

   - SpecIndex の `trace.*` / `doc.read_next` / role / scope などを利用して、
     seed_ids の「周辺ノード」集合を構築する。
2. **Section Layer（ID → 抜粋セクション集合）**

   - SectionSchema（DATA-901）の `rules` に従い、
     各 spec から LLM に渡すべきセクション（`tool_source: true`）を抽出する。
3. **Bundle Layer（ContextBundle の組み立て）**

   - 上記で得られた (spec, section) の集合を、

     - 優先度
     - 最大トークン数
     - 表示順序
       に従ってソート・間引きし、最終的な ContextBundle 構造として返す。

---

## 8. Graph Layer ? ID から近傍 ID を決める

### 8.1 入力パラメータ

- `seed_ids: list[str]`

  - 1 つ以上の spec ID（例: `["REQ-201"]`, `["IF-200", "DATA-101"]`）
- `depth: int`

  - グラフ探索の深さ（最短距離）。
  - `depth = 0` の場合：seed_ids 自身のみ
  - `depth = 1` の場合：seed_ids に加えて、1 hop で到達可能なノード（trace/doc 経由）も対象
- `roles: list[str] | None`

  - 対象とする role をフィルタする（例: `["req", "if", "data", "test"]`）。
  - `None` の場合、全 role を対象とする。

### 8.2 エッジの種類

SpecIndex から、以下のエッジを構成する：

- **Trace edge**

  - `node.trace.req`, `node.trace.if`, `node.trace.data`, `node.trace.test`, `node.trace.task`
  - それぞれ `node.id -> trace.*[i]` という有向エッジとする。
- **Doc edge**

  - `node.doc.read_next` に列挙される ID
    → `node.id -> read_next[i]` として有向エッジ。
- （将来）別種のリンク（`see_also` の ID 化など）を追加する可能性あり。

### 8.3 探索アルゴリズム（MVP）

1. seed_ids をキューに入れ、距離 0 とする。
2. BFS 風に探索し、距離 `d` のノードから出るエッジを辿って距離 `d+1` のノードを発見。
3. `depth` で指定された最大距離まで探索する。
4. 到達したノード集合から、`roles` / `scopes` などのフィルタをかける。

> 注意: `depth` は hop 数であり、trace/doc どちらのエッジも同じ 1 hop とみなす。
> role / kind ごとに重み付けを変えたい場合は拡張で扱う。

---

## 9. Section Layer ? どのセクションを拾うか

### 9.1 SectionSchema の利用

- SectionSchema（DATA-901）の `rules` から、`tool_source: true` なルールを抽出する。
- 各ルールについて：

  - `kinds` / `heading.level` / `heading.text` の条件に合致する見出しを spec 本文から探す。
  - `match: exact` または `prefix` に従ってマッチングする。

### 9.2 抽出単位

各 SpecNode について、以下の情報を抽出する：

- `id`, `file`, `kind`, `scope`, `role`
- 抽出セクション（SectionSnippet）のリスト

SectionSnippet の最小構造（ContextBundle 内で使用）：

| フィールド           | 型      | 説明                                                        |
| --------------- | ------ | --------------------------------------------------------- |
| `rule_id`       | string | section_schema 上の rule ID（例: `llm_brief`, `req_summary`）。 |
| `heading`       | string | 実際の見出しテキスト（例: `## LLM_BRIEF`）。                            |
| `level`         | int    | 見出しレベル。                                                   |
| `body`          | string | 見出しの直後から次の同レベル以上の見出しの直前までの Markdown テキスト。                 |
| `approx_tokens` | int    | トークン数の概算。                                                 |

### 9.3 抽出ポリシー（MVP）

- `tool_source: true` のセクションのみ抽出する。
- 1 つの rule に対して複数マッチした場合（`multiple: true` 許可のとき）、すべて SectionSnippet として採用する。
- 何もマッチしない rule がある場合でも、context ビルダー自体はエラーにせず、そのセクションを欠いた状態で続行する（代わりに lint が検出する前提）。

---

## 10. Bundle Layer ? ContextBundle の構造

### 10.1 ContextBundle 概要

ContextBundle とは、「どの spec から、どのセクションを、どの順番で LLM に渡すか」を表す構造体である。

最小構造（JSON イメージ）：

```jsonc
{
  "seed_ids": ["REQ-201"],
  "strategy": "default",
  "depth": 1,
  "roles": ["req", "if", "data", "test"],
  "max_tokens": 2000,
  "approx_tokens_total": 1480,
  "items": [
    {
      "id": "REQ-201",
      "file": "requirements/REQ-201_digits_segments.md",
      "kind": "requirements",
      "scope": "client.query_engine",
      "role": "req",
      "sections": [
        {
          "rule_id": "llm_brief",
          "heading": "## LLM_BRIEF",
          "level": 2,
          "body": "...",
          "approx_tokens": 120
        },
        {
          "rule_id": "req_summary",
          "heading": "## 4. Summary",
          "level": 2,
          "body": "...",
          "approx_tokens": 240
        }
      ]
    }
  ]
}
```

### 10.2 フィールド定義

| フィールド                 | 型               | 必須  | 説明                                              |
| --------------------- | --------------- | --- | ----------------------------------------------- |
| `seed_ids`            | string[]        | Yes | 入力として与えられた種 ID の一覧。                             |
| `strategy`            | string          | Yes | 使用した戦略名（例: `"default"`）。                        |
| `depth`               | int             | Yes | 探索に用いた depth。                                   |
| `roles`               | string[] \| null | No  | 対象とした role 一覧。                                  |
| `max_tokens`          | int \| null      | No  | 制約として渡された最大トークン数（なければ null）。                    |
| `approx_tokens_total` | int             | Yes | items 配下の全 SectionSnippet の `approx_tokens` 合計。 |
| `items`               | ContextItem[]   | Yes | 抽出された spec ごとのコンテキスト要素。                         |

ContextItem の構造：

| フィールド      | 型                | 必須  | 説明                    |
| ---------- | ---------------- | --- | --------------------- |
| `id`       | string           | Yes | SpecNode の ID。        |
| `file`     | string           | Yes | SpecNode のファイルパス。     |
| `kind`     | string           | Yes | kind。                 |
| `scope`    | string           | Yes | scope。                |
| `role`     | string           | Yes | role（req / if / ...）。 |
| `distance` | int              | Yes | seed からの hop 数（0 が種）。 |
| `sections` | SectionSnippet[] | Yes | 抽出されたセクションリスト。        |

SectionSnippet は §5.2 に定義したものを再利用する。

---

## 11. トークン制約と優先度

### 11.1 優先度の基本方針（MVP）

以下の順で優先度を決める（ざっくり）：

1. 距離（`distance` が小さいほど優先）
2. role（例: `req` > `if` > `data` > `test` > `task`）
3. section rule（例: `llm_brief` / summary 系 > usage / acceptance > その他）
4. scope / kind（必要があれば）

### 11.2 max_tokens の扱い

- `max_tokens == null` の場合
  → 全ての SectionSnippet を採用し、`approx_tokens_total` を単に計算するだけ。
- `max_tokens != null` の場合
  → 優先度順に SectionSnippet を追加していき、総和が `max_tokens` を超える直前で打ち切る。

トークン数の近似は例えば：

- 文字数 / 3（日本語前提）または `/ 4`（英語混在）などの簡易ルールでよい。

---

## 12. Acceptance Criteria（受け入れ条件）

1. **種 ID のコンテキスト構築**

   - `seed_ids = ["REQ-201"]`, `depth = 0` の場合、
     ContextBundle の `items` には `REQ-201` のみが含まれ、その `sections` には SectionSchema における `tool_source: true` なセクションが抽出されている。
2. **近傍ノードの取得**

   - `depth = 1` で trace / doc のエッジに沿って 1 hop 以内のノードが `items` に含まれる。
3. **role フィルタ**

   - `roles = ["req", "if"]` を指定した場合、`items[].role` に `data` / `test` / `task` が含まれない。
4. **トークン制約**

   - `max_tokens` を小さい値に設定した場合、
     `approx_tokens_total <= max_tokens` となるように SectionSnippet が切り詰められる。
5. **安定した順序**

   - 同じ入力（SpecIndex / SectionSchema / seed_ids / depth / roles / max_tokens）に対して、
     ContextBundle の `items` / `sections` の順序が安定して再現される（非決定的な順序にならない）。

---

## 13. Inputs / Outputs（コア関数）

### 13.1 Inputs

| 名前               | 型                | 必須  | 説明                               |
| ---------------- | ---------------- | --- | -------------------------------- |
| `index`          | SpecIndex        | Yes | DATA-900 準拠の SpecIndex オブジェクト。   |
| `section_schema` | SectionSchema    | Yes | DATA-901 準拠の SectionSchema 内部表現。 |
| `seed_ids`       | list[str]        | Yes | 1 つ以上の spec ID。                  |
| `depth`          | int              | No  | グラフ探索の最大距離（デフォルト 1）。             |
| `roles`          | list[str] \| None | No  | 対象とする role。                      |
| `max_tokens`     | int \| None       | No  | コンテキストの概算トークン上限。                 |
| `strategy`       | string           | No  | 戦略名（ `"default"` 以外の戦略追加用）。      |

### 13.2 Outputs

- 戻り値：`ContextBundle`（§6 で定義した構造体）

  - CLI `iori-spec context --format json` では、このオブジェクトをそのまま JSON にシリアライズして stdout へ出す。
  - `--format markdown` などのモードでは、ContextBundle から Markdown を生成して出力する。

---

## 14. 非機能要件（簡易）

- **性能**

  - SpecIndex のノード数 N, エッジ数 E に対して、グラフ探索は O(N + E) 程度とし、
    通常の `depth <= 2` であれば実用的な速度で動作すること。
- **拡張性**

  - `strategy` に `"default"` 以外の戦略（例: `"req-focused"`, `"impl-focused"`）を追加しても、
    ContextBundle のスキーマを変更せずに表現できる構造にしておく。
- **LLM フレンドリ**

  - ContextBundle の JSON をそのままプロンプト前処理に使いやすいよう、
    フラットかつ意味の分かりやすいフィールド名に統一する。
- **堅牢性**

  - 不明な ID（SpecIndex に存在しない seed_ids）が渡された場合でも、
    エラーで落とすのか、警告だけにして残りを処理するのかを仕様として明示し、実装で統一する（MVP では「検出して warning、ContextBundle 内の別フィールドに記録」など）。

---

## 15. 今後の拡張（メモ）

- ContextBundle の data_contract として `DATA-905_context_bundle` を切り出す。
- LLM に渡す前に、ContextBundle をもとに **プロンプト断片（prompt_parts）** を構築する IF を別途定義する（具体的なテンプレートや命令文を含める）。
- impact 用 IF（`IF-950_impact_analysis`）を定義し、
  trace グラフ観点での「影響範囲レポート」と context 用の近傍抽出ロジックを再利用する。



