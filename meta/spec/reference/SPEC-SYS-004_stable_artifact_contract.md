---
kind: reference
scope: spec_system
id: SPEC-SYS-004
spec_title: "iori-spec Stable Artifact Contract (index / pack / lint report)"
stability: core # core|extension
status: draft # draft|review|stable|deprecated
---

# SPEC-SYS-004 Stable Artifact Contract (index / pack / lint report)

## LLM_BRIEF

- kind: reference（scope: spec_system）
- iori-spec ツールが生成する成果物 **index（SSoT）／context pack（pack）／lint report** の **データ契約（shape・必須項目・意味論境界）**と、**決定性（同入力→同出力）／順序規約**、および **互換性方針（contract versioning / extensions）**を Stable Core として固定する。
- 併せて、artifact の **構造（shape）を検証する validation schema（JSON Schema 等）**を外部ファイルとして配布し、仕様書側には **生成スナップショット（DO NOT EDIT）**を掲載できる前提で、スナップショットの境界・決定性・衝突優先順位を契約として定義する。
- `trace` の意味論・ルールID体系は SPEC-SYS-003、lint の実行/CI ゲートは SPEC-SYS-005 を正とし、本仕様はそれらと整合する **成果物契約と正規化（Normalization）**に集中する。

## このドキュメントの役割

- 本仕様が決めること（主題＋抽象度）
  - iori-spec が出力する artifact（index / pack / lint_report）の **契約（機械可読な shape）**、必須/任意、意味論の境界、決定性、順序規約を **Stable Core（契約レイヤー）**として固定する。
  - 派生 artifact（pack / lint_report）が「どの index から生成されたか」を機械的に検証できる最小要件（`source_index`）を定義する。
  - 上記 artifact の **構造（shape）を検証する validation schema** を外部ファイルとして配布し得る前提で、仕様書内に掲示する **生成スナップショット（Snapshot）**の境界・決定性・衝突優先順位を契約化する。

- 本仕様が決めないこと（委譲先）
  - `trace` の意味論（edge の意味）・一般制約・ルールID体系（→ SPEC-SYS-003）
  - lint の実行方法、終了コード、CI ゲートの詳細（→ SPEC-SYS-005）
  - kind 定義・セクション定義の SSOT（→ SPEC-SYS-002）
  - CLI 名・引数・既定出力先・表示フォーマット等の UX（→ SPEC-SYS-005）
  - 保存場所・表示・実行形態など、運用都合に強く依存する事項（本仕様では **論理契約を優先**。物理配置は推奨プロファイルとして扱う）

- 本仕様が答える主要な問い（チェックリスト）
  - Producer は **何を出力すれば契約準拠**とみなされるか（必須フィールド・型・順序）
  - Consumer は **どこまでを前提**にしてよいか（未知フィールド/未知 `rule_id`/未知 `kind` の扱い）
  - 互換性に影響する変更を **どの単位（contract_version）で管理**し、どこまでを互換とみなすか
  - 同一入力から **同一出力**を得るために、どの正規化（path/配列/JSON）を必須とするか
  - pack / lint_report が参照する `source_index` を **どう検証**し、取り違え事故をどう防ぐか

## 範囲（Scope）と前提

### 対象（In scope）

- index（SSoT）のデータ契約（構造、必須/任意、意味論の境界、決定性、順序）
- pack のデータ契約（構造、必須/任意、抽出根拠、決定性、順序）
- lint report のデータ契約（構造、必須/任意、決定性、順序）
- 互換性方針（contract versioning、extensions の扱い）
- 正規化（Normalization）規約（path、順序、配列整列、fingerprint の算出）
- artifact の構造（shape）を検証する validation schema の配布前提（外部SSOT）と、当該 schema の仕様書内掲示（生成スナップショット）の契約
- 生成スナップショット（Snapshot）の境界（markers）・決定性（同入力→同出力）・編集禁止（DO NOT EDIT）
- 物理配置に関する **推奨準拠プロファイル（FS Layout v1）**（ただし中身の契約を優先）

### 非対象（Out of scope）

