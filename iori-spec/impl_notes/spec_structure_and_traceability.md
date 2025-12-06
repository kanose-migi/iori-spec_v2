---
kind: reference
scope: spec_structure
spec_title: "Spec Structure & Traceability Rules"
status: draft  # draft / review / stable
---
# Spec Structure & Traceability Rules

## 1. このドキュメントの役割

- `iori-spec` が扱う仕様書セットの**構造**と、
  仕様間の **トレースルール（依存関係・トレースの対象範囲）** を定義する。
- 仕様の整合性チェックや LLM によるレビューを行う際に、

  - どのドキュメントを「信頼できる唯一の情報源（SSOT）」と見なすか
  - どの関係を機械的に追跡するか（REQ→IF→DATA→TEST、DATA↔IF など）
    を明示する。

- グラフ理論的な観点から、仕様セット全体を

  - **要求トレースグラフ（G_trace）**
  - **Data–Process Graph（G_DP）**
  - **ドキュメント依存グラフ（G_doc）**
    として扱うための前提を示す。

本ドキュメントは、`iorispec index / trace / impact / context` 等のコマンド仕様の基礎となる。

## 2. 仕様書のメタレイヤー構造

### 2.1 ディレクトリ構造と kind / scope

docs/ 以下の仕様書は、少なくとも次のメタレイヤーに分類される。

| ディレクトリ             | kind            | 主な内容                                    |
| ------------------ | --------------- | --------------------------------------- |
| `steering/` (任意)   | `steering`      | ビジョン・スコープ・成功指標など                        |
| `requirements/`    | `requirements`  | 機能・非機能要件（REQ-xxx）                       |
| （同上）               | `requirements`  | `traceability_map.md`（REQ↔IF/DATA/TEST） |
| `architecture/`    | `architecture`  | コンポーネント構成・レイヤー・依存方向                     |
| `interfaces/`      | `interfaces`    | インターフェイス仕様（IF-xxx）                      |
| `data_contracts/`  | `data_contract` | データ構造・バイナリ仕様（DATA-xxx）                  |
| `tests/`           | `tests`         | テスト仕様（TEST-xxx）                         |
| `dev_tasks/` (任意)  | `dev_tasks`     | 開発タスクカード（TASK-xxx）                      |
| `reference/`       | `reference`     | iori_spec_guide / naming / how-to-write など    |
| `impl_notes/` (任意) | `impl_notes`    | 実装メモ・モジュール詳細設計                          |

各ファイルの front matter には、最低限以下を記載する。

```yaml
---
kind: requirements | architecture | interfaces | data_contract | tests | reference | steering | impl_notes | dev_tasks
scope: functional | nonfunctional | digits | lexicon | IF-100 | ...  # 任意のスコープ名
spec_title: "..." # 人間＆LLM向けタイトル
status: draft | review | stable                        # 任意（ある場合）
---
```

### 2.2 trace_role（トレース上の役割）

`iori-spec` は内部的に、各ドキュメントに対して次の `trace_role` を付与する。

- `trace_role = "source"`

  - REQ / IF / DATA / TEST の**定義元**。
  - 対象となるのは原則として：

    - `requirements/functional.md`, `requirements/nonfunctional.md` 等
    - `interfaces/**/IF-*_spec.md`
    - `data_contracts/*.md`
    - `tests/*.md`

- `trace_role = "trace_map"`

  - `requirements/traceability_map.md`
  - REQ↔IF/DATA/TEST の**公式な対応表（SSOT）**。

- `trace_role = "ref"`

  - `steering/`, `architecture/`, `reference/`, `impl_notes/`, `dev_tasks/` 等。
  - ここに現れる ID は**単なる言及**であり、トレーサビリティの網羅性チェック対象には**含めない**。

    - ただし、TASK-xxx 自体は ID として index 対象となる（3.1 参照）。

`trace_role` は、`kind`・`scope`・パス規則（ディレクトリ階層）から `iori-spec` が機械的に決定する。
ユーザーが明示的に設定する必要はない（※将来的に上書き設定を許可する可能性はある）。

