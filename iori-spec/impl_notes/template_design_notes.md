# template の設計検討

## YAML front matter

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

※ 配列はすべて「縦に並べるブロックスタイル」を推奨

- **diff** が読みやすい
- LLM に「**この行だけ消して**」と頼みやすい
- **各 ID ごとに**コメントを付けやすい

YAML front matter を共通ヘッダーとしているのは
「チェックする側 / ツール側の都合」ではあるものの、
iori-spec の思想「仕様そのもの ＋ 仕様を健全に保つ・誘導するためのメタ仕様」に基づいて、
ミニマムな schema で最大限機能を提供するため。

- 人間/LLM が読むときのフィルタ：「functional だけ見たい」「cli 周りだけ見たい」
- iori-spec の出力でのグルーピング：index のときに scope カラムでグループにまとまっていると嬉しい
- 将来的には lint / 一貫性チェック：scope: functional なのに明らかに impl_notes っぽい内容 → warning

逆に言うと、

- impact グラフや REQ↔IF↔DATA の正しさにとっては、scope は本質的ではない
- scope は「設計品質・見通しの良さ」を上げるメタ情報であって、SSOT の中核ではない

### front matter の仕様案

- front matter は **最小限の 4 項目だけ** にする
  - `kind`（ツールが扱い方を決めるキー）→ グローバル enum
  - `scope`（プロジェクトの分類軸）→ プロジェクト enum＋自由
  - `spec_title`（人間と LLM に見せるタイトル）
  - `status`（draft / review / stable / deprecated）

これくらいであれば、

- 「仕様書を書いている感」はそんなに損なわず、
- iori-spec 側も **適度に型情報を確保** できる、というバランスになるはず

- `kind` は iori-spec 側で完全列挙（ハードコード or config）
  - 「iori-spec がファイルをどう扱うか」に直結するので、グローバル enum にしてしまって良い