- lint の実行方法、終了コード、CI ゲートの詳細（→ SPEC-SYS-005）
- `trace` の意味論（edge の意味）・一般制約・ルールID体系（→ SPEC-SYS-003）
- kind 定義・セクション定義の SSOT（→ SPEC-SYS-002）
- CLI 名・引数・既定出力先・表示フォーマット等の UX（→ SPEC-SYS-005）

### 前提（Assumptions）

- 仕様ファイルは YAML front matter を持つ（SPEC-SYS-006）。
- `id` はグローバル一意で参照可能である。
- pack 生成は SPEC-SYS-002 の `include_in`（用途概念 `pack`）を抽出根拠とする。

### 用語/定義（Definitions）

- **Contract Version**: 本仕様で規定するデータ契約バージョン（互換性の単位）。
- **Determinism**: 同一入力（同一 repo 状態＋同一設定）から同一出力が得られる性質。

## 規範キーワード

本仕様は RFC 2119 に準拠する意味で以下を用いる。

- **MUST**（必須）: 満たさない場合、契約違反
- **MUST NOT**（禁止）: 満たす場合、契約違反
- **SHOULD**（推奨）: 原則満たす。満たさない場合、合理的理由を説明できること
- **MAY**（任意）: 必要に応じて選択

## 用語

- **Artifact**: Producer が出力し、Consumer が入力として利用する機械可読な成果物
- **Normative Artifact**: ツールと人が「正」とみなす規範（SSOT）として運用される外部ファイル（例: validation schema / lint rule catalog / severity profiles）。
- **Snapshot（生成スナップショット）**: Normative Artifact の内容を仕様書内へ埋め込んだ表示用ブロック。派生物であり手編集しない（DO NOT EDIT）。
- **artifact_kind**: artifact の用途概念（`index` / `pack` / `lint_report`）
- **file_role**: 同一 artifact_kind に属するファイルの役割（`data` / `manifest`）
- **Contract Version**: artifact のデータ契約バージョン（互換性の単位）
- **Producer / Consumer**: 生成側 / 利用側
- **Determinism**: 同一入力（同一 repo 状態＋同一設定）から同一出力が得られる性質
- **Normalization**: 表現のゆらぎ（順序、path、fingerprint 等）を規約で潰すこと
- **source_index**: 派生 artifact が「どの index から生成されたか」を示す参照情報
- **mention**: 本文から抽出された ID 言及。規範的関係（SSOT）ではない。

## 安定契約の基本方針

### 1) 契約の識別と互換性

- 各 artifact は `artifact_kind` と `contract_version` を持つ（MUST）。
- 互換性は SemVer ライクに扱う（SHOULD）。
  - **MAJOR**: 破壊的変更（既存 Consumer が誤解・失敗し得る）
  - **MINOR**: 後方互換の拡張（フィールド追加、列挙値追加、record 追加等）
  - **PATCH**: バグ修正（意味論は不変）
- Consumer は未知フィールドを無視できる（MUST）。
- Producer は既存フィールドの意味変更・再解釈をしてはならない（MUST NOT）。

### 2) 拡張（extensions）

- artifact には `extensions`（任意のオブジェクト）を追加してよい（MAY）。
- 拡張は `extensions` 配下に閉じ込める（SHOULD）。
- Consumer は `extensions` を無視しても成立すること（MUST）。

### 3) 意味論のSSOTと、出力表現のSSOTを分離する

- `trace` の意味論・一般制約・ルールID体系は SPEC-SYS-003 を正とする（MUST）。
- 本仕様（004）は「出力表現（shape）と決定性」を正とする（MUST）。
- lint の exit code / CI ゲート等の運用は SPEC-SYS-005 を正とする（MUST）。

## 規範成果物（Normative Artifacts: External SSOT）

### 基本方針

- artifact の **構造（shape）**を機械的に検証するための validation schema（JSON Schema 等）は、外部ファイルとして配布してよい（MAY）。
- これらの validation schema は、**構造（shape）に関する SSOT（Normative）**として扱ってよい（MAY）。
  - その場合、仕様書本文（本仕様を含む）は「意図・意味論・決定性・運用」を中心とする（Informative）位置づけとなる。
