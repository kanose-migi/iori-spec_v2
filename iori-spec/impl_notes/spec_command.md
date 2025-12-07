---
kind: impl_notes
scope: iori-spec
spec_title: "iori-spec Commands & TODOs"
status: draft
---
# iori-spec コマンド案

## このコマンド体系の設計意図

### 1. iori-spec の設計思想：軸①「局所コンテキスト化」と軸②「構造健全性」

iori-spec は、巨大な仕様セットを前提にしつつも、**LLM からは常に「小さな仕様」だけを読めば済む状態（軸①）**をつくることを狙っています。
同時に、依存関係・責務・トレースを明示的に表現し、**関心の分離や高凝集・疎結合といった設計上の良さ（軸②）**をツール側で支えることも重要な目的です。
このコマンド体系は、「局所コンテキスト化」と「構造健全性」の両方を実現するために、ID・グラフ・テンプレ生成を一貫したインターフェイスとして提供することを意図しています。

### 2. 仕様集合自身が「操作に対する影響範囲」を把握するためのインターフェイス設計

仕様集合を「ノード（ID）とエッジ（依存・トレース）」のグラフとして扱い、
**add / change / delete といった操作に対して、どの ID 群が影響を受けるかを自分で答えられる**ことをゴールにしています。
`index` で SSOT を構築し、`impact` や `context` で「この ID を変えたいときに、どこまでを一緒に見るべきか」を機械的に返せるようにすることで、
「仕様そのものが、自分自身の影響範囲を教えてくれる」インターフェイスを形にします。

### 3. LLM とツールの役割分担：構造はツール、意味判断は LLM

このコマンド体系では、**構造や依存関係の把握・列挙・圧縮はツールの責務**とし、
**その上で何をどう変更するか・どの案がよりよいかの判断は LLM（と人間）が担う**という役割分担を前提にしています。
たとえば、どの ID を読めばよいかを決めるのは `search / impact / context` などのコマンドであり、
そのコンテキストを受けて仕様文を設計・推敲するのが LLM の仕事、という分離がコマンド設計に反映されています。

### 4. コマンド群の役割分類とユースケース（探索 / 影響範囲 / コンテキスト / 品質維持 /生成）

コマンド群は、LLM が仕様と対話するときの典型フローに沿って、役割ごとに整理されています。
まず `search` で関係しそうな ID を「探索」し、`impact` で変更の「影響範囲」を把握し、`context` / `show` で必要最小限の「局所コンテキスト」を取得します。
`lint` / `trace lint` は仕様セット全体の「品質維持」を担い、`new` / scaffold 系コマンドは新しい REQ / IF / DATA / TEST / TASK を「生成」するときに、型のそろった高品質な仕様を書き出すための入り口になります。
このように、それぞれのコマンドは「どの段階のユースケースを支えるか」が明確になるように配置されています。

いい感じの流れになってきたので、そのまま続けて貼れる形でコマンド一覧を書きます。
MUST / SHOULD / NICE TO HAVE の意味も最初に一行だけ定義しておきます。

## コマンド一覧

> **優先度ラベルの意味**
>
> - 🔵 **MUST**: iori-spec を「LLM にとって扱いやすい SDD」にするうえで中核となるコマンド。
> - 🟢 **SHOULD**: 早い段階で用意すると運用の質が大きく上がるコマンド。
> - 🟡 **NICE TO HAVE**: コア機能が揃ったあとに、余力があれば追加したいコマンド。

### 1. 探索系コマンド（どの ID を起点にするかを決める）

#### `iori-spec search` — 🔵 **MUST**

- 役割: 自然文やキーワードから、関係しそうな ID（REQ / IF / DATA / TEST / TASK）候補を検索する。

- ねらい: 「どの ID を seed にすればよいか？」という最初の一歩を、LLM が自力で決められるようにする。
- 典型的な使い方:

  - 「数字列の分割アルゴリズムに関係する spec を探したい」
  - → `iori-spec search "digits segmentation" --kinds requirements,interfaces`

#### `iori-spec show` — 🟢 **SHOULD**

- 役割: 指定した ID の spec 本体（front matter＋主要セクション）だけをきれいに表示する。
- ねらい: seed 候補を 1 つに絞ったあとに、「まずその spec を一通り読む」ための入口を用意する。
- 備考: 実装としては `context <ID> --radius 0` の薄いラッパでもよい。

### 2. インデックス・グラフ構築系コマンド（SSOT の土台）

#### `iori-spec index` — 🔵 **MUST**

- 役割: 仕様ディレクトリを走査し、各ファイルの front matter / ID / kind / scope / trace / dp などを集約したインデックス（JSON 等）を構築する。
  - doc.* は今は index には載せない（context 時に必要なら別途ファイルを読む）
  - impl_notes のように id が無いファイルは、nodes には含めない（= グラフ外のメモ扱い）
- ねらい: すべてのコマンドが共有する「ID カタログ」と「グラフ構築の材料」として機能させる。
- 備考: 他のコマンドは `--index` でこの成果物を参照し、指定がなければ内部で `index` 相当を実行する想定。

#### `iori-spec graph export` — 🟡 **NICE TO HAVE**

- 役割: G_trace / G_dp / G_doc / G_task など内部グラフを DOT 等でエクスポートする。
- ねらい: 実装デバッグや可視化ツール連携のために、グラフ構造をそのまま外部に出せるようにする。
- 備考:
  - コア運用には必須ではないため、後回しにしてもよい。
  - G_task は TASK 系エッジだけ抜いたビュー（G_trace の部分グラフ）

#### `iori-spec graph neighbors` — 🟡 **NICE TO HAVE**

- 役割: 指定 ID の近傍ノード（depth N まで）を一覧するデバッグ用コマンド。
- ねらい: 「グラフがどう張られているか」を CLI から素早く検証する用途を想定。

### 3. 影響範囲 / コンテキスト系コマンド（軸①の本丸）

#### `iori-spec impact` — 🔵 **MUST**

- 役割: 指定した ID を add/change/delete したときに、影響を受けうる ID 一覧を列挙する。
- ねらい: 「この IF を変えるとどこに波及するか？」を、LLM に判断させる前の素材として機械的に提示する。
- 典型例:

  - `iori-spec impact IF-200 --max-depth 2 --include-roles req,data,test,task`

#### `iori-spec context` — 🔵 **MUST**

