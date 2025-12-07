---
kind: impl_notes
scope: iori-spec
spec_title: "iori-spec Templates & TODOs"
status: draft

# TODO spec_template.md の内容は spec_section_schema.yaml に移行して、最終的にはファイルを削除できるようにする。

---
# iori-spec template 案

## section の分類

セクションには「共通で意味を固定したいもの」と「kind / ファイルごとに変わるもの」の2〜3階層があります。

### layer1：**全 spec 共通で固定するセクション**

ここは **どのファイルでも“同じ意味”** を持つ前提で設計してます。

- `YAML front matter`
- `H1 タイトル`
- `## LLM_BRIEF`
- `## USAGE`
- `## READ_NEXT`
- `## 1. このドキュメントの役割`
- `## 2. 範囲（Scope）と前提`
- `## 3. 運用上の目安（LLM / SDD 観点）`

ここは **iori-spec 側が構造的に理解する前提**なので、意味（役割）は固定。
中身の具体的な文章はファイルごとに違うけど、「何を書く場所か」は共通です。

### layer2：**kind ごとの“型”として揃えたいセクション**

ここから先は **kind によって違う**けど、
「同じ kind ではパターンを揃えたい」層。

例：

- `requirements/REQ-101_digits_segmentation.md`

  - `## 4. 要件の概要（Summary）`
  - `## 6. Acceptance Criteria`

- `requirements/REQ-2xx_performance.md`

  - `## 4. 要件の概要（Summary）`
  - `## 6. Acceptance Criteria`

- `architecture/overview.md`

  - `## 4. コンポーネント一覧`
  - `## 5. レイヤー構造`
  - `## 6. データフローと依存ルール`

- `interfaces/IF-001_*.md`

  - `IF-001 見出し`
  - `Summary / 役割`
  - `入力 / 出力 / エラー`
  - `Examples`

この辺は **“requirements の template” “architecture の template”** としてテンプレートファイルを用意し、iori_spec_guide に書いておく。
「全 spec 共通」ではなく kind ごとに違って OK という位置づけ。

### layer3：**ファイル固有のセクション**

さらにその下は、**ファイルごとに自由**に記載する層。

例：

- `steering/product.md` だけが持つ

  - `## 4. コアとなる2つの目的（軸① / 軸②）`
  - `## 5. 想定ユーザと主要ユースケース`

- ある大きめの architecture ファイルだけが持つ

  - `「今後の拡張方針」`

- 特定プロジェクトだけの

  - `「XXX ドメイン固有ルール」` 等

ここは iori-spec は“中身を構造としては解釈しない”想定で、
LLM にとっても「読めたら嬉しいけど、必須スキーマではない」として扱う感じ。

## layer1 section 仕様

### `YAML front matter`（COMMON MUST）

#### 構成

```yaml
---
kind: interfaces                     # 【必須】このファイルの種別。steering / requirements / architecture / interfaces / data_contracts / tests / reference / dev_tasks / impl_notes など。
scope: client.query_engine           # 【必須】この仕様が属する領域・モジュール名。ツールは scope を「文字列ラベル」として扱い、グルーピングやフィルタに使う（分類の軸）。

id: IF-200                           # 【必須】このファイルで定義する ID。原則「1ファイル1ID」の前提で、index / trace のノード名になる。
spec_title: "Query Engine — digits→segments" # 【必須】人間＆LLM 向けタイトル。H1 見出し（`# {spec_title}`）と重複するが、ツールは front matter 側を信頼する。
status: review                       # 【必須】仕様の成熟度。draft / review / stable など。lint の厳しさや、LLM にどこまで信頼させるかのヒントに使う。
extension: true                      # 【任意】拡張機能として扱う場合に指定。trace lint は未トレース等を WARN 扱いに緩和。

# ---- 要求トレースグラフ（G_trace）用の情報 ----
trace:                               # 【必須（ID キャリア kind のみ）】REQ / IF / DATA / TEST / TASK との「論理的な関係」を宣言するブロック。
  req:                               # この IF が主に満たすことを意図している REQ-xxx の一覧（親となる要求）。
    - REQ-201                        # 例: digits セグメント化アルゴリズムの要件。
    - REQ-202                        # 例: パフォーマンス要件など。
  if: []                             # 関連する他の IF-xxx（派生 / ラッパ / 下位IF など）があれば列挙。なければ空配列。
  data:                              # 密接に関わる DATA-xxx（この IF が強く依存するデータ契約）を列挙。DPグラフよりも「論理的な関係」を表す。
    - DATA-101                       # 例: この IF が責任を持つ出力 DATA。
  test:                              # 主にこの IF を検証する TEST-xxx を列挙（カバレッジ把握用）。TEST 側からも trace してよい。
    - TEST-201
  task:                              # この IF を実装する TASK-xxx（開発タスク）を列挙。Graph には乗るが coverage ルールの対象ではない。
    - TASK-IF-200-01