- 構造（shape）に関して **schema と本文が衝突**する場合、構造検証の観点では **schema を優先**する（MUST）。
- 一方で、schema で表現しきれない **意味論・決定性・正規化・互換性方針**に関しては、本仕様（SPEC-SYS-004）を正とする（MUST）。

### 想定する配布単位（例）

- `.iori-spec/schemas/artifacts/index.schema.json`
- `.iori-spec/schemas/artifacts/pack_manifest.schema.json`
- `.iori-spec/schemas/artifacts/lint_report.schema.json`

## 生成スナップショット契約（Generated Snapshot Contract）

### Snapshot の性質（MUST）

- Snapshot は **派生物**であり、手編集してはならない（MUST NOT）。
- Snapshot は外部 Normative Artifact から **決定的に再生成**できること（diffゼロ）を前提とする（MUST）。
- Snapshot と外部 Normative Artifact の同期は doc-sync により検証され得る（手順は SPEC-SYS-005）。（SHOULD）

### Snapshot markers（境界）（MUST）

仕様書内の Snapshot ブロックは、機械的置換が可能な境界を持つ（MUST）。

````md
<!-- BEGIN: GENERATED FROM <path> -->

```yaml
# DO NOT EDIT - generated snapshot
...
```

<!-- END: GENERATED -->
````

## 決定性と正規化（Determinism & Normalization）

### 1) 同一入力判定（input_fingerprint）

各 artifact は `input_fingerprint` を持つ（MUST）。

```json
{
  "input_fingerprint": {
    "files_hash": "sha256:...",
    "config_hash": "sha256:..."
  }
}
```

#### files_hash（MUST）

- 対象ファイル集合を **repo root 相対 path 昇順**でソートする。

- 各ファイルについて `content_hash = sha256(raw_bytes)` を算出し、次のレコード文字列を作る（行末は `\n`）:

  `"{path}\t{content_hash}\n"`

- 全レコードを連結したバイト列に対して `sha256` を取り、`files_hash` とする（MUST）。

※ 目的は「同一ファイル集合・同一内容」を安定的に識別すること。Merkle 化は不要（中小規模最適）。

#### config_hash（MUST）

- index / pack / lint の生成に影響する設定値（例: 除外パターン、unknown_sections policy、pack follow 設定、limits、lint profile 等）を 1 つの JSON オブジェクトに集約する。
- canonical JSON として次を満たす形でシリアライズし、`sha256` を取る（MUST）。

  - オブジェクトのキー順は辞書順
  - 余計な空白・改行なし
  - 配列順は意味的に順序不変なら辞書順で正規化（例: follow.trace_edges は集合として扱い昇順に正規化）

### 2) JSON の正規化

- JSON 出力は UTF-8 とする（MUST）。
- 配列の順序は本仕様で規定するソートキーに従い固定する（MUST）。
- オブジェクトのキー順は辞書順で出力する（SHOULD）。

### 3) path の正規化

- `path` は repo root からの相対パスとし、区切りは `/` とする（MUST）。
- `.` / `..` の正規化を行い、等価な別表現を出力しない（SHOULD）。

### 4) 非決定要素の扱い

- タイムスタンプ（`generated_at` 等）は差分安定性を損なうため、既定では出力しない（SHOULD NOT）。
- 出力する場合は `extensions` など Consumer が無視できる領域に閉じ込める（MUST）。

### 5) 原子性（Atomic write）と complete

- Producer は出力を原子的に更新する（MUST）。
- `complete=false` の artifact は **「途中/失敗で信頼できない」**ことを意味する（MUST）。

`complete=false` の場合でも、Consumer が安全に扱えるよう次を満たす（MUST）:

- Common Header（後述）は必ず出力する
- `diagnostics.errors` に少なくとも 1 件のエラーを含める
- payload（findings、pack内容等）は欠落してよい（MAY）

## Artifact 共通ヘッダ（Common Header）

本仕様が定義する全 artifact の JSON（JSONL の meta レコード含む）は、以下の共通フィールドを含む（MUST）。

```json
{
  "artifact_kind": "index | pack | lint_report",
  "file_role": "data | manifest",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "complete": true,
  "diagnostics": { "errors": [] },
  "extensions": {}
}
```