- `scope` は「プロジェクトごとに列挙定義できる」ようにする
  - 例：docs/reference/scope_taxonomy.yaml や iori-spec.config.yaml に定義
  - iori-spec は その一覧を**推奨値**として扱う
  - 一覧にない scope が来たら：
    - v1 では warning（lint で出す）にとどめ、即エラーにはしない（実験的な scope も許容）
  - scope の粒度は「トップレベルは enum、サブパスは自由」
    - 例

    ```yaml
        # docs/reference/iori_spec_config.yaml

        kinds:
        - steering
        - requirements
        - architecture
        - interface
        - data_contract
        - test
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

    ```yaml
        # front matter 側
        scopes: functional

        scopes: cli.index
        
        scopes: builder.pipeline
    ```

    - iori-spec は scope の**先頭トークン（. まで）**を enum チェック
      - cli.index → cli が定義済みなら OK
      - それ以降はプロジェクト/人間側の自由分類

    こうすると、

    - 「大枠としての scope 軸」は lint できる
    - 細かい分類（cli.index / cli.trace …）はプロジェクトローカルで勝手に増やせる
  
- ID 配列 の記法はブロックスタイルの縦並びとする
  - 追加・削除・入れ替えが**行単位の diff**になるので、diff / レビューが圧倒的に読みやすい
  - **行単位の操作**になるのでフォーマット事故が起きづらく、LLM に編集させるときに圧倒的に安全
  - 1行 ID であれば、コメントを ID ごとに付けられる

### front matter 側の使い方

```yaml
---
kind: requirements       # → kinds enum でバリデート
scope: cli.index         # → 先頭の "cli" を scopes enum でバリデート
spec_title: "機能要件（CLI）"
status: draft
---
```

## 2. ファイル単位のルール（front matter）

### 2.1 必須の front matter

docs/ 以下の「仕様書」と見なされる Markdown ファイルは、次の 4 つのキーを持つ YAML front matter を **必須** とする：

```yaml
---
kind: <必須・列挙型>
scope: <必須・文字列>
spec_title: "<必須・人間向けタイトル>"
status: <必須・列挙型>
---
```

- `kind`
  - そのファイルが「どの種別の仕様か」を表す。
  - iori-spec がファイルの扱い方を決めるための **型情報**（グローバル enum）。
- `scope`

  - そのファイルが「どの領域・テーマの仕様か」を表す。
  - プロジェクトごとに定義可能な **分類ラベル**（後述 2.4）。
- `spec_title`

  - 人間と LLM に見せる正式タイトル。`index` 出力などにそのまま使う。
- `status`

  - 仕様書のライフサイクル状態。lint やフィルタで利用する。

### 2.2 kind の値と意味

`kind` は iori-spec 側で列挙される **グローバルな種別** とし、プロジェクトごとに意味が変わらないことを前提とする。

代表的な値：

- `steering`

  - プロダクトビジョン・方向性・スコープ・非ゴールなど（例: `steering/product.md`）
- `requirements`

  - 機能要件・非機能要件・トレースマップなど（REQ-xxx を含む）
- `architecture`

  - コンポーネント構成・レイヤー構造・データフローなど
- `interface`

  - 外部に公開するインターフェイス仕様（IF-xxx を含む）
- `data_contract`

  - データ構造・スキーマの契約（DATA-xxx を含む）
- `test`

  - テスト観点・テストケース・受け入れ条件（TEST-xxx を含む）
- `reference`

  - 用語集・命名規約・本 iori_spec_guide 自体などのリファレンス
- `dev_tasks`

  - 実装タスク・TODO（TASK-xxx を含む）
- `impl_notes`

  - 実装メモ・検討ログなど（自由形式）。

    - ここに書かれた内容は iori-spec にとって **参照値は低い** とみなされる。

**備考**

- 実際に使う `kind` の一覧は、`reference/iori_spec_config.yaml` の `kinds:` セクションに明示する。
- iori-spec は `kind` がこの一覧に含まれないファイルを見つけた場合、lint 時に warning を出してもよい。

### 2.3 status の値

`status` は仕様書の成熟状態を表す。代表的な値：

- `draft`

  - たたき台。内容の変更が頻繁に発生する前提。
- `review`

  - 一通り書き終わり、レビュー待ちの状態。
- `stable`

  - 合意済み。原則として大きな変更を行わない。
- `deprecated`

  - 廃止予定・参照のみ。新しい仕様への移行を前提とする。

**運用上の目安**

- LLM や新規参加者には、まず `stable` / `review` を中心に見せる。
- `draft` の仕様は「思考の途中」である可能性が高いため、
  LLM に渡すときは HOOKS などで注意書きを添える。

### 2.4 scope の意味と設計ルール（※このドキュメントの主題）

#### 2.4.1 scope が表すもの

`scope` は、

> 「この仕様書は、**プロジェクト全体のうち、どの領域の話をしているか**」

を表す **分類ラベル** である。

- `kind` が「仕様の型」（requirements / interface / data_contract …）であるのに対して、
- `scope` は「その型の中で、どの領域について述べているか」という **縦切りの軸** を表す。

例：

- `kind: requirements`, `scope: functional`
  → 機能要件の仕様書
- `kind: requirements`, `scope: nonfunctional`
  → 非機能要件の仕様書
- `kind: interface`, `scope: cli.index`
  → CLI のうち、index サブコマンド領域のインターフェイス仕様
- `kind: data_contract`, `scope: cli.index`
  → 上記 IF に対応する JSON 出力スキーマ

#### 2.4.2 scope の形式

`scope` は **必ず 1 つの文字列** とし、`.` 区切りによる階層表現を許可する：

```yaml
scope: functional
scope: nonfunctional
scope: cli
scope: cli.index
scope: builder.pipeline
scope: docs
```

- **先頭のトークン**（`.` より前の部分）を「トップレベル scope」と呼ぶ。

  - 例: `cli.index` → トップレベル scope は `cli`
- トップレベル scope は、プロジェクトごとに定義する **列挙型** とする（後述 2.4.3）。
- `.` 以降は、プロジェクトや著者の裁量で自由に分割してよい。

#### 2.4.3 scope の列挙と iori-spec のバリデーション

各プロジェクトは、`reference/iori_spec_config.yaml` に
**使用を許可するトップレベル scope の一覧** を定義する：

```yaml
# reference/iori_spec_config.yaml（例）

kinds:
  - steering
  - requirements
  - architecture
  - interface
  - data_contract
  - test
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

- iori-spec は、ファイルの `scope` を解釈するとき、
  **先頭のトークン** を取り出し、`scopes:` の一覧に含まれるかどうかをチェックする。

  - 例: `scope: cli.index` → 先頭トークンは `cli` → `scopes:` にあれば OK
  - 例: `scope: weird.experimental` → 先頭トークンは `weird` →一覧にない場合は **未知の scope** とみなす
- 未知の scope は、**lint 時に warning を出すが、即エラーにはしない**（v1 の方針）。

  - 実験的な分類や移行中のラベルを一時的に許容するため。

この設計により：

- **ツール側**はトップレベル scope を enum として扱える（フィルタ・グルーピング・lint がしやすい）。
- **プロジェクト側**は、`cli.index`, `cli.trace`, `builder.pipeline` など、
  より細かい階層表現を自由に導入できる。

#### 2.4.4 scope の決め方と運用ガイド

- 1 ファイルにつき scope は **1 つ** とする。

  - 「この仕様書の **主役となる領域**」を選ぶイメージ。
- クロスカットする内容（例: `cli` と `builder` 両方にまたがる話）がある場合：

  - どちらか一方を scope として採用し、もう一方は本文や ID タグ（`- [area] ...`）で表現する。
- **推奨例（iori-spec 自身のプロジェクト）**

  - 機能要件 → `scope: functional`
  - 非機能要件 → `scope: nonfunctional`
  - トレースマップ → `scope: traceability`
  - CLI 周りの IF / DATA / TEST → `scope: cli` または `cli.<subarea>`

    - index サブコマンド → `cli.index`
    - trace サブコマンド → `cli.trace`
  - ビルドパイプライン → `scope: builder` または `builder.pipeline`
  - 仕様の書き方・用語集 → `scope: docs`

