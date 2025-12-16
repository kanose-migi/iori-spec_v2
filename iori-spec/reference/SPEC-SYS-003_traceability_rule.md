---
kind: reference
scope: spec_system
id: SPEC-SYS-003
spec_title: "iori-spec Traceability Specification (Ruleset)"
stability: core
status: draft
---

# SPEC-SYS-003 Traceability Specification (Ruleset)

## LLM_BRIEF

- kind: reference（scope: spec_system）
- 本仕様は、iori-spec における `trace`（トレーサビリティ）を、機械可読な **有向グラフ**として扱うための **意味論（semantics）・記法（syntax）・最小整合性ルール** を定義する。
- 主目的は、REQ が **実装可能（IF/DATA）** かつ **検証可能（TEST）** な状態で維持されることを、ツールで点検・可視化できるようにすること。
- `trace` は関係（edge）の **SSOT** とし、本文の ID 言及（mentions）は **補助情報**として扱う。

## このドキュメントの役割

### 何を決めるか（本仕様の責務）

- `trace` を「ID 間の関係（Edge）」の **SSOT** として定義し、仕様ファイル群を **グラフ**として扱えるようにする。
- `trace` の **意味論（Semantics）・記法（Syntax）・最小整合性ルール** を定義し、ツールが機械的に点検できる最小核（core）を与える。
- REQ が IF/DATA/TEST により **実装可能・検証可能** な形に落ちているかを、最小カバレッジ条件として定義する。
- lint が指摘するための **標準ルール ID（Lint Rule Catalog）** を定義する（重大度や CI ゲートは別管理）。

### 何を決めないか（委譲先）

- lint の実行方法、終了コード、CI ゲートの詳細（→ SPEC-SYS-005）
- index / graph export / context bundle / lint report 等のツール出力の互換性契約（→ SPEC-SYS-004）
- kind 定義・セクション定義の SSOT（→ SPEC-SYS-002）

### 本仕様が答える主要な問い（チェックリスト）

- `trace` を YAML front matter にどう記述するか（許容形式・禁止事項は何か）。
- どのエッジ型が標準で、各エッジ型は何を意味するか（Semantics）。
- REQ が満たすべき最小カバレッジ条件は何か（IF/TEST/DATA の扱い）。
- ツールが最低限検出すべき整合性違反は何か（存在性、重複、自己参照、循環など）。
- ルール ID と重大度（ERROR/WARN/INFO）をどう分離して運用するか（プロファイルの位置づけ）。

## 範囲（Scope）と前提

### 対象（In scope）

- iori-spec の仕様ファイル群（1ファイル1ID）における `trace` の意味論・記法・整合性ルール。
- 主に REQ / IF / DATA / TEST の関係を対象とするが、ARCH / STEER / SPEC-SYS 等も関係として扱える。

### 非対象（Out of scope）

- lint の実行方法、終了コード、CI ゲートの詳細（→ SPEC-SYS-005）
- index / graph export / context bundle / lint report 等のツール出力契約（→ SPEC-SYS-004）
- kind 定義・セクション定義の SSOT（→ SPEC-SYS-002）

### 前提（Assumptions）

- 仕様ファイルは YAML front matter を持つ。
- `id` はグローバル一意で、参照可能である。
- `trace` は YAML front matter に記載される。

### 用語・定義（Definitions）

- **Node**: 仕様ファイル（1ファイル1ID）。
- **Edge**: `trace` が定義する ID 間の有向関係。
- **mentions**: 本文中の ID 言及。探索補助として扱い、規範根拠（SSOT）にはしない。

## Quickstart（最小で“合格”する書き方）

- REQ は `trace.satisfied_by` に **IF を 1 件以上**、`trace.verified_by` に **TEST を 1 件以上**結線する。
- DATA が要件上必須なら、`coverage_hints.data: required` を明示し、`trace.satisfied_by` に **DATA を 1 件以上**含める。
- 成立条件・実装順などの前提は `trace.depends_on` に書く（単なる関連は `trace.relates_to`）。

## 規範キーワード

本仕様は RFC 2119 に準拠する意味で以下を用いる。

- **MUST**（必須）: 満たさない場合、仕様違反
- **MUST NOT**（禁止）: 満たす場合、仕様違反
- **SHOULD**（推奨）: 原則満たす。満たさない場合、合理的理由を説明できること
- **MAY**（任意）: 必要に応じて選択

## 概念モデル

### ノード（Node）

- 仕様ファイル（1ファイル1ID）を **Node** とする。
- Node は `kind` を持つ（例: requirements / interfaces / data_contracts / tests / architecture / steering / reference など）。