制約:

- `artifact_kind` は **index / pack / lint_report のいずれか**（MUST）。
- `file_role` は **data / manifest のいずれか**（MUST）。
- `diagnostics` は存在させる（MUST）。`complete=false` の場合 `diagnostics.errors` は 1 件以上（MUST）。
- Consumer は未知フィールドを無視できる（MUST）。

## Artifact 一覧（Stable Core）

- **index**: spec 群を機械処理するための SSOT（メタ情報・抽出結果・trace edge 等）
- **pack**: LLM へ渡す局所コンテキスト束（manifest が SSOT）
- **lint_report**: 静的検査結果（規則違反・重大度・位置情報・要約）

---

## Artifact: index（SSoT）

### 目的

- spec 群をグラフ/検索/影響分析/pack 生成等へ供給するための機械可読 SSOT を提供する。
- `trace` は edge の SSOT（SPEC-SYS-003）であることを前提に、index は `trace_edge` として正規化出力する。

### 形式（data）

index の data は JSON Lines（JSONL）とする（MUST）。

- 1行=1 JSON object
- 先頭行は `record_type="meta"`（MUST）

#### record: meta（必須）

```json
{
  "record_type": "meta",
  "artifact_kind": "index",
  "file_role": "data",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "complete": true,
  "diagnostics": { "errors": [] },
  "extensions": {}
}
```

#### record: spec（推奨）

各 spec ファイルにつき 1 レコードを出力する（SHOULD）。

```json
{
  "record_type": "spec",
  "id": "REQ-001",
  "kind": "requirements",
  "scope": "functional",
  "status": "draft",
  "stability": "core",
  "spec_title": "YAML 辞書のインポート",
  "path": "requirements/REQ-001.md",
  "content_hash": "sha256:...",
  "front_matter": {
    "id": "REQ-001",
    "kind": "requirements",
    "scope": "functional",
    "status": "draft",
    "stability": "core",
    "spec_title": "YAML 辞書のインポート"
  },
  "sections": [
    {
      "section_id": "llm_brief",
      "heading": "LLM_BRIEF",
      "include_in": ["index", "render", "pack"]
    },
    {
      "section_id": "read_next",
      "heading": "READ_NEXT",
      "include_in": ["index", "render", "pack"]
    }
  ],
  "unknown_sections": [
    { "heading": "独自メモ", "line": 120 }
  ],
  "extensions": {}
}
```

制約:

- `kind` は文字列として扱い、未知値を拒否しない（MUST）。
- `sections.section_id` は registry（SPEC-SYS-002）で解決できたもののみ付与する（MUST）。
- registry で解決できない H2 は `unknown_sections` に入れる（SHOULD）。
- `include_in` は registry から導出した値であり、Consumer は参考情報として扱う（SHOULD）。

#### record: trace_edge（推奨）

`trace` から抽出した edge を列挙する（SHOULD）。出力は正規化済み shape とする（MUST）。

```json
{
  "record_type": "trace_edge",
  "source_id": "REQ-001",
  "edge_type": "satisfied_by",
  "target_id": "IF-010",
  "note": "importYamlDictionary の外部 IF",
  "extensions": {}
}
```

制約:

- `edge_type` は SPEC-SYS-003 が定義する標準エッジ型に従う（MUST）。
- 入力が文字列配列の場合、`note` は出力しない（MUST）。
- 入力がオブジェクト配列の場合、`note` があれば出力する（MAY）。

#### record: mention（任意）

本文から抽出した ID 言及（mentions）を列挙してよい（MAY）。ただし規範的関係ではない（MUST）。

```json
{
  "record_type": "mention",
  "is_normative": false,
  "source_id": "ARCH-001",
  "mentioned_id": "REQ-001",
  "context": { "heading": "背景", "line": 120 },
  "extensions": {}
}
```

制約:

- `is_normative` は常に `false`（MUST）。
- Consumer は mention を依存関係の根拠として扱ってはならない（MUST NOT）。

### レコード順序（決定性）

`spec_index.jsonl` のレコード順序は以下で固定する（MUST）。