## 3. ID モデルと定義規則

### 3.1 ID 体系

仕様で利用する ID の体系は次のとおりとする。

- 要求 ID: `REQ-\d{3}`（例: `REQ-001`, `REQ-201`）
- インターフェイス ID: `IF-\d{3}`（例: `IF-010`, `IF-200`）
- データ契約 ID: `DATA-\d{3}`（例: `DATA-010`, `DATA-101`）
- テスト ID: `TEST-\d{3}`（例: `TEST-001`, `TEST-201`）
- 開発タスク ID: `TASK-IF-\d{3}-\d{2}`（例: `TASK-IF-001-01`, `TASK-IF-100-03`）

**MUST**:

- 各 ID（REQ / IF / DATA / TEST / TASK）は **ちょうど 1 つのドキュメント** で「定義」される。

  - TASK-xxx の定義元は通常 `docs/dev_tasks/IF-xxx*_tasks.md`。
- 定義ブロックは Markdown 上で、次の形式の見出しを持つことが望ましい。

```markdown
## REQ-101: 辞書ビルド成果物をエクスポートできる
```

（REQ-101 の詳細が続く）

同様に：

```markdown
## IF-100: Export digits bins

## DATA-101: by_digits.bin — digits→ENT index

## TEST-201: レイテンシ測定（p95 ≤ 400ms）

## TASK-IF-100-01: CLI スケルトンの作成
```

**SHOULD NOT**:

- 定義ブロックおよび Traceability Map 内で、ID の“省略表記”（レンジ・ショートハンド）を使用してはならない。

  - 例：`REQ-101..104`, `REQ-101~104`, `REQ-101,102` など。
- これらの記法は、トレーサビリティチェックの対象外であるドキュメント（`architecture/` 等の `trace_role="ref"` であるドキュメント）内の説明目的に限り許可される。

※ 省略表記は lint ルールで検出し、`trace_role="source"` であるドキュメントおよび `traceability_map.md` 内ではエラーとして扱う。

## 4. Traceability Map のルール

### 4.1 役割

`requirements/traceability_map.md` は、
**REQ ↔ IF / DATA / TEST の公式な対応関係（トレーサビリティ）の SSOT**として機能する。

典型的な行は次の形式をとる。

```markdown
| REQ    | 説明                           | IF                        | DATA                           | TEST                  |
|--------|--------------------------------|---------------------------|--------------------------------|-----------------------|
| REQ-101| 辞書ビルド成果物をエクスポート | IF-100_digits_bins_spec   | DATA-101_by_digits_bin         | TEST-101, TEST-102    |
| REQ-002| ...                            | IF-200_query_engine_spec  | DATA-020_SURF_DIGITS, DATA-014 | TEST-201              |
```

**この 1 行が意味すること**:

- 当該 REQ-xxx は、

  - 記載された IF-xxx によって**実現され**、
  - 記載された DATA-xxx に**依存し**、
  - 記載された TEST-xxx によって**検証される**。

これを本ドキュメントでは

「REQ-xxx が IF/DATA/TEST にトレースされている」

と呼ぶ。

### 4.2 trace コマンドが行うチェック

`iori-spec trace` は、次の情報を用いて整合性をチェックする。

1. `trace_role="source"` のドキュメントから抽出した

   - 定義済み `REQ-xxx` / `IF-xxx` / `DATA-xxx` / `TEST-xxx` の集合
2. `traceability_map.md` の各行に出現する

   - `REQ` / `IF` / `DATA` / `TEST` の集合

**MUST**（基本ルール）:

- **未トレースの REQ があってはならない**。

  - `requirements/*` で定義されている REQ-xxx が、

    - `traceability_map.md` のどの行にも現れない場合、警告またはエラーとする。
- **Trace 行に載っている ID は、必ずどこかで定義されていなければならない**。

  - Traceability Map に記載されている IF-xxx / DATA-xxx / TEST-xxx が、

    - どの `interfaces/` / `data_contracts/` / `tests/` にも定義がない場合、エラーとする。

**SHOULD**（推奨ルール）:

