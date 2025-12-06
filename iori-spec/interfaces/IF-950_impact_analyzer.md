---
kind: interfaces
scope: tooling.impact
id: IF-950
spec_title: "IF-950: Impact Analyzer — Changed IDs → Impacted Specs"
status: draft

trace:
  req: []        # 例: REQ-8xx_impact_analysis などを後で紐付け
  if:
    - IF-910     # Spec Index Builder — SpecIndex を前提とする
    - IF-930     # Trace Lint — trace グラフの健全性チェック
  data:
    - DATA-900   # Spec Index Catalog（impact の唯一の必須 DATA）
    - DATA-905   # Context Bundle（将来、影響範囲コンテキストとの連携に利用可能）
  test: []
  task: []

dp:
  produces: []      # impact_report を DATA-906 として data_contract 化する案あり（将来）
  produced_by: []
  consumes:
    - DATA-900
  inputs: []

doc:
  read_next:
    - DATA-900
    - interfaces/IF-910_spec_index_builder.md
    - interfaces/IF-930_trace_lint.md
    - interfaces/IF-960_context_builder.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-950: Impact Analyzer — Changed IDs → Impacted Specs

## LLM_BRIEF

- role: この IF は、`spec_index.json`（DATA-900）を入力として、  
  **「どの REQ / IF / DATA / TEST / TASK を変更したら、どの spec が影響を受けるか」**を計算する  
  **Impact Analyzer（影響範囲分析モジュール）の振る舞い**を定義します。
- llm_action: あなた（LLM）はこの IF と DATA-900 を読み、`iori-spec impact` コマンドの中核となる  
  **Python モジュール（impact コア）** を設計・実装してください。  
  仕様ファイルそのものを読むのではなく、「SpecIndex（DATA-900）の trace グラフ上で  
  changed_ids から到達可能なノードを整理し、ImpactReport を返す」コードを書くことが目的です。

## USAGE

- ユースケース（CLI 層から見た想定）

  - 単純な影響範囲チェック  
    `iori-spec impact IF-200 DATA-101 --mode forward --max-distance 2 --format table`

  - REQ を変更したときに、どの IF / TEST に波及するかを確認  
    `iori-spec impact REQ-201 --mode forward --roles if,test --format json`

  - IF / DATA の変更が、どの REQ / TEST に跳ねるかを双方向で見る  
    `iori-spec impact IF-200 DATA-101 --mode both --max-distance 3`