1. meta（1行）
2. spec（`id` 昇順）
3. trace_edge（`source_id`, `edge_type`, `target_id` 昇順）
4. mention（`source_id`, `mentioned_id` 昇順）
5. 追加 `record_type` は末尾に置き、Consumer は無視できる（MUST）

### index_digest（推奨）

派生 artifact（pack / lint report）が参照できるよう、index の digest を算出してよい（SHOULD）。

- `index_digest = sha256(UTF-8 bytes of spec_index.jsonl with '\n' line endings)`
- digest 値は `sha256:...` 形式で表現する（SHOULD）

### index manifest（任意）

index の manifest は補助であり、存在しない場合でも index 利用は成立する（MAY）。

```json
{
  "artifact_kind": "index",
  "file_role": "manifest",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "complete": true,
  "diagnostics": { "errors": [] },
  "index_digest": "sha256:...",
  "locations": { "spec_index_jsonl": "artifacts/spec_index.jsonl" },
  "extensions": {}
}
```

---

## Artifact: pack（LLM 局所コンテキスト）

### 目的

- LLM に渡す局所コンテキストを、抽出済みかつ順序固定で提供する。
- **pack の Stable Core は manifest（JSON）**であり、本文コンテンツ（例: pack.md）は表示/投入用のテキストである（SHOULD）。

### 抽出根拠（Selection Source of Truth）

- pack は SPEC-SYS-002 の `include_in` に `pack` を含むセクションのみを抽出する（MUST）。
- registry で解決できない unknown section は既定では抽出しない（SHOULD）。

  - 抽出する場合は manifest.selection に明示する（MUST）。

### resolved_ids の決定（過剰設計回避・最小規範）

- `resolved_ids` は **seed_ids と trace traversal（選択した edge_type のみ）**で決定する（MUST）。
- `READ_NEXT` は差分不安定要因になりやすいため、既定では `resolved_ids` の決定に使わない（SHOULD）。

  - `READ_NEXT` 由来の候補は **hints として別枠に記録**する（MAY）。

### source_index（必須）

pack は、どの index から生成されたかを `source_index` として必ず保持する（MUST）。

```json
{
  "source_index": {
    "index_digest": "sha256:...",
    "index_contract_version": "0.1.0"
  }
}
```

### pack manifest（必須）

```json
{
  "artifact_kind": "pack",
  "file_role": "manifest",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "source_index": { "index_digest": "sha256:...", "index_contract_version": "0.1.0" },
  "pack_id": "pack-0001",
  "seed_ids": ["REQ-001"],
  "resolved_ids": ["DATA-020", "IF-010", "REQ-001", "TEST-005"],
  "selection": {
    "policy": "include_in=pack",
    "follow": {
      "trace_edges": ["depends_on", "satisfied_by", "verified_by"]
    },
    "limits": { "max_specs": 50, "max_chars": 200000 },
    "include_unknown_sections": false,
    "hints": {
      "read_next_ids": ["ARCH-001"]
    }
  },
  "truncation": { "truncated": false, "reason": null },
  "complete": true,
  "diagnostics": { "errors": [] },
  "extensions": {}
}
```

制約:

- `selection` は再現性の鍵であり必須（MUST）。
- `seed_ids` / `resolved_ids` / `selection.follow.trace_edges` は **重複除去**し、出力は **辞書順**で正規化する（MUST）。
- `selection.follow.trace_edges` は集合として扱い、順序は意味を持たない（MUST）。

### pack content（任意）

pack の実体（例: `pack.md`）は任意であり、manifest の `locations` または FS Layout で参照できればよい（MAY）。
Consumer は pack content を **機械パースの前提にしてはならない**（SHOULD）。

---

## Artifact: lint report（静的検査結果）

### 目的

- 仕様群の静的検査結果を、機械的に集計・可視化・CI 判定（の入力）に利用できる形で提供する。
- ルールID体系・意味論は SPEC-SYS-003 を参照し、report は「結果の形」を固定する。

### exit code ではなく run_status（Core）

lint の exit code は運用であり SPEC-SYS-005 を正とする。
本仕様では、契約として **`run_status`** を定義する（MUST）。

