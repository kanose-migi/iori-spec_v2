---
kind: interfaces
scope: tooling.lint
id: IF-920
spec_title: "IF-920: Lint Core — frontmatter / sections / ids"
status: draft

trace:
  req: []        # 例: REQ-8xx_tooling_lint などを後で紐付け
  if:
    - IF-910     # index ビルダー（index が前提 / 併用される想定）
  data:
    - DATA-900   # spec_index.json（必要に応じて利用）
    - DATA-901   # spec_section_schema.yaml（セクション構造の基準）
  test: []
  task: []

dp:
  produces: []      # lint の結果は将来的に DATA-9xx_lint_result として data_contract 化する想定
  produced_by: []
  consumes:
    - DATA-900
    - DATA-901
  inputs:
    - iori_spec_config.yaml   # 有効な kinds / scopes 定義
    - Markdown specs (*.md)   # 仕様ファイル群（YAML front matter 付き）

doc:
  read_next:
    - DATA-900
    - DATA-901
    - reference/iori_spec_guide.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-920: Lint Core — frontmatter / sections / ids

## LLM_BRIEF

- role: この IF は、`iori-spec` の仕様ファイル群に対して行う **構造・メタ情報 lint（frontmatter / sections / ids）** のコアロジックを定義します。
- llm_action: あなた（LLM）はこの IF と DATA-900 / DATA-901 を読み、`iori-spec lint` コマンドの中核となる **Python モジュール（lint コア）** を設計・実装してください。仕様ファイルそのものや `spec_index.json` / `spec_section_schema.yaml` を入力として、ここで定義されたルールに従って lint 結果を返すコードを書くことが目的です。

## USAGE

- ユースケース（CLI 層から見た想定）
  - `iori-spec lint --root . --config reference/iori_spec_config.yaml --sections --frontmatter --ids --format json`
  - 上記コマンドが内部で本 IF に従った関数を呼び出し、lint 結果（Issue の一覧）を JSON で返す。
- ユースケース（Python モジュールとしての関数イメージ）
  - `run_lint(root: Path, config_path: Path, section_schema_path: Path, index_path: Optional[Path], enabled_rules: list[str]) -> list[LintIssue]`
  - ここで `LintIssue` は「どのファイルのどの位置に、どのルール違反があるか」を表す構造体（後述）。

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- DATA-901: Spec Section Schema — spec_section_schema.yaml
- reference/iori_spec_guide.md（kind / scope / ID 命名規則など）
- impl_notes/spec_command.md（lint コマンド全体の位置づけ）

---

## 1. このドキュメントの役割

- `iori-spec` が管理する仕様書群に対して、以下の観点で **一貫した lint を行うためのインターフェイス**を定義する：
  - frontmatter（YAML メタ情報）の妥当性
  - sections（見出し構造）の妥当性
  - ids（ID の形式・一意性等）の妥当性
- コマンドライン（`iori-spec lint`）からは、この IF で定義されたインターフェイスを通じて lint を実行する。
- 実装側（Python モジュール）・テスト側・LLM から見て、「どの入力を受け取り、どのような lint ルールで何を返すか」の契約を明確化する。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- この IF は、**構造・メタ情報に関する lint** を対象とする。
  - frontmatter: `kind`, `scope`, `id`, `status`, `spec_title` 等
  - sections: `LLM_BRIEF`, `USAGE`, `READ_NEXT`, kind 固有の Summary / Acceptance など
  - ids: ID の形式・重複・「1 ファイル 1 ID」原則 等
- トレーサビリティ（REQ ↔ IF / DATA / TEST の coverage）は、別 IF（trace lint）で扱う前提。

### 2.2 前提

- 各 spec ファイルは、YAML front matter に最低限以下を持つことが期待される：
  - `kind` / `scope` / `id` / `spec_title` / `status`
- `kind` / `scope` の有効な値は `iori_spec_config.yaml` に定義されている。
- `paths.ignore_paths` に指定されたパス（例: `impl_notes/` や `**/README_SPEC.md`）は lint 対象から除外する前提とする。
- kind ごとの必須セクションや `tool_source` セクションは、DATA-901（spec_section_schema.yaml）に定義されている。
- `spec_index.json`（DATA-900）は存在すれば利用できるが、frontmatter / sections / ids lint 自体は、ファイルシステムを直接走査するだけでも実行可能。

---

## 3. 運用上の目安（LLM / SDD 観点）

- CI や定期ジョブでは `paths.ignore_paths` を適用し、全カテゴリ（frontmatter/sections/ids）を実行して型崩れを早期検知する。
- セクションスキーマ（DATA-901）が読み込めない場合はエラー扱いとして修復を促す。
- `--format json` での出力は DATA-902 相当としてそのまま収集できるよう、ログは標準エラーに分離する。

---

