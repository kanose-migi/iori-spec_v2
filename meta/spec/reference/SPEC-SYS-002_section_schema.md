---
kind: reference
scope: spec_system
id: SPEC-SYS-002
spec_title: "iori-spec Section Schema"
stability: core # core|edge
status: draft # draft|review|stable|deprecated
---

# SPEC-SYS-002 Section Schema

## LLM_BRIEF

- kind: reference
- iori-spec の仕様書群で用いる **標準セクション（H2）**を定義し、`spec_sections_registry.yaml` / `spec_sections_guide.yaml` を SSOT とする。
- registry/guide と本仕様の整合ルールに基づき、ツールが `lint` と `context pack` を決定的に生成できる状態を定義する。

## このドキュメントの役割

- 本仕様が決めること（主題＋抽象度）:
  - セクション定義を担う 2 つの定義ファイル（registry/guide）の **ファイル形式（YAML）**と、ツールが前提とする **整合ルール（Cross-file invariants / lint 観点）**を定義する。
- 本仕様が決めないこと（委譲先）:
  - 各 `section_id` の **具体的な適用範囲・必須/任意・並び順・抽出対象**などの実データは `spec_sections_registry.yaml` を正とする。
  - 各 `section_id` の **purpose / guidelines / examples** などの記載ガイド本文は `spec_sections_guide.yaml` を正とする。
  - ツール実装の詳細（アルゴリズム、CLI I/F、CI 設定）は SPEC-SYS-005 を正とする。
- 本仕様が答える主要な問い:
  - registry/guide の必須キー・許容値・制約（lint 条件）は何か
  - registry と guide の `section_id` はどのように 1:1 対応し、違反はどう検出されるか
  - unknown section（registry 未定義の見出し）をどう扱うか（allow/warn/error）をどこで規定するか
  - `include_in`（index/render/pack）と `priority` をどう解釈し、生成物の決定性をどう担保するか
  - 外部SSOT（規範）を参照するための `Normative References` / 外部SSOTの内容を掲載する `Generated Snapshot` を標準セクションとして扱う場合、どこで規定し、抽出方針をどう置くべきか
  - 機械可読スキーマ（Validation Schema）と本仕様の優先関係はどうなるか

## 範囲（Scope）と前提

### 対象（In scope）

- `spec_sections_registry.yaml` / `spec_sections_guide.yaml` のファイル形式、主要フィールド、制約、および Cross-file invariants
- セクション抽出用途（`include_in`: `index` / `render` / `pack`）の概念と、unknown section の扱いポリシー
- H2 セクションの標準並び順（`priority` に基づく Ordering）

### 非対象（Out of scope）

- 各プロジェクト固有のセクション設計やガイド本文（registry/guide の実データ内容そのもの）
- ツール実装の詳細（抽出アルゴリズム、CLI I/F、CI ゲート構成）

### 前提（Assumptions）

- iori-spec は推奨 `kind` として下記をデフォルトで用意する（ただし `kind` は拡張可能）:
  - `steering / requirements / interfaces / data_contracts / tests / architecture / reference / dev_tasks / impl_notes`
- 仕様書（Markdown）は YAML front matter を持つ（必須キーは別仕様で定義）。
- registry で定義されたセクションは見出しレベル **H2 固定**かつ `heading` と **完全一致**させる（表記ゆれは missing 扱い）。
- registry 未定義の見出し（unknown section）は `policy.unknown_sections` に従って扱う（デフォルト `allow`）。

### 用語/定義（Definitions）

- `section_id`: セクションを同定する論理キー（template / lint / 抽出のキー）
- `heading`: 実際の Markdown H2 見出しテキスト（`##` を除いた文字列）
- `include_in`: 抽出用途の集合（`index` / `render` / `pack`）
- `Normative References（規範参照）`: 当該 spec が依拠する外部SSOT（規範ファイル）への参照を列挙する共通セクション（推奨）
- `Generated Snapshot（生成スナップショット）`: 外部SSOT内容の表示用スナップショット（DO NOT EDIT）を格納する共通セクション（推奨）
- `variant`: front matter の kind 内一次分類（SPEC-SYS-006）。`applies_to_variants` を用いたセクション分岐の入力。

## スキーマ表現（概念モデル）