- `success`: error=0 かつ complete=true
- `warning`: error=0 かつ warn>0（info のみでも可）かつ complete=true
- `error`: error>0 かつ complete=true
- `fatal`: complete=false（入力不正/例外等で信頼不可）

### source_index（必須）

lint report は、どの index から生成されたかを `source_index` として必ず保持する（MUST）。

```json
{
  "source_index": {
    "index_digest": "sha256:...",
    "index_contract_version": "0.1.0"
  }
}
```

### lint_report.json（必須：data）

```json
{
  "artifact_kind": "lint_report",
  "file_role": "data",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "source_index": { "index_digest": "sha256:...", "index_contract_version": "0.1.0" },
  "profile": "balanced",
  "run_status": "warning",
  "summary": { "error": 0, "warn": 2, "info": 5 },
  "findings": [
    {
      "rule_id": "T001",
      "severity": "warn",
      "message": "REQ が satisfied_by に IF を含まない",
      "spec_id": "REQ-123",
      "path": "requirements/REQ-123.md",
      "location": { "heading": "範囲（Scope）と前提", "line": 42 },
      "related_ids": ["IF-010"],
      "suggestion": "trace.satisfied_by に IF-* を 1 件以上追加する"
    }
  ],
  "complete": true,
  "diagnostics": { "errors": [] },
  "extensions": {}
}
```

制約:

- `severity` は `{error,warn,info}`（MUST）。
- `rule_id` は SPEC-SYS-003 のルールID体系に従う（MUST）。
- `rule_id` が未知でも Consumer は許容し表示できる（MUST）。
- `profile` は自由文字列とし、未知値を拒否しない（MUST）。
- `profile` は「評価条件のラベル」であり、CIゲート条件そのものを含めてはならない（MUST NOT）。
- `complete=false` の場合 `run_status` は必ず `fatal`（MUST）。

#### findings の順序（決定性）

`findings` の順序は以下で固定（MUST）:

1. `severity`（error→warn→info）
2. `rule_id`
3. `spec_id`
4. `path`
5. `location.line`

### lint manifest（任意）

lint の manifest は補助であり、存在しない場合でも lint_report 利用は成立する（MAY）。

```json
{
  "artifact_kind": "lint_report",
  "file_role": "manifest",
  "contract_version": "0.1.0",
  "producer": { "name": "iori-spec", "version": "0.0.0" },
  "input_fingerprint": { "files_hash": "sha256:...", "config_hash": "sha256:..." },
  "source_index": { "index_digest": "sha256:...", "index_contract_version": "0.1.0" },
  "profile": "balanced",
  "run_status": "warning",
  "counts": { "findings": 7 },
  "locations": { "lint_report_json": "artifacts/reports/lint_report.json" },
  "complete": true,
  "diagnostics": { "errors": [] },
  "extensions": {}
}
```

---

## 物理配置プロファイル（FS Layout v1：推奨準拠）

本節は「ファイルシステムに出力する場合」の推奨プロファイルである（SHOULD）。
別配置を採用してもよいが、その場合でも **manifest.locations が実体の所在のSSOT** になるようにしてよい（MAY）。

推奨（例）:

- `artifacts/spec_index.jsonl`
- `artifacts/spec_index.manifest.json`（任意）
- `artifacts/packs/<pack_id>/manifest.json`（必須）
- `artifacts/packs/<pack_id>/pack.md`（任意）
- `artifacts/reports/lint_report.json`
- `artifacts/reports/lint.manifest.json`（任意）

## スキーマ配布（Validation Schemas）

- 各 artifact は検証用スキーマ（JSON Schema 等）を併設してよい（MAY）。
- validation schema を **構造（shape）の SSOT（Normative）**として運用する場合、構造に関する衝突は schema を優先する（MUST）。
- schema で表現しきれない **意味論・決定性・正規化・互換性方針**に関しては、本仕様（SPEC-SYS-004）を正とする（MUST）。
- schema を仕様書内に掲示する場合は、生成スナップショット（Snapshot）として掲載し、手編集してはならない（MUST NOT）。

## USAGE

### 想定読者（Who）

