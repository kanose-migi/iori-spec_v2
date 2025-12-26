---
kind: reference
scope: spec_system
id: ADR-SPEC-002
spec_title: "ADR: Externalize Normative Artifacts as Machine-Readable SSOT and Embed Generated Snapshots in Specs"
stability: core # core|extension
status: stable # draft|review|stable|deprecated
---

# ADR-SPEC-002: Externalize Normative Artifacts as Machine-Readable SSOT and Embed Generated Snapshots in Specs

## LLM_BRIEF

- 本 ADR は「仕様の一部として仕様書に記載したい」要求と「機械的に読み取れるSSOTが望ましい」要求の対立を解消するため、**規範（Normative）を機械可読な外部ファイルに集約し、仕様書（Markdown）には生成スナップショットを埋め込む**方針を採択する。
- 衝突時の優先順位、生成スナップショットの契約、CI による同期検証（doc-sync）を定義し、配置先（SPEC-SYS-001/002/004/005）を確定する。

## このドキュメントの役割

### 何を決めるか（本 ADR の決定事項）

- 規範（Normative）と参考（Informative）の分離方針、および **衝突時の優先順位**。
- 規範を担う SSOT を **外部ファイル（YAML/JSON/Schema）**とし、仕様書本文は「説明・意図・運用」を中心とする方針。
- 仕様書に「規範が書いてある状態」を維持するため、外部規範ファイルの内容を **生成スナップショット**として埋め込む方式（DO NOT EDIT）を採択。
- 仕様書内スナップショットと外部規範ファイルの一致を **CI で強制**する（doc-sync）。

### 何を決めないか（委譲先）

- 外部規範ファイルの個別のスキーマ詳細（front matter schema / artifacts schema 等）の内容は各 SPEC-SYS と将来の個別仕様に委譲する。
- ツール実装の詳細（コマンド名、出力形式の細部）は SPEC-SYS-005 の範囲で具体化する。

## 範囲（Scope）と前提（Assumptions）

### 対象（In scope）

- iori-spec の「規範（ルール列挙、enum、プロファイル、スキーマ）」を **機械可読 SSOT**へ外部化する設計方針。
- 仕様書（Markdown）側へ **生成スナップショット**を埋め込み、閲覧性とSSOT一意性を両立する運用。
- 仕様書群内での配置（どの SPEC-SYS に何を書くか）の確定。

### 非対象（Out of scope）

- 個別の規範内容の正否（例：各 rule の文言、profile の各 severity 割当）。
- 仕様本文の記述内容（要件・IF・データ契約・テスト）そのもの。

### 前提（Assumptions）

- 仕様書は YAML front matter を持ち、1ファイル1ID を満たす。
- unknown section は許容される（policy: allow）ため、ADR 固有セクションを追加できる。
- “規範の衝突” を避けるため、SSOT は一意であることが望ましい。

## Background / Context

仕様策定・運用では、次の二つの要求が同時に発生する。

1. 仕様の一部である以上、仕様書（Markdown）に「規範が記載されている」状態を維持したい（レビュー容易性、閲覧性、意思決定の可視性）。
2. ツールが機械的・決定的に読み取り検証できる SSOT が必要（lint/profile/schema/CI gate の正確性、差分管理、実装乖離の抑止）。

これらを単一の媒体（Markdown のみ、または外部ファイルのみ）で満たすと、いずれかが損なわれやすい。
そのため、媒体の役割分担と「衝突時の優先順位」を明文化し、両立する設計が必要となった。

## Decision

### 採択（Decision Outcome）

次の方針を採択する。

1. **Normative SSOT は機械可読な外部ファイル**とする（YAML/JSON/Schema）。
2. 仕様書（Markdown）は **Human Spec** として、意図・背景・運用・解釈規則を中心に記述する。
3. ただし、仕様書に「規範が書いてある状態」を維持するため、外部規範ファイルの内容を **生成スナップショット**として仕様書に埋め込む（DO NOT EDIT）。
4. 生成スナップショットは派生物であり、**衝突時は外部ファイル（Normative）を優先**する。
5. CI は doc-sync を実施し、外部ファイルから再生成したスナップショットと仕様書の一致（diffゼロ）を強制する。

### 用語（本 ADR での定義）

- **Normative**: 規範。ツールと人が「正」とみなす SSOT（外部ファイル）。
- **Informative**: 参考。説明、例、背景、設計意図（仕様書本文）。
- **Snapshot**: 外部規範ファイルの内容を仕様書内へ貼り付けた表示用ブロック。
- **doc-sync**: 外部規範ファイル → 仕様書スナップショットを再生成し、差分がないことを検証する手順。

## Rationale