# ---- Data–Process Graph（G_dp）用の情報 ----
dp:                                  # 【DATA / IF で利用】IF⇄DATA のビルド依存関係。二部グラフ G_dp を構成するための情報をまとめる。
  produces:                          # この IF が生成する DATA-xxx（P→D の向き）を列挙。ビルド成果物。
    - DATA-101                       # 例: by_digits.bin のようなバイナリアーティファクト。
  produced_by: []                    # DATA 側で「誰に作られるか」を書く場合はこちらを使用。IF 側では通常は空配列のまま。
  consumes:                          # この IF が読み取る DATA-xxx（D→P の向き）を列挙。入力として参照するデータ。
    - DATA-020                       # 例: SURF_DIGITS
    - DATA-014                       # 例: M_SURF_ENT
  inputs: []                         # より広い意味での入力（ファイル・外部サービスなど）を列挙したい場合に利用。未使用なら空配列。

# ---- ドキュメント依存グラフ（G_doc）用の情報 ----
doc:                                 # 【任意】「一緒に読むと理解しやすい仕様」のリンク。トレースではなく、コンテキスト生成用のヒント。
  read_next:                         # 「この spec を読むときに、次に読むと良い ID」のリスト。IDベースの近傍候補。
    - IF-210                         # 例: 近い層の別 IF。
    - DATA-130                       # 例: この IF と関わりの深い DATA 仕様。
  see_also:                          # ID でないドキュメントパスやトピック名など、ゆるい関連情報。G_doc では弱いリンクとして扱う想定。
    - "architecture/overview.md"     # 例: 全体アーキテクチャの説明 doc。
---
```

1. **Core メタ情報（仕様そのもののラベル）**

   - `kind`：このファイルの種別。ツールが扱い方を切り替えるための key。
   - `scope`：どの領域／モジュールに属するか。プロジェクトごとの分類軸。
   - `id`：グローバルに一意な仕様 ID（1ファイル1ID の前提）。
   - `spec_title`：人間・LLM が読むタイトル。
   - `status`：draft / review / stable / deprecated などの成熟度。

2. **Graph 情報（Trace / DP / Doc の SSOT）**

   - `trace.*`：REQ / IF / DATA / TEST / TASK 間の論理的つながり。
   - `dp.*`：IF⇄DATA の Data–Process 依存関係。
   - `doc.*`：READ_NEXT / SEE_ALSO といった「一緒に読むと良い」近傍情報。

- ※ 配列はすべて「縦に並べるブロックスタイル」を推奨
  - diff が読みやすい
  - LLM に「この行だけ消して」と頼みやすい
  - 各 ID ごとにコメントを付けやすい

#### 1. Core メタ情報

##### 1.1 kind

`kind` は **iori-spec がファイルの扱い方を決めるためのグローバルな列挙型**。
プロジェクトごとに意味が変わらないことを前提とする。

代表的な値と意味（v1 想定）：

- `steering`
  - プロダクトビジョン・方向性・非ゴールなど。例：`steering/product.md`
- `requirements`
  - 機能要件・非機能要件・トレースマップなど（REQ-xxx を含むファイル）。
- `architecture`
  - コンポーネント構成・レイヤー構造・データフローなどの設計。
- `interfaces`
  - 外部に公開するインターフェイス（CLI コマンド、API 等）。IF-xxx を含む。
- `data_contracts`
  - データ構造・スキーマ・テーブル定義など（DATA-xxx を含む）。
- `tests`
  - テスト観点・テストケース・受け入れ条件（TEST-xxx を含む）。
- `reference`
  - 用語集・命名規約・iori_spec_guide などのリファレンス。
- `dev_tasks`
  - 実装タスク・TODO（TASK-xxx-yy を含む）。
- `impl_notes`
  - 実装メモ・検討ログ。構造チェックの対象としては **参照優先度が低い** メモ扱い。

運用ルール（案）：

- 実際にプロジェクトで許可する `kind` 一覧は、
  `reference/iori_spec_config.yaml` の `kinds:` セクションに列挙する。
- lint 時には「unknown kind」があれば warning（必要なら将来 error）を出す。

##### 1.2 scope

`scope` は「この仕様書は、プロジェクト全体のうち **どの領域について述べているか**」を表すラベル。
`kind` が「型」（requirements / interfaces / …）なのに対し、`scope` は「縦に切る分類軸」。

###### 1.2.1 形式

- 型：文字列
- 形式：`トップレベル[.サブ1[.サブ2...]]`

例：

```yaml
scope: functional
scope: nonfunctional
scope: cli
scope: cli.index
scope: builder.pipeline
scope: docs
```

- 文字列の先頭（`.`より前の部分）を「トップレベル scope」と呼ぶ。

  - 例：`cli.index` → トップレベル scope は `cli`

###### 1.2.2 トップレベル scope の列挙

トップレベル scope は、各プロジェクトの設定ファイルに列挙する：

```yaml
# reference/iori_spec_config.yaml（例）
kinds:
  - steering
  - requirements
  - architecture
  - interfaces
  - data_contracts
  - tests
  - reference
  - dev_tasks
  - impl_notes