## 4. Summary

- Markdown 仕様の front matter・見出し・ID を静的検査し、FM-xxx / SEC-xxx / ID-xxx ルールで Issue を返す。
- 有効な kind/scope は DATA-910 を参照し、必須セクションは DATA-901 を基準にする。

---

## 5. Inputs

- Markdown specs（`spec_root` 配下、`spec_glob` / `ignore_paths` 適用）
- `reference/iori_spec_config.yaml`（DATA-910）
- `spec_section_schema.yaml`（DATA-901）
- （任意）`spec_index.json`（DATA-900, 拡張ルール時）

---

## 6. Outputs

- lint Issue の一覧（DATA-902 相当、text / json）
- Exit Code（0: 問題なし、3: 重大 Issue あり等、CLI ポリシーに準拠）

---

## 7. Lint ルールセット

本 IF では、lint ルールをいくつかのカテゴリに分ける。  
CLI からは `--rules` / `--frontmatter` / `--sections` / `--ids` 等で有効・無効を切り替えられる前提。

### 7.1 frontmatter ルール

対象：各 Markdown ファイルの YAML front matter

代表的なルール（最低限のセット）：

1. **FM-001: 必須キーの存在**
   - `kind`, `scope`, `id`, `spec_title`, `status` がすべて存在すること。
2. **FM-002: kind/scope の妥当性**
   - `kind` が `iori_spec_config.yaml` で定義された一覧に含まれること。
   - `scope` が `iori_spec_config.yaml` で定義された一覧（もしくは許容パターン）に含まれること。
3. **FM-003: status の妥当性**
   - `status` が `draft` / `review` / `stable` / `deprecated` 等、事前に定義された値のいずれかであること。
4. **FM-004: 1 ファイル 1 ID 原則**
   - 1 つのファイルにつき `id` が 1 つであること（複数 ID は禁止）。
5. **FM-005: kind と id プレフィックスの整合性（任意）**
   - 例：`kind: requirements` のファイルで `id: IF-200` が付いている場合、警告またはエラーにする。

### 7.2 sections ルール

対象：Markdown 本文の見出し構造

- DATA-901 の SectionRule に基づき、kind ごとにチェックを行う。

代表的なルール：

1. **SEC-001: 必須セクションの存在**
   - `required: true` な SectionRule について、対応する見出しが存在すること。
2. **SEC-002: セクションの多重定義**
   - `multiple: false` な SectionRule について、複数回出現していないこと。
3. **SEC-003: セクション順序（任意）**
   - `order` に基づき、明らかに順序が逆転している場合に警告を出す（厳密な並び順チェックはオプション）。
4. **SEC-004: 未知のセクション（任意）**
   - `options.allow_extra_sections == false` の場合、SectionRule に定義されていない見出しは警告またはエラーとする。

### 7.3 ids ルール

対象：ID の形式・一意性

代表的なルール：

1. **ID-001: 形式チェック**
   - `REQ-\d+`, `IF-\d+`, `DATA-\d+`, `TEST-\d+`, `TASK-\d+` 等、`iori_spec_guide` で定義されたパターンに従っていること。
2. **ID-002: index 内での一意性（任意）**
   - `spec_index.json` が利用可能な場合、`nodes[].id` が一意であることを確認する。
3. **ID-003: ファイル名との整合性（任意）**
   - ファイルパス（例: `requirements/REQ-201_digits_segments.md`）と `id` の組み合わせに一貫性があるかどうかをチェックする。
4. **ID-004: プレフィックスと role の整合性（任意）**
   - `id` のプレフィックスと DATA-900 内の `role` 計算ロジックが一致しているかを確認する。

### 7.4 index 一貫性ルール（任意）

対象：spec_index.json と実ファイルの整合性（拡張用）

代表的なルール：

1. **IDX-001: index に載っていない spec**
   - 実ファイルとして存在する ID 付き spec が、`spec_index.json.nodes` に含まれていない場合に警告。
2. **IDX-002: index 上の孤立ノード**
   - `spec_index.json` 上で参照されているファイルパスが実在しない場合に警告。

---

## 8. 処理フロー（概略）

### 8.1 エントリポイント

1. CLI からの入力（ルート・設定パス・有効ルール等）を受け取る。
2. 本 IF に従ったコア関数に集約し、LintIssue の一覧を受け取る。
3. CLI ではそれを JSON / テーブル等に整形して出力する。

### 8.2 コア処理

1. **設定の読み込み**
   - `iori_spec_config.yaml` から有効な `kinds` / `scopes` を取得。
   - `spec_section_schema.yaml`（DATA-901）から SectionRule 群と options を取得。
   - 任意で `spec_index.json`（DATA-900）を読み込む（存在すれば index 一貫性ルールで利用）。
