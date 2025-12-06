# 実装プラン

「まず MUST コマンド 6 本（search / index / impact / context / lint / trace lint）を
ちゃんと動かす」ことをゴールにした実装順のプランです。

大きくは、

- まず **index（SSOT）と lint（型の整合性）** を固めて、
- その上に **impact/context（局所コンテキスト化）** と
- **trace lint（トレーサビリティ健全性）** を乗せる、

という流れになります。

---

## Step 0. 基盤づくり（共通コンポーネント）

どのコマンドよりも先に、軽くでもよいので共通基盤を用意しておく。

- Markdown + front matter ローダ
  - `--- ... ---` を YAML としてパースし、本⽂と分離するユーティリティ
- `kind` / `scope` / ID（`REQ-xxx`, `IF-xxx`, ...）抽出ロジック
  - ID プレフィックスから ROLE（`req` / `if` / `data` / `test` / `task`）を導く関数
- 共通の CLI エントリ
  - `iori-spec <subcommand> ...` の枠組みだけ作る
- 設定・スキーマ読み込み
  - `reference/iori_spec_config.yaml` から `kinds` / `scopes` を読む
  - `spec_section_schema`（kind ごとの必須セクション / tool_source フラグ）を読み込む仕組み

> この Step 0 の成果物は、以降のすべてのコマンドから使い回す。

ここでは特定の IF / DATA ID はまだ持たせず、

- front matter ローダ
- SpecNode / SpecIndex 用の共通型
- Config / SectionSchema ローダ

を「共通ライブラリ層」として実装する方針。

それらを前提として、後続 Step の IF（IF-910 / 920 / 930 / 940 / 950 / 960 / 970）を組み立てる。

---

## Step 1. `index`（仕様インデックス）★最優先 MUST

**理由**：他の機能の「土台データ構造」になるから。

やること（MVP）:

- `--root` 以下の `**/*.md` を列挙し、
- front matter から以下を抽出して `nodes[]` を構築する：
  - `id`, `kind`, `scope`, `status`, `spec_title`
  - `trace.*`, `dp.*`, `doc.*`
- 上記を `artifacts/spec_index.json` に保存する
- 同時にメモリ上では、簡易なグラフ構造（G_trace / G_dp / G_doc）を作れるようにしておく

ここができると：

- `search` / `impact` / `context` / `lint` / `trace lint` のすべてが
  同じ SSOT（spec_index.json）を参照できるようになる。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-910_spec_index_builder**  
    - 入力:
      - Markdown specs (`**/*.md`)
      - `reference/iori_spec_config.yaml`
      - `spec_section_schema.yaml`（DATA-901）
    - 出力:
      - `artifacts/spec_index.json`（DATA-900）
- DATA
  - **DATA-900_spec_index**  
    - index コマンドの SSOT。全コマンドが参照するカタログ。
  - **DATA-901_spec_section_schema**  
    - kind ごとのセクション構造／tool_source 定義（index では読み取り専用）。

---

## Step 2. `lint`（構造・メタ情報 Lint）★ MUST

**理由**：仕様の「型」が崩れていると、上に乗る機能（impact/context）が信用できないから。

やること（MVP）:

- `--root` 以下のファイルを走査し、front matter＋本文をパース
- ルールセットごとにチェックする lint エンジンを実装：
  - `frontmatter` ルール：
    - `kind / scope / id / status` の存在
    - `kind` / `scope` が `iori_spec_config.yaml` の定義に含まれているか
  - `sections` ルール：
    - kind ごとの必須セクション（LLM_BRIEF / Summary / Acceptance 等）の有無
    - セクションの順番・重複見出しなど、最小限の構造チェック
  - `ids` ルール：
    - ID の形式（`REQ-\d+`, `IF-\d+` など）
    - 「1 ファイル 1 ID」の原則を破っていないか（採用するなら）
  - （将来）`labels` / `vocab` ルール：
    - ID ↔ spec_title の SSoT が崩れていないか
    - 用語集にない単語を使っていないか 等