scopes:
  - functional
  - nonfunctional
  - traceability
  - cli
  - builder
  - docs
```

- iori-spec は `scope` を解釈する際、

  - 先頭トークン（例：`cli.index` → `cli`）を取り出し、
  - それが `scopes:` に含まれているかどうかを lint でチェックする。
- 含まれていない場合は「未知の scope」として **warning** を出すが、v1 ではエラーにはしない。

  - 実験的な分類（`weird.experimental` 等）を許容するため。

###### 1.2.3 決め方のガイド

- scope は 1 ファイルにつき **1 つだけ**。

  - 「このファイルを 1文で説明したら？」の答えに近いものを選ぶ。
- クロスカット（例：`cli` と `builder` の両方を跨ぐ）場合：

  - どちらか一方を `scope` に採用し、もう一方は本文中や ID ブロック側のタグ（`[area]` 等）で表現する。
- iori-spec 自身の例：

  - 機能要件 → `scope: functional`
  - 非機能要件 → `scope: nonfunctional`
  - トレースマップ → `scope: traceability`
  - CLI 関連 IF / DATA / TEST → `scope: cli` または `cli.index`, `cli.trace` 等
  - ビルドパイプライン → `scope: builder` または `builder.pipeline`
  - 仕様の書き方や用語集 → `scope: docs`

##### 1.3 id

`id` は **仕様ノードを一意に識別するためのグローバル ID**。

- 型：文字列
- 前提：

  - 1ファイル 1 ID
  - プロジェクト全体でユニーク（重複禁止）

- 用途：

  - `index` の主キー（`node.id`）
  - `trace` / `dp` / `doc` から構成される各種グラフのノード名
  - CLI コマンド（`show` / `impact` / `context` / `graph ...` など）で指定するキー

- 代表的な形式（例）：

  - 要求仕様：`REQ-001`, `REQ-201` など（`requirements/` 配下）
  - インターフェイス：`IF-200` など（`interfaces/` 配下）
  - データ契約：`DATA-101` など（`data_contracts/` 配下）
  - テスト：`TEST-001` など（`tests/` 配下）
  - 実装タスク：`TASK-REQ-201-01` のように「対象 ID ＋連番」を含めることを推奨
  - リファレンス／メタ系：`REF-101_spec-meta`, `REF-102_section-guide` など（`reference/` 配下、ID は `REF-`+3桁以上で統一）

- 運用ルール（v1 想定）：

  - `id` は **すべての core spec ファイルで必須**（impl_notes など、例外を設ける場合は別途明記）。
    - ここでいう core spec とは、kind が steering / requirements / architecture / interfaces / data_contracts / tests / dev_tasks / reference のいずれかであるファイルを指す。
  - ファイル名と ID はできるだけ対応させる：
    - 例：`IF-200_query_engine.md` ↔ `id: IF-200`
  - ID のプレフィックスや桁数など詳細な命名規則は `reference/iori_spec_guide.md` 側で定義する。
  - impact/context で使う「ROLE」は、この ID プレフィックスから導かれる種別（例: `REQ-*` → `req`, `IF-*` → `if`）とする。

##### 1.4 spec_title

`spec_title` は **人間と LLM に見せる正式タイトル**。

- 型：文字列
- 用途：

  - `index` 出力のタイトル列
  - UI / CLI の一覧表示
  - context 生成時の「見出し」

運用上のガイド：

- ファイルの H1 見出し（`# ...`）とは **ほぼ同じ内容** にしておくと混乱がない。
- ただし SSOT としては front matter の `spec_title` を優先し、
  H1 は「表示用の重複」くらいの扱いにする。

##### 1.5 status

`status` は **仕様書のライフサイクル状態** を表す列挙型。

代表的な値：

- `draft`
  - たたき台。大きく書き換わる前提。
- `review`
  - ひと通り書き終わり、レビュー待ち。
- `stable`
  - 合意済み。本番運用中。大きな変更は原則避ける。
- `deprecated`
  - 廃止予定。参照のみ。新仕様への移行前提。

運用イメージ：

- LLM や新メンバーに「まず読んでほしい」のは `stable` / `review`。
- `draft` は「思考中のメモ」の可能性が高いので、context に含めるときは注意書きを添える。

※ 将来的に必要になれば、`experimental` などを追加する余地はあるが、v1 は上記 4 種類を想定。

#### 2. Graph 情報