- 役割: 指定した ID（＋任意の近傍）について、LLM に渡すのに十分な「局所コンテキストパック」を生成する。
- ねらい: 巨大仕様の中から、そのタスクに本当に必要な spec の断片だけを抜き出し、LLM に貼れる形にする。
- 典型例:

  - `iori-spec context REQ-201 --radius 1 --include-roles if,data,test --out ctx/REQ-201.md`
  - `iori-spec context TASK-IF-001-01 --radius 1 --include-roles if,req,data,test`

### 4. 品質維持系コマンド（構造健全性・トレース健全性）

#### `iori-spec lint` — 🔵 **MUST**

- 役割: 各 spec ファイルの構造・front matter・ID 形式が `spec_section_schema` / `iori_spec_guide` のルールに従っているかをチェックする。
- ねらい: 「LLM に渡す前提となる仕様の型」が崩れていないことを保証し、局所コンテキスト生成の前提を守る。
- チェック例:

  - kind ごとの必須セクションの有無
  - front matter に必須キー（id / kind / scope / spec_title / status）が揃っているか
  - ID 形式（REQ-xxx / IF-xxx …）が正しいか、など。

#### `iori-spec trace lint` — 🔵 **MUST**

- 役割: REQ ↔ IF / DATA / TEST のトレーサビリティ（G_trace）が破綻していないかをチェックする。
- ねらい: 「この REQ に対する IF / TEST が存在するか？」といった要求トレーサビリティのカバレッジを機械的に確認する。
- 備考: TASK は coverage 評価対象からは外し、Graph には参加させるが lint の必須条件にはしない。

#### `iori-spec trace report` / `iori-spec report trace` — 🟢 **SHOULD**

- 役割: front matter の情報から Traceability Map（REQ 起点 / IF 起点など）の Markdown レポートを生成する。
- ねらい: 人間が仕様全体のトレーサビリティを俯瞰するためのビューを、手書きではなく自動生成物として提供する。
- 備考: LLM に直接読ませるよりも、設計レビューやメンテナンスにおける「地図」としての役割を重視。

### 5. 仕様生成系コマンド（新しい ID を「型付き」で増やす）

#### `iori-spec new` / `iori-spec scaffold` — 🟢 **SHOULD（強め）**

- 役割: 新しい REQ / IF / DATA / TEST / TASK のための spec ファイルスケルトンを生成する。
- ねらい: 仕様の粒度とセクション構造を揃え、高品質な仕様書を量産しやすくする。LLM は「テンプレを埋める」ことに集中できる。
- 典型例:

  - `iori-spec new req --id REQ-310 --spec_title "digits segmentation のデフォルト戦略を差し替える"`
  - `iori-spec new if --id IF-200 --spec_title "Query Engine: digits → segments"`

### 6. タスク系コマンド（運用寄り／Graph を活かす補助）

#### `iori-spec tasks list` — 🟡 **NICE TO HAVE**

- 役割: REQ / IF / DATA / TEST などを起点に、関連する TASK ID の一覧を取得する。
- ねらい: 「この IF にぶら下がっている作業タスク」「この REQ に関連する未完了タスク」を素早く確認する。
- 備考: `impact` / `context` でも代替可能なため、優先度はやや低め。

#### `iori-spec report tasks` — 🟡 **NICE TO HAVE**

- 役割: IF ごとのタスクリストなど、TASK を中心としたレポートビューを生成する。
- ねらい: 実装計画や進捗確認など、運用寄りのダッシュボードとして利用する。

いいね、じゃあこのまま「仕様書としてそのまま貼れるレベル」で書いていきます。
先に共通仕様 → そのあとコマンドごと、という構成にします。

## 共通仕様

### 共通オプション

すべてのコマンドは、以下の共通オプションを受け付けるものとする。

- `--root <PATH>`（任意）

  - 仕様書ルートディレクトリ。
  - 省略時はカレントディレクトリ `.` をルートとして扱う。
- `--index <PATH>`（任意）

  - 既に生成済みのインデックスファイル（JSON）のパス。
  - 指定されている場合、可能な限りこのファイルを再利用する。
  - 指定されていない場合、コマンドは内部的に `iori-spec index` 相当の処理を行うか、`index` の実行を要求する。
- `--format <FORMAT>`（任意）

  - 標準出力のフォーマット。
  - デフォルトはコマンドごとに定義する（search/impact などは `json`、report/context などは `markdown` を想定）。
- `--verbose`（任意）

  - 追加のログ・デバッグ情報を標準エラー出力に表示する。

### インデックスファイル（概略）

`iori-spec index` が生成するインデックスファイルは、概ね次の情報を含む JSON とする（MVP の想定）。

```json
{
  "version": "0.1",
  "generated_at": "2025-12-02T12:34:56Z",
  "root": "./docs",
  "nodes": [
    {
      "id": "IF-200",
      "kind": "interfaces",
      "file": "interfaces/IF-200_query_engine.md",
      "scope": "client.query_engine",
      "status": "draft",
      "spec_title": "Query Engine: digits → segments",
      "trace": {
        "req":   ["REQ-201"],
        "if":    [],
        "data":  ["DATA-101"],
        "test":  ["TEST-201"],
        "task":  []
      },
      "dp": {
        "produces": ["DATA-101"],
        "consumes": ["DATA-201"]
      }
      // sections などの詳細情報は将来拡張とする
    }
  ]
}
```

## 1. 探索系コマンド

### 1.1 `iori-spec search` — MUST

#### 目的

自然文やキーワードから、仕様セット内の関連しそうな ID（REQ / IF / DATA / TEST / TASK）を検索し、
**「どの ID を seed にすべきか？」を決めるための候補リストを返す**。

#### シノプシス

```bash
iori-spec search <QUERY> \
  [--kinds <KIND_LIST>] \
  [--limit <N>] \
  [--format json|table|markdown] \
  [--root <PATH>] \
  [--index <PATH>]
```

#### 主なオプション

- `<QUERY>`（必須）

  - 自然文またはキーワード列。
  - 例: `"digits segmentation"`, `"数字列 分割 アルゴリズム"`.
- `--kinds <KIND_LIST>`（任意）

  - 検索対象とする kind をカンマ区切りで指定。
  - 例: `requirements,interfaces,data_contracts,tests,dev_tasks`
  - 省略時は全 kind を対象。
- `--limit <N>`（任意）

  - 返却する候補数の上限。デフォルト 20。
- `--format`（任意）

  - `json`（デフォルト） / `table` / `markdown`。

#### 挙動