#### 2.4.5 scope と他のメタ情報の違い

- `kind`（front matter）
  → ファイルの「型」を表す（requirements / interface / …）。
  iori-spec の解析・コマンドの挙動に直接関わる。
- `scope`（front matter）
  → ファイル全体が扱う「領域」を表す。
  フィルタ・グルーピング・lint の対象となる。
- `- [area] ...`（ID ブロック直下のタグ行）
  → 個々の REQ/IF/DATA/TEST についての **より細かい分類**。
  同じファイル内で複数の area を並立させてもよい。

**運用上の目安**

- 「このファイルを 1 文で説明するとしたら？」の答えが `scope`。
- 「この REQ/IF はもう一段細かく分類するとしたら？」の答えが `area` タグ。

---

## セクション

整理すると、セクションには「共通で意味を固定したいもの」と「kind / ファイルごとに変わるもの」の2〜3階層があります。

### レイヤー1：**全 spec 共通で意味を固定するセクション**

ここは **どのファイルでも“同じ意味”** を持つ前提で設計してます。

- `## LLM_BRIEF`
- `## USAGE`
- `## READ_NEXT`
- `## 1. このドキュメントの役割`
- `## 2. 範囲（Scope）と前提`
- `## 3. 運用上の目安（LLM / SDD 観点）`

ここは **iori-spec 側が構造的に理解する前提**なので、意味（役割）は固定。
中身の具体的な文章はファイルごとに違うけど、「何を書く場所か」は共通です。

### レイヤー2：**kind ごとの“型”として揃えたいセクション**

ここから先は **kind によって違う**けど、
「同じ kind ではなるべくパターンを揃えたい」層。

例：

- `requirements/functional.md`

  - 4. 要件の分類
  - 5. 機能要件（REQ-xxx）
- `requirements/nonfunctional.md`

  - 4. 非機能要件の分類
  - 5. 非機能要件（REQ-2xx）
- `architecture/overview.md`

  - 4. コンポーネント一覧
  - 5. レイヤー構造
  - 6. データフローと依存ルール
- `interfaces/IF-001_*.md`

  - IF-001 見出し
  - Summary / 役割
  - 入力 / 出力 / エラー
  - Examples

この辺は **“requirements のテンプレ” “architecture のテンプレ”** として iori_spec_guide に書いておく感じ。
でも「全 spec 共通」ではなく、kind ごとに違って OK という位置づけです。

---

### レイヤー3：**ファイル固有のセクション**

さらにその下は、**ファイルごとに自由**で大丈夫な層。

例：

- `steering/product.md` だけが持つ

  - 4. コアとなる2つの目的（軸① / 軸②）
  - 5. 想定ユーザと主要ユースケース
- ある大きめの architecture ファイルだけが持つ

  - 「今後の拡張方針」
- 特定プロジェクトだけの

  - 「XXX ドメイン固有ルール」 等

ここは iori-spec は“中身を構造としては解釈しない”想定で、
LLM にとっても「読めたら嬉しいけど、必須スキーマではない」として扱う感じ。

---

## まとめると

- **今いじってきた 6 つのセクション**
  → どの spec ファイルにも共通の意味を持たせたい「コア骨格」

- それ以外の本文セクション
  → 基本は **kind ごとのテンプレ**（requirements / architecture / interface …）で揃える
  　　＋ 各ファイル固有の構成を足していく

なので、あなたの言っている

> 他のセクションについてはファイルごとに異なるって感じでしょうか

に対しては、

- 「**意味を固定する必要があるのは今決めたところまで**」
- 「それ以外は **kind 単位でのパターンは持ちつつ、ファイルごとに増減してOK**」

くらいのニュアンスが一番近いです。

もし次に進めるなら、

- `requirements/functional.md` 用の「4. / 5. の正式テンプレ」
- `steering/product.md` 用の「4. 以降の正式テンプレ」

を iori_spec_guide 用テキストとして固める、って流れにできます。

## iori-spec の機能を実装するために各ドキュメントが持つべき情報

- **コマンド実装（index / trace / impact / context / lint）のために必要な最低限（MUST）**
- **設計品質のために極力入れてほしい（SHOULD）**
- 対象は **core な kind**：`steering / requirements / architecture / interface / data_contract / test / dev_tasks / reference`
  （`impl_notes` は「道具箱」扱いで、厳密な制約なしでも OK にしておく想定）

### 0. core spec ファイル共通の要素

#### MUST（iori-spec の機能のために必須）

1. **YAML Front Matter**

    - `kind`：index / trace での分類に必須
    - `scope`：仕様検索・フィルタ・コンテキスト抽出で利用
    - `spec_title`：`index` 出力や UI で表示する名称
    - `status`：lint や「古い spec を除外する」フィルタで利用

