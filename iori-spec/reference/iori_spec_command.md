---
kind: reference
scope: iori-spec
spec_title: "iori-spec Commands Reference"
status: draft
---
# iori-spec CLI コマンドリファレンス

## このドキュメントについて

`iori-spec` は、仕様書群（REQ / IF / DATA / TEST / TASK など）を LLM と人間が扱いやすい「小さな単位」に分解しつつ、
全体構造（依存関係・トレーサビリティ）の健全性をツール側で支えるための CLI です。

このドキュメントは、CLI 利用者（人間・LLM）向けに、

* 何ができるコマンドなのか
* どのコマンドをどう組み合わせて使うのか
* オプション・終了ステータスの意味

をまとめたリファレンスです。

## 基本概念

### ID と kind

`iori-spec` が扱う仕様は、基本的に「1 ファイル 1 ID」です。

- 代表的な ID プレフィックス

  - `REQ-xxx`：requirements
  - `IF-xxx`：interfaces
  - `DATA-xxx`：data_contracts
  - `TEST-xxx`：tests
  - `TASK-xxx` / `TASK-IF-xxx-yy`：dev_tasks など

- 各ファイルの front matter には少なくとも以下が入ります

  * `id`, `kind`, `scope`, `status`, `spec_title` など

CLI は主にこの front matter と、`trace.*` / `dp.*` フィールドを読み取って動きます。

### 「トレース」と「依存」の違い

`iori-spec` では、仕様同士の関係をざっくり次の 2 つに分けて扱います。

* **トレース（trace）**

  * 「どの REQ をどの IF / DATA / TEST がカバーしているか」といった、
    要求と設計・テストの**論理的なつながり**を表します。
  * front matter の `trace.req`, `trace.if`, `trace.data`, `trace.test`, `trace.task` などで表現します。
  * 例:

    * `IF-200` の `trace.req: ["REQ-201"]`
      → 「IF-200 は REQ-201 を満たすためのインターフェイス」

* **依存（dependency / dp）**

  * 「どの DATA を入力にして、どの DATA を出力するか」というような、
    **データフロー・実装上の依存関係**を表します。
  * front matter の `dp.produces`, `dp.consumes` などで表現します。
  * 例:

    * `IF-200` の `dp.produces: ["DATA-101"]`
      → 「IF-200 の結果として DATA-101 が生成される」

CLI の `impact` / `context` / `trace lint` は、主にこの「トレース」をたどって
影響範囲やカバレッジを評価します。依存関係（dp）は将来的な拡張要素として扱われます。

### ツールと LLM の役割分担（ざっくり）

* ツール（iori-spec CLI）

  * 構造や依存関係の把握・列挙・圧縮（どの ID がどこにつながるか）を機械的に行う。

* LLM / 人間

  * ツールが返した「候補 ID 群」「局所コンテキスト」を読んだうえで、

    * どこをどう修正するか
    * どの案がよりよいか
      といった**意味的な判断**を行う。

必要に応じて、LLM はコンテキスト外の情報（既存コードや外部ドキュメントなど）も自ら参照して構いません。

---

## 共通オプション

すべてのコマンドは、以下の共通オプションを受け付けます。

* `--root <PATH>`（任意）

  * 仕様書ルートディレクトリ。
  * 省略時はカレントディレクトリ `.` をルートとして扱います。

* `--index <PATH>`（任意）

  * 既に生成済みのインデックスファイル（JSON）のパス。
  * 指定されている場合、可能な限りこのファイルを再利用します。
  * 指定されていない場合、各コマンドは内部的に `iori-spec index` 相当の処理を行うか、
    `index` の実行を要求します（MVP では内部生成も許容）。

* `--format <FORMAT>`（任意）

  * 標準出力のフォーマット。
  * デフォルトはコマンドごとに異なります（例: `search` / `impact` は `json`、`context` は `markdown`）。

* `--verbose`（任意）

  * 追加のログ・デバッグ情報を標準エラー出力に表示します。

---

## 終了ステータス（MUST コマンド共通）

MUST 指定されているコマンドは、終了コードを次のように使います。

* `0`：正常終了

  * `lint` 系では「エラー 0 件」の場合。