1. `--index` が指定されていれば、それを読み込む。なければ `root` 以下を走査して一時的な index を構築する。
2. 各ノードについて、

   - `spec_title`
   - （将来的には Summary セクション等）
     を対象に検索スコアを計算する。
3. スコア順に上位 `limit` 件を返却する。

#### 出力フォーマット（JSON の例）

```json
[
  {
    "id": "REQ-201",
    "kind": "requirements",
    "file": "requirements/REQ-201_digits_segmentation.md",
    "score": 0.92,
    "spec_title": "digits を最適なセグメント列に分割する",
    "snippet": "digits を最適なセグメント列に分割し..."
  },
  {
    "id": "IF-200",
    "kind": "interfaces",
    "file": "interfaces/IF-200_query_engine.md",
    "score": 0.88,
    "spec_title": "Query Engine: digits → segments",
    "snippet": "digits を segments に分割し..."
  }
]
```

#### 代表的なユースケース

- LLM が「このテーマに関する REQ/IF を探したい」ときに最初に呼ぶ。
- 人間が CLI からサッと関連 spec を探したいときにも利用。

### 1.2 `iori-spec show` — SHOULD

#### 目的

指定した ID の spec 本体（front matter＋主要セクション）だけを表示し、
**「とりあえずこの ID の全体像を読みたい」というニーズに応える**。

#### シノプシス

```bash
iori-spec show <ID> \
  [--format markdown|json] \
  [--root <PATH>] \
  [--index <PATH>]
```

#### 主なオプション

- `<ID>`（必須）

  - 例: `REQ-201`, `IF-200`, `DATA-101`, `TEST-301`, `TASK-IF-200-01`.
- `--format`

  - `markdown`（デフォルト）:

    - front matter（必要なら簡略化）＋本文の主要セクションをそのまま出力。
  - `json`:

    - front matter／本文セクションをフィールドに分けた JSON を返す。

#### 挙動

1. index から `ID` に対応するファイルパスを特定する。
2. 対象ファイルをパースし、`spec_section_schema` で `tool_source=true` なセクションだけを抽出する。
3. 指定された `format` に応じて整形して出力する。

#### 代表的なユースケース

- `search` で絞り込んだ ID を「一度全文読んで理解する」ための入口。
- LLM が `context` を呼ぶ前に「まずこの ID の内容をざっと読みたい」ときに利用。

## 2. インデックス・グラフ構築系コマンド

### 2.1 `iori-spec index` — MUST

#### 目的

仕様ディレクトリから ID / kind / scope / front matter / trace / dp 等を抽出し、
**すべてのコマンドが共有する「仕様カタログ（SSOT）」を構築する**。

#### シノプシス

```bash
iori-spec index \
  [--root <PATH>] \
  [--out <PATH>] \
  [--format json]
```

#### 主なオプション

- `--root`

  - 仕様書のルートディレクトリ。デフォルト `.`。
- `--out`

  - 生成したインデックスファイルのパス。デフォルト `artifacts/spec_index.json` 想定。
- `--format`

  - 現状は `json` のみを想定（将来拡張余地あり）。

- 運用メモ（定期実行）

  - 定期的な index 再生成ジョブでは `reference/iori_spec_config.yaml` の `paths.ignore_dirs` を読み込んで除外パス（例: `impl_notes/`）を反映させること。

#### 挙動

1. `root` 以下の spec ファイル（拡張子 `.md` など）を走査。
2. 各ファイルの front matter をパースし、`id / kind / scope / status / spec_title / trace / dp` などを抽出。
3. 抽出結果を `nodes[]` として JSON にまとめ、`--out` に保存する。
4. 成功時は標準出力に生成ファイルパスか簡単なサマリを出して終了。

#### エラー条件（例）

- front matter に `id` が重複している。
- kind / id フォーマットが不正。
- 必須キーが欠落。

（詳細なルールは `lint` と共有する想定。）

### 2.2 `iori-spec graph export` — NICE TO HAVE

#### 目的

内部グラフ（G_trace / G_dp / G_doc / G_task など）を DOT 等でエクスポートし、
可視化やデバッグに利用できるようにする。
G_task は TASK 系エッジだけ抜いたビュー（G_trace の部分グラフ）

#### シノプシス

```bash
iori-spec graph export <GRAPH_KIND> \
  [--index <PATH>] \
  [--root <PATH>] \
  [--out <PATH>] \
  [--format dot|json]
```

#### 主なオプション

- `<GRAPH_KIND>`

  - `trace` / `dp` / `doc` / `task` など。
- `--format`

  - `dot`（デフォルト）: Graphviz 互換の DOT 記法。
  - `json`: ノードとエッジの JSON 表現。

### 2.3 `iori-spec graph neighbors` — NICE TO HAVE

#### 目的

指定 ID の近傍ノードを CLI から確認し、
**「この ID はどの ID とどう繋がっているか？」を手軽に可視化する**。

#### シノプシス

```bash
iori-spec graph neighbors <ID> \
  [--graph trace|dp|doc|task|all] \
  [--depth <N>] \
  [--include-kinds <KIND_LIST>] \
  [--index <PATH>] \
  [--root <PATH>]
```

## 3. 影響範囲 / コンテキスト系コマンド

### 3.1 `iori-spec impact` — MUST

#### 目的

指定 ID を add / change / delete した場合に、影響を受けうる ID を列挙し、
**「どこまで一緒に検討すべきか？」を決めるための材料を提供する**。

#### シノプシス

```bash
iori-spec impact <ID> \
  [--max-depth <N>] \
  [--include-roles <ROLE_LIST>] \
  [--format json|table|markdown] \
  [--index <PATH>] \
  [--root <PATH>]
```

#### 主なオプション

- `<ID>`（必須）
- `--max-depth`

  - 影響グラフを辿る最大ホップ数。デフォルト 2。
- `--include-roles`
  - 列挙に含める role。
  - ROLE は ID プレフィックスに対応するロール種別（例: `REQ-*` → `req`, `IF-*` → `if`）を表す。
- `--format`

  - デフォルト `json`。

#### 挙動

1. index から該当 ID ノードを取得。
2. G_trace / G_dp / G_task / G_doc の組み合わせから、影響グラフを構築。
3. depth 1〜N の範囲で到達可能なノードを集約し、kind・relation・distance などのメタ情報と共に出力。

#### JSON 出力イメージ

```json
[
  {
    "id": "REQ-201",
    "kind": "requirements",
    "relation": "upstream_req",
    "distance": 1
  },
  {
    "id": "DATA-101",
    "kind": "data_contracts",
    "relation": "produces",
    "distance": 1
  },
  {
    "id": "TEST-201",
    "kind": "tests",
    "relation": "verifies_if",
    "distance": 1
  }
]
```

