---
kind: interfaces
scope: tooling.spec_index
id: IF-910
spec_title: "IF-910: Spec Index Builder — Markdown Specs → spec_index.json"
status: draft

trace:
  req: []        # 例: REQ-801_tooling_index などを後で紐付け
  if: []
  data:
    - DATA-900   # 出力
    - DATA-901   # 必須ではないが、llm_brief/summary 抽出時に参照してもよい
  test: []
  task: []

dp:
  produces:
    - DATA-900   # spec_index.json を生成する
  produced_by: []
  consumes:
    - DATA-901   # (オプション) セクションスキーマを利用して LLMBRIEF / Summary 抽出を制御
  inputs:
    - iori_spec_config.yaml  # 有効な kinds / scopes 定義
    - Markdown specs (*.md)  # 仕様ファイル群（YAML front matter 付き）

doc:
  read_next:
    - DATA-900
    - DATA-901
  see_also:
    - reference/iori_spec_guide.md
---

# IF-910: Spec Index Builder — Markdown Specs → spec_index.json

## LLM_BRIEF

- role: この IF は、`--root` 以下の Markdown 仕様ファイル群から `DATA-900` で定義された `spec_index.json` を生成する **インデックスビルダー・モジュールの振る舞い**を定義します。
- llm_action: あなた（LLM）はこの IF を読み、DATA-900 の data_contract を満たす `spec_index.json` を生成する **Python モジュール／CLI サブコマンド（`iori-spec index`）のコード**を書いてください。spec_index.json を直接出力するのではなく、「こう振る舞う index ビルダーを実装する」ことがゴールです。

## USAGE

- ユースケース（CLI 層を実装するときの前提イメージ）
  - `iori-spec index --root . --config reference/iori_spec_config.yaml --output artifacts/spec_index.json`
  - 上記コマンドを叩いたときに、内部で本 IF に従ったビルダー関数が呼ばれる前提で実装する。
- ユースケース（Python モジュールとして実装するときの関数イメージ）
  - `build_spec_index(root: Path, config_path: Path, section_schema_path: Optional[Path]) -> SpecIndex`
  - ここで `SpecIndex` は DATA-900 で定義したトップレベル構造（`version`, `generated_at`, `root`, `nodes[]`）を持つオブジェクトとする。

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- DATA-901: Spec Section Schema — spec_section_schema.yaml
- reference/iori_spec_guide.md

---

## 1. このドキュメントの役割

- Markdown ベースの仕様セットから **機械可読な spec インデックス（DATA-900）を生成するためのインターフェイス**を定義する。
- コマンドライン層（`iori-spec index`）と、実装のコア関数（Python モジュール）との「契約」を明確にし、
  - 実装
  - テスト
  - LLM からの利用
  を安定させる。

---

## 2. 範囲（Scope）と前提

- 対象: `spec_index.json`（DATA-900）を生成するビルダーの振る舞いと CLI サブコマンド `iori-spec index`。
- 前提: DATA-910 のパス設定と DATA-901 のセクションスキーマを参照可能であること。`paths.ignore_paths` などの除外設定を尊重して走査する。

---

## 3. 運用上の目安（LLM / SDD 観点）

- index は全コマンドの SSOT となるため、config 変更や仕様追加のたびに再生成する。
- CI などの定期ジョブでは `ignore_paths` を適用した状態で生成し、成果物を artifacts 配下に出力する。
- セクションスキーマが読み込めない場合は graceful に続行しつつ警告を出す（MVP）。

---

## 4. Summary

- Markdown 仕様群を走査し、front matter と本文から ID / kind / scope / trace / dp / doc を抽出して DATA-900 を構築する。
- DATA-901 を利用できる場合は `llm_brief` / summary も抽出する。

---

## 5. Inputs

- Markdown specs（`spec_root` 配下、`spec_glob` または `ignore_paths` の設定に従う）
- `reference/iori_spec_config.yaml`（DATA-910）
- `spec_section_schema.yaml`（DATA-901、任意）

---

## 6. Outputs

- `artifacts/spec_index.json`（DATA-900）または標準出力（`--output -` 指定時）
- メモリ上の SpecIndex オブジェクト（ライブラリ利用時）

---

## 7. インターフェイスの概要

### 7.1 入力（abstract）

- ルートディレクトリ（`root_dir`）
- `iori_spec_config.yaml` のパス（`config_path`）
- `spec_section_schema.yaml` のパス（`section_schema_path`、任意）
- オプション設定（例）
  - `ignore_patterns`（`["**/node_modules/**", ".git/**", "artifacts/**"]` など）
  - `glob`（デフォルト: `"**/*.md"`）

### 7.2 出力（abstract）

- DATA-900 で定義された `spec_index.json` 相当のオブジェクト
  - トップレベル:
    - `version`
    - `generated_at`
    - `root`
    - `nodes[]: SpecNode`
  - `SpecNode` の構造は DATA-900 を参照

---

## 8. 詳細仕様

### 8.1 処理フロー（概略）

1. **設定ファイルの読み込み**
   - `iori_spec_config.yaml` を読み込み、有効な `kinds` / `scopes` 一覧を取得する。
