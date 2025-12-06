---
kind: interfaces
scope: tooling.search
id: IF-940
spec_title: "IF-940: Search Specs — spec_index.json → ID Candidates"
status: draft

trace:
  req: []        # 例: REQ-8xz_search_specs などを後で紐付け
  if:
    - IF-910     # Spec Index Builder — spec_index.json を前提とする
  data:
    - DATA-900   # Spec Index Catalog（検索対象）
  test: []
  task: []

dp:
  produces: []      # 永続 DATA は生成しない（search の結果は一時的なレスポンス）
  produced_by: []
  consumes:
    - DATA-900
  inputs: []

doc:
  read_next:
    - DATA-900
    - interfaces/IF-910_spec_index_builder.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-940: Search Specs — spec_index.json → ID Candidates

## LLM_BRIEF

- role: この IF は、`spec_index.json`（DATA-900）を入力として、仕様 ID・タイトル・スコープなどをキーワードで検索し、**ID 候補（SearchHit の一覧）**を返す search モジュールの振る舞いを定義します。
- llm_action: あなた（LLM）はこの IF と DATA-900 を読み、`iori-spec search` コマンドの中核となる **Python モジュール（search コア）** を設計・実装してください。仕様ファイルそのものを全文検索するのではなく、「SpecIndex（DATA-900）のメタ情報だけを使って ID 候補を返す」コードを書くことが目的です。

## USAGE

- ユースケース（CLI 層から見た想定）
  - `iori-spec search "digits segments" --format table`
  - `iori-spec search "digits" --kind requirements --scope client.query_engine --limit 20 --format json`
- ユースケース（Python モジュールとしての関数イメージ）
  - `search_specs(index: SpecIndex, query: str, *, kinds: list[str] | None = None, scopes: list[str] | None = None, roles: list[str] | None = None, limit: int = 50) -> list[SearchHit]`
  - ここで `SpecIndex` は DATA-900 の構造、`SearchHit` は本 IF で定義する最小構造を持つ。

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- IF-910: Spec Index Builder — Markdown Specs → spec_index.json
- impl_notes/spec_command.md（search コマンド全体の位置づけ）
- reference/iori_spec_guide.md（role / kind / scope の定義）

---

## 1. このドキュメントの役割

- `iori-spec` 仕様セットの中から、**目的の ID や spec をすばやく絞り込むための search 機能**のインターフェイスを定義する。
- 具体的には、以下を明確にする：
  - 入力：`spec_index.json` と検索クエリ（文字列）、各種フィルタ（kind / scope / role）
  - 出力：ID 候補（SearchHit 配列）の JSON 表現
  - 検索対象フィールド・フィルタ条件・スコアリングの最低限の要件
- コマンドライン（`iori-spec search`）・Python モジュール・LLM から見た「検索 API の契約」として機能する。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- この IF は **メタ情報検索（index ベースの search）** のみを対象とする。
  - 対象：`spec_index.json.nodes[]` に含まれる SpecNode の
    - `id`
    - `spec_title`
    - `scope`
    - `kind`
    - `role`
    - `llm_brief`
    - （必要なら `summary`）
- 仕様本文の全文検索は範囲外（必要なら別 IF / 別コマンドで扱う）。

### 2.2 前提

- `spec_index.json` は IF-910 により生成済みであり、DATA-900 のスキーマに準拠している。
- search は副作用を持たず、**read-only** な操作である。
- CLI の `--format json` は、この IF で定義する `SearchHit[]` をそのまま JSON 出力する。

---

## 3. 運用上の目安（LLM / SDD 観点）

- 入力となる SpecIndex（DATA-900）は config の `paths.ignore_dirs` を適用して最新化しておく。
- CI や定期ジョブでは `--format json` を用いてヒット一覧（DATA-904 相当）を収集し、ログは標準エラーに分離する。
- スコアリングは単純な TF/一致数ベースでもよいが、同じ入力なら同じ結果を返すことを重視する。

---

## 4. Summary

