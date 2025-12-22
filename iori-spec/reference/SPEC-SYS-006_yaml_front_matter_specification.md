---
kind: reference
scope: spec_system
id: SPEC-SYS-006
spec_title: "iori-spec YAML Front Matter Specification (Schema & Rules)"
stability: core # core|extension
status: draft # draft|review|stable|deprecated
---

# SPEC-SYS-006 YAML Front Matter Specification (Schema & Rules)

## LLM_BRIEF

- kind: reference
- 本仕様は、iori-spec の各 spec ファイル先頭に置く **YAML front matter** の「必須キー・型・記法・拡張方針」を SSOT として定義する。
- 本仕様は **front matter としての配置・必須性・型制約**を規範化する。
- `trace` の意味論・記法は SPEC-SYS-003、ツール成果物（index/pack/lint_report）の契約は SPEC-SYS-004、設定解決と profile/gate は SPEC-SYS-005 を正とする。

## このドキュメントの役割

### 何を決めるか（本仕様の SSOT）

- YAML front matter の **構文上の制約**（位置、区切り、許容する YAML 機能の範囲）
- 必須キー（`kind/scope/id/spec_title/status/stability`）の **一覧・型・許容値**
- `kind`（グローバル enum）と `scope`（プロジェクト taxonomy）の **設計と検査方針**
- 追加メタデータの **拡張方針**（既存 Consumer を壊さない拡張の作法）
- front matter 由来の **lint ルール（ルールID）**の定義

### 何を決めないか（委譲先）

- セクション定義（H2 見出し、include_in、ordering）: SPEC-SYS-002
- `trace` の意味論・整合性ルール・ルールID体系: SPEC-SYS-003
- index/pack/lint_report の成果物契約・互換性・決定性: SPEC-SYS-004
- lint の実行モデル、CI ゲート、exit code / プロファイル運用: SPEC-SYS-005

## 範囲（Scope）と前提

### 対象（In scope）

- iori-spec の spec ファイル（Markdown、1ファイル1ID）における YAML front matter の規約。

### 非対象（Out of scope）

- YAML 自体の一般仕様の網羅（本仕様は「運用上許容する最小サブセット」を定めるに留める）
- front matter 以外の本文構造（→ SPEC-SYS-002）
- 成果物の型定義・正規化（→ SPEC-SYS-004）
- 設定解決・プロファイル運用の詳細（→ SPEC-SYS-005）

### 前提（Assumptions）

- 仕様ファイルは YAML front matter を持つ（MUST）。
- `id` はグローバル一意であり参照可能である（MUST）。
- front matter は「仕様そのもの」ではなく「仕様をチェックする側（ツール側）の都合」で導入されるメタ情報である。
  - そのため、front matter を **最小・機械的**に保つことを推奨（SHOULD）。

## Quickstart（最小で“合格”する書き方）

最小の front matter（trace なしの例）:

```yaml
---
kind: reference
scope: spec_system
id: SPEC-SYS-006
spec_title: "iori-spec YAML Front Matter Specification (Schema & Rules)"
stability: core
status: draft
---
```

`scope` のサブ分類（root.subpath）例:

```yaml
---
kind: requirements
scope: cli.index
id: REQ-010
spec_title: "CLI: index コマンド要件"
stability: core
status: draft
---
```

## 規範キーワード

本仕様は RFC 2119 に準拠する意味で以下を用いる。

- **MUST**（必須）: 満たさない場合、仕様違反
- **MUST NOT**（禁止）: 満たす場合、仕様違反
- **SHOULD**（推奨）: 原則満たす。満たさない場合、合理的理由を説明できること
- **MAY**（任意）: 必要に応じて選択

## 用語/定義（Definitions）

- **Front matter**: Markdown ファイル先頭に置かれる `---` で囲まれた YAML ブロック。
- **必須キー（Required keys）**: 全 spec が必ず持つべき front matter キー集合。
- **kind（グローバル enum）**: iori-spec が「ファイルをどう扱うか」を決める分類キー。
- **scope（project taxonomy）**: プロジェクト内の分類軸。`root` は enum で検査し、`.subpath` は自由分類。
- **Taxonomy**: `kind`/`scope` の許容語彙を列挙した一覧（config 経由で供給され得る）。

## YAML front matter の記法（Syntax）

### 1) 位置と区切り

- front matter は、ファイルの **最初**に置かなければならない（MUST）。

  - 許容: UTF-8 BOM のみ（存在してもよい）。
  - 禁止: front matter より前に本文・見出し・空行以外の文字列がある（MUST NOT）。
- front matter は次の区切りで囲む（MUST）。

  - 開始行: `---`
  - 終了行: `---`