- どの REQ にも紐付いていない IF / DATA / TEST の存在は、
  「孤立仕様」として警告する（ただしツール側オプションで無効化可能とする）。

**NOTE**:

- `architecture/` や `reference/`、`dev_tasks/` など `trace_role="ref"` のドキュメント内で ID が出現しても、
  それは「単なる言及」であり、トレーサビリティの欠如として扱わない。
- TASK-xxx は Traceability Map の対象外であり、未トレースでもエラーとはならない。

## 5. DATA と IF の依存関係（Data–Process Graph）

### 5.1 front matter での記述

DATA と IF の**ビルド依存関係**は、
**データノード（DATA）と処理ノード（IF）からなる有向二部グラフ**としてモデリングする。

各 `data_contracts/*.md` / `interfaces/*.md` の front matter に
以下のような情報を（必要に応じて）記述する。

**DATA 側の例**:

```yaml
---
kind: data_contract
id: DATA-101
spec_title: "by_digits.bin — digits→ENT index"
produced_by:
  - IF-100               # この DATA を生成する IF
inputs:
  - DATA-020             # SURF_DIGITS
  - DATA-014             # M_SURF_ENT
  - DATA-105             # entry_meta.bin
---
```

**IF 側の例**:

```yaml
---
kind: interfaces
id: IF-100
spec_title: "Export digits bins"
produces:
  - DATA-101
consumes:
  - DATA-020
  - DATA-014
  - DATA-105
---
```

**MUST**:

- いずれか一方、または両方の側から、

  - 「どの DATA を読み、どの DATA を生成するか」が判別できる必要がある。
- `iori-spec` は `produced_by / produces / inputs / consumes` などのキーから
  IF⇄DATA 関係を統合し、整合性チェックを行う。

### 5.2 Data–Process Graph としての定義

上記情報から、`iori-spec` は Data–Process Graph (G_DP) を構築する。

- ノード集合

  - D: すべての DATA-xxx
  - P: すべての IF-xxx
- 辺集合

  - D → P: IF がその DATA を**読む**（consumes / inputs）
  - P → D: IF がその DATA を**生成する**（produces / produced_by）

これはグラフ理論的には、次のように表現できる。

- (G_\text{DP} = (V, E))
- ただし (V = D \cup P)、
- (D \cap P = \emptyset)、
- 辺 (E \subseteq (D \times P) \cup (P \times D)) の有向二部グラフ。

**派生ビュー**として、「DATA 同士の依存だけ」を見たい場合、
すべてのパス (DATA_i \to IF_k \to DATA_j) をたどることで
**DATA→DATA 辺**を導出してもよい。これはあくまでビューであり、SSoT は IF⇄DATA の関係にある。

### 5.3 静的チェックの例

`iori-spec` は (G_\text{DP}) を用いて次のようなチェックを行える。

- 存在チェック

  - `inputs` / `consumes` / `produces` / `produced_by` で参照されている全 ID が
    実際に定義されているか。
- 循環チェック

  - (G_\text{DP}) または DATA-only 派生グラフが、有向閉路を含まないか（DAG か）。
- 未使用 DATA / IF

  - 定義されているが、どの辺にも出現しない DATA-xxx / IF-xxx を警告する。

## 6. 要求トレースグラフ（G_trace）

Traceability Map と `trace_role="source"` の定義から、
`iori-spec` は要求トレースグラフ (G_\text{trace}) を構築できる。

- ノード集合：

  - (V_\text{REQ}): すべての REQ-xxx
  - (V_\text{IF}): すべての IF-xxx
  - (V_\text{DATA}): すべての DATA-xxx
  - (V_\text{TEST}): すべての TEST-xxx
- 辺集合：

  - Traceability Map の各行について

    - (REQ \to IF)
    - (REQ \to DATA)
    - (REQ \to TEST)
      を追加したもの（多重辺を許容）。

**使い道**（一例）:

- ある REQ-xxx の仕様を変更した際に、

  - どの IF / DATA / TEST が「意味的に影響を受けうるか」を列挙し、
  - それらの定義ブロックだけを LLM に渡してレビューを頼む。