概念モデルは **理解補助のための要約（非規範）** である。厳密な型・必須/任意・制約・エラー条件は
「定義ファイル仕様（Registry / Guide）」および「整合ルール（Cross-file invariants / lint）」を規範とする。
「定義ファイル仕様」および「整合ルール」に追従して更新するが、両者が矛盾する場合は **定義ファイル仕様側を正** とする。

### Registry / Guide の役割（概念）

- **Registry（`spec_sections_registry.yaml`）**：セクション構造の SSOT（何が必須か／どう識別するか／どの用途に抽出するか）
- **Guide（`spec_sections_guide.yaml`）**：Registry の `section_id` に紐づく記載ガイド（何を書くべきか）

### spec_sections_registry.yaml（主要フィールドの要約）

※完全な項目一覧・型・制約は「定義ファイル仕様（Registry）」を参照。

- `section_id`: セクションの論理 ID（テンプレ生成・lint・抽出のキー）
- `applies_to_kinds`: 適用 `kind` の集合（`"*"` は全 kind に適用するワイルドカード）
- `applies_to_variants`: 適用 `variant` の集合（省略時は全 variant。`variant` は SPEC-SYS-006）
- `heading`: 期待する見出し文字列（「H2 見出しのテキスト」に対応）
- `required`: 必須/任意
- `multiple`: 同一セクションの複数出現を許すか
- `include_in`: 抽出用途（`index` / `render` / `pack` の部分集合）
- `priority`: 並び順の安定化に使う整数（小さいほど先）

### spec_sections_guide.yaml（主要フィールドの要約）

※完全な項目一覧・型・制約は「定義ファイル仕様（Guide）」を参照。

- `section_id`: セクションの論理 ID（Registry と 1:1 対応）
- `purpose`: セクションの目的
- `guidelines`: 書き方の目安
- `examples`: 例（0..N、推奨 2）

### include_in の意味（用途概念）

- `index`：
  - 索引生成・検索・静的解析など、機械処理で参照する抽出対象に含める。
- `render`：
  - 人間向け表示のための **構造化ビュー**の抽出対象に含める。
  - unknown section の扱い（許容・警告・エラー）は `policy.unknown_sections (allow|warn|error)` に従う。
  - unknown_sections=allow のとき unknown は render しない（＝デフォルト非表示）
- `pack`：
  - LLM に渡す **局所コンテクスト**の抽出対象に含める。
  - 具体的にどのセクションを pack に含めるかは、Registry 側の `include_in` 設定が規範（ここでの例示は非規範）。

（NOTE: CLI のコマンド名は将来変わり得るため、仕様上は「用途概念（index/render/pack）」を安定値として固定する。）

### 外部SSOT参照と Snapshot の位置づけ（概念）

- `Normative References（規範参照）` は、spec が依拠する外部SSOT（例: rule catalog / profiles / schemas）を列挙し、閲覧・レビュー・ツール運用の導線を与えるための共通セクションである。
- `Generated Snapshot（生成スナップショット）` は、外部SSOTの内容を仕様書側に「書いてある状態」で提示するための表示用ブロックを収容する。内容は派生物であり、手編集しない（DO NOT EDIT）。

## セクションの並び順（Ordering）

- 本仕様が定義する priority は、テンプレ生成・表示・抽出の決定性を担保するための基準である。人間が読む仕様書の可読性と差分の安定性を高めるため、各ファイルは原則として以下の順序で H2 見出しを配置する。

### 全 kind 共通のセクション（core）の並び順

1. **LLM_BRIEF**（最短の意図・要点）
2. **このドキュメントの役割**（何を決め、何を決めないか）
3. **範囲（Scope）と前提**（適用範囲・前提・定義）
4. **kind 別本体セクション群**
   - 当該 kind に適用されるセクションを priority 昇順で並べる（registry の定義が正）。
5. **USAGE**（どう使うか：人間向け運用/参照方法）
6. **運用上の目安（LLM / SDD 観点）**（LLM運用・分割・更新ルール）
7. **Normative References（規範参照）**（外部SSOTの参照先。推奨）
8. **Generated Snapshot（生成スナップショット）**（外部SSOTの表示用スナップショット。推奨）
9. **READ_NEXT**

## 定義ファイル仕様（Registry / Guide）

本仕様は、セクション定義を担う 2 つの定義ファイル（registry/guide）の**ファイル形式（YAML）**と、ツールが前提とする**制約（invariants）**を規定する。

### `spec_sections_registry.yaml`（構造定義）