ここまでで、

- 「仕様フォーマットに沿っていないファイル」を早期に検出できるようになる。
- index / impact / context の前提条件を機械的に保証できる。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-920_lint_core**  
    - 入力:
      - Markdown specs (`**/*.md`)
      - `reference/iori_spec_config.yaml`
      - `spec_section_schema.yaml`（DATA-901）
    - 出力:
      - lint 結果（DATA-902）  
        （ルール種別や severity ごとに Issue を列挙）
- DATA
  - **DATA-901_spec_section_schema**  
    - kind ごとの必須/任意セクション、tool_source フラグを定義。
  - **DATA-902_lint_result**  
    - lint コマンド全体の Issue リスト（JSON）。

---

## Step 3. `trace lint`（トレーサビリティ Lint）★ MUST

**理由**：REQ ↔ IF / DATA / TEST のつながりが破綻していると、
そもそも impact/context の意味づけが怪しくなるから。

やること（MVP）:

- `index` の `nodes[].trace` と `id/kind` から G_trace を構築
- 以下をチェック：
  - 各 REQ に対して、少なくとも 1 つ以上の IF / DATA / TEST が紐づくか
  - 各 IF / DATA / TEST が、少なくとも 1 つ以上の REQ と紐づくか
  - `trace.*` で参照している ID が index に存在するか
  - TASK は coverage 対象外（孤立していても警告どまり）

結果として、

- 「未実装の要求」「未テストの要求」「孤立した DATA / TEST」などが機械的に見つかる。
- この情報をもとに、あとから `trace report` を付け足すのも容易になる。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-930_trace_lint**  
    - 入力:
      - `artifacts/spec_index.json`（DATA-900）
    - 出力:
      - trace 用 lint 結果（DATA-902、rule 種別で trace 系と分かるようにする）
- DATA
  - **DATA-900_spec_index**  
    - trace グラフ構築の入力。
  - **DATA-902_lint_result**  
    - trace lint の Issue も同一スキーマで格納（rule_id や source で区別）。

---

## Step 4. `search`（ID 候補の探索）★ MUST

**理由**：LLM / 人間が「どの ID から読めばいいか？」を決める入口になるから。

やること（MVP）:

- `spec_index.json` を入力として、
  - `id`
  - `spec_title`
  - `scope`
  を対象にシンプルな全文検索を実装する
- `--kinds` / `--limit` / `--format`（json|table|markdown）対応
- `snippet` はまず `spec_title` ベースで簡易に返し、
  余裕があれば LLM_BRIEF から 1〜2 行抜粋する実装を追加

ここまで行くと、

- 「digits segmentation に関係する spec は？」という問いに対して、
  CLI 1 発で ID 候補リストを返せるようになる。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-940_search_specs**  
    - 入力:
      - `artifacts/spec_index.json`（DATA-900）
      - 検索クエリ、種別フィルタ（kinds / scopes / roles / limit）
    - 出力:
      - SearchHit の配列（DATA-904）
- DATA
  - **DATA-900_spec_index**  
    - 検索対象となるノード情報の SSOT。
  - **DATA-904_search_result**  
    - `iori-spec search --format json` の戻り値となる SearchHit[]。

---

## Step 5. `impact`（影響範囲の列挙）★ MUST

**理由**：ID を変更したときの「波及先」を自動で出せると、仕様変更のコスト見積りが一気に楽になるから。

やること（MVP）:

- Step 1 で用意した G_trace / G_dp / G_doc を使って、
  指定 ID を始点に BFS で近傍ノードを辿る
- `--max-depth` / `--include-roles` で辿る範囲を制御
- 各ノードについて、
  - `id`, `kind`, `relation`, `distance`
  を JSON / table / markdown で返す

これにより、