詳細な構造（`trace.*` / `dp.*` / `doc.*` の具体的キー）は別ドキュメントで詰めるとして、
ここでは **「何のためのフィールドか」「どんな値が入るか」だけ**をざっくり定義しておく。

##### 2.1 trace.*（トレースグラフ G_trace 用）

役割：

- REQ / IF / DATA / TEST / TASK 間の **論理的な「つながり」** を front matter 上に表現する。
- ここに書かれた ID 同士の関係から、ツールが G_trace を構築する。

値のイメージ（案）：

```yaml
trace:
  req:
    - REQ-101
    - REQ-102
  if:
    - IF-001
  data:
    - DATA-001
  test:
    - TEST-201
  task:
    - TASK-REQ-101-01
```

- 各フィールドは **ID 文字列の配列**。
- ID の形式（`REQ-XXX`, `IF-XXX`, `DATA-XXX`, `TEST-XXX`, `TASK-...`）は別途 iori_spec_guide 側で定義。

##### 2.2 dp.*（データとプロセスの依存関係 G_dp 用）

役割：

- IF ⇄ DATA の「誰がどのデータを読み書きするか」を表すメタ情報。
- 将来的に「この DATA に影響する IF 一覧」「この IF に関係する DATA 一覧」を出すときの材料になる。

値のイメージ（例）：

```yaml
dp:
  produces:
    - DATA-RESULT-001   # この IF が主に生成する DATA
  produced_by: []       # DATA 側で「どの IF によって作られるか」を明示したいときに使う
  consumes:
    - DATA-INPUT-001    # この IF が入力として読む DATA
  inputs: []            # ファイルパスや外部サービスなど、「DATA-xxx 以外の入力」を書きたい場合に使う
```

- こちらも ID 文字列の配列を基本とし、詳細キー（produces / consumes 等）は今後の仕様で詰める。

##### 2.3 doc.*（ドキュメント近傍情報 G_doc 用）

役割：

- 「一緒に読むと理解しやすい spec」のリンク集。
- impact / context で近傍ドキュメントを引くときのヒント。

値のイメージ：

```yaml
doc:
  read_next:
    - REQ-101
    - REQ-102
  see_also:
    - artifacts/traceability_map.md
```

- ファイルパス or ID の配列。
- v1 では形式を厳しく縛らず、「存在すれば優先して context に混ぜる」程度の扱いでもよい。

#### 設計意図（要約）

- **共通ヘッダー YAML front matter の役割**

  - iori-spec の思想

    - ①局所コンテキスト化（LLM から見ると常に“小さい一部分だけ読めば済む状態”）
    - ②構造健全性（仕様どうしの依存関係・トレース・責務分担が壊れないようにツールで構造をチェック＆誘導）

    を達成するための 1ファイル（= 1ノード）の**最小限の schema**を定義するのが YAML front matter。

- **front matter は「仕様ノードの SSOT」**

  - 各 spec ファイルは原則「1ファイル1ID」。
  - `id / kind / scope / spec_title / status` と、`trace / dp / doc` を front matter に集約し、
    ここから **G_trace / G_dp / G_doc** を機械的に復元できるようにする。

- **Traceability Map はビュー扱い**

  - 人間・LLM が読むときに理解しやすいよう整形された「表示用ビュー」であって、
    トレーサビリティの SSOT はあくまで front matter 側。
  - 必要なら「front matter とビューの不一致」を別 lint で検出する。

- **scope は構造の中核ではなく、“メタな分類軸”**

  - Graph の正しさ（REQ↔IF↔DATA など）には本質的ではない。
  - ただし、仕様の見通し・検索性・レビュー効率のために、
    `scope` を「トップレベル enum＋サブパス自由」というルールで設ける。
  - 例：`functional.requirements` / `nonfunctional.performance` / `cli.index` / `builder.pipeline`。

- **status は「どこまで厳しく見るか」のヒント**

  - `draft / review / stable / deprecated` などで成熟度を表す。
  - trace lint の coverage ルール（REQ に IF/TEST が付いているか等）の厳しさを、status に応じて変えることを想定。

#### 設計意図（詳説）

##### 1. Core メタ情報としての front matter

front matter は iori-spec にとって、**仕様ノードを識別・分類するための最小限の型情報**を担う。
v1 では次の項目を core として扱う：

- `kind`

  - ファイル種別。`requirements / interfaces / data_contracts / tests / dev_tasks / steering / architecture / reference / impl_notes` など。
  - iori-spec がファイルをどう扱うか（index に載せるか / trace lint の対象にするか等）に直結するため、**グローバル enum**として定義する。

- `scope`

  - 仕様が属する領域・モジュールを表す **プロジェクト内の分類軸**。
  - 先頭トークンだけ enum として定義し（例：`functional / nonfunctional / cli / builder / docs / traceability` など）、
    `.` 以降はプロジェクトローカルの自由な階層にする。
  - LLM や CLI からの利用イメージ：

    - 「`functional.*` の requirements だけ一覧を出す」
    - 「`cli.*` の interfaces をまとめて impact/context したい」