### エッジ（Edge）

- `trace` が定義する ID 間の有向関係を **Edge** とする。
- Edge は **型（type）** を持つ（satisfied_by / verified_by / depends_on / derived_from / supersedes / relates_to 等）。

### SSOT と補助情報（mentions）

- `trace` は **関係（Edge）の SSOT**。
- 本文中の ID 言及は **mentions（補助）** として扱い、関係の規範根拠にはしない。

## trace 記法（Syntax）

### 1. 記載場所

- `trace` は YAML front matter に記載する（MUST）。

### 2. 許容形式

各エッジ型は、以下のどちらかの形式で記述できる（MUST）。

#### 2.1 文字列配列（最簡易）

```yaml
trace:
  satisfied_by:
    - IF-010
    - DATA-020
  verified_by:
    - TEST-005
```

#### 2.2 オブジェクト配列（注釈付き）

```yaml
trace:
  satisfied_by:
    - id: IF-010
      note: importYamlDictionary の外部 IF
    - id: DATA-020
      note: YAML 辞書フォーマット
  verified_by:
    - id: TEST-005
      note: 正常系/異常系の最小セット
```

- オブジェクト形式は `id` を MUST とし、`note` は MAY とする。
- ツールは内部的に正規化して扱う（例: string → `{id: ...}`）。

### 3. 一般制約

- 同一キー内での ID 重複は **禁止**（MUST NOT）。
- 自己参照（`id` が自分自身）は **禁止**（MUST NOT）。
- **エッジ型キー**（`satisfied_by` / `verified_by` / `depends_on` / `derived_from` / `supersedes` / `relates_to`）の値は **配列** とする（MUST）。スカラー単体は許容しない。
- 補助フィールド（例: `coverage_hints`）は **オブジェクト**を許容する（MAY）。

### 4. 補助フィールド（任意）

#### coverage_hints（DATA 充足の要否ヒント）

DATA の有無が曖昧になりやすい場合、REQ は次のヒントを持てる（MAY）。

```yaml
trace:
  coverage_hints:
    data: required   # required | optional | auto
```

- `required`: DATA 充足（DATA-* の satisfied_by）が必須
- `optional`: DATA 充足は不要
- `auto`（省略時既定）: ツールがヒューリスティクスで指摘（WARN/INFO）し得る

判断例（ガイド）:

- `required`: 外部入出力のフォーマット／スキーマ互換性が要件の成立条件になる場合
- `optional`: 実装内部のみで完結し、データ契約を独立仕様として維持する必要が薄い場合
- `auto`: まだ判断が揺れている・初期フェーズで後から収束させる場合

## エッジ型（Semantics）

本仕様で定義する標準エッジ型は以下とする。

### A. satisfied_by（充足 / 実装の落とし込み）

#### 定義

`B ∈ A.trace.satisfied_by` のとき、**B satisfies A**（B が A を満たす）を意味する。
日本語補助：A の要求・意図が B に具体化され、A が **実装可能** な形に落ちている。

#### 主用途（標準）

- `REQ-*` → `IF-*` : 実装境界（API/CLI/イベント/ジョブ等）に落とし込む
- `REQ-*` → `DATA-*` : データ契約（スキーマ/フォーマット/互換性）に落とし込む

#### 指針

- REQ は、少なくとも IF を 1 件以上 `satisfied_by` に含める（MUST）。
- DATA が成立条件として重要な場合、REQ は DATA を `satisfied_by` に含める（SHOULD）。曖昧なら `coverage_hints.data` を用いる（MAY）。

### B. verified_by（検証 / 合否基準の定義）

#### 定義

`B ∈ A.trace.verified_by` のとき、**B verifies A**（B が A を検証する）を意味する。
日本語補助：A の合否基準が B に定義され、A が **検証可能**（テスト可能/観測可能）になっている。

#### 主用途（標準）

- `REQ-*` → `TEST-*` : テスト観点と合否基準（自動/手動/観測）への接続

#### 指針

- REQ は、少なくとも TEST を 1 件以上 `verified_by` に含める（MUST）。

### C. depends_on（依存 / 前提）

#### 定義

`B ∈ A.trace.depends_on` のとき、**A depends on B**（A は B を前提として成立する）を意味する。
実装順・理解順・成立条件（制約/方針/外部仕様）を表す。

#### 主用途

- 仕様の前提関係（読む順・実装順・成立条件）
- 例: IF が DATA を前提にする、TEST が IF/DATA を前提にする、ARCH が STEER を前提にする