* `1`：仕様上のエラー

  * 例:

    * `lint` でルール違反を検出
    * `trace lint` でトレーサビリティ破綻を検出
* `2`：実行時エラー

  * 例:

    * 引数不正
    * I/O エラー
    * index ファイルの破損
    * front matter のパース不能 など

CI で利用する際は、`1` を「仕様エラーとして落とす」運用が基本になります。

---

## コマンド一覧（概要）

優先度ラベルの意味は次の通りです。

* 🔵 **MUST**： iori-spec を「LLM にとって扱いやすい SDD」にするうえで中核となるコマンド
* 🟢 **SHOULD**： 早期に用意すると運用の質が大きく上がるコマンド
* 🟡 **NICE TO HAVE**： 余力があれば追加したい補助コマンド

| カテゴリ   | コマンド               | 優先度           | 役割の概要                                     |
| ------ | ------------------ | ------------- | ----------------------------------------- |
| 探索     | `search`           | 🔵 MUST       | 自然文から関連しそうな ID を検索                        |
| 探索     | `show`             | 🟢 SHOULD     | 指定 ID の spec 本文を表示                        |
| インデックス | `index`            | 🔵 MUST       | 仕様セット全体のインデックスを構築                         |
| グラフ    | `graph export`     | 🟡 NICE       | トレースグラフなどを DOT / JSON で出力                 |
| グラフ    | `graph neighbors`  | 🟡 NICE       | 指定 ID 周辺のノードを一覧                           |
| 影響範囲   | `impact`           | 🔵 MUST       | 指定 ID の変更が及ぶ影響範囲を列挙                       |
| コンテキスト | `context`          | 🔵 MUST       | LLM に渡す局所コンテキストパックを生成                     |
| 品質     | `lint`             | 🔵 MUST       | 仕様ファイルの構造・front matter・ID を検証             |
| 品質     | `trace lint`       | 🔵 MUST       | トレーサビリティの coverage / 整合性を検証               |
| 品質     | `trace report`     | 🟢 SHOULD     | Traceability Map レポートを生成                  |
| 生成     | `new` / `scaffold` | 🟢 SHOULD（強め） | 新しい REQ / IF / DATA / TEST / TASK のテンプレ生成 |
| タスク    | `tasks list`       | 🟡 NICE       | ID を起点に関連 TASK を一覧                        |
| タスク    | `report tasks`     | 🟡 NICE       | TASK 中心のレポートビューを生成                        |

以下では、実際の使い方をイメージしやすいよう、コマンドごとに概要と主なオプション・典型的なユースケースを示します。

---

## 1. 探索系コマンド

### 1.1 `iori-spec search`（🔵 MUST）

**目的**
自然文やキーワードから、仕様セット内の関連しそうな ID を検索し、
「どの ID から読み始めるか？」を決めるための候補リストを返します。

**シノプシス**

```bash
iori-spec search <QUERY> \
  [--kinds <KIND_LIST>] \
  [--limit <N>] \
  [--format json|table|markdown] \
  [--root <PATH>] \
  [--index <PATH>]
```

**主なオプション**

* `<QUERY>`（必須）

  * 自然文またはキーワード列。日本語・英語混在可。
* `--kinds <KIND_LIST>`

  * 対象とする `kind` をカンマ区切りで制限。
  * 例: `requirements,interfaces,data_contracts,tests,dev_tasks`
* `--limit <N>`

  * 返す候補数の上限（デフォルト 20）。
* `--format`

  * デフォルト `json`。
    CLI からざっと見るなら `table` や `markdown` も便利です。

**出力イメージ（`--format json`）**

```json
[
  {
    "id": "REQ-201",
    "kind": "requirements",
    "file": "requirements/REQ-201_digits_segmentation.md",
    "score": 0.92,
    "spec_title": "digits を最適なセグメント列に分割する",
    "snippet": "digits を最適なセグメント列に分割し..."
  }
]
```

**代表的な使い方**

* LLM が「数字列分割アルゴリズムに関する仕様を探したい」とき

  ```bash
  iori-spec search "digits segmentation" --kinds requirements,interfaces
  ```

---

### 1.2 `iori-spec show`（🟢 SHOULD）

**目的**
指定した ID の spec 本体（front matter＋主要セクション）だけを表示し、
「まずこの ID の全体像を読みたい」というニーズに応えます。