- `id`

  - グローバルに一意な仕様 ID（例：`REQ-201` / `IF-200` / `DATA-101` / `TEST-201` / `TASK-IF-200-01` など）。
  - 原則「1ファイル1ID」。
  - index / trace lint / impact / context が扱う **グラフノード名そのもの**になる。

- `spec_title`

  - 人間と LLM に見せるタイトル。本文側の H1 見出しと一致させる想定。
  - index の一覧や context 生成時に「ID にぶら下がるラベル」として使う。

- `status`

  - 仕様の成熟度（`draft / review / stable / deprecated` など）。
  - trace lint のルール（例：stable な REQ に IF/TEST が無い場合は ERROR、draft なら WARN…）の閾値を決める材料として使う。

これらは **「仕様そのもの」＋「仕様をどこまで信頼してよいか」というメタ情報**に相当する。

##### 2. Graph（Trace / DP / Doc）の SSOT としての front matter

**Graph 系の情報は front matter だけに寄せる**方針。

- `trace` ブロック

  - REQ / IF / DATA / TEST / TASK 同士の **論理的な関係**を定義する。
  - ここから G_trace を構築し、trace lint の coverage チェックもこの情報だけを見て行う。

- `dp` ブロック

  - IF⇄DATA の **Data–Process 依存関係**を定義する。
  - ここから G_dp を構築し、「どの IF がどの DATA を生成／消費するか」をツールで追えるようにする。

- `doc` ブロック

  - READ_NEXT / SEE_ALSO による **ドキュメントレベルの近傍関係（G_doc）**を定義する。
  - 影響範囲というより、「一緒に読むと理解がスムーズな spec」を示すナビゲーション情報として利用する。

これにより：

- ツールは front matter だけを読めば、
  G_trace / G_dp / G_doc を機械的に再構築できる。
- Traceability Map は、「front matter を見やすく展開したビュー」として扱える。

##### 3. BODY 側の役割：ビュー＆コンテキスト

本文（BODY）は、あくまで **人間と LLM が読むコンテンツ**の領域として扱う。

- Summary / Details / Acceptance / Inputs / Outputs / Steps …
  → context 生成や search の対象（`tool_source = true`）として使う。
- Traceability Map
  → front matter に書かれた trace/dp/doc を、
  人間・LLM にとって読みやすい形でミラーするビュー。
  **Graph の SSOT ではない。**

この分離により：

- Graph の構造は **front matter からのみ構築**され、
  「本文に trace 情報を書き忘れた／書き足した」ことによる不整合を減らせる。
- 本文は、より自由に／読みやすく構成できる（自然文や図・表などに集中できる）。

##### 4. scope と status の位置づけ

- `scope`

  - Graph の正しさ自体には関与しないが、
    「どの spec を同じバケツに入れるか」という観点で **設計品質・見通しの良さ**に強く効く。
  - iori-spec のコマンド（search / index / context）でも、
    scope を軸に絞り込み・グルーピングできるようにする前提。

- `status`

  - 仕様がどこまでレビューされているかを示すサイン。
  - trace lint の severity（ERROR / WARN / INFO）や CI の閾値を、status に応じて変えるためのフラグとして使う。

##### 5. Tags をあえて入れない理由（v1 時点）

- 軸が増えるほど、LLM とツールの両方が「どのフィールドを見れば何がわかるのか」で迷いやすくなる。
- v1 では、

  - 構造の中核：`id / kind / scope / trace / dp / doc`
  - メタな成熟度：`status`
    に絞り込み、
  - axis / area などの追加軸は **ユースケース（コマンド仕様）が明確になってから** 導入する。

この「front matter に寄せつつも、項目は絞る」方針が、

- iori-spec の思想（仕様＋メタ仕様）と、
- 「LLM にとって扱いやすい SDD」「局所コンテキスト化」のゴール

の両方にフィットする、というのが現時点の設計意図です。

### `H1 タイトル`（COMMON MUST）

- 表示用タイトル
- **「COMMON MUST = core spec に対して」**

  ```markdown
  # {spec_title と同じ or ほぼ同じタイトル}
  ```

### `LLM_BRIEF`（COMMON MUST）

- iori-spec ワークフローの中での役割＋ LLM への指示（kind ごとにほぼ固定）
  - role: このファイルが iori-spec の仕様セットの中で担う役割
  - llm_action: このファイルを渡された LLM に主にしてほしいこと

