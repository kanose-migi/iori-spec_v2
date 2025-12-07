---
kind: reference
scope: meta
id: REF-100
spec_title: "仕様書の書き方・ID/構造ルール"
status: review        # draft / review / stable
---
# 仕様書の書き方・ID/構造ルール

## LLM_BRIEF
仕様書の型・IDルール・front matter 必須項目をまとめた基準書。iori-spec の lint / index / trace が前提とする仕様形状をここで定義する。

## USAGE
- 新規に仕様ファイルを作る前に、必須の front matter と heading 構造を確認する。
- 既存仕様を lint で修正するときに、ID 命名やセクション構成の判断基準として参照する。
- LLM に仕様の書き方や ID ルールを説明する際の一次参照として渡す。

## READ_NEXT
- [reference/spec_structure_and_traceability.md](./spec_structure_and_traceability.md)
- [reference/iori_spec_section_schema_guide.md](./iori_spec_section_schema_guide.md)
- [reference/iori_spec_config.yaml](./iori_spec_config.yaml)
- [reference/spec_section_schema.yaml](./spec_section_schema.yaml) — セクション構造の SSOT（YAML）
- [reference/sample/spec_section_schema.sample.yaml](./sample/spec_section_schema.sample.yaml) — スキーマのサンプルコピー

## 1. このドキュメントの役割

- `iori-spec/` 以下に置かれる「仕様書」の共通ルール（front matter, ID, 見出し構造など）を定める。
- iori-spec が仕様書を parse / index / trace するときの前提条件を明文化する。
- 新しく仕様ファイルを追加するときに、「どこに・どういう形式で書けばよいか」を迷わないようにする。
- 仕様の新規作成・追加・変更の手順を統一し、**REQ / IF / DATA / TEST の整合性**を保つ。
- 人間と AI が同じルールで仕様を読み書きできるようにする。
- 実装時に「どのファイルを読めばよいか」「どのファイルを同期すべきか」を迷わないようにする。
- プロンプト時に不要なコンテキストを貼りすぎず、**SDD (Specification Driven Development)** を効率よく回せるようにする。
- セクション構造の正本は `spec_section_schema.yaml`（YAML, 機械可読）とし、本ガイド／section schema ガイドはその自然言語説明として位置づける。

## 2. 範囲（Scope）と前提

このメタ仕様の対象範囲：

- `requirements/*.md`（REQ）
- `interfaces/*.md`（IF）
- `data_contracts/*.md`（DATA）
- `tests/*.md`（TEST）
- `architecture/*.md` のうち、Traceability に関係する部分

アプリケーションコードや CI 設定、そのほかの一般的なドキュメントは対象外とする。

## 3. 運用上の目安（LLM / SDD 観点）

- LLM に渡すときは `LLM_BRIEF` と合わせて、必要なセクションを最小限に抜粋する（全文貼りを避ける）。
- lint で指摘された場合は、本書と `spec_section_schema.yaml` を突き合わせて heading 不足を補う。
- ID 追加・命名を行うときは、`vocab` の kind/scope に合致するかと重複の有無を確認する。
- コアと拡張を分けたい場合は、拡張ノードの front matter に `extension: true` を付ける。trace lint は拡張の未トレース/孤立を WARN 扱いとし、`extension` が無いものはすべてコア扱い（ERROR 対象）とする。

## 4. ID 空間とファイル対応

### 4.1 ID 種別

- **REQ-xxx** (Requirements): `requirements/REQ-xxx_*.md`（例: `requirements/REQ-800_tooling_cli.md`）
- **IF-xxx** (Interfaces): `interfaces/IF-xxx_*.md`（例: `interfaces/IF-900_tooling_cli.md`）
- **DATA-xxx** (Data Contracts): `data_contracts/DATA-xxx_*.md`
- **TEST-xxx** (Tests): `tests/TEST-xxx_*.md`
- **REF-xxx** (Reference / Meta): `reference/*.md`。`REF-` に続く3桁以上の数字を必須とする

### 4.2 Traceability Map

- `artifacts/traceability_map.md` は `iori-spec trace report` が front matter の `trace.*` と SpecIndex から生成するビュー（手書きしない）。
- IF や DATA を新規作成・変更した場合は、`trace.*` を更新し、必要に応じて Traceability Map を再生成する。
- 拡張機能（`extension: true`）のノードも trace report には出力してよいが、カバレッジ判定は WARN に緩和する。

## 5. 参照順ルール（タスク別フロー）

### 5.1 IF を実装するとき（コードを書くとき）

1. 対象の `IF-xxx` を決める（例: IF-900）
2. `interfaces/IF-xxx_*.md`（例: `interfaces/IF-900_tooling_cli.md`）を読む（入出力・前提・エッジケース）
3. 仕様内で参照されている `DATA-xxx` を `data_contracts/*.md` から読む
4. 必要に応じて、対応する `REQ-xxx` を `requirements/REQ-xxx_*.md` で確認する
5. テストを書く場合は `tests/TEST-xxx_*.md` を参照する