#### 指針

- `depends_on` は「成立条件」を表す。単なる参照や関連は `relates_to` を使う（SHOULD）。
- 循環依存は原則避ける（SHOULD）。発生する場合は設計上の理由を説明できること。

### D. derived_from（派生 / 分解元）

#### 定義

`B ∈ A.trace.derived_from` のとき、**A is derived from B**（A は B から派生した）を意味する。
仕様の由来・根拠・逆参照（探索性）に用いる。

#### 主用途

- IF/DATA/TEST が「どの REQ 由来か」を逆方向で示す（探索性）
- REQ の分割・再構成（REQ-010 が REQ-001/002 から派生、など）

#### 指針

- IF/DATA/TEST が REQ から生じた場合、`derived_from` を付与することで探索性を高められる（SHOULD）。
- `derived_from` は必須ではない（MAY）。主たる SSOT は REQ 側の `satisfied_by/verified_by` に置く。

### E. supersedes（置換 / 世代交代）

#### 定義

`B ∈ A.trace.supersedes` のとき、**A supersedes B**（A が B を置換する）を意味する。
置換元 B は原則 deprecated に移行し、参照先を最新へ誘導する。

#### 主用途

- 仕様の世代交代（deprecated 化、リネーム、統合、分割後の後継宣言）

#### 指針

- `supersedes` がある場合、置換元（B）の `status` は `deprecated` を推奨（SHOULD）。
- ツールは `supersedes` 鎖を辿って「最新」を提示できる（MAY）。

### F. relates_to（関連 / ナビゲーション）

#### 定義

`A.trace.relates_to` は、意味的関連があることを示す（探索・理解の導線）。規範的な依存/充足/検証は表さない。

#### 指針

- `relates_to` と `satisfied_by / verified_by / depends_on` を混同しない（MUST）。

## kind 間の推奨関係（Relationship Guidance）

以下は推奨（SHOULD）の関係パターンであり、全面禁止の表ではない。

### requirements（REQ）

- MUST: `verified_by` に `TEST-*` を ≥1 件
- MUST: `satisfied_by` に `IF-*` を ≥1 件
- SHOULD: データを伴う場合 `satisfied_by` に `DATA-*` を ≥1 件（または `coverage_hints.data=required`）
- MAY: `depends_on`（前提となる上位 REQ や STEER）

### interfaces（IF）

- SHOULD: `derived_from` に `REQ-*` を ≥1 件（探索性）
- MAY: `depends_on` に `DATA-*` や `ARCH-*`（前提）

### data_contracts（DATA）

- SHOULD: `derived_from` に `REQ-*` または `IF-*`
- MAY: `depends_on`（外部仕様、互換性方針、参照データなど）

### test（TEST）

- SHOULD: `derived_from` に `REQ-*`
- SHOULD: `depends_on` に `IF-*` や `DATA-*`（対象・前提）

### architecture / steering / spec_system（ARCH / STEER / SPEC-SYS）

- MAY: `depends_on`（方針の継承、上位原則）
- MAY: `relates_to`（背景・採用理由・参照）

## 必須カバレッジ最小条件（Minimum Coverage）

### 1. REQ の最小条件（MUST）

各 `REQ-*` は `trace` に以下を満たす参照を含めなければならない。

- **実装充足（satisfaction）**: `trace.satisfied_by` に `IF-*` を少なくとも 1 件
- **検証（verification）**: `trace.verified_by` に `TEST-*` を少なくとも 1 件
- **DATA（条件付き必須）**:

  - データ契約が必要な要求は `trace.satisfied_by` に `DATA-*` を少なくとも 1 件
  - 不要なら省略可能（`coverage_hints.data` により明示してよい）

### 2. DATA 必要性の表明（任意・推奨）

- `coverage_hints.data=required|optional|auto` を用いて、DATA 充足の要否を明示できる（MAY）。
  - `required`: DATA カバレッジを MUST として扱う
  - `optional`: DATA カバレッジを要求しない
  - `auto`（省略時既定）: ツールがヒューリスティクスで指摘（WARN/INFO）し得る

## 整合性ルール（Integrity Constraints）

ツールは最低限、以下を検出可能であること（MUST）。

1. **存在性**: 参照先 ID が実在する（dangling を検出）
2. **重複**: 同一キー内の重複参照を検出
3. **自己参照**: 自己参照を検出
4. **型整合**: 明らかに不適切な kind 組み合わせ（プロファイルで ERROR 化可能）
5. **置換整合**: `supersedes` の対象が deprecated でない等の不整合（指摘可能）
6. **依存循環**: `depends_on` の循環がある（検出可能。重大度はプロファイルで決める）

