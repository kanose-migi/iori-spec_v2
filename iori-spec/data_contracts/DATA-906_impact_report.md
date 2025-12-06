---
kind: data_contracts
scope: tooling.impact
id: DATA-906
spec_title: "DATA-906: Impact Report — Changed IDs → Impacted Specs (JSON)"
status: draft

trace:
  req: []        # 例: REQ-8xx_impact_analysis などを後で紐付け
  if:
    - IF-950     # Impact Analyzer — Changed IDs → Impacted Specs
  data:
    - DATA-900   # 入力: Spec Index Catalog
  test: []
  task: []

dp:
  produces:
    - DATA-906   # IF-950 が生成する impact_report
  produced_by:
    - IF-950
  consumes:
    - DATA-900
  inputs:
    - iori_spec_config.yaml
    - Markdown specs (*.md)

doc:
  read_next:
    - DATA-900
    - interfaces/IF-950_impact_analyzer.md
  see_also:
    - DATA-902_lint_result.md
    - DATA-905_context_bundle.md
    - impl_notes/spec_command.md
---

# DATA-906: Impact Report — Changed IDs → Impacted Specs (JSON)

## LLM_BRIEF

- role: このファイルは、`iori-spec impact` コマンドや IF-950（Impact Analyzer）が生成する  
  **「影響範囲レポート（ImpactReport）」のデータ構造**を定義する data_contract です。
- llm_action: あなた（LLM）は IF-950 を実装するとき、この data_contract を  
  **「impact コマンドの JSON 出力／Python 戻り値のフォーマット」**として参照し、  
  ここで定義された構造を持つ `ImpactReport` オブジェクトを返すコードを書いてください。  
  `impact_report.json` を手で書くのではなく、「常にこの構造に従う実装」を行うことが目的です。

## USAGE

- コマンド出力（CLI）
  - `iori-spec impact REQ-201 IF-200 --mode forward --max-distance 2 --format json`  
    → 標準出力に **ImpactReport（DATA-906 準拠の 1 オブジェクト）** を JSON として出す。
- Python ライブラリとして
  - `analyze_impact(...) -> ImpactReport`  
    → 関数戻り値の構造が DATA-906 に準拠する。
- 他ツールからの利用
  - エディタ拡張・CI・独自スクリプトは、この data_contract に従って ImpactReport をパースし、  
    `nodes[]` をもとに「どの spec / test を見直すべきか」を表示・ゲーティングに利用する。

## READ_NEXT

- IF-950: Impact Analyzer — Changed IDs → Impacted Specs
- DATA-900: Spec Index Catalog — spec_index.json
- DATA-902: Lint Result — LintIssue List (JSON)

---

## 1. このドキュメントの役割

- impact 系の入出力を SSOT 化するために、
  - ImpactReport（トップレベル）
  - ImpactNode（spec 単位の要素）
  の構造とフィールド意味を定義する。
- これにより、
  - IF-950 の実装
  - `iori-spec impact` の CLI 出力
  - 影響範囲を扱う周辺ツール（CI、エディタ、ダッシュボード）
  が、同じ前提で ImpactReport を扱えるようになる。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- DATA-906 は **1 回の impact 実行で得られる「影響範囲レポート 1 つ」**のフォーマットを定義する。
- トップレベルは **1 つの JSON オブジェクト**（ImpactReport）とする。