### 5.2 新しい IF を追加するとき（新しい処理ステージ）

1. まず REQ を決める（`requirements/REQ-xxx_*.md` に追加するか既存 REQ に紐づける）
2. 必要なら DATA を定義する（入出力となる `DATA-yyy` を `data_contracts/DATA-yyy_*.md` に追加）
3. IF を定義する：`interfaces/IF-zzz_<short_name>.md` を作成し、front matter と対応 ID を記述
4. TEST を定義する：`tests/TEST-zzz_<short_name>.md` に受入条件・テストケースを記述
5. `trace.*` を埋め、必要に応じて Traceability Map を再生成する

### 5.3 DATA 契約（データ構造）を変更するとき

1. `data_contracts/DATA-xxx_*.md` を修正する（ここが SSoT）
2. その DATA を参照する IF を検索し、入出力定義を同期する
3. 対応する TEST を更新する（フィールド変更時はテストケースも見直す）
4. 必要に応じて `architecture/ARCH-900_tooling_core.md` など関連図を更新する
5. `trace.*` が古くなっていないか確認し、必要に応じて Traceability Map を再生成する

### 5.4 REQ を変更・追加するとき

1. `requirements/REQ-xxx_*.md` で `REQ-xxx` を編集・追加
2. 影響を受ける IF を確認（`interfaces/` で `REQ-xxx` を検索）
3. 仕様やテストに影響があれば、対応する IF / DATA / TEST を更新する
4. `trace.*` を更新し、必要に応じて Traceability Map を再生成する

## 6. ファイル命名ルール / Naming Conventions

### 6.1 IF ファイル

- 本体 spec: `interfaces/IF-xxx_<short_name>.md`（例: `interfaces/IF-900_tooling_cli.md`）。原則1ファイル1ID。

#### front matter の例（最小構成）

```markdown
---
kind: interfaces
scope: tooling.cli
id: IF-900
spec_title: "IF-900: iori-spec CLI (例)"
status: draft
# extension: true  # 拡張扱いにする場合のみ付与（任意）
trace:
  req:
    - REQ-800
  if: []
  data:
    - DATA-900
  test: []
  task: []
dp:
  produces: []
  produced_by: []
  consumes:
    - DATA-900
  inputs: []
doc:
  read_next:
    - requirements/REQ-800_tooling_cli.md
  see_also: []
---
# IF-900: iori-spec CLI (例)
```

- セクション見出しは `spec_section_schema.yaml`（正本）に従う。サンプル構造は `reference/iori_spec_section_schema_guide.md` や `reference/sample/spec_section_schema.sample.yaml` を参照。
```

## 7. ID・見出しブロックのルール（概要）

### 7.1 ID ブロックの見出し形式

- ID を持つブロックはすべて **見出しレベル 2（`##`）** とする：

```markdown
## REQ-101: index コマンドで仕様 ID 一覧を取得できること
## IF-001: メイン CLI インターフェイス
## DATA-001: index 出力 JSON
## TEST-001: CLI スモークテスト
## TASK-IF-001-01: main CLI エントリの実装
```

### 7.2 ID ブロック直下のタグ行

- ID 見出しの直下には、必要に応じて **機械可読なタグ行**（`- [key] value`）を置く：

```markdown
## REQ-101: index コマンドで仕様 ID 一覧を取得できること

- [level] MUST
- [area] cli.index
- [rel-IF] IF-001
- [rel-DATA] DATA-001
- [rel-TEST] TEST-001
```

- 代表的な key：
  - `level`（MUST / SHOULD / MAY / INFO）
  - `area`（scope より細かい分類）
  - `rel-REQ` / `rel-IF` / `rel-DATA` / `rel-TEST` / `rel-TASK`（関連 ID）

## 8. ディレクトリ構成と役割（概要）

- `steering/`：プロダクトビジョン・スコープ・非ゴール
- `requirements/`：機能 / 非機能 / トレースマップ（REQ-xxx）
- `architecture/`：コンポーネント / レイヤー / データフロー
- `interfaces/`：外部インターフェイス（IF-xxx）
- `data_contracts/`：スキーマ・フォーマット（DATA-xxx）
- `tests/`：テスト観点 / ケース（TEST-xxx）
- `reference/`：本ガイド、用語集、命名規約など
- `dev_tasks/`：実装タスク（TASK-xxx）
- `impl_notes/`：実装メモ・設計検討ログ（自由形式）

## 9. iori-spec と iori_spec_guide の関係

- iori-spec のパーサ・CLI コマンドは、原則として本ガイドを前提に実装される。
- 本ガイドの変更は「仕様書の型そのものの変更」を意味するため、ツール実装や既存 docs への影響をレビューすること。