- SpecIndex の id/spec_title/scope/llm_brief/summary を対象にシンプルな検索を行い、SearchHit 配列（DATA-904）を返す。
- kinds/scopes/roles/limit などのフィルタと、text/table/json 出力をサポートする。

---

## 5. Inputs

- `artifacts/spec_index.json`（DATA-900）
- 検索クエリ、フィルタ（kinds/scopes/roles）、limit、format

---

## 6. Outputs

- SearchHit 配列（DATA-904 相当、json/table/markdown）
- Exit Code（検索は基本 0、入力不正時のみエラー）

---

## 7. 検索要件

### 7.1 入力クエリ

- `query: str`
  - 空文字列や空白のみの場合、**全件検索は行わない**（エラーとするか、help を表示する実装を推奨）。
  - 複数語が含まれる場合（例: `"digits segments"`）は、「スペース区切りのキーワード列」として扱ってよい（MVP では単純 AND マッチで可）。

### 7.2 フィルタ

- kinds フィルタ
  - `kinds: list[str] | None`
  - 例：`["requirements", "interfaces"]`
- scopes フィルタ
  - `scopes: list[str] | None`
  - 例：`["client.query_engine", "build_system"]`
- roles フィルタ
  - `roles: list[str] | None`
  - 例：`["req", "if", "data", "test", "task"]`
- いずれも `None` の場合はフィルタ無し（index 全体から検索）。

### 7.3 検索対象フィールド

最低限、以下のフィールドが検索対象となる：

- `id`（例: `"REQ-201"`, `"IF-200"`）
- `spec_title`
- `scope`
- `kind`
- `llm_brief`（存在すれば）
- `summary`（存在すれば）

> 実装上は、これらを 1 本の文字列に連結した「検索用テキスト」を内部で持ち、  
> `query` 中のキーワードとのマッチングを行ってよい。

### 7.4 マッチング・スコアリングの最低要件

アルゴリズムは実装に委ねるが、**少なくとも以下を満たす**こと：

1. **ID の完全一致を最優先**
   - `query` が `"REQ-201"` のような ID と完全一致する場合、そのノードが最上位に来る。
2. **ID の前方一致も優先**
   - `query` が `"REQ-2"` の場合、`"REQ-201"`, `"REQ-200"` 等の前方一致が高スコア扱い。
3. **キーワード（単語）マッチ**
   - スペース区切りで分割した各キーワードが、対象フィールド（タイトル・scope・llm_brief 等）に含まれている度合いに応じてスコアを上げる。
   - 具体的には「どのフィールドに何回出現したか」に基づき簡易スコアを実装してよい。
4. **スコア順ソート**
   - 上記のルールを満たすようにスコアを定義し、結果は `score` の降順（高い順）で返す。

---

## 8. 処理フロー（概略）

1. **SpecIndex の読み込み**
   - `spec_index.json` を読み込み、DATA-900 のスキーマに従って `SpecIndex` オブジェクトを構築する。
2. **フィルタ適用**
   - `kinds` / `scopes` / `roles` に基づき、対象ノード集合を絞り込む。
3. **クエリ解析**
   - `query` をトリムし、空の場合はエラー／早期終了とする。
   - スペース（半角/全角）で分割し、キーワード配列を得る。
4. **スコアリング**
   - 各 SpecNode について、以下の情報を用いてスコアを計算する：
     - `id` 完全一致・前方一致
     - `spec_title` / `scope` / `kind`・`llm_brief` / `summary` に対するキーワード出現
   - スコア計算の具体式は IF では固定しないが、ID 一致が最優先であることだけ保証する。
5. **結果の整形**
   - スコア上位から `SearchHit` を構築し、`limit` 件まで返す。
6. **CLI 出力**
   - `--format json` の場合：`SearchHit[]` をそのまま JSON 出力。
   - `--format table` などの場合：ID / scope / title / score を表形式に整形して出力。

---

## 9. Acceptance Criteria（受け入れ条件）

1. **ID 直接検索**
   - `iori-spec search "REQ-201"` を実行したとき、`id == "REQ-201"` のノードが最上位（または唯一の）結果として返る。