- Producer 実装者（index/pack/lint を生成するツール実装者）
- Consumer 実装者（CI 判定、可視化、検索、影響分析、LLM オーケストレーション等）
- 運用者（プロファイル設計、ゲート設計、品質管理）

### 参照タイミング（When）

- 新しい artifact（record_type / フィールド）を追加・変更するとき
- 決定性（順序・正規化・fingerprint）に関する不具合を修正するとき
- Consumer 側の互換性判断（契約バージョン対応、未知フィールド対応）を実装・更新するとき
- pack / lint_report の取り違え事故や再現性問題を調査するとき

### 使い方（How）

- Producer: Common Header・正規化・順序規約・`source_index` を満たす形で出力し、差分安定性（同入力→同出力）を担保する。
- Consumer: `contract_version` と `complete` を検査してから利用し、未知フィールド（`extensions` を含む）や未知 `rule_id` を許容したうえで既知フィールドのみで動作する。
- pack / lint_report: `source_index.index_digest` により参照元 index を検証し、取り違えを検知できるようにする。

### セットで読む spec（With）

- SPEC-SYS-003 — `trace` の意味論・ルールID体系（artifact が参照する意味論の SSOT）
- SPEC-SYS-005 — lint 実行/CI ゲートなど運用仕様（exit code 等の運用は 005 を正とする）
- SPEC-SYS-002 — `include_in` 等、pack 抽出根拠となるセクション定義

## 運用上の目安（LLM / SDD 観点）

### 更新トリガー（Trigger → Action）

- artifact の shape（必須フィールド/型/順序）の変更:
  - Action: 互換性影響を判定し、`contract_version` を MAJOR/MINOR/PATCH として更新する。Producer/Consumer 両方の互換性を点検し、必要なら移行メモ（破壊的変更の理由・回避策）を残す。
- 意味論の境界変更（同じフィールドの再解釈・意味変更）:
  - Action: **破壊的変更（MAJOR）**として扱うことを原則とし、既存 Consumer が誤解し得ない形（新フィールド追加＋旧フィールド維持、等）を優先する。
- 決定性・正規化（path/配列/JSON/fingerprint）に関する規約変更:
  - Action: “同入力→同出力” を満たすことを最優先に、規約変更の影響（差分、digest、再現性）を検証する。必要に応じて golden テスト/比較ベクトルを更新する。
- pack 抽出根拠（`include_in=pack`、follow 条件、limits 等）の変更:
  - Action: SPEC-SYS-002 / SPEC-SYS-005 と整合するように更新し、manifest の `selection`（再現性の鍵）が意図どおり記録されることを確認する。

### LLM 連携の原則（貼り方・渡し方）

- 最小セット: LLM_BRIEF + 変更対象の該当節（diff）+ 期待成果物（例: 互換性判定、契約更新案、Consumer 側対応方針）
- 拡張セット: 関連する artifact の該当スキーマ断片（Common Header/manifest 等）+ SPEC-SYS-003（意味論）+ SPEC-SYS-005（運用/ゲート）

### ツール運用（lint / テンプレ生成 / 抽出）

- PR 時: 変更が契約に影響する場合、`contract_version` 更新の妥当性（MAJOR/MINOR/PATCH）と、未知フィールド許容（Consumer 側の後方互換）をレビュー観点に含める。
- リリース前: 代表入力から生成した artifact の digest/順序が安定すること、`complete=false` を含む異常系でも Consumer が安全に扱えることを確認する。

### 更新時の作法（どう更新するか）

- 本仕様では、互換性（`contract_version`）・意味論変更・決定性・pack 抽出根拠の扱いを、上記「更新トリガー（Trigger → Action）」の Action として規定する。

## READ_NEXT

- SPEC-SYS-001 — Normative / Informative、外部SSOTと生成スナップショット（Snapshot）、衝突時優先順位の全体原則。
- SPEC-SYS-002 — pack 抽出根拠（`include_in`）やセクション解決規約（registry/guide）の SSOT。
- SPEC-SYS-003 — `trace` の意味論・一般制約・ルールID体系（artifact が依拠する意味論の SSOT）。
- SPEC-SYS-005 — lint 実行/exit code/CI ゲート、および pack 運用・出力先などの運用仕様。