2. **H1 タイトル**

    ```markdown
    # {spec_title と同じ or ほぼ同じタイトル}
    ```

3. **`## LLM_BRIEF` セクション**

    ```markdown
    ## LLM_BRIEF

    - role: このファイルが iori-spec の仕様セットの中で担う役割
    - llm_action: このファイルを渡された LLM に主にしてほしいこと
    ```

    - `context` コマンドが**最初に読む場所**として必須
    - 「このファイルをコンテキストに含める意味があるか？」の判定にも使う

4. **`## READ_NEXT` セクション**

    ```markdown
    ## READ_NEXT

    - 非機能要件 → `requirements/nonfunctional.md`
    - トレースマップ → `artifacts/traceability_map.md`
    - …（3〜5件程度）
    ```

    - `impact` / `context` で「一緒に読む候補ファイル」を提示するために利用
    - **“ローカルな小さな地図”**として機能させる

5. **`## 1. このドキュメントの役割`**

   - 「このファイルが何の正本か」「何を決めて何を決めないか」を明示
   - trace / impact で「どの kind/scope を見るべきか」を考えるときの基準になる

6. **`## 2. 範囲（Scope）と前提`**

   - `scope` の具体的な意味、前提にする他 spec / 外部システム、Out of Scope を記述
   - 「この質問はこのファイルだけで完結しない」ことを LLM が判断しやすくなる

7. **`## 3. 運用上の目安（LLM / SDD 観点）`**

   - 1 ファイルあたりの ID 数の目安／分割方針／LLM に渡す推奨コンテキストなど
   - 将来の lint やサジェスト（「このファイルはデカすぎるので分割しませんか？」）にも使える

### 1. kind 別の「必須セクション」：大枠

ここからは kind ごとに「**MUST（ツール上必要）** / **SHOULD（構造健全性のため強く推奨）**」で整理します。

#### 1-1. `kind: steering`（例：`steering/product.md`）

##### **MUST**

- 上記の共通 7 要素
- 追加で、本文側に次のどれか（名前は多少変えても良いが、意味は保つ）：

  - `## 4. プロダクト概要`
    - そのプロダクトが何をするものか、一言説明

  - `## 5. 解決したい課題と提供価値`（名前はおまかせ）
    - プロダクトが解決する問題と、ユーザへの価値

  - `## 6. 想定ユーザと主要ユースケース`
    - どんな人が、どんなときに使うか

　※ iori-spec ではここに「軸① / 軸②」の話が入る想定（ただしそれは中身の話であって、スキーマとして強制はしない）

##### **SHOULD**

- `## スコープと非ゴール（Non-goals）`
- `## 成功指標（Success Criteria）`

→ steering は **ID ブロックを持たない**ので、ツール視点では「ファイル単位で読めればいい」前提です。

#### 1-2. `kind: requirements`（`functional.md` / `nonfunctional.md` など）

requirements 系は **ID ブロック（REQ-xxx）を持つ「ID キャリア」**なので、
**ファイルレベルの必須＋ID ブロックレベルの必須** を分けて定義します。

##### ファイルレベルの MUST

- 共通 7 要素
- `## 4. 要件の分類`（名前は変えてもよいが、「どの領域にどんな REQ があるか」の概要セクションは 1 つ用意）
  → ここは **SHOULD 寄り**でもよいが、「仕様の地図」としてかなり効くのでほぼ必須扱い推奨
- `## 5. 機能要件（REQ-xxx）` もしくはそれに相当する「REQ ブロック一覧セクション」

##### REQ ブロック（ID レベル）の MUST

各 REQ は、以下の形を必須とするのがよさそうです：

```markdown
## REQ-XXX: 要件のタイトル

MACHINE_TAGS:
- [kind] REQ
- [level] MUST        # MUST / SHOULD / MAY / INFO
- [area] cli.index    # 領域（cli.index / cli.trace / builder.pipeline 等）
- [rel-IF] IF-001     # 関連する IF（複数可）（任意）
- [rel-DATA] DATA-001 # 関連する DATA（複数可）（任意）
- [rel-TEST] TEST-001 # 関連する TEST（複数可）（任意）
- [rel-TASK] TASK-001-01 # 実装タスク（任意）

### Summary

- 3行以内で、この REQ が何を要求しているか

### Details  （任意）

- 前提・補足・境界条件など

### Acceptance Criteria

- この REQ が満たされているとみなす条件を箇条書きで
```

REQ ブロック内の**MUST 要素：**

- H2 見出し：`## REQ-XXX: ...`（`REQ-` プレフィックス＋数字）
  → `index` / `trace` / `impact` の核
- `MACHINE_TAGS:` ブロック（最低限 `[kind]`, `[area]`、トレース用として `[rel-IF]` 等は空でもよい）
- `### Summary`
- `### Acceptance Criteria`

REQ ブロック内の**SHOULD 要素：**

- `[level]`（MUST / SHOULD / MAY…）
- `[rel-IF]`, `[rel-DATA]`, `[rel-TEST]`, `[rel-TASK]` などのトレース情報
- `### Details`