- SSOT を外部ファイルに集約することで、lint/profile/schema/CI の判断が決定的になり、実装乖離を減らせる。
- 仕様書に生成スナップショットを載せることで、閲覧・レビューの導線を維持できる（「仕様書に書いてある」要求を満たす）。
- 衝突時の優先順位を規範化することで、仕様の矛盾が運用事故に直結することを防げる。
- “生成物は編集禁止”を CI で担保することで、二重管理（ドキュメントと外部ファイルの手編集競合）を回避できる。

## Considered Options

1. **外部SSOT＋生成スナップショット（採択）**
   - Pros: SSOT 一意、機械検証が強い、閲覧性も担保
   - Cons: 生成・同期の仕組みが必要（doc-sync）

2. Markdown を SSOT とし、外部ファイルは抽出物（Doc-first）
   - Pros: “仕様書に書いてある”を最大化
   - Cons: 抽出の脆さ、編集事故、差分レビュー困難、長期運用で破綻しやすい

3. 完全分離（外部SSOTのみ、仕様書は参照のみ）
   - Pros: SSOT 明快
   - Cons: “仕様書に記載したい”要求を満たしにくく、レビュー導線が悪化

## Consequences

### Positive

- ルールカタログ／プロファイル／スキーマの変更が差分レビューしやすくなる。
- ツールが参照する SSOT が一意になり、CI ゲートの信頼性が上がる。
- 仕様書の閲覧性・合意形成（レビュー）が維持される。

### Negative / Costs

- doc-sync の実装と CI 組み込みが必要。
- 生成境界（BEGIN/END）やファイル配置などの規約を追加で維持する必要がある。

### Neutral / Trade-offs

- 仕様書本文は規範の“全文列挙”ではなく、**意図・適用・解釈**に重点が移る。

## SPEC-SYS への反映（配置の確定）

本決定の反映先を以下の通り確定する。

1. **SPEC-SYS-001**（原則の SSOT）
   - Normative / Informative の定義
   - 衝突時の優先順位（Normative 優先）
   - Snapshot（生成物）と編集禁止の原則
   - 更新フローの概略（外部ファイル起点→再生成→検証）

2. **SPEC-SYS-002**（仕様書構造の標準化）
   - 仕様書内に Normative 参照と Snapshot を置くための標準セクション（例：Normative References / Generated Snapshot）を追加（推奨）

3. **SPEC-SYS-004**（契約）
   - 外部規範ファイル（schemas/profiles/catalog 等）を “規範成果物” として扱う契約
   - Snapshot の生成境界、決定性、派生物としての位置づけ

4. **SPEC-SYS-005**（手順）
   - doc-sync の手順（生成と一致検証）
   - CI gate / exit code / report への統合

5. **SPEC-SYS-003 / SPEC-SYS-006**（最小追記）
   - 規範列挙（ルールID定義、schema定義等）が外部SSOTにある場合の参照先明記
   - 本文は意味論／解釈／例へ寄せ、重複列挙を避ける

## Normative Artifacts（外部SSOT）の想定カテゴリ

本 ADR は、少なくとも以下のカテゴリの外部SSOT化を想定する（具体のパスはプロジェクトで確定する）。

- Lint rule catalog（FM/S/T の統合カタログ）
- Severity profiles（strict/balanced/exploratory）
- Schemas（front matter / config / artifacts 等）

## Appendix: Generated Snapshot Markers（推奨）

仕様書内の生成ブロックは、機械的置換が可能な境界を持つ（例）。

````md
<!-- BEGIN: GENERATED FROM docs/spec_system/lint_rule_catalog.yaml -->

```yaml
# DO NOT EDIT - generated snapshot
...
```

<!-- END: GENERATED -->
````

## USAGE

- この ADR は、外部SSOT化と生成スナップショット方式を導入／拡張する際の根拠として参照する。
- 規範内容を変更する場合は、まず外部SSOTを更新し、doc-sync により仕様書スナップショットを更新する。

## 運用上の目安（LLM / SDD 観点）

- LLM に「規範の正」を問う場合は、常に Normative（外部SSOT）を優先して参照する。
- LLM に「意図・背景・運用」を問う場合は、仕様書本文（Informative）を参照する。
- 仕様書内の Snapshot は閲覧用であり、編集対象ではない（編集は外部SSOT起点）。

## READ_NEXT

- SPEC-SYS-001 Spec System Operating Guide（Normative/Informative 原則の反映）
- SPEC-SYS-002 Section Schema（標準セクションとしての Normative References / Snapshot 追加）
- SPEC-SYS-004 Stable Artifact Contract（外部規範成果物と Snapshot の契約化）
- SPEC-SYS-005 Tooling Specification（doc-sync の実行手順・CI 統合）