- IF / DATA / TEST 観点から、

  - 「この仕様はどの REQ に紐付いているか？」
    を逆引きする。

※ TASK-xxx は (G_\text{trace}) の対象外であり、
開発フロー上の補助情報として別レイヤー（dev_tasks）に保持する。

## 7. ドキュメント依存グラフ（G_doc）

ID グラフから、doc 単位の依存グラフ (G_\text{doc}) を定義する。

- ノード集合：

  - すべてのドキュメント（`doc_id` = パス or 論理名）
- 辺集合：

  - ドキュメント A 内の ID のうち、
    その ID の「定義元ドキュメント」が B であれば、
    A → B の辺を張る。

**例**:

- `interfaces/digits/IF-100_digits_bins_spec.md` 内で `DATA-101` を参照している

  - → `interfaces/digits/IF-100...` → `data_contracts/by_digits_bin` という辺

**使い道**:

- 「どの仕様ファイルから実装を開始すべきか？」の判断材料として、

  - 多くのドキュメントから依存されている doc を「基盤」とみなし、
  - そこから実装・修正を開始する戦略を組み立てる。
- 変更時に、

  - ある doc を起点として上流・下流にどの doc がぶら下がっているかを
    機械的に抽出し、LLM に渡すコンテキストを絞り込む。

TASK-xxx を含む `dev_tasks/` も、ここでは通常の doc として扱われ、
IF や REQ との依存関係（「このタスクはどの IF/REQ に紐づくか」）を可視化できる。

## 8. LLM / ツール連携における利用想定

本ドキュメントで定義した構造とトレースルールは、
次のような LLM 活用フローを想定している。

1. `iori-spec index`
   仕様セット全体から ID・doc 情報を収集し、
   `G_trace`, `G_DP`, `G_doc` 構築の基礎データを作る。
   TASK-xxx も含めて ID をインデックスする。

2. `iori-spec trace`
   REQ↔IF/DATA/TEST の対応関係の欠落・不整合を機械的に検出。

3. `iori-spec impact <ID>`
   REQ/IF/DATA/TEST いずれかの ID を起点に、
   `G_trace` / `G_DP` / `G_doc` 上で上下流ノードをたどり、

   - 「影響を受けうる ID 群」
   - 「関連する doc 群」

   を JSON 等で出力する。
   将来的には、TASK-xxx を seed とした impact も検討する。

4. `iori-spec context <ID...>`
   指定された ID 群が定義されている doc の
   該当行周辺だけを抽出し、LLM にそのまま渡せるテキストを生成する。

5. LLM 側タスク例

   - 「DATA-014 の仕様を A→B に変更したい。
     `impact` と `context` の結果を踏まえて、矛盾しそうな点・書き換えが必要そうな箇所を列挙してほしい。」
   - 「この REQ-101 を満たすために、どの IF / DATA / TEST から実装・修正を始めるのがよさそうか？」
   - 「IF-100 の実装を進めたい。対応する TASK-IF-100-* を順番にこなす計画を立ててほしい。」

このように、
**依存グラフ構築と影響範囲の絞り込みをスクリプト側で行い、
意味的な整合性チェックと実装戦略の検討を LLM に任せる**
という役割分担を前提としている。

## 9. 今後の拡張の余地

- 省略表記の正式サポート

  - 例：`REQ-101..104` を「REQ-101〜REQ-104 のレンジ」として展開する
    専用の記法とパーサを、lint / trace と連動させる。
- `trace_role` のユーザー定義上書き

  - 特定の doc だけ `source` / `ref` を切り替えたい場合の設定方法。
- ID 以外のラベル（タグ）の導入

  - コンポーネント単位・サブシステム単位のラベルを導入し、
    `impact` や `context` の絞り込み軸にする。
- TASK グラフの導入

  - TASK-IF-xxx-* 同士の依存関係や、REQ/IF/DATA/TEST との紐付けを
    別グラフとして表現し、タスク計画・自動生成に活かす。

本ドキュメントは、
`iori-spec` の実装および仕様書テンプレートの改善に合わせて更新されることを想定する。

---