- front matter は YAML の **単一のマッピング（object）**でなければならない（MUST）。
- YAML の複数ドキュメント（`---` が複数回現れる等）は禁止（MUST NOT）。

### 2) 許容する YAML 機能（運用サブセット）

互換性・決定性・実装容易性のため、front matter は次のサブセットに制限する。

- 許容（ツールが対応しなければならない MUST）

  - スカラー（string/bool/number として YAML が解釈し得る値）
  - 配列（sequence）
  - オブジェクト（mapping）

- 禁止（MUST NOT）

  - アンカー/エイリアス/マージ（`&` / `*` / `<<:`）
  - 任意タグ（`!Something`）
  - 暗黙の型付けに依存する表現（timestamp 等）を必須キーに用いること

> NOTE: YAML パーサに依存する“暗黙変換”を避けるため、必須キー値は **文字列として解釈される書き方**を推奨する（後述）。

### 3) キー命名規約

- 本仕様が定義するキーは **lower_snake_case** とする（MUST）。
- 必須キー名は固定であり、別名は設けない（MUST NOT）。

## 必須キー（Required Keys）

全 spec は、以下 6 キーを front matter に含めなければならない（MUST）。

- `kind`（enum string, MUST）
- `scope`（string, MUST）
- `id`（string, MUST）
- `spec_title`（string, MUST）
- `status`（enum string, MUST）
- `stability`（enum string, MUST）

> NOTE: front matter はツール都合のメタ情報であるため、「人間に意味がある」軸は主に `kind/scope/spec_title/status` に集約される。
> 一方で iori-spec の運用不変条件（1ファイル1ID、Stable Core 境界）を満たすため、`id/stability` も必須とする。

## `kind`（MUST, global enum）

### 型と書式

- 型: string（MUST）
- 書式: `^[a-z][a-z0-9_]*$`（MUST）
- 空文字は不可（MUST NOT）。

### 許容値（Effective Kinds）

`kind` は **iori-spec が列挙する enum**であり、ツールが扱い方（例: セクション適用、lint 期待、pack 既定）を決めるキーである。

- ツールは少なくとも以下の kind を **既定でサポート**しなければならない（MUST）。

  - `steering`
  - `requirements`
  - `interfaces`
  - `data_contracts`
  - `tests`
  - `architecture`
  - `reference`
  - `dev_tasks`
  - `impl_notes`

- さらに、プロジェクトローカルで kind を増やす場合、config により追加語彙を供給してよい（MAY）。

  - 追加語彙を解決した最終集合を **Effective Kinds** と呼ぶ。

### 検査方針（lint）

- `kind` が Effective Kinds に含まれない場合、lint は **違反**として報告しなければならない（MUST）。

  - 重大度（error/warn/info）や CI ゲートは profile/gate（SPEC-SYS-005）で決める。
  - ただし parse/scan/index 生成は、未知 kind があっても可能な限り継続する（SHOULD）。

## `scope`（MUST, project taxonomy + exception tolerant）

### 型と書式（ドット階層）

- 型: string（MUST）
- 書式: `root` または `root.subpath`（`.` 区切り）とする（MUST）。

#### トークン規則

- `scope` は `.` で分割したトークン列 `t0, t1, ...` として解釈する。
- 各トークンは `^[a-z][a-z0-9_]*$` を満たす（MUST）。
- 先頭トークン `t0` を **scope_root** と呼ぶ。
- `t1..`（存在する場合）を **scope_subpath** と呼ぶ。

例:

- `functional` → scope_root=`functional`
- `cli.index` → scope_root=`cli`, scope_subpath=`index`
- `builder.pipeline.v2` → scope_root=`builder`, scope_subpath=`pipeline.v2`

### Taxonomy による検査（root のみ）

`scope` はプロジェクトごとに語彙が異なるため、**project taxonomy（enum）**に基づいて scope_root を検査する。

- ツールは、project taxonomy（`taxonomy.scopes`）が提供されている場合、

  - `scope_root` がその一覧に含まれるかを検査しなければならない（MUST）。
- `scope_subpath` の内容はプロジェクト/人間側の自由分類であり、ツールは原則として検査しない（MAY）。

### 例外許容（warning）

- `scope_root` が taxonomy に存在しない場合、lint は **「未定義 scope_root」**として報告する（MUST）。
- ただし v1 の既定運用として、これは **即エラーに固定しない**（warning 想定）。

  - 重大度はプロファイルで制御できる（SPEC-SYS-005）。

## `id`（MUST）

- 型: string（MUST）
- 意味: グローバル一意の仕様 ID
- 制約:

  - 空文字は不可（MUST NOT）
  - スペースを含めない（MUST NOT）
  - 1ファイル1ID、および置換運用は SPEC-SYS-001 / SPEC-SYS-003 に従う（MUST）