- `context` コマンドが**最初に読む場所**として必須
- 「このファイルをコンテキストに含める意味があるか？」の判定にも使う
- **「COMMON MUST = core spec に対して」**

  ```markdown
  ## LLM_BRIEF

  - role: このファイルは、LLM×SDD ツール iori-spec のプロダクトビジョン（目指す方向性と設計方針）を定義する SSOT です。
  - llm_action: 仕様修正・新機能追加を行う前に、このビジョンと照らし合わせて、案がビジョンに沿っているかを確認してください。
  ```

### `USAGE`（COMMON MUST）

- 人間＋ LLM のための**この spec の使い方のガイド・参照タイミングのガイド**
- この仕様書を「いつ」「誰が」「どんな場面で」読むか（例：設計レビュー前に読む、実装前に読む等）
- この仕様書をコンテキストとして LLM に渡すときの基本パターン（例: どのセクション／ID を渡すか等）
- 他のどの kind / ディレクトリとセットで見ることが多いか
- **「COMMON MUST = core spec に対して」**

  ```markdown
  ## USAGE

  - 人間・LLM が「このプロダクトは何ができるべきか」を確認するときは、このファイルを参照します。
  - 実装やインターフェイス仕様は `interfaces/`・`data_contracts/` に記載され、本ファイルはそれらの根拠となる要件を定義します。
  - LLM に特定の機能の追加・変更を依頼する場合は、このファイルから該当 REQ-xxx だけを抜き出して渡すことを推奨します。
  ```

### `READ_NEXT`（COMMON MUST）

- このファイルを読んだあとに、どの仕様を・どんな目的で読むと良いかをリスト形式で示す
- `impact` / `context` で「一緒に読む候補ファイル」を提示するために利用
- **“ローカルな小さな地図”**として機能させる
- 各行には読むべきファイル名とあわせて、なぜそれを見るのか（役割）も併記する
- **「COMMON MUST = core spec に対して」**

  ```markdown
  ## READ_NEXT

  - 非機能要件 → `requirements/nonfunctional.md`
- トレースマップ → `artifacts/traceability_map.md`
  - …（3〜5件程度）
  ```

### `1. このドキュメントの役割`（COMMON MUST）

- 「このドキュメントが何の SSOT か」「このドキュメントが何を決めて何を決めないか」を明示
- このファイルで「決めること」と「決めないこと」の境界を明示し、責務の肥大化を防ぐ
- 他の仕様（requirements / architecture / interfaces / data_contracts 等）との役割分担を、人間と LLM の両方に分かりやすく伝える
- `trace` / `impact` で「どの kind / scope を見るべきか」を考えるときの基準になる
- **「COMMON MUST = core spec に対して」**

### `2. 範囲（Scope）と前提`（COMMON MUST）

- この仕様書がカバーする範囲（Scope）と、その前提となる他仕様・外部システムを明示する
- scope（front matter の値）の意味を自然言語で補足し、このファイルの射程を明確にする
- 「このファイルが想定している前提条件（既知の仕様・環境・制約）」を明らかにし、誤読や二重定義を防ぐ
- 「この質問はこのファイルだけで完結しない」ことを LLM が判断しやすくなる
- **「COMMON MUST = core spec に対して」**

### `3. 運用上の目安（LLM / SDD 観点）`（COMMON MUST）

- この仕様書をどのように維持・分割・利用していくかについての「運用ガイドライン」
- 1 ファイルあたりの ID 数の目安／分割方針／LLM に渡す推奨コンテキストなど
- 将来の lint やサジェスト（「このファイルはデカすぎるので分割しませんか？」）にも使える
- **「COMMON MUST = core spec に対して」**

## layer2 section 仕様

### `kind: requirements`（REQ-xxx）

1ファイル = 1 要件（REQ-xxx）を記述する想定。

**推奨セクション構成：**

```markdown
## 4. 要件の概要（Summary）

- この REQ が何を要求しているかを 3行以内で。

## 5. 背景・コンテキスト（任意）

- なぜこの要件が必要か、どのようなユーザストーリー／ユースケースに紐づくか。

## 6. Acceptance Criteria

- この要件が満たされているとみなす条件を箇条書きで。
- 「観測可能な挙動」「検証方法」にフォーカスする。

## 7. 非ゴール / 除外事項（任意）

- この REQ のスコープに含めないこと（誤解しやすい境界）を明示する。
```

- **MUST（v1 想定）**

  - `## 4. 要件の概要（Summary）`
  - `## 6. Acceptance Criteria`

- **SHOULD**

  - `## 5. 背景・コンテキスト`
  - `## 7. 非ゴール / 除外事項`

> trace./dp./doc. との関係：
> REQ 側では、`trace.if` / `trace.data` / `trace.test` によって
> 「この REQ を主に実現・検証している IF / DATA / TEST」を front matter 上で宣言する。

### `kind: interfaces`（IF-xxx）

CLI コマンドや API 等、外部から呼び出されるインターフェイス。

**推奨セクション構成：**