2. **ファイル列挙**
   - `root` 以下の Markdown ファイルを再帰的に列挙。
  - 無視パターン（`.git/`, `node_modules/`, `artifacts/` 等）を適用。
  - config の `paths.ignore_paths`（`spec_root` 相対のパスまたは glob）も除外対象に含める。
3. **frontmatter パース & frontmatter ルール判定**
   - YAML front matter をパースし、`FM-xxx` 系ルールを適用。
4. **sections 抽出 & sections ルール判定**
   - Markdown 本文から見出し一覧を抽出し、SectionRule に基づき `SEC-xxx` 系ルールを適用。
5. **ids ルール判定**
   - frontmatter から取得した `id` / `kind` / ファイルパス / index 情報を用いて `ID-xxx` 系ルールを適用。
6. **index 一貫性ルール（任意）**
   - `spec_index.json` を利用して `IDX-xxx` 系ルールを適用。
7. **LintIssue の集約**
   - 各ルールから上がってきた issue を集約し、返却用の配列（list[LintIssue]）にまとめる。

---

## 9. Acceptance Criteria（受け入れ条件）

1. **必須ルールの実装**
   - 少なくとも `FM-001〜003`, `SEC-001〜002`, `ID-001` が実装されていること。
2. **再現性**
   - 同じ入力（ルート・設定・spec 内容）に対して、同じルールセットを有効にした場合、LintIssue の一覧が安定して再現されること。
3. **フィルタリング**
   - CLI から特定カテゴリのみを有効化した場合（例: `--frontmatter` のみ）、該当カテゴリの Issue のみが出力されること。
4. **フォーマット**
   - `--format json` が指定された場合、stdout には純粋な JSON（LintIssue の配列）のみを出力し、ログや警告は stderr に分離されていること。
5. **パフォーマンス（目安）**
   - 数百〜数千ファイル規模の spec セットに対して、数秒以内に lint を完走できること（詳細な数値は別途 REQ / TEST で定義）。

---

## 10. Inputs / Outputs

### 10.1 Inputs（コア関数）

| 名前                  | 型              | 必須 | 説明 |
|-----------------------|-----------------|------|------|
| `root_dir`            | Path            | Yes  | 仕様ファイル群のルートディレクトリ。 |
| `config_path`         | Path            | Yes  | `iori_spec_config.yaml` のパス。kind / scope の定義に使用。 |
| `section_schema_path` | Path            | Yes  | `spec_section_schema.yaml`（DATA-901）のパス。 |
| `index_path`          | Path \| None    | No   | `spec_index.json`（DATA-900）のパス。指定されていない場合、index 依存ルールはスキップ可。 |
| `enabled_rules`       | list\[str]      | No   | 有効化するルールカテゴリ名・ルール ID（例: `["frontmatter", "sections", "ids", "IDX-001"]`）。 |
| `ignore_patterns`     | list\[str]      | No   | 無視するパスの glob パターン。 |

### 10.2 Outputs（コア関数）

戻り値：`list[LintIssue]`

LintIssue の最小構造（後で DATA-902 として data_contract 化する想定）：

| フィールド    | 型        | 説明 |
|---------------|-----------|------|
| `rule_id`     | string    | どのルールに違反したか（例: `"FM-001"`, `"SEC-002"`）。 |
| `severity`    | string    | `"error"` / `"warning"` / `"info"` のいずれか。 |
| `file`        | string    | 問題が発生したファイルパス（root からの相対パス）。 |
| `line`        | int \| null | 主に該当する行番号（わからない場合は null）。 |
| `message`     | string    | 人間が読める説明。 |
| `hint`        | string \| null | 修正のヒント（例: 「kind を 'requirements' に修正してください」）。 |
| `extra`       | object \| null | 追加情報（問題のある値や期待値など）を格納するための自由領域。 |

---

## 11. 非機能要件（簡易）

- **拡張性**
  - 新しいルールカテゴリやルール ID を追加しても、既存の利用箇所が壊れないように設計する（例: ルール ID は文字列で扱う、未知のルール ID は無視するなど）。
- **可観測性**
  - 有効なルール数・検査したファイル数・検出された Issue 数を簡単にログ出力できることが望ましい。
- **LLM フレンドリ**
  - ルール ID・フィールド名・関数名は、意味が推測しやすい素直な英単語を用いる（略語過多にしない）。
  - LintIssue の構造はフラットで、JSON 化しやすい形に保つ。

---

## 12. 今後の拡張（メモ）

- lint 結果（LintIssue の配列）を正式な data_contract として `DATA-902_lint_result` などに切り出す。
- Rule 定義を YAML 化し、コード側は「ルールエンジン」として汎用化する案も検討する。
- `trace lint`（IF-93x 系）と共通部分（ID 解釈や index 参照ロジック）をモジュール化し、重複実装を避ける。