## `spec_title`（MUST）

- 型: string（MUST）
- 意味: 人間・LLM が読むタイトル（表示用）
- 制約:

  - 空文字は不可（MUST NOT）
  - 記号を含む場合は YAML として安全なように引用符で囲むことを推奨（SHOULD）

## `status`（MUST）

- 型: string（MUST）
- 許容値（Stable Core）:

  - `draft` / `review` / `stable` / `deprecated`（MUST）
- 上記以外は禁止（MUST NOT）

## `stability`（MUST）

- 型: string（MUST）
- 許容値（Stable Core）:

  - `core` / `extension`（MUST）
- 上記以外は禁止（MUST NOT）

## 任意キー（Optional Keys）

### `trace`（MAY）

- 型: object（MUST if present）
- 役割: spec 間の関係（有向エッジ）の SSOT。
- 記法・意味論・制約: SPEC-SYS-003 を正とする（MUST）。
- REQ の最小カバレッジ条件（satisfied_by / verified_by 等）は SPEC-SYS-003 の規定に従う。

### `extensions`（MAY）

- 型: object（MUST if present）
- 目的:追加メタデータは `extensions` 配下に隔離する（SHOULD）。
- `extensions` の直下は **名前空間単位**で分割する（SHOULD）。
  - 例: `extensions: { project: {...}, tooling: {...} }`

```yaml
---
kind: reference
scope: spec_system
id: SPEC-SYS-999
spec_title: "Example with extensions"
stability: extension
status: draft
extensions:
  project:
    owner: "team-abc"
    ticket: "JIRA-123"
  tooling:
    lint_profile_hint: "relaxed"
---
```

## Project Taxonomy（config 経由）

### 位置（推奨）

project taxonomy は、既定の config 位置（SPEC-SYS-005）に含めることを推奨する（SHOULD）。

- `<spec_root>/.iori-spec/config.yaml`

### 最小スキーマ（本仕様が追加する部分）

config の最小スキーマは SPEC-SYS-005 を正とし、本仕様は以下の `taxonomy` を追加で定義する。

```yaml
taxonomy:
  kinds: # 任意（MAY）。追加 kind（Effective Kinds の拡張）として扱う
    - dev_tasks
    - impl_notes
  scopes: # 推奨（SHOULD）。scope_root の推奨語彙（project enum）
    - spec_system
    - functional
    - nonfunctional
    - traceability
    - cli
    - builder
    - docs
```

### 検査規約

- `taxonomy.scopes` が存在する場合、`scope_root` の未定義は報告対象（MUST）。
- `taxonomy.scopes` が存在しない場合、ツールは scope_root の enum 検査を行わない（MAY）。

  - ただし、プロジェクトに taxonomy 導入を促す目的で info を出してよい（MAY）。

## lint 観点（本仕様から導ける検査）

本仕様は、lint が指摘するための標準ルール ID を定義する。
重大度（error/warn/info）と CI ゲートはプロファイルで定義する（SPEC-SYS-005）。

### ルールID体系（Front Matter）

- **FM001**: YAML front matter が存在しない
- **FM002**: YAML front matter が parse できない
- **FM003**: front matter が単一 mapping ではない
- **FM010**: 必須キー欠落（`kind/scope/id/spec_title/status/stability` のいずれか）
- **FM011**: 必須キーの型不正（例: `id` が配列）
- **FM012**: `kind` が Effective Kinds に含まれない（未知 kind）
- **FM013**: `scope` の書式不正（ドット階層/トークン規則違反）
- **FM014**: `scope_root` が taxonomy.scopes に存在しない（未定義 scope_root）
- **FM015**: `status` が許容値でない
- **FM016**: `stability` が許容値でない
- **FM020**: top-level に未知キーがある（`extensions` へ移すべき）※推奨違反（SHOULD）

## 記載例（Examples）

### 1) `scope_root` のみ

```yaml
---
kind: requirements
scope: functional
id: REQ-001
spec_title: "YAML 辞書のインポート"
stability: core
status: draft
---
```

### 2) `scope_root.subpath`（root のみ lint）

```yaml
---
kind: requirements
scope: cli.index
id: REQ-010
spec_title: "CLI: index コマンド要件"
stability: core
status: draft
---
```

### 3) 未定義 scope_root（warning 想定）

```yaml
---
kind: requirements
scope: weird.experimental
id: REQ-999
spec_title: "実験: 新しい分類の検討"
stability: extension
status: draft
---
```

## USAGE

### 想定読者（Who）

- spec の作成者（REQ/IF/DATA/TEST/steering 等の執筆者）
- レビュア（front matter 規約違反の検出・是正担当）
- ツール実装者（parse/validation/index 実装担当）