#### 1-3. `kind: interface`（`interfaces/IF-XXX_*.md`）

こちらも **ID キャリア（IF-xxx）**。

##### ファイルレベル MUST

- 共通 7 要素

##### IF ブロック MUST

```markdown
## IF-XXX: インターフェイス名

MACHINE_TAGS:
- [kind] IF
- [area] cli.index       # or api.backend 等
- [rel-REQ] REQ-101      # この IF が主に満たす REQ
- [rel-DATA] DATA-001    # 入出力で使う DATA
- [rel-TEST] TEST-201    # 主にこの IF を検証する TEST

### Summary

- この IF が提供する機能の一行要約

### Inputs

- 引数 / パラメータ / 入力ファイルなど

### Outputs

- 標準出力 / 戻り値 / 生成されるファイルなど

### Errors

- 主なエラーケースと振る舞い（CLI の exit code など）

### Examples  （SHOULD）

- 典型的な使用例
```

IF ブロック内の**MUST：**

- `## IF-XXX: ...`
- `MACHINE_TAGS:`（最低限 `[kind] IF`, `[area]`, `[rel-REQ]`）
- `### Summary`
- `### Inputs`
- `### Outputs`

IF ブロック内の**SHOULD：**

- `### Errors`
- `### Examples`

#### 1-4. `kind: data_contract`（`data_contracts/DATA-XXX_*.md`）

##### ファイルレベル MUST

- 共通 7 要素

##### DATA ブロック MUST

````markdown
## DATA-XXX: データ構造名

MACHINE_TAGS:
- [kind] DATA
- [area] builder.pipeline   # どこで使われるデータか
- [rel-REQ] REQ-201         # このデータと強く結びつく要件
- [rel-IF] IF-010           # このデータをやりとりする IF
- [rel-TEST] TEST-301       # このデータ構造を検証するテスト

### Summary

- このデータ構造が何のために存在するかの要約

### Schema

// JSON Schema, TypeScript 型定義、テーブル定義など

### Constraints  （SHOULD）

- バリデーションルール、制約（NULL 許可 / 範囲 / ユニーク制約など）

````

DATA ブロック内の**MUST：**

- `## DATA-XXX: ...`
- `MACHINE_TAGS`（最低限 `[kind] DATA`）
- `### Summary`
- `### Schema`（何らかの構造定義）

DATA ブロック内の**SHOULD：**

- `### Constraints`

#### 1-5. `kind: test`（`tests/TEST-XXX_*.md` 的な想定）

##### ファイルレベル MUST

- 共通 7 要素

##### TEST ブロック MUST

```markdown
## TEST-XXX: テストケース名

MACHINE_TAGS:
- [kind] TEST
- [area] cli.index
- [rel-REQ] REQ-101
- [rel-IF] IF-001
- [rel-DATA] DATA-001

### Summary

- このテストが何を検証するか

### Preconditions  （任意）

- 前提条件（環境・データ状態など）

### Steps

- 手順（CLI 実行コマンド等）

### Expected Results

- 期待される結果（出力・状態変化など）
````

TEST ブロック内の**MUST：**

- `## TEST-XXX: ...`
- `MACHINE_TAGS`
- `### Summary`
- `### Steps`
- `### Expected Results`

TEST ブロック内の**SHOULD：**

- `### Preconditions`

#### 1-6. `kind: dev_tasks`（タスク分解用：`TASK-XXX-YY`）

##### ファイルレベル MUST

- 共通 7 要素

##### TASK ブロック MUST

```markdown
## TASK-REQ-101-01: タスク名

MACHINE_TAGS:
- [kind] TASK
- [area] cli.index
- [rel-REQ] REQ-101
- [rel-IF] IF-001
- [rel-DATA] DATA-001

### Summary

- タスクの一行要約

### Steps

- 実作業の手順（PR 単位など）

### Done Criteria

- このタスクが完了したとみなす条件
```

TASK ブロック内の**MUST：**

- `## TASK-...` 見出し
- `MACHINE_TAGS`
- `### Summary`
- `### Steps`
- `### Done Criteria`

#### 1-7. `kind: architecture` / `kind: reference`

ここは **ID ブロックを持たないファイルも多い**想定なので、

- 共通 7 要素 **だけを MUST**
- それ以外のセクション構造は **kind ごとのテンプレで揃える（SHOULD）**

例：`architecture/overview.md`

- `## 4. コンポーネント一覧`
- `## 5. レイヤー構造`
- `## 6. 主なデータフローと依存ルール`

例：`reference/iori_spec_guide.md`

- `## 4. 仕様の書き方ルール`
- `## 5. ID / kind / scope の定義`
- `## 6. テンプレート一覧`

→ ここは iori-spec の機能的には「**doc 単位で読めればよい**」ので、
　ツール観点の MUST は「front matter＋共通 7 要素」までにとどめるのがバランス良さそうです。

#### 1-8. `kind: impl_notes`

