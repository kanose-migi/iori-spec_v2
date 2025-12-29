---
kind: steering
scope: spec_system
id: STEER-002
spec_title: "Technical Steering (Stable Core Boundary / Compatibility Policy)"
stability: core # core|edge
status: draft # draft|review|stable|deprecated
---

# STEER-002 Technical Steering (Stable Core Boundary / Compatibility Policy)

## LLM_BRIEF

- kind: steering（scope: spec_system）
- iori-spec の技術指針（Stable Core 境界、依存方向、互換性・決定性の方針）を定義する。
- 本仕様は「どこを安定させ、どこを拡張に任せるか」「互換性に影響する変更をどう分類し、どう扱うか」の上位基準を提供する。
- プロダクト目的・非目的・成功指標は STEER-001 を正とし、本仕様はそれを実現するための技術的ガードレールに集中する。

## このドキュメントの役割

### 何を決めるか（本仕様の SSOT）

本仕様（STEER-002）は、iori-spec の設計・運用を通じて “迷わない・壊れない” 状態を維持するために、以下を SSOT として定義する。

- Stable Core（安定側）と Edge（拡張側）の境界、および依存方向の規律
- 互換性に影響する変更の運用ルール（breaking/deprecation の分類と扱い）
- 成果物（index/pack/lint_report）およびツールI/Fに関する “決定性（determinism）” の基本方針
- 拡張点（extensions 等）を「互換性を壊さずに拡張する」ための原則
- 設計上の判断をどこに残すか（ARCH を薄く保ち、ADR へ退避する等）の原則

### 何を決めないか（委譲先）

- 仕様書の書き方・運用フロー（新規/修正/参照の手順、チェックリスト）：SPEC-SYS-001 が SSOT
- セクション定義（H2見出し）と適用ルール：SPEC-SYS-002 が SSOT
- trace の意味論・最小カバレッジ：SPEC-SYS-003 が SSOT
- 成果物契約（shape、contract_version、extensions 仕様、正規化の詳細）：SPEC-SYS-004 が SSOT
- ツール実行仕様・CI Gate（exit code 等）：SPEC-SYS-005 が SSOT
- 個別アプリ/プロダクト固有の要件・境界・データ契約：REQ/IF/DATA/TEST が SSOT

### 本仕様が答える主要な問い（チェックリスト）

- 何を Stable Core として固定し、何を Edge（拡張）に委ねるべきか
- Stable Core が Edge に依存しないための依存方向はどうあるべきか
- 互換性に影響する変更を、どの基準で breaking / deprecation / compatible に分類するか
- 破壊的変更や非推奨化を避けるために、どの拡張点を使うべきか（extensions 等）
- ツール成果物に必要な決定性を、どのレベルで担保するべきか（再現性・順序・正規化）
- “仕様が増えても迷わない” 状態を維持するために、どの情報をどこに残すべきか（ARCH/ADR/trace/pack）

## 範囲（Scope）と前提（Assumptions）

### 対象（In scope）

- iori-spec の Stable Core 境界と依存方向（内→外の規律）
- 互換性（breaking/deprecation を含む）と決定性に関する上位方針
- 拡張点の設計原則（互換性を壊さない拡張の仕方）
- 設計意思決定の残し方（ARCH/ADR の役割分担）と、変更に強い運用ループの前提

### 非対象（Out of scope）

- 成果物契約（JSON の具体スキーマ、フィールド一覧、正規化手順の詳細）：SPEC-SYS-004
- lint/trace/index/pack の具体手順・CLI仕様・CIゲート：SPEC-SYS-005
- 各 kind の具体仕様（REQ/IF/DATA/TEST の本文）およびアプリ固有のポリシー

### 前提（Assumptions）

- 仕様は「人間＋LLM の協働」を前提とし、局所コンテキスト（pack）とトレーサビリティ（trace）により更新容易性を担保する。
- 仕様・成果物・ツールI/Fは、利用者（Consumer）が段階的に増える可能性を見込み、互換性と決定性を Stable Core として扱う。
- “規約＋ツール”の二重化（文章の規範だけでなく、lint/trace-lint/CI gate による検知）で運用を成立させる。