```markdown
## 4. Summary

- この IF が提供する機能を一文で。

## 5. Inputs

- 引数 / パラメータ / 入力ファイルなど。
- 型・必須/任意・デフォルト値・制約などを整理する。

## 6. Outputs

- 標準出力 / 戻り値 / 生成されるファイル / ステータスコードなど。

## 7. Errors（任意）

- 主なエラーケースと挙動（メッセージ、exit code など）。

## 8. Examples（任意）

- よく使う具体例（CLI コマンド例など）。
```

- **MUST**

  - `## 4. Summary`
  - `## 5. Inputs`
  - `## 6. Outputs`

- **SHOULD**

  - `## 7. Errors`
  - `## 8. Examples`

> Graph との関係：
>
> - `trace.req`：この IF が主に満たす REQ-xxx
> - `trace.data`：密接に関わる DATA-xxx
> - `dp.produces` / `dp.consumes`：IF⇄DATA の「生成」「利用」関係
> - `doc.read_next`：一緒に読むとよい REQ / DATA / TEST / 他 IF

### `kind: data_contracts`（DATA-xxx）

バイナリ形式やテーブル定義など、データ構造の仕様。

**推奨セクション構成：**

```markdown
## 4. Summary

- このデータ構造が何のために存在するか。

## 5. Schema

- JSON Schema / テーブル定義 / TypeScript 型など、機械可読な形で構造を定義。

## 6. Constraints（任意）

- 値の制約（範囲 / NOT NULL / 一意制約 / 正規表現など）。

## 7. 利用箇所の概要（任意）

- 主にどの IF / プロセスで利用されるかを文章でまとめる。
```

- **MUST**

  - `## 4. Summary`
  - `## 5. Schema`

- **SHOULD**

  - `## 6. Constraints`
  - `## 7. 利用箇所の概要`

> Graph との関係：
>
> - `trace.req` / `trace.if` / `trace.test`：この DATA と論理的に結びつく要素
> - `dp.produced_by` / `dp.consumes`：どの IF が生成・利用するか
> - `doc.read_next`：関連する IF / architecture 文書 など

### `kind: tests`（TEST-xxx）

受け入れテストや結合テストなど。

**推奨セクション構成：**

```markdown
## 4. Summary

- この TEST が何を検証するか。

## 5. Preconditions（任意）

- 前提条件（環境 / データ状態など）。

## 6. Steps

- 手順（CLI コマンドや操作手順）。

## 7. Expected Results

- 期待される結果（出力、状態変化など）。
```

- **MUST**

  - `## 4. Summary`
  - `## 6. Steps`
  - `## 7. Expected Results`

- **SHOULD**

  - `## 5. Preconditions`

> Graph との関係：
>
> - `trace.req`：この TEST が主に検証する REQ-xxx
> - `trace.if` / `trace.data`：テスト対象の IF / DATA
> - `doc.read_next`：テスト対象 IF / DATA / REQ など

### `kind: dev_tasks`（TASK-...）

実装タスクや作業単位。

**推奨セクション構成：**

```markdown
## 4. Summary

- タスクの一行要約。

## 5. Steps

- 実作業のステップ（PR 単位やチケット単位など）。

## 6. Done Criteria

- このタスクが完了したとみなす条件。
```

- **MUST**

  - `## 4. Summary`
  - `## 5. Steps`
  - `## 6. Done Criteria`

> Graph との関係：
>
> - `trace.req` / `trace.if` / `trace.data` / `trace.test`：この TASK が紐づく対象
> - `doc.read_next`：関連 PR 規約や実装メモなど

### `kind: steering / architecture / reference`

- `steering`：
  - プロダクトビジョン・非ゴール・成功指標など。

- `architecture`：
  - コンポーネント一覧・レイヤー構造・主なデータフローなど。

- `reference`：
  - 用語集・命名規約・iori_spec_guide など。

**最低限の前提：**

- layer1 の共通セクション（LLM_BRIEF〜3.運用上の目安）は必須。
- それ以降はプロジェクトごとにテンプレを決めてよい：

  - 例：`architecture/overview.md`

    - `## 4. コンポーネント一覧`
    - `## 5. レイヤー構造`
    - `## 6. 主なデータフローと依存ルール`

  - 例：`reference/iori_spec_guide.md`

    - `## 4. 仕様の書き方ルール`
    - `## 5. ID / kind / scope の定義`
    - `## 6. テンプレート一覧`

> ここでは iori-spec は「本文構造をスキーマとしてまでは固定しない」が、
> front matter の `Core メタ情報 + Graph 情報` は 1ファイル1ID の前提で揃える。

### `kind: impl_notes`

- 実装メモ・検討ログなど「ゆるい」ノート。
- SSOT としては優先度低めだが、可能なら layer1 の共通セクションを持たせると LLM が扱いやすい。

**推奨：**