2. **フィルタ動作**
   - `--kind requirements` を付けた場合、結果の `kind` がすべて `"requirements"` である。
   - `--role req,if` を指定した場合、その他の role（data/test/task 等）は含まれない。
3. **結果数制御**
   - `--limit N` を付けた場合、結果件数は `N` 以下である（ヒット数が N 未満ならヒット数分）。
4. **空クエリハンドリング**
   - `query` が空文字列・空白のみの場合、エラー／ヘルプ表示など、明示的な挙動が定義されている（静かに全件返さない）。
5. **JSON 形式の安定性**
   - `--format json` の出力が、後述の `SearchHit` スキーマに従っている。
   - ログや余計な文字列は stdout に混在しない（stderr に出す）。

---

## 10. Inputs / Outputs

### 10.1 Inputs（コア関数）

| 名前       | 型                | 必須 | 説明 |
|------------|-------------------|------|------|
| `index`    | SpecIndex         | Yes  | DATA-900 準拠の SpecIndex オブジェクト。 |
| `query`    | string            | Yes  | 検索文字列。空ではないこと。 |
| `kinds`    | list\[str] \| None  | No   | 絞り込み対象の `kind` 一覧。 |
| `scopes`   | list\[str] \| None  | No   | 絞り込み対象の `scope` 一覧。 |
| `roles`    | list\[str] \| None  | No   | 絞り込み対象の `role` 一覧。 |
| `limit`    | int               | No   | 最大件数（デフォルト 50 程度を想定）。 |

※ CLI 実装では `index_path: Path` / `--kind` / `--scope` / `--role` / `--limit` などにマッピングされる。

### 10.2 Outputs（コア関数）

戻り値：`list[SearchHit]`

SearchHit の最小構造（後で DATA-904 として data_contract 化してもよい）：

| フィールド     | 型       | 必須 | 説明 |
|----------------|----------|------|------|
| `id`           | string   | Yes  | SpecNode の ID（例: `"REQ-201"`）。 |
| `file`         | string   | Yes  | SpecNode のファイルパス（リポジトリ root からの相対）。 |
| `kind`         | string   | Yes  | SpecNode の kind。 |
| `scope`        | string   | Yes  | SpecNode の scope。 |
| `role`         | string   | Yes  | SpecNode の role（req / if / data / test / task / ...）。 |
| `spec_title`   | string   | Yes  | 仕様タイトル。 |
| `score`        | number   | Yes  | 検索スコア（相対値。0 以上を推奨）。 |
| `snippet`      | string \| null | No   | `llm_brief` / `summary` 等から抜粋した短いテキスト。 |
| `matched_fields` | string[] \| null | No | マッチに寄与したフィールド名（例: `["id", "spec_title"]`）。 |

> 実装上は、この SearchHit をそのまま JSON にシリアライズして `--format json` で返す。

---

## 11. 非機能要件（簡易）

- **性能**
  - 数百〜数千ノード規模の SpecIndex に対して、通常の search（limit 50 程度）は 1 秒未満で完了することを目安とする。
  - MVP では in-memory 線形スキャンでよいが、必要に応じてインデックス構造の導入も検討する。
- **安定性**
  - SpecIndex に不正なノード（必須フィールド欠落など）があっても、可能な限り検索処理は継続し、問題のあるノードだけスキップする実装が望ましい（ただし lint で先に検出される前提）。
- **LLM フレンドリ**
  - フィールド名・関数名は素直な英単語にする（`search_specs`, `SearchHit`, `score` など）。
  - SearchHit はフラットな構造に保ち、ネストを深くしない。

---

## 12. 今後の拝張（メモ）

- SearchHit の data_contract として `DATA-904_search_result` を切り出す（必要になったタイミングで）。
- 高度な検索機能：
  - role / kind のデフォルト優先順位（例: まず REQ / IF を優先表示 等）
  - スコアの説明（why this matched?）を `extra` フィールドなどで返す。
- LLM 連携：
  - `iori-spec` が ID を見つけやすいように、SearchHit に `llm_prompt_hint` のようなフィールドを追加し、「この spec を読むときの一言解説」を仕込む案もあり。