- ユースケース（Python モジュールとしての関数イメージ）

  ```python
  analyze_impact(
      index: SpecIndex,
      changed_ids: list[str],
      *,
      mode: str = "forward",         # "forward" | "backward" | "both"
      max_distance: int | None = None,
      roles: list[str] | None = None,
      include_doc_links: bool = False,
  ) -> ImpactReport
  ````

- `SpecIndex` … DATA-900 の構造
- `ImpactReport` … 本 IF で定義する構造（後述）

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- IF-930: Trace Lint — REQ / IF / DATA / TEST Coverage
- IF-960: Context Builder — Spec IDs → LLM Context Bundle
- reference/iori_spec_guide.md（role / kind / scope / trace 方針）

---

## 1. このドキュメントの役割

- 仕様変更時に「どこまで直せばいいか」「どの spec / test を見直すべきか」を判断するための
  **影響範囲分析のインターフェイス**を定義する。
- 具体的には：

  - 入力：changed_ids（変更対象 ID 群）、SpecIndex、各種オプション（mode / max_distance / roles）
  - 出力：ImpactReport（影響を受ける spec の一覧＋距離・カテゴリ・経路情報）
- CLI (`iori-spec impact`) / Python モジュール / LLM から見た
  **一貫した「impact API の契約」**として機能する。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- 対象とするグラフ：

  - SpecIndex（DATA-900）の

    - `nodes[].id`
    - `nodes[].role`
    - `nodes[].trace.*`（req / if / data / test / task）
    - （オプション）`nodes[].doc.read_next`
- 影響とみなす経路：

  - **trace edge** が主対象。
    → 実装・テスト上の「依存関係」「責務の紐付き」を表す。
  - `include_doc_links: true` の場合のみ、`doc.read_next` エッジも影響経路として扱う。

### 2.2 前提

- `spec_index.json` は IF-910 により生成済みであり、
  可能であれば IF-930（trace lint）で重大な不整合が修正されている。
- `changed_ids` に未知の ID が渡された場合の挙動は明示する（後述）。
- ImpactReport のスキーマは、将来的に DATA-906 として data_contract 化する予定。

---

## 3. 運用上の目安（LLM / SDD 観点）

- 参照する SpecIndex（DATA-900）は config の `paths.ignore_dirs` を適用して最新化する。
- 変更対象 ID（changed_ids）は CI などで差分検知から渡し、`max_distance` や roles フィルタは運用ポリシーに沿って設定する。
- 出力（DATA-906 相当）はレビューやタスク起票にそのまま添付できるよう、再現性のある探索順序（BFS）と安定したソートを心がける。

---

## 4. Summary

- SpecIndex から G_trace/G_dp/G_doc を組み合わせ、指定 ID からの近傍ノードを BFS で列挙する impact 分析のインターフェイスを定義する。
- 方向（upstream/downstream/both）や距離、roles、docリンクの有無で探索範囲を制御し、ImpactReport（DATA-906）を生成する。

---

## 5. Inputs

- `artifacts/spec_index.json`（DATA-900）
- changed_ids, mode, max_distance, roles, include_doc_links などのパラメータ

---

## 6. Outputs

- ImpactReport（DATA-906、json/table/markdown を想定）
- Exit Code（異常時のみ非 0）

---

## 7. Impact Model（影響モデル）

### 7.1 mode（方向）の定義

- `mode: "forward"`

  - changed_ids から **下流方向**（依存される側 → 依存する側）に影響が伝播するとみなす。
  - 例：`REQ -> IF -> TEST` の場合、REQ を変えると IF / TEST も見直しが必要。
- `mode: "backward"`

  - changed_ids から **上流方向**（依存する側 → 依存される側）に影響が伝播するとみなす。
  - 例：TEST を変えたとき、「どの REQ を検証しているテストなのか」を遡る。
- `mode: "both"`

  - forward / backward の両方を計算し、結果をマージする。

> 厳密な「どっちが上流か」はシステム定義次第だが、
> MVP では「REQ が上流、IF / DATA / TEST / TASK が下流」という前提でよい。

### 7.2 エッジの向き

- Trace edge

  - `node.id -> trace.req[]`
    → 「このノードは、列挙された REQ に紐づいている」
    → REQ を上流、実装/テストを下流とみなす場合：

    - forward: `REQ -> current node`
    - backward: `current node -> REQ`
  - `node.id -> trace.if[]` / `trace.data[]` / `trace.test[]` / `trace.task[]` についても同様に扱う。
- Doc edge（オプション）

  - `node.id -> doc.read_next[]`
    → context 的な関連。impact 的には重要度を下げて扱うか、`include_doc_links` で明示的に有効化。

> 具体的な「エッジ向き」の決め方は、`iori_spec_guide` か本 IF の補足で定義してもよいが、
> MVP では「REQ を中心に、実装側が REQ を参照する」という素朴なモデルで十分。

---

## 8. フィルタとモード

### 8.1 changed_ids

- 1 つ以上の spec ID を受け取る。
- changed_ids 自身も ImpactReport に含める（カテゴリー `"changed"`）。

### 8.2 max_distance

- `max_distance: int | None`

  - `None` の場合：到達可能なノードは全て対象。
  - `0` の場合：changed_ids のみが対象。
  - `1` の場合：changed_ids と、そこから 1 hop で到達可能なノードが対象。
  - それ以上の場合：BFS 的に展開。

### 8.3 roles フィルタ

- `roles: list[str] | None`

  - 例：`["req", "if", "test"]`
  - `None` の場合：全 role を対象とする。

### 8.4 include_doc_links

- `include_doc_links: bool`

  - `false` の場合：

    - trace edge のみを影響経路として扱う。
  - `true` の場合：

    - `doc.read_next` を影響経路として追加し、追加 hop として扱う。

---

## 9. ImpactReport の構造（案）

※ ここでは IF として必要な最小構造を定義する。
　後続の DATA-906 で data_contract 化する際の素案としても利用する。

### 9.1 ImpactReport（トップレベル）

| フィールド               | 型               | 必須  | 説明                                     |
| ------------------- | --------------- | --- | -------------------------------------- |
| `changed_ids`       | string[]        | Yes | 入力として与えられた変更対象 ID 一覧。                  |
| `mode`              | string          | Yes | `"forward"` / `"backward"` / `"both"`。 |
| `max_distance`      | int \| null      | No  | 探索に用いた最大距離。指定なしは `null`。               |
| `roles`             | string[] \| null | No  | フィルタに用いた role。指定なしは `null`。            |
| `include_doc_links` | bool            | Yes | doc.read_next も影響経路に含めたかどうか。           |
| `nodes`             | ImpactNode[]    | Yes | 影響を受けるノード（changed を含む）の一覧。             |

### 9.2 ImpactNode

| フィールド          | 型               | 必須  | 説明                                                                                                             |
| -------------- | --------------- | --- | -------------------------------------------------------------------------------------------------------------- |
| `id`           | string          | Yes | SpecNode の ID。                                                                                                 |
| `file`         | string          | Yes | SpecNode のファイルパス。                                                                                              |
| `kind`         | string          | Yes | kind。                                                                                                          |
| `scope`        | string          | Yes | scope。                                                                                                         |
| `role`         | string          | Yes | role（req / if / data / test / task / ...）。                                                                     |
| `status`       | string          | Yes | status（draft / review / stable / deprecated）。                                                                  |
| `category`     | string          | Yes | `"changed"` / `"downstream_direct"` / `"downstream_indirect"` / `"upstream_direct"` / `"upstream_indirect"` 等。 |
| `distance`     | int             | Yes | changed_ids からの最短距離（0 が自身）。                                                                                    |
| `from_changed` | string[]        | Yes | このノードに到達可能だった changed_ids の一覧。                                                                                 |
| `sample_path`  | string[] \| null | No  | 代表的な経路を ID の列で表現（例: `["REQ-201","IF-200","TEST-300"]`）。                                                        |

> **MVP の方針**
>
> - `nodes` だけで impact を利用するツールが多い想定。
> - `sample_path` は、1 ノードあたり 1 パス（最短経路など）を任意で計算すればよい。

---

## 10. 処理フロー（概略）

### 10.1 エントリポイント

1. `spec_index.json`（DATA-900）を読み込み、SpecIndex オブジェクトを構築。
2. `changed_ids`, `mode`, `max_distance`, `roles`, `include_doc_links` を受け取る。
3. グラフ構築・探索を行い、ImpactReport を構築する。

### 10.2 グラフ構築

1. **ノード辞書の構築**

   - `nodes_by_id: dict[str, SpecNode]`
2. **エッジ集合の構築**

   - trace 由来：

     - 例えば、`node.trace.req` に ID 群があるとき、

       - 「REQ が上流」で「node が下流」という前提で

         - upstream_edges: `node.id -> req_id`
         - downstream_edges: `req_id -> node.id`
     - 他の trace フィールド（if / data / test / task）も同様に扱う。
   - doc 由来（オプション）：

     - `include_doc_links == true` の場合のみ、

       - upstream / downstream 両方向のエッジに `doc.read_next` を混ぜてもよい（設計次第）。
3. **探索方向の決定**

   - `mode == "forward"` の場合 … downstream_edges を使って changed_ids から探索。
   - `mode == "backward"` の場合 … upstream_edges を使って探索。
   - `mode == "both"` の場合 … 両方の探索を行って結果をマージ。

### 10.3 探索アルゴリズム（BFS ベース）

1. それぞれの方向（forward/backward）について：

   - `queue := [(id, distance=0)]` を初期化（id は changed_ids）。
   - 訪問済み集合 `visited[direction]` を管理。
   - BFS で `max_distance` までのノードを探索。
   - 各ノードについて、最短距離・どの changed_id から到達したかを記録。
2. forward / backward の両方を使う場合：

   - 方向ごとに `distance` を持つか、統合して「最小距離」とするかは設計次第だが、
     MVP では「mode ごとに別々に探索 → ノード単位で merge」でもよい。

### 10.4 カテゴリ付け

- `category` の例：

  - `id ∈ changed_ids` → `"changed"`
  - forward 探索で距離 1 のノード → `"downstream_direct"`
  - forward 探索で距離 ≥ 2 のノード → `"downstream_indirect"`
  - backward 探索で距離 1 のノード → `"upstream_direct"`
  - backward 探索で距離 ≥ 2 のノード → `"upstream_indirect"`

- `mode == "both"` の場合：

  - 片方だけでヒットした場合はそのカテゴリ。
  - 双方向でヒットした場合はルールを決めて優先度をつける（例: upstream を優先、など）。

### 10.5 sample_path の構築（任意）

- BFS で親ポインタを保持しておくことで、各ノードへの最短経路を復元できる。
- `sample_path` として、
  `changed_id → ... → node.id` の ID 列を 1 パスだけ格納すればよい。

---

## 11. Acceptance Criteria（受け入れ条件）

1. **基本動作**

   - `changed_ids = ["REQ-201"]`, `mode = "forward"`, `max_distance = 1` のとき、

     - `REQ-201` 自身が `category = "changed"` で含まれる。
     - `REQ-201` に紐づく IF / DATA / TEST ノードが `category = "downstream_direct"` で含まれる。
2. **距離の扱い**

   - `max_distance = 0` の場合 … `nodes` には changed_ids のみが含まれる。
   - `max_distance = None` の場合 … 到達可能なノード全てが対象となる。
3. **roles フィルタ**

   - `roles = ["req", "if"]` を指定した場合、
     `nodes[].role` に `"data" / "test" / "task"` が含まれない。
4. **未知 ID の扱い**

   - `changed_ids` に SpecIndex に存在しない ID が含まれる場合：

     - その ID は `nodes` には含めず、ImpactReport 内で検出される（例: 別フィールドで列挙する、または警告ログを出す）。
5. **複数 changed_ids の扱い**

   - 複数の changed_ids から到達できるノードについて、

     - `from_changed` に全ての起点 ID が列挙されている。
6. **複雑性**

   - SpecIndex のノード数 N, trace エッジ数 E に対して、
     影響範囲探索の計算量は O(N + E) 程度に収まる（BFS ベース）。

---

## 12. Inputs / Outputs（コア関数）

### 12.1 Inputs

| 名前                  | 型                | 必須  | 説明                                                        |
| ------------------- | ---------------- | --- | --------------------------------------------------------- |
| `index`             | SpecIndex        | Yes | DATA-900 準拠の SpecIndex オブジェクト。                            |
| `changed_ids`       | list[str]        | Yes | 変更対象とみなす spec ID 群。                                       |
| `mode`              | string           | No  | `"forward"` / `"backward"` / `"both"`（デフォルト `"forward"`）。 |
| `max_distance`      | int \| None       | No  | BFS 探索の距離上限。`None` は上限なし。                                 |
| `roles`             | list[str] \| None | No  | 対象とする role のフィルタ。                                         |
| `include_doc_links` | bool             | No  | `doc.read_next` を影響経路に含めるか（デフォルト `False`）。                |

### 12.2 Outputs

- 戻り値：`ImpactReport`（§5.1 で定義した構造体）

  - CLI `iori-spec impact --format json` では、このオブジェクトをそのまま JSON にシリアライズして stdout へ出力する。

---

## 13. 非機能要件（簡易）

- **性能**

  - 通常の SpecIndex 規模（数百〜数千ノード程度）に対して、
    1 回の impact 分析が体感的にストレスのない時間内で完了すること（数秒以内を目安）。
- **堅牢性**

  - trace の不整合（存在しない ID 参照など）があっても、
    可能な限り impact 計算を継続し、問題箇所は別途 lint（IF-930）で検出する設計とする。
- **LLM フレンドリ**

  - フィールド名・関数名は素直な英単語（`analyze_impact`, `ImpactReport`, `ImpactNode` など）とし、
    JSON から Python / TypeScript へのマッピングがしやすい形を保つ。
- **拡張性**

  - 将来的に ImpactReport を DATA-906 として正式 data_contract 化するときに、
    既存コード・ツールが大きく壊れないよう、フィールドの追加は optional / 後方互換を前提とする。

---

## 14. 今後の拡張（メモ）

- ImpactReport の正式な data_contract として `DATA-906_impact_report` を定義する。
- `category` の粒度を増やす（例: `"downstream_if"`, `"downstream_test"` など）ことで、
  UI でのグルーピングやフィルタリングをしやすくする。
- IF-960（Context Builder）と連携し、

  - ImpactReport で得られた impacted IDs をそのまま seed_ids に渡してコンテキスト生成する
    「impact → context」ワークフローを標準パターンとして整理する。