- front matter（kind / scope / id / spec_title / status）は付ける（id はメモ単位の ID で OK）。
- 本文のセクション構成は自由（layer3 の世界）とし、layer2 では必須スキーマを課さない。

## TODO

### TODO: Tags / Axis 将来拡張メモ

現時点（v1）では、front matter に `tags` フィールドは定義しない。  
メタ情報は `scope` / `trace` / `dp` / `doc` を中核とし、Tags は将来の拡張候補として扱う。

### TODO-1: v1 における前提の明文化

- [ ] front matter の設計方針として、以下を明記する：
  - `scope` をメイン軸とし、仕様の「属するモジュール／関心領域」の表現に集中させる。
  - `tags` は **現時点では未実装** とし、ツールロジックは一切 `tags` に依存しない。
  - Trace / DP / Doc のグラフ構築は、あくまで `trace.*` / `dp.*` / `doc.*` のみを利用する。

### TODO-2: 将来の `tags` 導入方針（候補A: free-form 方式）

- [ ] 将来 `tags` を導入する際は、まず以下の「最小パターンA」から検討する：
  - `tags` は単純な文字列配列とする：
    - 例: `tags: ["performance", "cli", "LLM"]`
  - 役割：
    - LLM にとってのヒント（検索・要約のキーワード）
    - CLI での軽量フィルタ（例: `iori-spec search --tag performance`）
  - 制約：
    - `scope` の意味役割と **意図的に分離** する（構造・依存の判断は scope と trace/dp/doc が担当）。
    - `tags` は core ロジック（trace lint / impact / context）の前提には使わない。

### TODO-3: 「axis」をどこで表現するかの設計方針

#### **候補A：構造化タグとして表現する（tags.axis / tags.area）**

- [ ] 具体的なユースケースが挙がったときに再検討する：
  - 例: `iori-spec list-reqs --axis performance`
  - 例: `iori-spec search --area cli`
- [ ] 導入する場合は、責務分担を明確にする：
  - `scope` … モジュール・コンポーネント（技術的な位置）
  - `tags.axis` … 性能 / UX / 信頼性などの「品質特性・観点」
  - `tags.area` … ユーザーから見た機能エリア（CLI / Web UI / digits など）
- [ ] schema レベルで定義する：
  - `tags.axis` 候補値（`functional`, `nonfunctional`, `performance`, `ux`, `reliability`, …）
  - `tags.area` 候補値（`cli`, `web-ui`, `digits`, `import-pipeline`, …）
  - lint ルール（不明な axis/area を WARN にするかどうか）

#### **候補B：`scope` の階層として axis を表現する**

- [ ] axis を別フィールドにせず、`scope` を階層化して表現する案も検討する：
  - 例: `scope: functional.requirements`
  - 例: `scope: nonfunctional.performance`
  - 例: `scope: digits.query_engine`
- [ ] この場合のルール案：
  - 最上位のセグメント（例: `functional` / `nonfunctional`）を「axis」とみなす。
  - 2セグメント目以降を「モジュール／レイヤー」とみなす（例: `.requirements`, `.performance`, `.query_engine`）。
- [ ] 将来 `scope` ベースでフィルタする CLI を追加する：
  - 例: `iori-spec search --scope-prefix functional.`  
  - 例: `iori-spec list --scope-prefix nonfunctional.performance`

### TODO-4: 移行パスの検討（将来）

- [ ] 既存の `scope` に「axis 的な意味」が混入している場合の整理方針を決める：
  - パターンA（構造化タグを導入する）の場合：
    - 例: `scope: nonfunctional` を
      - `scope: requirements` ＋ `tags: ["axis:nonfunctional"]` に正規化する、など。
  - パターンB（scope 階層に axis を含める）の場合：
    - 例: `scope: nonfunctional` を
      - `scope: nonfunctional.performance` / `scope: nonfunctional.security` のように細分化する。
- [ ] `tags` / scope 階層導入時は、以下を lint の対象にするか検討する：
  - `scope` と `tags.axis` / `tags.area` の意味が過度に重複していないか（INFO/WARN レベル）。
  - `functional` / `nonfunctional` などの axis が、どこか 1 箇所に一貫して表現されているか。

### TODO-5: ドキュメントへの反映

- [ ] `iori_spec_section_schema_guide.md` に以下の方針を追記する：
  - 「v1 では tags は定義しない。  
     将来導入する場合は free-form tags を基本とし、axis/area 等の構造化情報は  
     ① tags.axis/tags.area として持つ案、  
     ② scope を階層化して表現する案、  
     のいずれか（または両者の組み合わせ）を、その時点のユースケースに応じて再設計する。」
- [ ] `spec_structure_and_traceability.md` 側にも、`scope` をメイン軸とすること、  
  および axis を scope 側で扱うか tags 側で扱うかは将来の検討事項であることを簡潔に記載する。