- ツール観点では **必須セクションなし**でも良い（`kind: impl_notes` というだけで“ゆるいメモ”扱いにできる）
- ただし最低限、front matter + H1 はあった方が index しやすいので **MUST 推奨**
- LLM_BRIEF / USAGE 等は任意（書いてあったら読みに行く、くらいの扱い）

### MUST / SHOULD まとめ

- **全 core spec ファイル共通の MUST：**

  - YAML front matter（kind / scope / spec_title / status）
  - H1 タイトル
  - `## LLM_BRIEF`
  - `## READ_NEXT`
  - `## 1. このドキュメントの役割`
  - `## 2. 範囲（Scope）と前提`
  - `## 3. 運用上の目安（LLM / SDD 観点)`
- **ID を持つ kind（requirements / interface / data_contract / test / dev_tasks）は、各 ID ブロックに：**

  - `## ID-XXX: タイトル`
  - `MACHINE_TAGS` ブロック
  - `### Summary`
  - その種別ごとの必須サブセクション（Acceptance Criteria / Inputs / Outputs / Steps など）

これを `reference/iori_spec_guide.md` に「MUST / SHOULD」付きで書いておけば、
iori-spec の `index / trace / impact / context / lint` が前提とする“仕様スキーマ”がほぼ固まります。

`### core spec 共通の必須セクション`

1. YAML front matter
   - `kind / scope / spec_title / status`
2. H1 タイトル
3. `## LLM_BRIEF`
   - role / llm_action（短く）
4. `## USAGE`
5. `## READ_NEXT`
6. `## 1. このドキュメントの役割`
7. `## 2. 範囲（Scope）と前提`
8. `## 3. 運用上の目安（LLM / SDD 観点）`

`### kind 別の MUST / SHOULD セクション`

1. 上記の COMMON MUST 8項目
2. H1 タイトル
3. `## LLM_BRIEF`
   - role / llm_action（短く）
4. `## USAGE`
5. `## READ_NEXT`
6. `## 1. このドキュメントの役割`
7. `## 2. 範囲（Scope）と前提`
8. `## 3. 運用上の目安（LLM / SDD 観点）`

いい整理ポイントなので、一回きれいに「一覧表モード」にしますね。

まずは **kind ごとの ID 周りの性質**、次に **セクション一覧（MUST/SHOULD）** の順で出します。

---

## 1. Kind ごとの ID 性質まとめ

「is IDキャリア / has File単位ID / has Block単位ID」をざっくり俯瞰するテーブルです。

| Kind          | 説明                    | is IDキャリア | has File単位ID | has Block単位ID |
| ------------- | --------------------- | --------- | ------------ | ------------- |
| steering      | プロダクトビジョン・方針など        | ❌         | ❌            | ❌             |
| requirements  | 機能・非機能要件（REQ-xxx）     | ✅         | ❌            | ✅             |
| architecture  | コンポーネント構成・レイヤー等       | ❌         | ❌            | ❌             |
| interface     | IF-xxx（CLI/API などのIF） | ✅         | ❌            | ✅             |
| data_contract | DATA-xxx（スキーマ・テーブル等）  | ✅         | ❌            | ✅             |
| test          | TEST-xxx（テスト仕様）       | ✅         | ❌            | ✅             |
| dev_tasks     | TASK-xxx-yy（開発タスク）    | ✅         | ❌            | ✅             |
| reference     | iori_spec_guide 等のリファレンス    | ❌         | ❌            | ❌             |
| impl_notes    | 実装メモ・下書き              | ❌         | ❌            | ❌             |

- **IDキャリア** = 「REQ / IF / DATA / TEST / TASK などの *IDブロック* が主役の kind」
- 現時点では、**どの kind もファイル自体に ID は振らない前提**（= `has File単位ID` はすべて ❌）

---

いい整理ポイント 👍
じゃあ「ツールがそこを**情報源として見るかどうか**」も含めて、全体をもう一段スッキリ整理し直します。

---

## 前提：tool_source 列の意味

今回の `tool_source` はこう定義します：

> **tool_source = ○**
> iori-spec のツールが、そのセクションを
>
> - 構造的にパースしたり
> - context 抽出の起点として“明示的に”読む
>   ことを前提としている。

> **tool_source = ×**
>
> - 主に人間用の説明
> - LLM に context を渡すときは「おまけ」で付く可能性はあるが、
>   iori-spec のロジックはそのセクションを前提にしない。

※ 将来の拡張で △（ヒント程度）を入れてもいいけど、いったん **○/× の二値**で整理します。

※ △ は「文章として ID が出てくる可能性はあるが、**構造的な ID 参照源としては期待しない**」という意味で付けています

---

## A. core spec 共通セクション

core spec（steering / requirements / architecture / interface / data_contract / test / dev_tasks / reference）に共通の **Schema-MUST** から。