## ルールID体系（Lint Rule Catalog）

本仕様は、lint が指摘するための標準ルール ID を定義する。
重大度（ERROR/WARN/INFO）と CI ゲートは「プロファイル」で定義する。

- **T001**: REQ が `satisfied_by` に IF を含まない（Missing IF satisfaction）
- **T002**: REQ が `verified_by` に TEST を含まない（Missing verification）
- **T003**: `coverage_hints.data=required` なのに `satisfied_by` に DATA がない（Missing required DATA satisfaction）
- **T004**: 参照先 ID が存在しない（Dangling reference）
- **T005**: 同一キー内で ID が重複（Duplicate reference）
- **T006**: 自己参照（Self reference）
- **T007**: kind 組み合わせが不適切（Type mismatch / disallowed edge by policy）
- **T008**: `depends_on` に循環がある（Dependency cycle）
- **T009**: `supersedes` の対象が deprecated でない（Superseded target not deprecated）
- **T010**: deprecated な ID を `satisfied_by/verified_by/depends_on` で参照している（Use of deprecated target）
- **T011**: 孤立ノード（Orphan）
- **T012**: `relates_to` のみで必要な `satisfied_by/verified_by` が不足している（Misuse of relates_to）

※ T011/T012 はプロジェクトにより不要な場合が多く、既定では WARN/INFO 扱いが想定される（プロファイルで変更可能）。

## 重大度プロファイル（Severity Profiles）

プロファイルは運用設定であり、具体の格納場所・指定方法は SPEC-SYS-005 が規定する。
本仕様では代表的なプロファイル例を示す。

### Profile: strict（厳格）

- ERROR: T001, T002, T003, T004, T006, T007, T010
- WARN : T008, T011, T012
- INFO : （なし）

### Profile: balanced（既定想定）

- ERROR: T001, T002, T003, T004, T005,T006
- WARN : T007, T008, T009, T010
- INFO : T011, T012

### Profile: exploratory（探索/初期）

- ERROR: T004, T005, T006
- WARN : T001, T002, T003
- INFO : T007, T008, T009, T010, T011, T012

## 記載例（Examples）

### 1) REQ（satisfied_by + verified_by + hint）

```yaml
---
kind: requirements
scope: functional
id: REQ-001
spec_title: YAML 辞書のインポート
status: draft
trace:
  coverage_hints:
    data: required
  satisfied_by:
    - id: IF-010
      note: importYamlDictionary() 外部IF
    - id: DATA-020
      note: YAML 辞書フォーマット
  verified_by:
    - id: TEST-005
      note: 正常/異常の最小セット
---
```

### 2) IF（由来を逆参照で付与）

```yaml
---
kind: interfaces
scope: functional
id: IF-010
spec_title: 辞書インポートIF
status: draft
trace:
  derived_from:
    - REQ-001
  depends_on:
    - DATA-020
---
```

### 3) DATA（REQ/IF 由来、外部仕様に依存）

```yaml
---
kind: data_contracts
scope: functional
id: DATA-020
spec_title: YAML辞書フォーマット
status: draft
trace:
  derived_from:
    - REQ-001
    - IF-010
  depends_on:
    - STEER-010
---
```

### 4) TEST（REQ 由来、対象 IF/DATA を前提にする）

```yaml
---
kind: tests
scope: functional
id: TEST-005
spec_title: YAMLインポートの統合テスト
status: draft
trace:
  derived_from:
    - REQ-001
  depends_on:
    - IF-010
    - DATA-020
---
```

### 5) 置換（supersedes）

```yaml
---
kind: requirements
scope: functional
id: REQ-101
spec_title: インポート要件（改訂版）
status: draft
trace:
  supersedes:
    - REQ-001
  satisfied_by:
    - IF-010
    - DATA-020
  verified_by:
    - TEST-105
---
```

## 変更方針（本仕様の整合性と変更容易性を継続的に担保するための運用ルール）

- 本仕様は「最小核（core）」として、**汎用性と安定性**を優先する。
- 詳細な運用（CI ゲート、出力形式、プロジェクト固有の許容関係）は別仕様（SPEC-SYS-004 / SPEC-SYS-005）で拡張する。
- 新しいエッジ型を追加する場合は、既存の意味論との衝突がないことを確認し、最小限の整合性ルールと併せて導入する。

## USAGE