### 3.2 `iori-spec context` — MUST

#### 目的

指定 ID（とその近傍）の spec のうち、LLM に必要な部分だけを抜き出した
**「局所コンテキストパック」**を生成する。

#### シノプシス

```bash
iori-spec context <ID> \
  [--radius <N>] \
  [--include-kinds <KIND_LIST>] \
  [--format markdown|json] \
  [--out <PATH>] \
  [--index <PATH>] \
  [--root <PATH>]
```

#### 主なオプション

- `<ID>`（必須）
- `--radius`

  - 近傍ノードを辿るホップ数。デフォルト 1。
  - `0` を指定すると seed ID の spec のみ。
- `--include-roles`
  - 近傍として含める role。
  - ROLE は ID プレフィックスに対応するロール種別（例: `REQ-*` → `req`, `IF-*` → `if`）を表す。

- `--format`

  - デフォルト `markdown`（LLM に貼り付けやすい形）。
- `--out`

  - 書き出し先ファイル。省略時は標準出力。

#### 挙動

1. `impact` と同様に、`radius` / `include-kinds` に従って近傍ノードを決定。
2. 各 ID について、

   - `show` 相当の処理で主要セクション（Summary / Details / Schema / Steps / Acceptance など）を抽出。
3. seed ID → 近傍 ID の順にまとめて 1 本の Markdown / JSON として出力。

#### 出力例（Markdown・概略）

```markdown
# Context for IF-200 (and neighbors)

---

## IF-200: Query Engine: digits → segments
(front matter の抜粋)
### Summary
...

### Details
...

---

## REQ-201: digits segmentation の要件
...

---

## DATA-101: by_digits.bin
...
```

## 4. 品質維持系コマンド

### 4.1 `iori-spec lint` — MUST

#### 目的

仕様書の構造・front matter・ID 形式などが、
`spec_section_schema` / `iori_spec_guide` のルールに従っているかを検証し、
**「LLM に渡す前提となる仕様の型」を保つ**。

#### シノプシス

```bash
iori-spec lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--rules <RULE_LIST>] \
  [--format text|json]
```

#### 主なオプション

- `--rules`

  - 適用するルールのサブセット。例: `sections,frontmatter,ids`.
  - 省略時はすべてのルールを適用。

#### 主なチェック例

- kind ごとの必須セクションが揃っているか（`spec_section_schema` 参照）。
- front matter に `id/kind/scope/status` が存在するか。
- ID 形式が規約どおりか（`REQ-\d+`, `IF-\d+`, など）。
- 1 ID = 1 ファイル原則を破っていないか（採用する場合）。

### 4.2 `iori-spec trace lint` — MUST

#### 目的

REQ ↔ IF / DATA / TEST のトレーサビリティ（G_trace）が破綻していないかを検証し、
**要求トレーサビリティ coverage の最低限の保証を行う**。

#### シノプシス

```bash
iori-spec trace lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--format text|json]
```

#### 主なチェック例

- 各 REQ に対して、少なくとも 1 つ以上の IF/DATA/TEST が紐づいているか。
- 各 IF/DATA/TEST が、少なくとも 1 つ以上の REQ と紐づいているか。
- trace.* で参照している ID が index に存在するか。
- TASK は coverage チェックの対象外（孤立していてもエラーにはしない）。

### 4.3 `iori-spec trace report` — SHOULD

#### 目的

front matter の trace.* 情報から Traceability Map（REQ 起点 / IF 起点など）を Markdown レポートとして生成し、
**人間がトレーサビリティを俯瞰するためのビュー**を提供する。

#### シノプシス

```bash
iori-spec trace report \
  [--by req|if|data|test] \
  [--root <PATH>] \
  [--index <PATH>] \
  [--out <PATH>]
```

#### 挙動（例）

- `--by req` の場合：

  - 行: REQ-xxx
  - 列: IF/DATA/TEST ID 一覧
  - 各セルにリンク有無をマークした表、または箇条書きのリストを生成。
- `--out` に Markdown ファイルを出力（先頭に「AUTO-GENERATED」コメントを付与）。

## 5. 仕様生成系コマンド

### 5.1 `iori-spec new` / `iori-spec scaffold` — SHOULD（強め）

#### 目的

新しい REQ / IF / DATA / TEST / TASK のための spec ファイルテンプレート（スケルトン）を生成し、
**型の揃った高品質な仕様書を簡単に増やせるようにする**。

#### シノプシス

```bash
iori-spec new <KIND> \
  --id <ID> \
  --spec_title "<TITLE>" \
  [--scope <SCOPE>] \
  [--status <STATUS>] \
  [--root <PATH>] \
  [--out <PATH>]
```

#### 主なオプション

- `<KIND>`

  - `req` / `if` / `data` / `test` / `task` など。
- `--id`

  - 例: `REQ-310`, `IF-200`, `DATA-101`, `TEST-201`, `TASK-IF-200-01`.
- `--spec_title`

  - H1 / H2 見出しに用いるタイトル文字列。
- `--scope`

  - 任意。例: `client.query_engine`。
- `--status`

  - 初期ステータス。例: `draft`（デフォルト）。

#### 挙動

1. `kind` に応じて適切なテンプレートを選択。
2. front matter（id/kind/scope/status/trace/dp 等の初期値）を埋める。
3. `spec_section_schema` に基づく必要最小限のセクションを生成してファイルに書き出す。
4. LLM はこのテンプレートを入力として、Summary / Details / Acceptance などを埋めていくことを想定。

## 6. タスク系コマンド（運用寄り）

### 6.1 `iori-spec tasks list` — NICE TO HAVE

#### 目的

IF / REQ / DATA / TEST などを起点に、関連する TASK ID の一覧を取得し、
**タスクビューから仕様との紐付きを確認できるようにする**。

#### シノプシス

```bash
iori-spec tasks list \
  [--if <IF_ID>] \
  [--req <REQ_ID>] \
  [--data <DATA_ID>] \
  [--test <TEST_ID>] \
  [--index <PATH>] \
  [--root <PATH>] \
  [--format json|table]
```

### 6.2 `iori-spec report tasks` — NICE TO HAVE

#### 目的

TASK を中心にしたレポートビュー（例: IF ごとのタスクリスト）を生成し、
**実装計画や進捗確認など運用寄りのダッシュボード**として利用できるようにする。

#### シノプシス