**シノプシス**

```bash
iori-spec show <ID> \
  [--format markdown|json] \
  [--root <PATH>] \
  [--index <PATH>]
```

**使いどころ**

* `search` で候補を絞ったあと、

  * 「この ID として本当に妥当か？」
  * 「どんな前提で書かれた仕様か？」
* を確認するために 1 ファイル分だけ読むとき。

---

## 2. インデックス・グラフ系コマンド

### 2.1 `iori-spec index`（🔵 MUST）

**目的**
仕様ディレクトリを走査し、ID / kind / scope / status / trace / dp などを集約した
**仕様カタログ（インデックス）**を構築します。

**シノプシス**

```bash
iori-spec index \
  [--root <PATH>] \
  [--out <PATH>] \
  [--format json]
```

**ポイント**

* 生成物は JSON（例: `artifacts/spec_index.json`）。
* 他のコマンドは原則この index を入力として利用します。
* ID 重複や front matter 不備はエラーとして検出されます。

典型的には、リポジトリ更新後に

```bash
iori-spec index --root docs --out artifacts/spec_index.json
```

を叩き、以降のコマンドで `--index artifacts/spec_index.json` を使う運用を想定しています。

---

### 2.2 `iori-spec graph export`（🟡 NICE TO HAVE）

**目的**
内部グラフ（トレース / dp / doc / task）を DOT / JSON でエクスポートし、
外部ツールで可視化・デバッグできるようにします。

**シノプシス**

```bash
iori-spec graph export <GRAPH_KIND> \
  [--index <PATH>] \
  [--root <PATH>] \
  [--out <PATH>] \
  [--format dot|json]
```

**主なユースケース**

* Graphviz 等でトレース構造を俯瞰したいとき
* グラフ構築ロジックのデバッグ

---

### 2.3 `iori-spec graph neighbors`（🟡 NICE TO HAVE）

**目的**
指定 ID の近傍ノードを CLI から一覧し、
「この ID はどの ID とどの程度つながっているか？」を素早く把握します。

---

## 3. 影響範囲 / コンテキスト系コマンド

### 3.1 `iori-spec impact`（🔵 MUST）

**目的**
指定 ID を add / change / delete したときに影響を受けうる ID を列挙し、
「どこまで一緒に検討すべきか？」を決めるための材料を提供します。

**シノプシス**

```bash
iori-spec impact <ID> \
  [--max-depth <N>] \
  [--include-kinds <KIND_LIST>] \
  [--format json|table|markdown] \
  [--index <PATH>] \
  [--root <PATH>]
```

**典型的な使い方**

```bash
# IF-200 を変更したとき、2 ホップ先までどの spec に波及しうるか？
iori-spec impact IF-200 --max-depth 2 --include-kinds requirements,interfaces,data_contracts,tests
```

`impact` の結果を見て、

* どの REQ / IF / DATA / TEST を一緒に読み直すべきか
* どの TASK を追加・更新すべきか

を判断していく、というのが基本的なフローです。

---

### 3.2 `iori-spec context`（🔵 MUST）

**目的**
指定 ID（＋その近傍）の spec のうち、LLM に必要な部分だけを抜き出して
**「局所コンテキストパック」**を生成します。

**シノプシス**

```bash
iori-spec context <ID> \
  [--radius <N>] \
  [--include-kinds <KIND_LIST>] \
  [--format markdown|json] \
  [--out <PATH>] \
  [--index <PATH>] \
  [--root <PATH>]
```

**イメージ**

```bash
# REQ-201 と、その 1 ホップ近傍（IF / DATA / TEST）をコンテキスト化
iori-spec context REQ-201 \
  --radius 1 \
  --include-kinds requirements,interfaces,data_contracts,tests \
  --format markdown \
  --out ctx/REQ-201.md
```

生成された Markdown は、そのまま LLM に貼り付けて

* 仕様のレビュー
* 差分設計
* 実装タスク分解

などに利用することを想定しています。

---

## 4. 品質維持系コマンド

### 4.1 `iori-spec lint`（🔵 MUST）