```jsonc
{
  "changed_ids": ["REQ-201"],
  "mode": "forward",
  "max_distance": 2,
  "roles": ["req", "if", "test"],
  "include_doc_links": false,
  "unknown_ids": [],
  "nodes": [
    { /* ImpactNode */ }
  ]
}
````

### 2.2 前提

- ImpactReport は SpecIndex（DATA-900）にもとづき、
  IF-950 が trace グラフ上の到達可能ノードを整理して構築する。
- 影響経路の詳細（全パス）は必須ではなく、MVP では「代表的な 1 パス（sample_path）」だけ持てばよい。

---

## 3. 運用上の目安（LLM / SDD 観点）

- `changed_ids` に存在しない ID が混じる場合は `unknown_ids` に明示し、レポートとしては続行する。
- forward/backward/both の方針は IF-950 側で統一し、ImpactReport のスキーマは固定する。
- Context など他ツールに渡す際は、距離や role でフィルタし直せるように情報を保持する。

---

## 4. Summary

- **ImpactReport** は、「どの ID の変更を起点に」「どの方向・距離で」
  「どの spec が影響を受けるとみなされるか」を一覧するレポート。
- 構造は：

  - `ImpactReport` … 実行条件＋ `nodes[]`
  - `ImpactNode` … spec 1 件分の影響情報
    という 2 層で構成される。

---

## 5. Schema

### 5.1 ImpactReport（トップレベル）

#### 5.1.1 フィールド一覧

| フィールド               | 型               | 必須  | 説明                                                       |
| ------------------- | --------------- | --- | -------------------------------------------------------- |
| `changed_ids`       | string[]        | Yes | 入力として与えられた変更対象 ID 一覧。                                    |
| `mode`              | string          | Yes | `"forward"` / `"backward"` / `"both"`。                   |
| `max_distance`      | int \| null      | No  | BFS 探索に用いた距離上限。指定なしは `null`。                             |
| `roles`             | string[] \| null | No  | フィルタに用いた role 一覧（例: `["req","if","test"]`）。指定なしは `null`。 |
| `include_doc_links` | bool            | Yes | `doc.read_next` を影響経路に含めたかどうか。                           |
| `unknown_ids`       | string[]        | Yes | SpecIndex に存在しなかった changed_ids（なければ空配列）。                 |
| `nodes`             | ImpactNode[]    | Yes | 影響を受けるノード（changed を含む）の一覧。                               |

#### 5.1.2 フィールド詳細

- `changed_ids`

  - CLI / API で impact 対象として指定された ID を、そのまま配列で持つ。
  - SpecIndex に存在しない ID が含まれる場合も、そのままここには残す（unknown_ids で補足）。
- `mode`

  - IF-950 で定義した方向指定：

    - `"forward"`：上流 → 下流への影響
    - `"backward"`：下流 → 上流への影響
    - `"both"`：両方向
- `max_distance`

  - hop 数上限（depth）。
  - `null` は「上限なし」を意味する。
- `roles`

  - ImpactNode を生成する際にフィルタした role。
  - `null` の場合、「role で絞り込んでいない」と解釈する。
- `include_doc_links`

  - `true` の場合、`doc.read_next` も影響経路として扱った。
  - `false` の場合、trace edge のみを利用した。
- `unknown_ids`

  - `changed_ids` のうち、SpecIndex に存在しなかった ID 一覧。
  - 存在しない ID は `nodes` には含めず、ここで補足する。
- `nodes`

  - changed_ids を含む、impact 計算の結果として得られた spec 群。
  - 配列順序は実装側（IF-950）のルール（距離・category・role 等）に基づき安定していることが望ましい。

---

### 5.2 ImpactNode（spec 単位の要素）

#### 5.2.1 構造（一覧）

| フィールド          | 型               | 必須  | 説明                                                                                                              |
| -------------- | --------------- | --- | -------------------------------------------------------------------- |
| `id`           | string          | Yes | SpecNode の ID。|
| `file`         | string          | Yes | SpecNode のファイルパス（root からの相対）。|
| `kind`         | string          | Yes | SpecNode の kind。|
| `scope`        | string          | Yes | SpecNode の scope。|
| `role`         | string          | Yes | SpecNode の role（req / if / data / test / task / ...）。|
| `status`       | string          | Yes | SpecNode の status（draft / review / stable / deprecated）。|
| `category`     | string          | Yes | `"changed"` / `"downstream_direct"` / `"downstream_indirect"` / `"upstream_direct"` / `"upstream_indirect"` など。 |
| `distance`     | int             | Yes | changed_ids からの最短距離（0 が自身）。|
| `from_changed` | string[]        | Yes | このノードに到達可能だった changed_ids の一覧。|
| `sample_path`  | string[] \| null | No  | 代表的な経路を ID 列で表現（例: `["REQ-201","IF-200","TEST-300"]`）。|

#### 5.2.2 フィールド詳細

- `id`

  - SpecIndex の `nodes[].id` と一致する値。
- `file`

  - SpecIndex の `nodes[].file` と一致する相対パス。
- `kind` / `scope` / `role` / `status`

  - SpecIndex の対応フィールドをそのまま保持する。
  - `role` は `req` / `if` / `data` / `test` / `task` 等。
- `category`

  - 影響の種類を示すラベル。MVP では次の値を想定：

    - `"changed"`
      → `id ∈ changed_ids`（起点ノード）
    - `"downstream_direct"`
      → forward 探索で distance == 1 のノード
    - `"downstream_indirect"`
      → forward 探索で distance >= 2 のノード
    - `"upstream_direct"`
      → backward 探索で distance == 1 のノード
    - `"upstream_indirect"`
      → backward 探索で distance >= 2 のノード

  - `mode == "both"` で forward / backward の両方に現れた場合の優先順は IF-950 で定義（例: upstream を優先、あるいは別カテゴリを追加）してよい。
- `distance`

  - changed_ids からの最短 hop 数。
  - `0` … changed 自身
  - `1` … 1 hop で到達可能
- `from_changed`

  - このノードに到達可能だった changed_ids の一覧。
  - 複数変更がある場合に、「どの変更がどこに影響するか」を集約して確認する用途に使う。
- `sample_path`

  - 代表的な経路（最短経路など）を、ID のシーケンスとして表現。
  - 例：`["REQ-201","IF-200","TEST-300"]`
  - 経路が複数ある場合でも、MVP では 1 パスのみを入れればよい。
    詳細な全経路が必要な場合は将来の拡張で別フィールドを導入する。

---

## 6. 例

簡易な ImpactReport の例：

```jsonc
{
  "changed_ids": ["REQ-201"],
  "mode": "forward",
  "max_distance": 2,
  "roles": ["req", "if", "test"],
  "include_doc_links": false,
  "unknown_ids": [],
  "nodes": [
    {
      "id": "REQ-201",
      "file": "requirements/REQ-201_digits_segments.md",
      "kind": "requirements",
      "scope": "client.query_engine",
      "role": "req",
      "status": "stable",
      "category": "changed",
      "distance": 0,
      "from_changed": ["REQ-201"],
      "sample_path": ["REQ-201"]
    },
    {
      "id": "IF-200",
      "file": "interfaces/IF-200_query_engine.md",
      "kind": "interfaces",
      "scope": "client.query_engine",
      "role": "if",
      "status": "review",
      "category": "downstream_direct",
      "distance": 1,
      "from_changed": ["REQ-201"],
      "sample_path": ["REQ-201", "IF-200"]
    },
    {
      "id": "TEST-300",
      "file": "tests/TEST-300_query_engine_basic.md",
      "kind": "test",
      "scope": "client.query_engine",
      "role": "test",
      "status": "draft",
      "category": "downstream_indirect",
      "distance": 2,
      "from_changed": ["REQ-201"],
      "sample_path": ["REQ-201", "IF-200", "TEST-300"]
    }
  ]
}
```

---

## 7. Constraints（制約）

- トップレベルは常に **1 オブジェクト**（配列ではない）。
- `nodes` は配列であり、影響を受けるノードがない場合は `[]`。
- `distance` は非負整数（0 以上）。
- `changed_ids` / `unknown_ids` / `from_changed` は重複を含まない配列であることが望ましい。
- `mode` は `"forward"` / `"backward"` / `"both"` のいずれか。
- `category` は IF-950 で定義された値セット内にある必要がある。

---

## 8. IF-950 との関係

- IF-950（Impact Analyzer）は、この DATA-906 を

  - Python 戻り値の型
  - CLI `--format json` の出力フォーマット
    として採用する。
- IF-950 側では、グラフ探索の結果を
  ここで定義した ImpactReport / ImpactNode にマッピングして返す実装を行う。

---

## 9. 今後の拡張（メモ）

- `summary` フィールドを ImpactReport に追加し、

  - `total_nodes`
  - `changed_count`
  - `downstream_count`
  - `upstream_count`
    などの集計値を持たせる案もある（後方互換性に配慮して optional に追加する）。
- `category` のバリエーションを増やし、

  - `"downstream_if"`, `"downstream_test"` など role 別カテゴリを導入してもよい。
- ImpactReport から ContextBundle（DATA-905）を直接生成する IF（例: `IF-955: impact → context`）を定義し、
  「影響範囲をそのまま LLM コンテキストにする」ワークフローを標準化することも検討対象。