```bash
iori-spec report tasks \
  [--by if|req] \
  [--index <PATH>] \
  [--root <PATH>] \
  [--out <PATH>]
```

## 7. プロンプト生成コマンド（拡張 / アダプタ層）

### 7.1 `iori-spec prompt` — NICE TO HAVE（拡張）

#### 目的

ContextBundle（DATA-905）を入力として、LLM に渡せる PromptBundle（DATA-907）を構築する。
コア機能（index / lint / trace / search / impact / context）の下流に位置するアダプタとして、
preset / language に応じた system / user / context_markdown をまとめる。

#### シノプシス

```bash
iori-spec prompt \
  [--preset <NAME>] \
  [--language <ja|en|...>] \
  [--format json] \
  [--root <PATH>] \
  [--index <PATH>]
```

#### 備考

- REQ-810 / IF-970 / DATA-907 に紐づく拡張機能。コアのトレーサビリティ／カバレッジとは切り離し、status=draft で開始する。
- ContextBundle の生成は IF-960 / `context` コマンドに依存する。
- JSON 出力（DATA-907 準拠）を基本とし、LLM クライアント側で各プロバイダ形式にマッピングする。
- front matter に `extension: true` を付けることで、trace lint は未トレース/孤立を WARN 扱い（コアは ERROR）。

## MUST コマンド詳細仕様

対象コマンド：

- `iori-spec search`
- `iori-spec index`
- `iori-spec impact`
- `iori-spec context`
- `iori-spec lint`
- `iori-spec trace lint`

共通の前提：

- すべてのコマンドは `--root` と `--index` の共通オプションを受け付ける。
- 走査対象の除外は **config の `paths.ignore_dirs`** を SSOT とし、定期実行時はこの設定を尊重する（例: `impl_notes/` を除外）。
- `--index` 未指定の場合、

  - `index` が既に存在し、かつ新鮮であることを**必須**とはしない（MVP）
  - 各コマンドが必要に応じて内部で `index` 相当の処理を行ってもよい
    （ただし将来的には「index を明示的に叩く」運用へ寄せたい）。

### 共通の終了ステータス（MUST コマンド共通）

- `0` : 正常終了（lint 系では「エラー 0 件」のとき）
- `1` : **仕様上のエラー**

  - 例: lint でルール違反を検出した / 影響 ID が見つからないわけではないが構造が不整合 等
- `2` : **実行時エラー**

  - 例: 引数不正 / I/O エラー / index 破損 / パース不能 など

## 1. `iori-spec search`（MUST）

### 1.1 目的

仕様集合の中から、自然文クエリに関連しそうな ID（REQ / IF / DATA / TEST / TASK 等）を検索し、
**「どの ID を seed にするか？」を決めるための候補リストを返す**。

### 1.2 シノプシス

```bash
iori-spec search <QUERY> \
  [--kinds <KIND_LIST>] \
  [--limit <N>] \
  [--format json|table|markdown] \
  [--root <PATH>] \
  [--index <PATH>]
```

### 1.3 引数・オプション

- `<QUERY>`（必須・文字列）

  - 自然文・キーワードを問わない。
  - UTF-8 前提。日本語・英語混在可。
- `--kinds <KIND_LIST>`（任意・文字列）

  - カンマ区切りで対象 kind を制限する。
  - 例: `requirements,interfaces,data_contracts,tests,dev_tasks`
  - 省略時: すべての kind を対象。
- `--limit <N>`（任意・整数）

  - 返却件数上限。デフォルト `20`。
- `--format`（任意）

  - `json`（デフォルト） / `table` / `markdown`。

### 1.4 入力データ（index 依存）

`search` は index の `nodes[]` を主な入力とする。MUST として依存するフィールド：

- `id`（文字列）
- `kind`（文字列）
- `file`（文字列・相対パス）
- `spec_title`（文字列・任意）
- `scope`（任意）

将来：必要に応じ、summary 等のセクションを index に含めることで検索精度を上げる。

### 1.5 挙動（MVP 想定）

1. index をロードする（`--index` or 自動生成）。
2. 各ノードについて、検索対象テキストを構築する：

   - `id`
   - `spec_title`
   - `scope`
3. クエリ `<QUERY>` をトークン（空白区切り）に分解し、
   シンプルなスコアリングを行う（MVP では以下程度）：

   - 完全一致（タイトル / ID に含まれる）で加点
   - 部分一致で小さめに加点
   - 大文字小文字は無視
4. スコア順にソートし、上位 `limit` 件を返却。
5. 該当ノードが 0 件でも、それ自体はエラー扱いにはしない（終了ステータス 0）。

※ スコアリングアルゴリズムは将来改善可能とし、「結果が安定していること（同じ index, 同じ query に対して同じ結果）」のみを必須とする。

### 1.6 出力仕様

#### `--format json`（デフォルト）

配列形式：

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

- `score` は 0〜1 の相対値（厳密な意味は実装依存）。
- `snippet` は、可能であればタイトルや Summary から一部を抜粋。なければ空文字でもよい。

#### `--format table`

人間向けのシンプルな表（タブ区切り or Markdown table）。
MUST なのは「id / kind / score / spec_title / file」が列として含まれることのみ。

## 2. `iori-spec index`（MUST）

### 2.1 目的

仕様ルートディレクトリ以下の spec ファイルを走査し、
**ID / kind / scope / status / trace / dp 等を集約したインデックス（SSOT）を構築する**。

### 2.2 シノプシス

```bash
iori-spec index \
  [--root <PATH>] \
  [--out <PATH>] \
  [--format json]
```

### 2.3 引数・オプション

- `--root`

  - デフォルト `.`。
- `--out`

  - デフォルト `artifacts/spec_index.json` を想定。
- `--format`

  - 現状 `json` のみ。将来拡張可。

### 2.4 対象ファイル

- デフォルトでは `root` 以下の `**/*.md` を対象とする。
- 一部ディレクトリ（例: `node_modules`, `.git`, `artifacts`, `reports`）は自動的に除外する前提でよい（仕様書側で列挙）。

### 2.5 index JSON スキーマ（MVP）

MUST として含めるフィールド：