### 参照タイミング（When）

- 新規 spec 作成時（front matter を先に確定し、1ファイル1IDの前提を満たす）
- lint で front matter 由来の指摘（FM***）が出たとき（原因特定と是正）
- taxonomy（kinds/scopes）を導入・更新するとき（Effective Kinds / scope_root 検査の整合）
- YAML front matter の許容サブセット（禁止機能・書式）を見直すとき（互換性・決定性への影響があるため）

### 使い方（How）

- まず必須キー 6 点（`kind/scope/id/spec_title/status/stability`）を満たす。
- `kind` はグローバル enum（Effective Kinds）として lint 対象、`scope` は `root`（taxoで検査）＋必要なら `.subpath`（自由分類）として扱う。
- 追加メタデータは top-level に増やさず、`extensions` 配下に隔離する（Consumer 互換性を維持するため）。
- `trace` を使う場合は、本仕様ではなく SPEC-SYS-003 の Syntax/Semantics を正として従う。

### セットで読む spec（With）

- SPEC-SYS-005 — lint/CI ゲート、プロファイル運用、exit code（FM 由来指摘の運用と接続）
- SPEC-SYS-004 — index/pack/lint_report の成果物契約（front matter が index にどう反映されるか）
- SPEC-SYS-003 — `trace` の意味論・記法（front matter の `trace` を扱う場合の SSOT）

## 運用上の目安（LLM / SDD 観点）

### 更新トリガー（Trigger → Action）

- 必須キーの追加/削除、必須キーの型変更、`status`/`stability`/`kind` の許容値変更:
  - Action: **Breaking になり得る**ため、STEER-002 の互換性方針（deprecation 推奨）に従い、移行期間・lint 指摘（WARN→ERROR 等）の段階導入を設計する。
  - Action: SPEC-SYS-004（index へ出す front_matter shape）と SPEC-SYS-005（lint/CI ゲート運用）を点検し、必要なら同一 PR で追随させる。
- `scope` taxonomy の検査方針変更（taxonomy 必須化、未定義 scope_root の重大度変更など）:
  - Action: taxonomy の供給元（config）と lint ルール（FM014 等）の期待挙動を揃え、CI での Gate 影響を明記する（運用は SPEC-SYS-005）。
- YAML front matter の許容サブセット変更（アンカー禁止などの範囲変更）:
  - Action: パーサ互換性・実装容易性・決定性への影響を評価し、scan/index の継続可否（可能な限り継続）と `complete=false` の扱い（SPEC-SYS-004）を含めて整合を取る。
- front matter 由来の lint ルール ID（FM***）の追加/変更:
  - Action: ルール ID の意味を本仕様で固定し、重大度はプロファイル（SPEC-SYS-005）で運用する方針を維持する。

### LLM 連携の原則（貼り方・渡し方）

- 最小セット: 本仕様の LLM_BRIEF + 変更対象（front matter の差分 or 違反箇所）+ 期待成果物（例: 正しい front matter 提案、FM 指摘の修正案）
- 拡張セット: taxonomy（config の該当部分）+ 関連 SSOT（SPEC-SYS-003/004/005 の該当箇所）
- 実務上のコツ:
  - spec 新規作成は、本文より先に front matter（6キー）を確定させると、後工程（index/lint/pack）が安定する。

### ツール運用（lint / index 連携 / CI）

- PR 時: front matter 由来の lint 指摘（FM***）を早期に解消し、`kind/scope/id` の揺れを放置しない（index の探索性・影響分析が崩れるため）。
- taxonomy 導入時: 未定義 scope_root を “即 ERROR 固定” にしない運用（warning 想定）を取る場合は、プロファイルと Gate 閾値の組み合わせで段階導入する。

### 更新時の作法（どう更新するか）

- front matter はツール都合のメタ情報であるため、**最小・機械的**を優先する（情報増は `extensions` に隔離）。
- 互換性に影響する変更（必須キー変更、許容値変更、検査方針変更）は、必ず STEER-002 の方針に従い、段階導入（deprecation → enforcement）を設計する。

## READ_NEXT

- SPEC-SYS-001 — 仕様書群の運用フローと編集不変条件（1ファイル1ID 等）。
- SPEC-SYS-002 — セクション定義（registry/guide）、Ordering、unknown section policy。
- SPEC-SYS-003 — `trace` の意味論・記法・最小整合性ルール。
- SPEC-SYS-004 — index/pack/lint_report の成果物契約と互換性・決定性。
- SPEC-SYS-005 — lint/CI ゲート、プロファイル運用、exit code。
- STEER-002 — Stable Core 境界、拡張点（extensions）、互換性と deprecation の上位方針。