- 目的：仕様書群で使用可能なセクションをカタログ化し、各 `kind` に対する「必須/任意」「抽出対象」「並び順」を決定する。
- 推奨配置（標準）：
  - `<project_root>/.iori-spec/sections/spec_sections_registry.yaml`

- ルート構造：
  - `version: string`（例: `0.1`）

  - `policy: object`（任意）
    - `unknown_sections: (allow|warn|error)`（任意。デフォルト `allow`）
      - `allow`: unknown section を許容（lint はしない／抽出対象にはしない）
      - `warn`: unknown section を許容するが lint warning を出す
      - `error`: unknown section が存在したら lint error

  - `sections: SectionRule[]`

- `SectionRule`（1 セクション定義）

  - `section_id: string`（必須）
    - 正規形：`^[a-z][a-z0-9_]*$`（snake_case）
    - 同一 registry 内で一意（重複は `lint` エラー）

  - `heading: string`（必須）
    - Markdown の H2 見出し文字列（`##` を除いたテキスト）
    - 同一 `kind` 内での衝突は `lint` error（見出しテキストによる同定が曖昧になり、抽出・必須判定が不安定になるため）

  - `applies_to_kinds: string[]`（必須）
    - 当該セクションが適用される `kind` の集合（1 つ以上）
    - "*" は全 `kind` に適用するワイルドカードとする。

  - `applies_to_variants: string[]`（任意）
    - 当該セクションが適用される `variant` の集合（1 つ以上）
    - 省略時は「全 variant」に適用される。
    - 制約（簡素化のため）:
      - `applies_to_variants` を用いる場合、`applies_to_kinds` は **単一 kind**（かつ `*` を含まない）でなければならない（MUST）。
      - `variant` は SPEC-SYS-006 の `taxonomy.variants[kind]` により列挙される（推奨）。ツールは可能なら taxonomy に照らして検査する（MAY）。

  - `required: boolean`（必須）
    - `true` の場合、該当 `kind` の仕様書に当該セクションが存在しないことは `lint` エラー

  - `multiple: boolean`（必須）
    - `false` の場合、同一ファイル内に同一セクションが複数回出現したら `lint` エラー

  - `include_in: (index|render|pack)[]`（必須）
    - セクションを抽出対象に含める用途（`index` / `render` / `pack`）

  - `priority: integer`（必須）
    - 小さいほど先（テンプレ生成・抽出の決定性を担保）
    - 同一 `kind` 内で `priority` が同値の場合、ツールのタイブレークは `section_id` 昇順（決定性のため）。lint は warning を推奨する。

### `spec_sections_guide.yaml`（記載ガイド）

- 目的：registry の `section_id` に対し、「何を書くべきか」を一貫して提示できるようにする。
- 推奨配置（標準）：
  - `<project_root>/.iori-spec/sections/spec_sections_guide.yaml`

- ルート構造：
  - `version: string`（例: `0.1`）
  - `sections: SectionGuide[]`

- `SectionGuide`（1 セクションのガイド）
  - `section_id: string`（必須）
    - 同一 guide 内で一意（重複は `lint` エラー）
  - `purpose: string`（必須）
  - `guidelines: string`（任意）
  - `examples: Example[]`（任意。0..N、推奨 2）

- `Example`（例のオブジェクト）
  - `app: string`（必須）
    - プロジェクト名 + "（" + どんなアプリか簡潔な説明 + "）"
  - `title: string`（必須）
    - 例のタイトル
  - `content: string`（必須）
    - 例本文。該当セクションに何を記載すべきかを説明する。Markdown / 複数行テキストを想定
  - 注：将来拡張のため、`Example` 内の未知キーはツールが無視できる実装を推奨（互換性のため）

### Cross-file invariants（整合ルール）

- registry と guide は `section_id` により **1:1 対応**する。

  - registry に存在して guide に存在しない `section_id` は `lint` エラー
  - guide に存在して registry に存在しない `section_id` は `lint` エラー

### 機械可読スキーマ（Validation Schema）

- 上記のファイル形式は、別ファイルとして提供する機械可読スキーマ（YAML で表現した JSON Schema）でも検証できるようにする。
- スキーマは SPEC-SYS-002 の規範を機械的に表現したものであり、両者が不一致の場合は SPEC-SYS-002 を正とする。
- 推奨配置（例）：

  - `.iori-spec/schemas/sections/spec_sections_registry.schema.yaml`
  - `.iori-spec/schemas/sections/spec_sections_guide.schema.yaml`