| セクション / 要素名                                     | IDを持つ | IDを参照し得る    | tool_source | 備考                                                        |
| ----------------------------------------------- | ----- | ----------- | ----------- | --------------------------------------------------------- |
| YAML front matter（kind/scope/spec_title/status） | ×     | ×           | ○           | kind/scope/status に基づいて index / trace / context のフィルタを行う。 |
| H1 タイトル（`# {spec_title}`）                       | ×     | ×           | ×           | 表示用。front matter の spec_title とほぼ重複なのでツールからは見ない想定。        |
| `## LLM_BRIEF`                                  | ×     | ×           | ○           | context 生成の最初の入口。role / llm_action を読む。                   |
| `## USAGE`                                      | ×     | △           | ×           | 人間向けの「使い方ガイド」。ツールは必須ロジックに使わない。                            |
| `## READ_NEXT`                                  | ×     | △（ファイルパスなど） | ○           | 関連 spec の候補リストとしてパースし、context/impact で「一緒に読む」候補に使う。       |
| `## 1. このドキュメントの役割`                             | ×     | ×           | ×           | 役割宣言。LLM には有用だが、ツールロジックは直接依存しない。                          |
| `## 2. 範囲（Scope）と前提`                            | ×     | △           | ×           | scope の自然文補足。構造的な scope は front matter 側で持つ。              |
| `## 3. 運用上の目安（LLM / SDD 観点）`                    | ×     | ×           | ×           | lint のヒントにはなるが、初期バージョンではパース対象にしない前提。                      |

---

## B. IDキャリア kind の ID ブロック内セクション

ここからは **ID を持つブロック**（REQ / IF / DATA / TEST / TASK）の中身について。

### B-1. requirements（REQ ブロック）

| セクション / ブロック名                | IDを持つ | IDを参照し得る | tool_source | 備考                                                                           |
| ---------------------------- | ----- | -------- | ----------- | ---------------------------------------------------------------------------- |
| REQ ブロック全体（`## REQ-XXX: …`〜） | ○     | ○        | ○           | context 抽出単位として“丸ごと”対象。                                                      |
| `## REQ-XXX: タイトル`           | ○     | ×        | ○           | ID 定義の起点としてパース。                                                              |
| `MACHINE_TAGS`               | ×     | ○        | ○           | [kind]/[area]/[rel-IF]/[rel-DATA]/[rel-TEST]/[rel-TASK] など、**トレースグラフの中核情報**。 |
| `### Summary`                | ×     | ×        | ○           | context 生成時に REQ 説明として必ず含める想定。                                               |
| `### Details`                | ×     | ×        | ○           | あれば context に含めるが、グラフ構築には使わない。                                               |
| `### Acceptance Criteria`    | ×     | ×        | ○           | テスト生成や DONE 判定のための重要情報として context に含める。                                      |

---

### B-2. interface（IF ブロック）

| セクション / ブロック名              | IDを持つ | IDを参照し得る | tool_source | 備考                                            |
| -------------------------- | ----- | -------- | ----------- | --------------------------------------------- |
| IF ブロック全体（`## IF-XXX: …`〜） | ○     | ○        | ○           | context 単位。                                   |
| `## IF-XXX: インターフェイス名`     | ○     | ×        | ○           | IF ID の定義。                                    |
| `MACHINE_TAGS`             | ×     | ○        | ○           | [rel-REQ] / [rel-DATA] / [rel-TEST] 等の紐づけに使う。 |
| `### Summary`              | ×     | ×        | ○           | IF の概要として context に必ず含める。                     |
| `### Inputs`               | ×     | △        | ○           | 入力仕様（DATA-XXX 名などが出ても、構造参照は MACHINE_TAGS 側）。  |
| `### Outputs`              | ×     | △        | ○           | 出力仕様。                                         |
| `### Errors`（SHOULD）       | ×     | ×        | ○           | エラー振る舞いの説明として context に含めるが、グラフ構築には使わない。      |
| `### Examples`（SHOULD）     | ×     | ×        | ○           | 例示として context に含める。                           |

---

### B-3. data_contract（DATA ブロック）

| セクション / ブロック名             | IDを持つ | IDを参照し得る | tool_source | 備考                                          |
| ------------------------- | ----- | -------- | ----------- | ------------------------------------------- |
| DATA ブロック全体               | ○     | ○        | ○           | context 単位。                                 |
| `## DATA-XXX: データ構造名`     | ○     | ×        | ○           | DATA ID の定義。                                |
| `MACHINE_TAGS`            | ×     | ○        | ○           | どの REQ/IF/TEST と結びつくかのトレース情報。               |
| `### Summary`             | ×     | ×        | ○           | データの役割説明として context に含める。                   |
| `### Schema`              | ×     | △        | ○           | 型定義／テーブル定義。ツールは「このセクション丸ごとを context に渡す」想定。 |
| `### Constraints`（SHOULD） | ×     | ×        | ○           | バリデーションや制約の詳細として context に含める。              |

---

### B-4. test（TEST ブロック）