**目的**
各 spec ファイルの構造・front matter・ID 形式が
`spec_section_schema` / `iori_spec_guide` のルールに従っているかをチェックし、
「LLM に渡す前提となる仕様の型」を保ちます。

**シノプシス**

```bash
iori-spec lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--rules <RULE_LIST>] \
  [--format text|json]
```

**主なチェック**

* front matter ルール

  * `id`, `kind`, `status` 等の有無・形式
* ids ルール

  * ID 重複の有無
* sections ルール

  * kind ごとの必須セクション有無（`spec_section_schema` に基づく）

CI などで定期的に叩き、status が `review` / `stable` の spec の型崩れを防ぎます。

---

### 4.2 `iori-spec trace lint`（🔵 MUST）

**目的**
REQ ↔ IF / DATA / TEST のトレーサビリティが破綻していないかをチェックし、
要求トレーサビリティ coverage の最低限の保証を行います。

**シノプシス**

```bash
iori-spec trace lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--format text|json]
```

**代表的なルールイメージ**

* unknown_target_id：trace で参照している ID が存在しない → ERROR
* req_has_no_impl：REQ に対し IF / DATA / TEST が 1 つも紐づかない
* if_not_linked_from_any_req：REQ に紐づかない IF
* isolated_node_in_trace_graph：トレースグラフから孤立しているノード など

`status` によって WARN / ERROR のレベルを変えることで、
draft 期の柔軟性と、stable 期の厳しさを両立させる設計になっています。

---

### 4.3 `iori-spec trace report`（🟢 SHOULD）

**目的**
front matter の `trace.*` 情報から Traceability Map を Markdown で生成し、
人間がトレーサビリティを俯瞰できるビューを提供します。

レビュー会などで「どの REQ がどの IF / TEST でカバーされているか」を
一枚のレポートで確認したいときに便利です。

---

## 5. 仕様生成系コマンド

### 5.1 `iori-spec new` / `iori-spec scaffold`（🟢 SHOULD・強め）

**目的**
新しい REQ / IF / DATA / TEST / TASK のための spec ファイルテンプレートを生成し、
「型の揃った仕様書」を簡単に増やせるようにします。

**シノプシス**

```bash
iori-spec new <KIND> \
  --id <ID> \
  --spec_title "<TITLE>" \
  [--scope <SCOPE>] \
  [--status <STATUS>] \
  [--root <PATH>] \
  [--out <PATH>]
```

**例**

```bash
# 新しい REQ を追加
iori-spec new req \
  --id REQ-310 \
  --spec_title "digits segmentation のデフォルト戦略を差し替える" \
  --scope client.query_engine
```

生成されたファイルには

* front matter（id / kind / scope / status / trace / dp の初期値）
* `spec_section_schema` に基づく必須セクション

が入っており、LLM は「テンプレを埋める」ことに専念できます。

---

## 6. タスク系コマンド

### 6.1 `iori-spec tasks list`（🟡 NICE TO HAVE）

**目的**
IF / REQ / DATA / TEST などを起点に、関連する TASK ID を一覧し、
「この spec にぶら下がっている作業」を確認します。

### 6.2 `iori-spec report tasks`（🟡 NICE TO HAVE）

**目的**
TASK を中心にしたレポートビュー（例: IF ごとのタスクリスト）を生成し、
実装計画や進捗確認を支援します。

---

## 7. 典型ワークフロー例

### 7.1 既存仕様を変更する場合

1. `search` でテーマに関連する ID を探す

   ```bash
   iori-spec search "digits segmentation" --kinds requirements,interfaces
   ```
2. 候補から中心となる ID を選び、`show` で中身を確認
3. `impact` で影響範囲を確認

   ```bash
   iori-spec impact IF-200 --max-depth 2 --include-kinds requirements,interfaces,data_contracts,tests
   ```
4. `context` で局所コンテキストを生成し、LLM に渡して設計・文言を検討
5. 修正後に `lint` / `trace lint` を実行し、構造的な破綻がないか確認

### 7.2 新しい仕様を追加する場合

1. `new` でテンプレを生成
2. LLM にテンプレを埋めさせる（コンテキストとして関連 REQ / IF を渡す）
3. `lint` / `trace lint` を通し、ID・トレースの整合を確認
4. 必要なら `tasks list` で実装タスクを洗い出す