## 全 kind 共通（core MUST）

`stability`: core を持つ spec で必須の H2 見出し：

- `## LLM_BRIEF`
- `## このドキュメントの役割`
- `## 範囲（Scope）と前提`
- `## USAGE`
- `## 運用上の目安（LLM / SDD 観点）`
- `## READ_NEXT`

## 全 kind 共通（core SHOULD）

`stability`: core を持つ spec で推奨される H2 見出し：

- `## Normative References（規範参照）`
- `## Generated Snapshot（生成スナップショット）`

### include_in の推奨デフォルト（非規範）

- `LLM_BRIEF`: `[index, render, pack]`
- `このドキュメントの役割`: `[index, render]`
- `範囲（Scope）と前提`: `[index, render]`
- `USAGE`: `[render]`
- `運用上の目安（LLM / SDD 観点）`: `[render]`
- `READ_NEXT`: `[index, render, pack]`
- `Normative References（規範参照）`: `[index, render, pack]`
- `Generated Snapshot（生成スナップショット）`: `[render]`（NOTE: 大容量化し得るため、既定では index/pack から除外することを推奨）

## 追加セクション（自由拡張）の扱い

- `policy.unknown_sections: allow` を前提とし、スキーマ未定義の追加見出し（自由セクション）を許容する。
- ただし、必須見出しの欠落や重複は lint で検出される。
- **registry で定義されたセクション**については、H2テキストは完全一致が MUST。**追加セクションは許容**（unknown扱い）

## lint 観点（本スキーマから導ける検査）

ツールは最低限、以下を検査できる。

- required セクションの欠落（error）
  - 対象は、当該 spec の `kind`（および `variant` がある場合は `applies_to_variants`）でフィルタされた Effective Section Rules とする
- 見出しの重複（`multiple: false` のセクションが複数回出現）
- `include_in` の値が許可集合 `{index, render, pack}` から外れていない
- `priority` の重複（同一 kind 内での衝突は warning。決定性が崩れるため）
- 見出し順序の逸脱（推奨順／`priority` 昇順から外れている場合は warning。テンプレ生成とレビューの安定性のため）

## 最小例（新規ユーザー / LLM 向け）

### `spec_sections_registry.yaml`（最小例）

```yaml
version: "0.1"
policy:
  unknown_sections: allow
sections:
  - section_id: llm_brief
    heading: "LLM_BRIEF"
    applies_to_kinds: ["requirements", "architecture"]
    required: true
    multiple: false
    include_in: [index, render, pack]
    priority: 10
```

### `applies_to_variants` を用いた例（参考）

```yaml
version: "0.1"
sections:
  - section_id: functional_requirements
    heading: "Functional Requirements"
    applies_to_kinds: ["requirements"]
    applies_to_variants: ["functional"]
    required: true
    multiple: false
    include_in: [index, render, pack]
    priority: 100

  - section_id: nonfunctional_requirements
    heading: "Nonfunctional Requirements"
    applies_to_kinds: ["requirements"]
    applies_to_variants: ["nonfunctional"]
    required: true
    multiple: false
    include_in: [index, render, pack]
    priority: 110
```

### `spec_sections_guide.yaml`（最小例）

```yaml
version: "0.1"
sections:
  - section_id: llm_brief
    purpose: |
      ファイル全体を LLM に渡したときに「何をさせたいか／何の仕様か」を 2〜4 行程度で端的に説明するセクション。
      kind（requirements / interfaces など）と、この spec がカバーする主なテーマを明示する。
    guidelines: |
      - 先頭行に必ず kind を明記する（書式固定）:
        - `- kind: <kind>`
        - `<kind>` は YAML front matter の `kind` と一致させる（front matter の再掲）。
      - 行数は 2〜4 行（上記の kind 行を含めて数える）。
      - LLM に依頼したいタスク（要件整理・IF 実装・テスト生成など）を具体的に書く。
      - 仕様の全文要約ではなく、「このファイルに何が書かれているか」と「どう使ってほしいか」に絞る。
      - 主テーマは 1〜2 点に圧縮する（複数テーマが混ざる場合は 1 ファイル 1 PURPOSE を優先し、分割を検討する）。
    examples:
      - app: "HabitLog（個人〜中規模向け習慣トラッカー）"
        title: "習慣作成機能 REQ の LLM_BRIEF"
        content: |
          - kind: requirements
          - HabitLog の「習慣作成機能」の要件を定義する。
          - 本 spec をもとに REST API・フォーム実装・E2E テストケースを生成/更新できる状態にする。
      - app: "BookMart（大規模オンライン書店／EC サイト）"
        title: "注文作成 API IF の LLM_BRIEF"
        content: |
          - kind: interfaces
          - BookMart の注文作成 API（IF-201）の外部仕様を定義する。
          - 決済・在庫の前提を整理し、本 spec をもとに実装と統合テストを安全に進められる状態にする。
```