2. **ファイル列挙**
   - `root_dir` 以下を再帰的に走査し、`glob`（デフォルト: `**/*.md`）にマッチするファイルを抽出する。
   - `ignore_patterns` にマッチするパスは除外する。
   - `iori_spec_config.yaml` の `paths.ignore_paths` で与えられたパス（`spec_root` 相対、glob 可）も除外に含める。
3. **YAML front matter のパース**
   - 各 Markdown から `YAML front matter` を抽出し、以下のキーを取得する：
     - `kind`, `scope`, `id`, `spec_title`, `status`
     - `trace`, `dp`, `doc`（存在すれば）
   - `id` が存在しない、または `kind` / `scope` が無効な場合は、そのファイルを index 対象外とするか、警告として記録する（方針は IF-910 にて定義）。
4. **role の決定**
   - `id` のプレフィックスから `role` を決定する：
     - `REQ-` → `req`
     - `IF-`  → `if`
     - `DATA-` → `data`
     - `TEST-` → `test`
     - `TASK-` → `task`
     - それ以外は `ref` / `doc` / `impl` / `unknown` 等、`iori_spec_guide` で定義されたマッピングに従う。
5. **llm_brief / summary の抽出（任意）**
   - `section_schema_path` が指定されている場合（かつファイルが存在する場合）：
     - DATA-901 の rules を読み込み、`tool_source` / `id` に基づいて `LLM_BRIEF` や Summary に相当するセクションを抽出する。
     - 抽出した本文の先頭数行を `llm_brief` / `summary` フィールドに保存する。
   - 指定されていない場合：
     - `llm_brief` / `summary` は `null` のままとしてよい（MVP）。
6. **hash / frontmatter_range の計算**
   - ファイル内容のハッシュ（例: SHA-256）を計算し、`hash` に格納する。
   - front matter の行範囲（1-origin の `start` / `end`）がわかる場合は `frontmatter_range` に格納する。
7. **SpecIndex オブジェクトの構築**
   - 上記情報をもとに `SpecNode` を生成し、`nodes[]` に push する。
   - トップレベルに `version`, `generated_at`, `root` を設定する。
8. **JSON 出力**
   - 内部表現をそのまま返す（ライブラリ関数の場合）。
   - CLI 経由の場合は、指定された `--output` パスに JSON 形式で書き出す。

---

## 9. Acceptance Criteria（受け入れ条件）

1. **DATA-900 準拠**
   - 生成された `spec_index.json` は、DATA-900 で定義したスキーマに準拠する。
   - 少なくとも `version`, `generated_at`, `root`, `nodes[].(id, kind, scope, status, spec_title, role, file)` が正しくセットされている。
2. **再現性**
   - 同一の `root_dir` / `config_path` / `section_schema_path` / ファイル内容 / ignore 設定で実行した場合、ハッシュ値や `generated_at` を除いて同じ index が生成される。
3. **不正 front matter の扱い**
   - `kind` / `scope` / `id` が欠落しているファイルを index に含めない場合、その挙動がドキュメント化されている。
   - 可能であれば、`--strict` オプションでエラーにするか、`--ignore-errors` で警告にとどめるなど、モードを切り替えられる。
4. **パフォーマンス（目安）**
   - 数百〜数千ファイル規模の spec セットに対して、数秒以内に index を生成できる（具体値は別途 REQ / TEST で定義）。
5. **LLM との親和性**
   - `--format json` で CLI を実行した場合、標準出力には純粋な JSON のみを出力し、ログや警告は標準エラーに分離されている。

---

## 10. Inputs / Outputs（詳細）

### 10.1 Inputs

| 名前                | 型          | 必須 | 説明 |
|---------------------|-------------|------|------|
| `root_dir`          | Path        | Yes  | 仕様ファイル群が格納されているディレクトリ。 |
| `config_path`       | Path        | Yes  | `iori_spec_config.yaml` のパス。`kinds` / `scopes` 定義を参照する。 |
| `section_schema_path` | Path\|None | No   | `spec_section_schema.yaml` のパス。指定されない場合、`llm_brief` / `summary` の抽出は行わなくてもよい。 |
| `ignore_patterns`   | string[]    | No   | 走査時に除外する glob パターン。 |
| `glob`              | string      | No   | 対象とする Markdown ファイルの glob（デフォルト: `**/*.md`）。 |

### 10.2 Outputs

- Python ライブラリとしての戻り値
  - `SpecIndex` 型（DATA-900 に準拠した dict / dataclass）。
- CLI としての出力
  - `--output PATH` が指定されている場合、そのパスに JSON を書き出す。
  - `--output -` または未指定の場合、標準出力に JSON を出力する。

---

## 11. 非機能要件（簡易）

- 安定性
  - 無効なファイルや front matter を検出した場合も、可能な限り index 生成を継続し、問題のあるファイルだけをスキップできることが望ましい。
- 拡張性
  - 新しいフィールド（例: `tags`, `owner`, `component` など）を SpecNode に追加する場合でも、既存コードが壊れないように設計する。
- 可観測性
  - `--verbose` オプションなどで、何ファイルをスキャンし、何件の SpecNode が生成されたかをログに出せることが望ましい。