- 想定読者（Who）:
  - 仕様の作成・改訂を行う執筆者（REQ/IF/DATA/TEST/ARCH/STEER/SPEC-SYS）
  - レビュー担当者（整合性・更新漏れの確認）
  - ツール実装者（index/lint/trace report などの実装・運用）
- 参照トリガー（When）:
  - 新規に REQ を作成・分割・統合するとき（最小カバレッジの確保）
  - IF/DATA/TEST を追加・改訂するとき（由来・前提の明示、更新漏れの防止）
  - lint/CI ゲートのルール運用を見直すとき（ルールIDと重大度プロファイルの分離）
  - 不整合（dangling/循環/型不一致等）の原因調査をするとき
- 使い方（How）:
  - REQ は `trace.satisfied_by` に **IF を ≥1 件**、`trace.verified_by` に **TEST を ≥1 件**結線し、最小条件を満たす。
  - DATA が要件上必須なら `coverage_hints.data: required` を明示し、`satisfied_by` に DATA を含める。
  - 成立条件・実装順などの前提は `trace.depends_on` に書く（単なる関連は `trace.relates_to`）。
  - IF/DATA/TEST は必要に応じて `derived_from` を付け、探索性を高める（主たるSSOTは REQ 側）。
  - 置換・改訂は `trace.supersedes` で明示し、参照先を最新へ誘導する。
- セット読み（With）:
  - SPEC-SYS-005（lint/CI ゲートと重大度プロファイルの運用）
  - SPEC-SYS-004（trace map 等の出力契約・互換性）
  - SPEC-SYS-001（仕様書群の運用フロー：作成/修正/参照の標準手順）

## 運用上の目安（LLM / SDD 観点）

- 更新トリガー（Trigger → Action）:
  - エッジ型（Semantics）を追加・変更する:
    - Action: 本仕様（定義・指針・整合性ルール）を更新し、ツールの解釈と齟齬が出ないよう SPEC-SYS-005（lint/CI）および実装側も同一 PR で追随する。
  - 最小カバレッジ条件（Minimum Coverage）を変更する:
    - Action: 既存 REQ 群への影響（未達の発生）を評価し、必要なら移行期間やプロファイル調整（WARN→ERROR など）を SPEC-SYS-005 側で管理する。
  - ルールID体系（Lint Rule Catalog）を追加・変更する:
    - Action: ルール ID の意味（検出対象）を本仕様で固定し、重大度の割当はプロファイル（運用設定）で管理する。
  - trace 記法（Syntax）を拡張する（新フィールド、許容形式の追加など）:
    - Action: 正規化方針（string→object 等）と後方互換の考え方を明記し、SPEC-SYS-004（出力契約）と整合させる。
  - `supersedes` / deprecation の運用を変更する:
    - Action: 参照先の最新化導線（READ_NEXT/運用規約）と、lint 指摘（deprecated参照など）の扱いを一貫させる。

- LLM 連携（貼り方）:
  - 最小セット: 本仕様の LLM_BRIEF + 変更対象セクション（diff）+ 期待成果物（例: 新エッジ型の定義案、整合性ルール案、ルールID追加案）。
  - 拡張セット: 影響する SPEC-SYS-004（出力契約）/ SPEC-SYS-005（CIゲート）/ 代表的な REQ/IF/DATA/TEST 例（移行の妥当性確認用）を追加で渡す。

- ツール運用（Gate）:
  - PR 時: `lint` / `trace lint`（重大度プロファイルに従う）で、dangling/重複/自己参照/最小カバレッジ不足を早期に検出する。
  - リリース前: 重大度プロファイルの変更がある場合、既存仕様群に対する影響（新規 ERROR の発生）を棚卸しし、移行手順と合わせて適用する。

- 実務上の注意:
  - “本文に書いてあるから分かる”はスケールしない。ツールが辿れる導線を `trace` に残すことを優先する。
  - `depends_on` は「成立条件」。単なる参照・関連は `relates_to` に逃がす（意味を混ぜない）。

## READ_NEXT

- SPEC-SYS-005 — lint/CI ゲートと重大度プロファイル（ERROR/WARN/INFO）の運用を規定する。
- SPEC-SYS-004 — trace map / lint report / context pack 等の出力契約と互換性を規定する。
- SPEC-SYS-002 — セクション定義（Ordering / include_in）と、仕様ファイルの構造 SSOT を規定する。
- SPEC-SYS-001 — 仕様書群の作成・修正・参照フロー（運用・記述規約）を規定する。
- STEER-002 — 互換性・deprecation・依存方向などの上位方針（成立条件の背景）を提供する。
