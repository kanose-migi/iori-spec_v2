---
kind: reference
scope: spec_system
id: ADR-SPEC-001
spec_title: "Front Matter に `variant` を導入し、kind 内一次分類でテンプレ生成を決定化する"
stability: edge
status: accepted
---

# ADR-SPEC-001 Front Matter に `variant` を導入し、kind 内一次分類でテンプレ生成を決定化する

## 1. 決定事項（Decision）

iori-spec は、YAML front matter に `variant` を導入し、**`kind` を維持したまま kind 内の一次分類を `variant` で表現**する。

- `variant` は **単一スカラー値**（配列不可）とする。
- `variant` は **kind ごとに enum で定義**される（taxonomy により許容値を決定）。
- テンプレ生成・lint・（必要に応じて）セクション適用は、原則として **`kind + variant`** を入力にして決定的に行う。
- 多軸の汎用分類（例：axes/facets の一般機構）は導入しない（仕様肥大の抑制）。

### 採択する `variant`（暫定 taxonomy）

- `requirements`: `functional` | `nonfunctional`
- `interfaces`: `external` | `internal`
- `tests`: `unit` | `integration` | `contract`
- `data_contracts`: `batch` | `event`（当面は任意運用から開始）

## 2. 背景（Context）

LLM が `REQ-*.md` 等の仕様書を作成する際、`requirements` 内の **機能要件/非機能要件**のように、テンプレ（必須観点・推奨セクション）が実質的に別物となるケースがある。

一方、分類機構を一般化しすぎると、iori-spec の仕様・ツール・学習コストが増大し、運用が重くなる。よって、最小の追加概念で **テンプレ生成の決定性**を確保する方針を採る。

## 3. 影響範囲（SPEC-SYS Impact Scope）

本ADRは、以下の SPEC-SYS に直接の変更（追記・拡張）を要求する。

### 3.1 MUST（規範の更新が必須）

- **SPEC-SYS-006（YAML front matter 仕様）**
  - `variant` フィールドを新設し、型・制約・解釈（lint、未知値、必須化ポリシー）を規定する。
  - kind ごとの許容 `variant` を決定する taxonomy の置き場所と読み込み規約（プロジェクト config）を規定する。

### 3.2 SHOULD（運用上、更新が強く推奨）

- **SPEC-SYS-005（Tooling Specification）**
  - lint が `variant` を検証する（kindごとの許容値、必須化、未知値）ことを規定する。
  - テンプレ生成（または prompt-bundle/context-bundle）が `kind + variant` を入力としてテンプレを選択できることを規定する。

- **SPEC-SYS-002（Section Schema / registry 仕様）**
  - セクション適用条件を、最小拡張として `applies_to_variants`（任意）で表現できるようにする（必要な場合のみ）。
  - 目的は「テンプレ生成時に、variant によりセクション集合を機械的に分岐」するため。

### 3.3 MAY（必要性が出た段階で更新）

- **SPEC-SYS-004（Stable Artifact Contract）**
  - `index` / `pack` のメタに `variant?: string` を含めるかは任意。
  - ただし後続工程（テンプレ再生成・統計・検索・ゲート）で利点があるため、互換性を崩さない形（optional）で追加する余地を残す。

- **SPEC-SYS-001（Spec System Guide）**
  - 人間/LLM 向けに「どの kind で variant を付けるべきか」「未指定時の扱い」など運用ガイドを追記する余地がある。

### 3.4 影響なし（本ADRの対象外）

- **SPEC-SYS-003（Traceability Rule）**
  - `kind` の分割や多軸化を行わないため、トレース規約の根本変更は不要。
  - 将来、variant ごとに必須トレースが変わる場合のみ拡張を検討する。

## 4. 仕様（Normative Semantics）

### 4.1 Front matter: `variant`

- 形式:
  - `variant` は lower_snake_case を推奨（例：`nonfunctional`, `integration`）。
  - `variant` は単一スカラー（string）。
- 有効性:
  - `variant` の許容値は kind ごとの enum により決定される（taxonomy）。
  - kind が variant を定義している場合、`variant` を **必須（error）**にするか、**警告（warn）**にするかはツールポリシーで選べる。
- 意味:
  - テンプレ生成・lint・セクション適用の分岐の一次入力は `kind + variant` とする。

### 4.2 Taxonomy（kind ごとの許容 `variant`）

- プロジェクト設定（例：`.iori-spec/config.yaml`）に、kind→variant列挙を定義する。
- 仕様としては「SSOT は taxonomy」。front matter はそれに従う。

例（概念）:

```yaml
taxonomy:
  variants:
    requirements: [functional, nonfunctional]
    interfaces: [external, internal]
    tests: [unit, integration, contract]
    data_contracts: [batch, event]
```

````
### 4.3 Section registry（最小拡張）

必要な場合のみ、セクションに `applies_to_variants` を追加できる。

- 適用条件（概念）:

  - `applies_to_kinds` に一致し、
  - かつ `applies_to_variants` が無い、または `variant` が列挙に含まれる場合に適用。

例（概念）:

```yaml
- section_id: slos
  applies_to_kinds: ["requirements"]
  applies_to_variants: ["nonfunctional"]
```

## 5. 期待される効果（Consequences）

- **テンプレ生成の決定性**: `kind + variant` により、LLM に渡すテンプレが一意に決まる。
- **仕様肥大の抑制**: 多軸一般機構を導入せず、追加概念を `variant` に限定する。
- **運用の安全性**: 付け忘れ・誤指定は lint で機械的に検出できる。
- **拡張余地**: 必要なら `interfaces` / `tests` / `data_contracts` でも同一機構で分岐できる。

## 6. 代替案（Considered Alternatives）

- kind の細分化（例：`nonfunctional_requirements` を kind に追加）

  - 却下: `kind` の増殖・SSOT の肥大・保守コスト増。
- 多軸分類（axes/facets の一般機構）

  - 却下: 表現力は高いが、仕様の表面積と学習コストが大きい。
- Tag のみで一次分類（例：`req:functional`）

  - 却下: 決定性・検証性・表記揺れの観点で一次SSOTに不向き。

## 7. 移行方針（Migration）

- 既存ファイルは `variant` 未指定でも直ちに破壊しない（後方互換）。
- lint ポリシーは段階導入とする:

  - Phase 1: kind が variant を持つ場合、未指定を warn
  - Phase 2: 対象 kind（まず `requirements`）のみ error に引き上げ
- テンプレ生成は `kind+variant` 指定を優先し、未指定の場合は生成を拒否またはベーステンプレのみ生成（ツール方針で規定）。

## 8. オープン事項（Open Questions）

- `variant` taxonomy を SPEC-SYS-006 に完全内包するか、プロジェクト config を SSOT として参照するか（推奨は config SSOT）。
- `data_contracts` の `variant` をいつ必須化するか（運用開始後の実態に合わせて判断）。
- `SPEC-SYS-004` の index/pack に `variant` を含めるか（optional 追加の可否と互換方針）。
````