### 用語・定義（Definitions）

- **Stable Core**：長期に互換性を保つべき中核（成果物契約、基本I/F、最小規約）。
- **Edge / Extension**：プロジェクト固有・実験的・変更頻度が高い領域。Stable Core を壊さない形で拡張する。
- **互換性（Compatibility）**：既存の Consumer / 既存の運用が破綻しない性質。
- **Breaking Change**：後方互換を破る変更（既存 Consumer が修正なしでは動かない／解釈できない）。
- **Deprecation**：現在は利用可能だが将来撤去予定として非推奨にする運用。
- **決定性（Determinism）**：同一入力（同一 repo 状態＋同一設定）から同一出力が得られる性質。

## 技術指針の全体像

本仕様の技術指針は、次の2つの目標を同時に満たすためのガードレールである。

- **進化可能性**：要求や運用が変わっても、Edge 側で柔軟に対応できること
- **安定性**：Stable Core（成果物契約・導線・最小規約）が崩れず、LLM運用・CI運用が壊れないこと

そのために、Stable Core と Edge を分離し、互換性・決定性・依存方向を「破れないルール」として扱う。

## Stable Core 境界と依存方向

### Stable Core に含めるもの（例）

- Spec System（SPEC-SYS-001〜005）と、それが規定する成果物契約・運用規約
- index/pack/lint_report の契約と、その互換性単位（contract_version）の考え方（詳細は SPEC-SYS-004）
- lint/trace/index/pack と CI gate の基本I/F（詳細は SPEC-SYS-005）

### Edge に委ねるもの（例）

- アプリ固有の REQ/IF/DATA/TEST の増減・分割・運用の細部
- 実験的な評価指標や補助ツール、追加のメタデータ（ただし互換性を壊さない形式で）

### 依存方向の原則

- Stable Core は Edge に依存してはならない（MUST NOT）。
- Edge は Stable Core に依存してよい（MAY）。
- 例外的に “参照” が必要な場合でも、Stable Core 側の成果物・契約・動作は Edge の有無で変わらないこと（MUST）。

## 互換性に影響する変更の運用ルール（breaking/deprecation の分類と扱い）

### 変更の分類（判断基準）

- **Compatible（後方互換）**：
  - Consumer が未知フィールド等を許容する設計で、既存運用が破綻しない拡張
  - 例：フィールド追加（任意）、列挙値追加（Consumer が未知値を許容する場合）
- **Deprecation（非推奨化）**：
  - 代替手段を提示し、一定期間の猶予を設けたうえで撤去する計画を伴う変更
  - 例：フィールドの非推奨化（残すが利用を推奨しない）、旧コマンドの段階的撤去
- **Breaking Change（破壊的変更）**：
  - 既存 Consumer が修正なしでは解釈できない／動作しない変更
  - 例：必須フィールド追加、意味論の変更、型変更、フィールド削除、契約の解釈変更

※具体の契約単位（contract_version の更新規則、extensions の互換性要求）は SPEC-SYS-004 を正とする。

### “壊さずに拡張する” 原則（推奨）

- 追加情報は、既存 Consumer が無視できる拡張領域に閉じ込める（例：`extensions`）ことを優先する。
- 互換性が疑わしい場合は、まず Deprecation を挟み、移行導線を用意する。
- Breaking を許容する場合は、影響範囲・回避策・移行方針を明文化し、CI gate とレビュー観点に組み込む。

## 決定性（Determinism）の基本方針

- ツール成果物（index/pack/lint_report）は、同一入力から同一出力になるべきである（SHOULD、Stable Core は可能な限り MUST）。
- 決定性を壊す要因（例：時刻埋め込み、非決定順序、環境依存のパス）は原則排除する。
- 決定性の詳細（正規化、ソート規則、ダイジェスト）は SPEC-SYS-004 を正とする。

## 拡張点の設計原則（extensions / Extension Sections）

- 拡張は “閉じた領域” に隔離し、既存 Consumer が無視しても成立する形にする（MUST）。
- 拡張の追加は、Stable Core の意味論を変えない（MUST）。
- 拡張が運用上必須になった場合は、Stable Core への昇格（契約化）を検討し、適切な互換性単位で管理する。