| セクション / ブロック名               | IDを持つ | IDを参照し得る | tool_source | 備考                                             |
| --------------------------- | ----- | -------- | ----------- | ---------------------------------------------- |
| TEST ブロック全体                 | ○     | ○        | ○           | context 単位。                                    |
| `## TEST-XXX: テストケース名`      | ○     | ×        | ○           | TEST ID の定義。                                   |
| `MACHINE_TAGS`              | ×     | ○        | ○           | どの REQ/IF/DATA を検証するかをトレースする。                  |
| `### Summary`               | ×     | ×        | ○           | テストの目的を説明。                                     |
| `### Preconditions`（SHOULD） | ×     | △        | ○           | 前提条件。context には含めるが、ID グラフ構築には使わない。            |
| `### Steps`                 | ×     | △        | ○           | 手順。IF-XXX などが自然文に出てきても、構造参照は MACHINE_TAGS が正本。 |
| `### Expected Results`      | ×     | ×        | ○           | 期待結果を context に含める。                            |

---

### B-5. dev_tasks（TASK ブロック）

| セクション / ブロック名       | IDを持つ | IDを参照し得る | tool_source | 備考                               |
| ------------------- | ----- | -------- | ----------- | -------------------------------- |
| TASK ブロック全体         | ○     | ○        | ○           | context 単位。                      |
| `## TASK-…: タスク名`   | ○     | ×        | ○           | TASK ID の定義。                     |
| `MACHINE_TAGS`      | ×     | ○        | ○           | どの REQ/IF/DATA/TEST に紐づくタスクかを示す。 |
| `### Summary`       | ×     | ×        | ○           | タスク概要として context に含める。           |
| `### Steps`         | ×     | △        | ○           | 実作業の手順として context に含める。          |
| `### Done Criteria` | ×     | △        | ○           | 完了条件。context に含める。               |

---

## C. steering / architecture / reference / impl_notes

これらは **ID キャリアではない**ので、「IDを持つ」はすべて × です。

### C-1. steering / architecture / reference（core spec 扱い）

- 共通 8 セクション（front matter〜3.運用上の目安）は **A セクションの表の通り**。
- それ以外の「コンポーネント一覧」や「成功指標」などは：

| Kind         | セクション例                   | IDを持つ | IDを参照し得る | tool_source | 備考                                            |
| ------------ | ------------------------ | ----- | -------- | ----------- | --------------------------------------------- |
| steering     | プロダクト概要 / 課題と価値 / ユーザ像など | ×     | ×〜△      | ×           | ツールは「全文 context として投げたいとき」には読むが、構造パースの対象ではない。 |
| architecture | コンポーネント一覧 / レイヤー構造 / フロー | ×     | △        | ×           | 将来的なアーキテクチャ lint の候補だが、現段階ではツール必須情報ではない。      |
| reference    | ID ルール / テンプレ一覧など        | ×     | △        | ×           | 人間・LLM向けのリファレンス。ツールロジックは固定で持つ想定。              |

### C-2. impl_notes

| Kind       | セクション例    | IDを持つ | IDを参照し得る | tool_source | 備考                                           |
| ---------- | --------- | ----- | -------- | ----------- | -------------------------------------------- |
| impl_notes | 任意のメモ・下書き | ×     | ×〜△      | ×           | デフォルトでは iori-spec の index/trace/context 対象外。 |

---

## ざっくりまとめ

- **構造的にツールの情報収集源になるセクション（tool_source = ○）：**

  - front matter
  - `LLM_BRIEF`（ファイルレベルの役割＆LLMのすべきこと）
  - `READ_NEXT`（関連 spec の手がかり）
  - 各 ID ブロックの

    - 見出し（`## REQ-XXX` など）
    - `MACHINE_TAGS`
    - その ID にぶら下がる小見出し群（Summary / Acceptance / Inputs / Outputs / Steps…）
      → これらは「その ID の context を構成するテキスト」として丸ごと拾う

- **主に人間・LLM向けの“読み物”だが、ツールのロジックは前提にしないもの（tool_source = ×）：**

  - `USAGE`
  - 1〜3 の共通セクション（役割 / 範囲 / 運用目安）
  - steering / architecture / reference の本文の多く
  - impl_notes 全般

この整理を `iori_spec_guide.md` 側にそのまま載せると、

> - どのセクションが **スキーマとしての MUST** か
> - どこを iori-spec のツールが「構造的な情報源」として見るか

が一目で分かる状態になると思います。

[ ] コマンドから逆算して、各ドキュメントに必要な項目をリストアップする
[ ] LLM に質問したいことから逆算して、各ドキュメントに必要な項目をリストアップする
   「この機能案は価値に寄与してる？」

[ ] 共通 `## 2. 範囲（Scope）と前提` には「扱わないもの（Out of Scope / Non-goals）」も含む（多項目で立項したくない）
[ ] steering/product.md `## 成功指標（Success Criteria）` は現時点では優先順位低いか

[ ] 表形式でまとめるべき？
    Kind、MUST/SHOULD、セクション名、is IDキャリア、has File単位ID、has Block単位ID、