```jsonc
{
  "version": "0.1",
  "generated_at": "2025-12-02T12:34:56Z",
  "root": "./docs",
  "nodes": [
    {
      "id": "IF-200",                    // 必須
      "kind": "interfaces",              // 必須
      "file": "interfaces/IF-200.md",    // root からの相対パス (必須)
      "scope": "client.query_engine",    // 任意だが推奨
      "status": "draft",                 // 任意だが推奨
      "spec_title": "Query Engine: ...",      // 任意だが推奨

      "trace": {                           // すべて省略可能
        "req":   ["REQ-201"],
        "if":    [],
        "data":  ["DATA-101"],
        "test":  ["TEST-201"],
        "task":  []
      },

      "dp": {                            // すべて省略可能
        "produces": ["DATA-101"],
        "consumes": ["DATA-201"]
      }
    }
  ]
}
```

- `nodes` 内の `id` は一意でなければならない（重複はエラー）。

### 2.6 挙動

1. `root` 以下の対象ファイルを列挙。
2. 各ファイルの front matter を YAML としてパース。
3. 必須フィールド（`id`, `kind`, `file`）が欠落している場合はエラー（終了コード 2）。
4. `id` が既に登録済みの場合もエラー（終了コード 2）。
5. すべてのファイルを処理し、`nodes[]` を構築。
6. `--out` で指定されたパスに JSON を書き出し、正常終了（0）。

## 3. `iori-spec impact`（MUST）

### 3.1 目的

指定 ID を add / change / delete した場合に、
**影響を受けうる ID の一覧（および関係種別）を列挙する**。

### 3.2 シノプシス

```bash
iori-spec impact <ID> \
  [--max-depth <N>] \
  [--include-kinds <KIND_LIST>] \
  [--format json|table|markdown] \
  [--index <PATH>] \
  [--root <PATH>]
```

### 3.3 引数・オプション

- `<ID>`（必須）

  - index 内で一意に存在する ID。
- `--max-depth`

  - 影響グラフを辿る最大ホップ数。デフォルト `2`。
  - `1` を指定すると、直接接続されたノードのみ。
- `--include-kinds`

  - 出力に含める kind。デフォルトは全 kind。
- `--format`

  - デフォルト `json`。

### 3.4 影響グラフの定義（MVP）

MVP では、以下の情報から無向グラフを構成する：

- `nodes[i].trace.*` による関連：

  - 例: `A.trace.req` に `B` が含まれる → A-B 間に「trace.req」エッジ。

※ `dp.produces/consumes` や G_doc 等は将来拡張とし、MVP の `impact` では「trace.*」によるグラフを必須とする。

### 3.5 挙動

1. index を取得し、`<ID>` に対応するノードを探す。

   - 見つからない場合は実行時エラー（終了コード 2）。
2. 上記の定義にしたがって、影響グラフを構築。
3. `<ID>` を起点に BFS を行い、最大 `max-depth` ホップ内で到達可能なノードを集める。
4. `--include-kinds` で絞り込み、`<ID>` 自身を除外する。
5. 各ノードについて、

   - `id` / `kind` / `distance`（ホップ数）
   - `relations`（最短経路中に現れたエッジ種別の集合）
     を付与して出力。

### 3.6 出力仕様（JSON）

```json
[
  {
    "id": "REQ-201",
    "kind": "requirements",
    "distance": 1,
    "relations": ["trace.req"]
  },
  {
    "id": "DATA-101",
    "kind": "data_contracts",
    "distance": 1,
    "relations": ["trace.data"]
  },
  {
    "id": "TASK-IF-200-01",
    "kind": "dev_tasks",
    "distance": 1,
    "relations": ["trace.if"]
  }
]
```

- 順序は `distance` → `kind` → `id` の昇順（安定ソート）。

## 4. `iori-spec context`（MUST）

### 4.1 目的

指定 ID およびその近傍 ID について、
**LLM に渡すのに十分な「局所コンテキスト」を 1 ファイルにまとめる**。

### 4.2 シノプシス

```bash
iori-spec context <ID> \
  [--radius <N>] \
  [--include-kinds <KIND_LIST>] \
  [--format markdown|json] \
  [--out <PATH>] \
  [--index <PATH>] \
  [--root <PATH>]
```

### 4.3 引数・オプション

- `<ID>`（必須）
- `--radius`

  - 近傍ノードを辿るホップ数。デフォルト `1`。
  - `0` の場合は `<ID>` 単体のみ。
- `--include-kinds`

  - 近傍として含める kind。デフォルトは全 kind。
- `--format`

  - デフォルト `markdown`。
- `--out`

  - 出力先。省略時は標準出力。

### 4.4 コンテキスト対象ノードの決定

1. `impact <ID> --max-depth=radius --include-kinds=<…>` 相当の処理で近傍 ID を決める。
2. seed ID `<ID>` と近傍 ID 群を、以下の順に並べる：

   - 先頭: seed ID
   - 以降: `distance` → `kind` → `id` の順でソートされた近傍 ID

### 4.5 セクション抽出ルール

`spec_section_schema` において、各セクションには少なくとも以下の属性が定義されている前提とする：

- `tool_source: true|false`

  - `true` のセクションのみ、LLM に渡す対象。
- （将来的に）`tool_priority` などを導入してもよい。

MVP では：

- 各 ID のファイルから、

  - front matter（`id/kind/scope/status/spec_title` など最低限の情報）
  - `tool_source=true` なセクションすべて
- を抽出し、コンテキストに含める。

### 4.6 出力仕様（markdown）

```markdown
# Context for IF-200 (radius=1)

---

## IF-200: Query Engine: digits → segments

<front matter の抜粋 or 整形表示>

### Summary
...

### Details
...

### Acceptance Criteria
...

---

## REQ-201: digits segmentation の要件

### Summary
...

...

---
```

- 各 ID ごとに `## <ID>: <title>` を見出しとしてまとめる。
- front matter は全文を載せてもよいが、`id/kind/scope/status` のようなキーだけを載せる簡易表示でもよい（仕様でどちらかに寄せても可）。

### 4.7 出力仕様（JSON）

JSON モードでは、各 ID ごとにオブジェクトを返す：

```json
[
  {
    "id": "IF-200",
    "kind": "interfaces",
    "spec_title": "Query Engine: digits → segments",
    "file": "interfaces/IF-200.md",
    "front_formatter": {
      "id": "IF-200",
      "kind": "interfaces",
      "scope": "client.query_engine",
      "status": "draft"
    },
    "sections": {
      "summary": "....",
      "details": "....",
      "acceptance": "...."
    }
  }
]
```

## 5. `iori-spec lint`（MUST）

### 5.1 目的

仕様書ファイル単体の構造・front matter・ID 形式などが
**「LLM に渡すことを前提とした型（spec_section_schema / iori_spec_guide）」に従っているか**を検証する。