## 変更管理と設計意思決定の残し方（ARCH / ADR）

- ARCH は “迷子防止の地図” に徹し、詳細な根拠・分岐は ADR に退避する（SHOULD）。
- 互換性・決定性・依存方向に関わる意思決定は、後から追跡できる形で残す（SHOULD）。
- 仕様や契約が増えるほど “局所推論導線（LLM_BRIEF/READ_NEXT/pack）” の品質を優先する。

## USAGE

- 想定読者（Who）:
  - spec_system の設計者（Tech Lead/アーキテクト）、ツール実装者、CI運用者、仕様のレビュワー
- 参照トリガー（When）:
  - 成果物契約やツールI/Fに影響する設計変更を検討するとき
  - “互換性に影響する変更” が発生した／発生しそうなとき（breaking/deprecation 判断が必要）
  - 決定性（同一入力で同一出力）が崩れた／疑われるとき
- 使い方（How）:
  - 変更の分類（compatible / deprecation / breaking）を判断し、更新範囲（SPEC-SYS-004/005 等）とゲート方針を決める
  - 拡張点（extensions 等）を用いて “壊さずに拡張” できないかを先に検討する
  - Stable Core と Edge の境界を侵していないか（依存方向）をレビュー観点として用いる
- セット読み（With）:
  - STEER-001 — 目的・非目的・成功指標（技術判断の上位目的）
  - SPEC-SYS-004 — 成果物契約（互換性単位・正規化・extensions の詳細）
  - SPEC-SYS-005 — ツール実行仕様・CI Gate（運用上の止めどころ）
  - SPEC-SYS-003 — trace 規約（影響範囲の把握と更新漏れ防止）

## 運用上の目安（LLM / SDD 観点）

- 更新トリガー（Trigger → Action）:
  - 新しい artifact_kind / 新しい stable 出力を追加する:
    - Action: まず STEER-002 の Stable Core 境界・互換性方針に照らして妥当性を確認し、SPEC-SYS-004（契約）と SPEC-SYS-005（ゲート）を同一PRで更新する
  - 互換性判断（breaking/deprecation/compatible）の基準を変更したい:
    - Action: 本仕様を更新し、SPEC-SYS-004 の contract_version 運用および SPEC-SYS-005 のゲート（ERROR基準等）を見直す
  - 決定性が崩れた（出力差分が安定しない／環境で揺れる）:
    - Action: 本仕様の決定性方針に照らして原因分類し、SPEC-SYS-004 の正規化・ダイジェスト・ソート規則の点検と修正を行う
  - Edge 側の運用が Stable Core に “逆流” してきた（例：拡張が必須化している）:
    - Action: 拡張を extensions に閉じ込める／Stable Core へ昇格する（契約化）いずれかを判断し、必要なら SPEC-SYS-004 を更新する
- LLM 連携（貼り方）:
  - 最小セット: 本仕様の LLM_BRIEF + 変更内容（diff）+ 互換性分類案（compatible/deprecation/breaking）+ 期待成果物（方針に沿った更新案）
  - 拡張セット: SPEC-SYS-004（該当節）+ SPEC-SYS-005（ゲート）+ 影響する trace 近傍（関連 spec）を追加で渡す
- ツール運用（Gate）:
  - “互換性に影響する変更” を含むPRでは、contract_version の更新妥当性（MAJOR/MINOR/PATCH）と Consumer 側の未知フィールド耐性をレビュー観点に含める
  - 決定性に関する変更は、出力差分が再現可能であること（同一入力で同一出力）を CI 上で確認する（具体は SPEC-SYS-005）

## READ_NEXT

- STEER-001 — プロダクト目的・非目的・成功指標（技術判断の上位目的に戻る）
- SPEC-SYS-004 — 成果物契約（互換性単位・extensions・正規化の詳細）
- SPEC-SYS-005 — ツール仕様・CI Gate（運用上の検知と止めどころ）
- SPEC-SYS-003 — trace 規約（影響範囲の把握と更新漏れ防止）
- SPEC-SYS-001 — 仕様書群の運用フロー（新規/修正/参照の標準手順）