## USAGE

### 想定読者（Who）

- 仕様書の作成・更新を行う編集者（人間/LLM）
- `spec_sections_registry.yaml` / `spec_sections_guide.yaml` のメンテナ（規約策定者）
- iori-spec ツール実装者 / CI・運用担当

### 参照タイミング（When）

- 標準セクションを追加・変更・廃止するとき（registry/guide を触るとき）
- `include_in`（index/render/pack）や `priority` の扱いを変えるとき
- unknown section の扱い（allow/warn/error）を変更するとき
- lint がセクション欠落・不一致・重複などを検知したとき

### 使い方（How）

- 変更は「registry（構造）」と「guide（記載）」を分けて行い、`section_id` の 1:1 対応を維持する。
- 見出しテキストは H2 で `heading` と完全一致させ、抽出・必須判定を決定的に保つ。
- 変更後は registry/guide の lint と、テンプレ生成・抽出（pack）の決定性が崩れていないことを確認する。

### セットで読む spec（With）

- SPEC-SYS-001 — 仕様書群の編集・参照フロー（運用規約）
- SPEC-SYS-005 — `index` / `lint` / `context pack` / CI ゲートの実行仕様

## 運用上の目安（LLM / SDD 観点）

### 更新トリガー（Trigger → Action）

- 標準セクションの追加/変更/廃止（`section_id` / `heading` / 適用 kind / required / include_in / priority の変更を含む）:
  - Action: registry と guide を **同一 PR**で更新し、`section_id` の 1:1 対応を維持する（必要ならテンプレ/生成物も同一 PR で更新）。
  - Action: `lint`（必須欠落・重複・見出し不一致・1:1対応）を実行し、warning/error を解消する。
- `include_in`（index/render/pack）の意味・抽出方針を変更する:
  - Action: 影響する成果物（pack/index/render）と契約（SPEC-SYS-004）・実行仕様（SPEC-SYS-005）を点検し、整合を取る。
- unknown section ポリシー（allow/warn/error）を変更する:
  - Action: lint の扱いと、人間向け render / LLM 向け pack の扱いが意図どおりになることを確認する（運用ルールは SPEC-SYS-001 と整合させる）。

### LLM 連携の原則（貼り方・渡し方）

- 最小セット: 本仕様の LLM_BRIEF + 変更対象セクション（diff）+ 期待成果物（例: registry/guide 更新案、lint 修正案）
- 拡張セット: 影響する registry/guide の該当箇所 + 関連する SPEC-SYS-001/004/005 の該当箇所

### ツール運用（lint / テンプレ生成 / 抽出）

- PR 時: registry/guide の `lint` を必須にし、`section_id` 1:1 対応・見出し一致・必須欠落を早期検出する。
- リリース前: テンプレ生成・抽出（pack）の決定性と、機械可読スキーマ（Validation Schema）検証が成立することを確認する。

### 更新時の作法（どう更新するか）

- 構造（registry）と記載ガイド（guide）を分離しつつ、`section_id` の 1:1 対応を破らないことを最優先にする。
- 見出し表記（H2 / `heading` 完全一致）と、抽出用途（`include_in`）と、並び順（`priority`）が **ツールの決定性**を崩さないことを確認しながら更新する。

## READ_NEXT

- SPEC-SYS-001 — 仕様書群の編集・参照・更新フロー（運用規約）
- SPEC-SYS-005 — `index` / `lint` / `context pack` / CI ゲートの実行仕様
- SPEC-SYS-004 — 生成物（index/pack/lint_report など）の成果物契約と互換性ルール
- SPEC-SYS-003 — `trace` の意味論とトレーサビリティ規約（関連仕様の前提）