- 「この IF を変えたら、どの REQ / DATA / TEST / TASK を一緒に見直すべきか」が
  コマンド 1 発で可視化される。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-950_impact_analyzer**  
    - 入力:
      - `artifacts/spec_index.json`（DATA-900）
      - `changed_ids`（impact 対象 ID 群）
      - `mode` / `max_distance` / `roles` / `include_doc_links`
    - 出力:
      - ImpactReport（DATA-906）
- DATA
  - **DATA-900_spec_index**  
    - trace グラフの基礎データ。
  - **DATA-906_impact_report**  
    - impact コマンドの JSON 出力／上位ツールへのインターフェイス。

---

## Step 6. `context`（局所コンテキストパック生成）★ MUST

**理由**：LLM に渡す「ちょうどよい量のコンテキスト」を自動で作るのが iori-spec の軸①の本丸だから。

やること（MVP）:

- `impact` 相当の処理で seed ID と近傍 ID を決定（`radius` / `include-roles`）
- 各 ID について、
  - front matter（必要部分）
  - `spec_section_schema` で `tool_source=true` なセクション
  を抽出して Markdown / JSON に整形
- seed → 近傍の順に連結した「Context for IF-200 (and neighbors)」のような 1 本のファイルを生成

ここまでで、

- 「IF-200 周辺の仕様一式を LLM に貼るためのコンテキスト」を
  `iori-spec context IF-200 --radius 1` で自動生成できるようになる。

### 対応 IF / DATA（MVP 時点）

- IF
  - **IF-960_context_builder**  
    - 入力:
      - `artifacts/spec_index.json`（DATA-900）
      - `spec_section_schema.yaml`（DATA-901）
      - seed_ids / depth / roles / max_tokens などの条件
    - 出力:
      - ContextBundle（DATA-905）
- DATA
  - **DATA-900_spec_index**  
    - コンテキスト対象ノードの探索に利用。
  - **DATA-901_spec_section_schema**  
    - `tool_source=true` なセクション抽出ルールとして利用。
  - **DATA-905_context_bundle**  
    - `iori-spec context --format json` の出力／LLM 連携の中間形式。

### （将来拡張）`prompt` コマンドとの関係

- IF
  - **IF-970_prompt_bundle_builder**  
    - 入力:
      - ContextBundle（DATA-905）
      - preset / language / extra_instruction
    - 出力:
      - PromptBundle（DATA-907）
- DATA
  - **DATA-907_prompt_bundle**  
    - LLM API クライアントがそのまま消費できるプロンプト構造（system / user / context_markdown）。

---

## Step 7. SHOULD / NICE TO HAVE コマンド（余力フェーズ）

MUST が揃ったあと、余力に応じて追加していくコマンド群。

- `show`（SHOULD）
  - `context <ID> --radius 0` 相当の薄いラッパとして実装可能
  - （IF-960 / DATA-905 をそのまま再利用）
- `trace report`（SHOULD）
  - Step 3 の `trace lint` と同じ G_trace を使って、
    Traceability Map を Markdown で自動生成する
- `new` / `scaffold`（SHOULD（強め））
  - `spec_section_schema` に基づいて、新しい REQ / IF / DATA / TEST / TASK テンプレートを生成
- `graph export` / `graph neighbors`（NICE TO HAVE）
  - G_trace / G_dp / G_doc を DOT / JSON として吐き出し、可視化やデバッグに利用
- `tasks list` / `report tasks`（NICE TO HAVE）
  - TASK を中心にしたビュー（IF ごとのタスクリストなど）を生成

これらはすべて、Step 0〜6 の基盤の上に「薄いビュー」を足すだけで実装できるよう設計しておく。

### 対応 IF / DATA（MVP 時点）

- このフェーズで必要になる IF / DATA は、実装時に個別の ID を採番する。
- 現時点では、
  - `show` は **IF-960 / DATA-905** をそのままラップするだけ
  - `trace report` は **IF-930 / DATA-900** を再利用するだけ
  - という方針を前提にしつつ、追加の IF/DATA が必要になった時点で改めて設計する。