### 5.2 シノプシス

```bash
iori-spec lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--rules <RULE_LIST>] \
  [--format text|json]
```

### 5.3 主なオプション

- `--rules`

  - 適用するルールセット。例:

    - `frontmatter` : front matter の必須キー・型
    - `ids`         : ID 形式・重複
    - `sections`    : kind ごとの必須セクション
  - 省略時はすべてのルールを適用。
- `--format`

  - `text`（デフォルト） / `json`。

- 運用メモ（定期実行）

  - lint/index の定期ジョブは `reference/iori_spec_config.yaml` の `paths.ignore_dirs` を必ず読み込み、除外したいディレクトリ（例: `impl_notes/`）は config 側で管理する。

### 5.4 チェックの範囲（MVP）

- **frontmatter ルール**

  - すべての対象ファイルに `id` / `kind` / `status`（任意かどうかは iori_spec_guide 依存）が存在するか。
  - `id` の形式が kind ごとの規約（例: `REQ-\d{3}`）に従っているか。
  - `kind` が既知の値か。
- **ids ルール**

  - index 中で `id` が重複していないか（index での検査と一貫させる）。
- **sections ルール**

  - `spec_section_schema` で kind ごとに定義された「必須セクション」がすべて存在するか。
  - セクションの順序が schema と大きく乖離していないか（MVP では順序チェックは Optional にしてもよい）。

### 5.5 出力仕様

#### `--format text`

- 例：

```text
[ERROR] interfaces/IF-200.md: frontmatter.id is missing
[WARN ] requirements/REQ-201.md: section 'Acceptance Criteria' is missing
```

- エラー（ERROR）が 1 件以上ある場合は終了コード 1。
- WARN のみの場合は終了コード 0。

#### `--format json`

```json
{
  "errors": [
    {
      "file": "interfaces/IF-200.md",
      "id": "IF-200",
      "rule": "frontmatter.id.required",
      "severity": "error",
      "message": "frontmatter.id is missing"
    }
  ],
  "warnings": [
    {
      "file": "requirements/REQ-201.md",
      "id": "REQ-201",
      "rule": "sections.acceptance.required",
      "severity": "warning",
      "message": "section 'Acceptance Criteria' is missing"
    }
  ]
}
```

## 6. `iori-spec trace lint`（MUST）

### 6.1 目的

REQ ↔ IF / DATA / TEST の間のトレーサビリティを検証し、
**要求トレーサビリティ coverage の最低限の保証を行う**。

### 6.2 シノプシス

```bash
iori-spec trace lint \
  [--root <PATH>] \
  [--index <PATH>] \
  [--format text|json]
```

### 6.3 チェックの範囲（MVP）

- **ID 存在チェック**

  - すべての `nodes[i].trace.*` の参照先 ID が index に存在するか。
- **REQ coverage**

  - 各 REQ ノードに対して、

    - 少なくとも 1 つ以上の IF / DATA / TEST がトレースされているか。
- **IF / DATA / TEST coverage**

  - 各 IF / DATA / TEST ノードに対して、

    - 少なくとも 1 つ以上の REQ にトレースされているか。
- **TASK の扱い**

  - TASK ノードは coverage の評価対象外とする。
  - ただし `trace.*` の参照が存在しない場合もエラーにはしない（警告程度に留めるか完全無視）。

### 6.4 出力仕様

#### `--format text`

```text
[ERROR] REQ-201: no related IF/DATA/TEST found
[ERROR] IF-300: not linked from any REQ
[ERROR] DATA-101: refers to unknown ID 'REQ-999'
```

- エラーが 1 件以上ある場合は終了コード 1。
- エラー 0 件の場合は終了コード 0。

#### `--format json`

```json
{
  "errors": [
    {
      "id": "REQ-201",
      "kind": "requirements",
      "rule": "trace.req.coverage",
      "severity": "error",
      "message": "no related IF/DATA/TEST found"
    },
    {
      "id": "IF-300",
      "kind": "interfaces",
      "rule": "trace.if.coverage",
      "severity": "error",
      "message": "not linked from any REQ"
    }
  ]
}
```

## trace lint のルールセット

### 0. 前提とゴール

- 対象は **Traceability Graph（G_trace）**：
  - 主に `REQ / IF / DATA / TEST` の `trace.*` フィールド（＋必要に応じて `kind` / `status`）。

- `TASK` は **Graph には乗るが coverage 対象外**。
  - ＝「REQ↔IF/DATA/TEST がちゃんと繋がっているか？」を見るのが `trace lint` の役目。

- ここで決めるのは：
  - 各ルールの **条件**
  - そのルールの **severity（INFO / WARN / ERROR）**
  - 必要があれば **status（draft / review / stable）による強さの違い**

### 1. severity の意味づけ

まずは `trace lint` 専用の severity の意味をはっきりさせておく：

- **ERROR**

  - 「構造として破綻している」「放置すると LLM / ツールが正しく動かない」レベル。
  - `trace lint` の終了コードを **1** にする（CI 落ちてもよいレベル）。
- **WARN**

  - 「仕様として未充足 or 危険な匂いはあるが、構造的には壊れていない」レベル。
  - 終了コードは **0 のまま**だが、修正を強く推奨。
- **拡張（extension: true）**

  - front matter に `extension: true` が付与されているノードは「拡張扱い」とし、孤立/未トレースなど本来 ERROR となるケースも WARN に緩和する。
  - 付与されていないものはすべてコア扱い（通常の ERROR 判定）とする。
- **INFO**

  - 「設計上の傾向や TODO を知らせるための情報」レベル。
  - 情報提供のみ。終了コード 0。

将来的に `--strict` などで「WARN も ERROR 扱い」にするのはアリだけど、
**デフォルトの線引き**は上記の通り、という前提でルールを作る。

### 2. ルール一覧（ID / 条件 / severity）

#### 2.1 参照整合性（Referential Integrity）

##### TRACE-001: unknown_target_id

- **条件**

  - あるノード `X` の `trace.*` に含まれている ID `Y` が、index の `nodes[].id` に存在しない。
- **severity**

  - 常に **ERROR**
- **理由**

  - グラフが閉じておらず、`impact` や `context` で辿れないノードが発生する。
  - 完全に typo / 削除漏れなので、放置すると LLM が誤った影響範囲を認識する。

##### TRACE-002: self_reference

- **条件**

  - ノード `X` の `trace.*` に `X.id` 自身が含まれている。
- **severity**

  - デフォルト **WARN**
- **理由**

  - 構造的には致命傷ではないが、ほぼ確実に設定ミス。
  - 将来 `impact` / `context` の結果がおかしく見える原因になる。

#### 2.2 REQ 側の coverage（上流要件が宙ぶらりんになっていないか）

##### TRACE-010: req_has_no_impl

- **条件**

  - kind が `requirement` のノード `R` について、

    - `R` に紐づく IF / DATA / TEST が 1 つも存在しない。
  - 「紐づく」は、`R` 自身の `trace.*` だけでなく、
    **他ノードの `trace.req` に `R.id` が含まれている場合も含む**（片方向登録でもOK）。
- **severity（status 依存）**

  - `R.status = draft`   → **WARN**
  - `R.status = review`  → **ERROR**
  - `R.status = stable`  → **ERROR**
- **理由**

  - draft の段階では「まだ実装対象が決まっていない要件」があってもよいが、
    review / stable では「実装 or データ or テスト」が 1 つも紐づいていないのは要件漏れ。

##### TRACE-011: req_has_no_test

- **条件**

  - requirement ノード `R` について、

    - 紐づく TEST ノードが 1 つもない。
- **severity（status 依存）**

  - `R.status = draft`   → **INFO**
  - `R.status = review`  → **WARN**
  - `R.status = stable`  → **ERROR**
- **理由**

  - 「要件に対するテストが 1 つもない」のは、最終的には避けたい状態。
  - ただし初期フェーズでは準備中のことが多いため、段階的に厳しくする。

#### 2.3 IF / DATA / TEST 側の coverage（下流の仕様が誰のために存在しているか）

##### TRACE-020: if_not_linked_from_any_req

- **条件**

  - interface ノード `I` について、

    - `I` と紐づく requirement ノードが 1 つもない。
    - ※ ここでも「紐づく」は、`I.trace.req` だけでなく `REQ.trace.if` など他ノード側の登録も含む。
- **severity（status 依存）**

  - `I.status = draft`   → **WARN**
  - `I.status = review`  → **ERROR**
  - `I.status = stable`  → **ERROR**
- **理由**

  - REQ と無関係な IF が増えると、「何のためのインターフェイスか」が不明瞭になり、LLM も判断しづらい。
  - review / stable の段階で REQ に紐づいていない IF はバグの可能性が高い。

##### TRACE-021: data_not_linked

- **条件**

  - data_contract（等）ノード `D` について、

    - 紐づく REQ / IF / TEST が 1 つもない。
- **severity（status 依存）**

  - `D.status = draft`   → **INFO**
  - `D.status = review`  → **WARN**
  - `D.status = stable`  → **WARN**（or 運用ポリシー次第で ERROR に昇格可能）
- **理由**

  - 「誰からも参照されていない DATA」は死にテーブルの可能性が高いが、
  - 一方でライブラリ的な共通 DATA を先に定義するケースもありうるため、やや弱めに設定。

##### TRACE-022: test_not_linked

- **条件**

  - test ノード `T` について、

    - 紐づく REQ / IF が 1 つもない。
- **severity（status 依存）**

  - `T.status = draft`   → **WARN**
  - `T.status = review`  → **ERROR**
  - `T.status = stable`  → **ERROR**
- **理由**

  - 「何を検証しているテストか分からない TEST」は評価しづらい。
  - draft では試験的な TEST を書き捨てることもあるので WARN 止まり、
    しかし review/stable では REQ/IF に紐づけるべき。

#### 2.4 トレーサビリティの「孤立ノード」

##### TRACE-030: isolated_node_in_trace_graph

- **条件**

  - `kind ∈ {requirements, interfaces, data_contracts, tests}` のノード `X` について、

    - `X.trace.*` が全て空であり、
    - 他ノードの `trace.*` にも一切 `X.id` が現れない（= グラフとして完全に孤立）。
- **severity（status 依存）**

  - `X.status = draft`   → **INFO**
  - `X.status = review`  → **WARN**
  - `X.status = stable`  → **ERROR**
- **理由**

  - draft では「書きかけの spec」などが孤立していてもよいが、
  - 安定期に孤立ノードが残っているのは設計漏れ or ゴミの可能性が高い。

#### 2.5 TASK の扱い（coverage からは外すが、参照整合性は見る）

##### TRACE-040: task_refers_unknown_id

- **条件**

  - `kind = dev_tasks` のノード `T` について、

    - `T.trace.*` が未知の ID を参照している。
- **severity**

  - **ERROR**（TRACE-001 のサブケースとして扱ってもよい）
- **理由**

  - TASK は coverage 対象ではないが、unknown ID を指していると `impact/context` で誤誘導。

##### TRACE-041: task_without_owner

- **条件**

  - ``kind = dev_tasks` のノード `T` について、

    - `trace.*` にも IF/REQ/DATA/TEST が 1 つもない。
- **severity**

  - **WARN**
- **理由**

  - 「どの spec にぶら下がるタスクか」が不明で、LLM から見ても扱いづらい。
  - ただし、完全に禁止するほどではないので WARN 止まり。

#### 3. ルール -> severity をどう適用するか（ドラフト）

`trace lint` の出力設計はこんな感じでいけます：

- 各違反について：

  - `id` / `kind` / `rule` / `severity` / `message` を JSON or text で出力。
- 終了コード：

  - **ERROR が 1 件以上あれば exit 1**。
  - WARN / INFO のみなら exit 0。

status 依存のルール（TRACE-010 / 011 / 020 / 021 / 022 / 030）は、

- そのノード自身の `status` を見て severity を決定。
- status 未設定の場合は、保守的に `draft` 相当として扱う（＝厳しさを少し緩める）。

#### 4. このあとやると良さそうなこと

あなたが書いてくれた通り：

> spec_section_schema との整合はそレを反映後、最新ファイルに準拠して比較検討したい。

なので、いま決めたルールセットを前提にして、

1. `trace lint` が参照するフィールド（`id/kind/status/trace.*`）が
   **front matter と schema のどこで定義されているか**を spec_section_schema 側で確認。
2. 必要なら

   - 「trace lint が見るべきセクション／項目」を
     spec_section_schema のどこかに一行で明記する（例: `trace_lint_target: true` 的なフラグ）。
3. そのうえで、`trace lint` の仕様ファイルと `spec_section_schema` の差分を詰めていく。

…という流れで合わせると綺麗にハマるはず。

まずはこのルールセットをベースラインとして、
「このルールは重すぎる / 足りない」と感じるところがあれば、そこから微調整していこう。
