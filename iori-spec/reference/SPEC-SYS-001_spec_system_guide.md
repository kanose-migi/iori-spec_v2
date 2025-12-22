---
kind: reference
scope: spec_system
id: SPEC-SYS-001
spec_title: "iori-spec Spec System Operating Guide (Authoring / Review / Reference Flow)"
stability: core # core|extension
status: draft # draft|review|stable|deprecated
---

# SPEC-SYS-001 Spec System Operating Guide (Authoring / Review / Reference Flow)

## LLM_BRIEF

- kind: reference（scope: spec_system）として、iori-spec における仕様書群を **新規作成・修正・参照**する際の「書き方」と「運用フロー」を定義する。
- セクションの抽出範囲は **`include_in`（特に `pack`）**を規範とし、局所コンテキストは **pack** を正として運用する。
- `trace` の意味論は SPEC-SYS-003、成果物契約は SPEC-SYS-004、実行/CI ゲートは SPEC-SYS-005、セクション定義は SPEC-SYS-002 を正とする
- 本仕様はそれらの**整合性を保つための運用・編集上の不変条件**に集中する。

## このドキュメントの役割

### 何を決めるか（本仕様の SSOT）

本仕様（SPEC-SYS-001）は、仕様書群（Markdown）の**整合性と変更容易性を継続的に担保するための運用ルール**を SSOT とする。

- 1ファイル1ID、命名、粒度（分割）といった **編集上の不変条件**
- セクション（H2見出し）の運用（追加・変更・未知セクションの扱い）
- `LLM_BRIEF` / `READ_NEXT` / `trace` を使った **局所推論の導線**の作り方
- 新規作成・修正・参照の **標準フロー**（チェックリスト含む）
- 破壊的変更／非推奨化などの互換性に影響する変更に関する運用ルール（breaking/deprecation の分類と扱い）

### 何を決めないか（他仕様へ委譲）

- セクション定義（registry/guide、`include_in`、ordering）: **SPEC-SYS-002**
- `trace` の意味論・整合性ルール・ルールID体系: **SPEC-SYS-003**
- index / pack / lint_report の成果物契約（shape・互換性・決定性）: **SPEC-SYS-004**
- ツールの実行モデル（scan→index→lint→pack）、CIゲート・exit code・profile: **SPEC-SYS-005**
- 物理配置（FS Layout）やコマンド名などの UX 詳細: 原則 **SPEC-SYS-004/005**（本仕様では必要最小限の指針のみ）

### 本仕様が答える主要な問い（チェックリスト）

- 新規 spec を作成するとき、最低限守るべき「編集上の不変条件」は何か。
- 仕様ファイルの標準セクション（H2見出し）を、どの順序で配置すべきか。
- 標準セクションを追加・変更したい場合、どの SSOT をどの手順で更新すべきか。
- `trace` / mentions / `READ_NEXT` を、それぞれどの役割（SSOT / 補助 / 導線）として扱うべきか。
- 新規作成・修正・参照の各フェーズで、どのフローに従えば破綻しにくいか。
- PR 前に確認すべき最小チェックリストは何か。

## 範囲（Scope）と前提（Assumptions）

### 対象（In scope）

- 本リポジトリで管理する **iori-spec 仕様書群（Markdown）**の「新規作成・修正・参照」に関する運用ルール。
- セクション（H2見出し）の運用（標準セクションの遵守、unknown section の扱い、標準セクションの追加・変更手順）。
- `LLM_BRIEF` / `READ_NEXT` / `trace` を使った **局所推論の導線**の作り方（ただし、`trace` の意味論そのものは含めない）。
- LLM には全文ではなく **pack（局所コンテキスト）を正**として渡す、という運用原則。

### 非対象（Out of scope）

- ドメイン仕様（REQ/IF/DATA/TEST）の妥当性や内容レビューの方法論そのもの（本仕様は「書き方/運用フロー」を扱い、内容の正誤は扱わない）。
- セクション定義（registry/guide、`include_in`、ordering）の具体仕様（→ **SPEC-SYS-002**）。
- `trace` の意味論・整合性ルール・最小カバレッジ要件（→ **SPEC-SYS-003**）。
- index / pack / lint_report の成果物契約（shape・互換性・決定性）（→ **SPEC-SYS-004**）。
- ツールの実行モデル（scan→index→lint→pack）、CI ゲート、exit code、profile（→ **SPEC-SYS-005**）。

### 前提（Assumptions）

- 仕様ファイルは YAML front matter を持つ。
- `id` はグローバル一意であり、参照可能である。
- セクション（H2見出し）の規範は `spec_sections_registry.yaml` / `spec_sections_guide.yaml`（SPEC-SYS-002）で定義される。
- 局所コンテキストとして LLM に渡す対象は、原則として `include_in: pack` により抽出される（成果物としての pack は SPEC-SYS-004、生成運用は SPEC-SYS-005）。

### 用語/定義（Definitions）

- **規範キーワード**: 本仕様は RFC 2119 の意味で MUST / MUST NOT / SHOULD / MAY を用いる。
- **Spec**: 本リポジトリで管理する Markdown 仕様ファイル（1ファイル1ID）。
- **Stable Core / Edge**: 互換性・決定性・CI 安定性の観点で固定すべき領域（Core）と、改善速度優先で変化を許容する領域（Edge）。
- **pack**: LLM に渡す局所コンテキスト束。抽出根拠は `include_in: pack`（SPEC-SYS-002）であり、成果物契約は SPEC-SYS-004。
- **mentions**: 本文中の ID 言及。`trace`（SSOT）を補助するが、関係の規範根拠にはしない（SPEC-SYS-003）。

## 編集上の不変条件（Authoring Invariants）

### 1ファイル1ID（MUST）

- 各 spec ファイルは **1 つの `id`**を持つ（MUST）。
- 1つの `id` は **1ファイルにのみ**現れる（MUST）。
- 仕様の置換・改訂は **新しい `id` を発行**し、`trace.supersedes` で旧 `id` を参照する（SHOULD）。詳細は SPEC-SYS-003。

### YAML front matter（MUST）

全 spec は YAML front matter を持ち、少なくとも以下を含める（MUST）。

- `kind`: 種別（例: requirements / interfaces / data_contracts / tests / architecture / steering / reference / impl_notes / dev_tasks など）
- `scope`: 対象領域（自由記述だが、プロジェクト内で語彙を揃えることを推奨）
- `id`: グローバル一意の仕様 ID
- `spec_title`: 人間・LLM が読むタイトル
- `status`: draft / review / stable / deprecated 等
- `stability`: core / extension 等（Stable Core 境界に関わる）

注: 必須キーの厳密な一覧や lint ルールは、プロジェクト側の規約（または将来の別仕様）で拡張し得る（MAY）。
ただし **`id/kind/scope/spec_title/status` は欠落させない**こと（SHOULD）。

### 粒度（MUST / SHOULD）

- 仕様は **1ファイル1責務**を原則とする（SHOULD）。
- 1つの spec に複数の独立したユースケースやルールが混在する場合、分割を検討する（SHOULD）。
- REQ は「テスト可能な粒度」を満たすよう原子化する（SHOULD）。最小カバレッジ要件は SPEC-SYS-003。

### 禁止事項（MUST NOT）

- **曖昧参照**（「これ」「上記」「例のやつ」等、ID によらない参照）を規範根拠として使ってはならない（MUST NOT）。
- **本文だけで関係が分かる前提**（trace を書かずに本文で匂わせる）に依存してはならない（MUST NOT）。
- セクション見出しの表記ゆれ（registry 定義の H2 と不一致）を放置してはならない（MUST NOT）。扱いは SPEC-SYS-002 の `policy.unknown_sections` に従う。

## セクション運用（H2見出し）

### 標準セクションの遵守（MUST）

- registry で定義されたセクションは **H2 見出しテキスト完全一致**で記述する（MUST）。根拠: SPEC-SYS-002。
- 仕様ファイルは原則として SPEC-SYS-002 の推奨順（LLM_BRIEF→役割→Scope→kind別→USAGE→運用目安→READ_NEXT）に従う（SHOULD）。

### unknown section の扱い（SHOULD）

- `policy.unknown_sections=allow` を前提に、未知セクションの追加は許容され得る（SHOULD）。
- ただし、未知セクションは **抽出対象（index/pack/render）に入らない**ことが多い。LLM に確実に渡したい情報は、registry/guide に登録されたセクションへ移す（SHOULD）。

### セクションを追加・変更する手順（MUST）

新しいセクションを「標準」として導入する場合:

1. `spec_sections_registry.yaml` に `section_id` を追加（必須/任意、applies_to_kinds、include_in、priority 等を定義）
2. `spec_sections_guide.yaml` に同一 `section_id` の guide を追加（purpose / guidelines / examples）
3. 同一PRで両方を更新し、lint を通す（MUST）

根拠: registry/guide の 1:1 対応は SPEC-SYS-002 の Cross-file invariants。

## 参照と導線（trace / mentions / READ_NEXT）

### trace を SSOT とする（MUST）

- ID 間の関係（実装可能性・検証可能性・依存・置換）は **`trace` に記述する**（MUST）。意味論は SPEC-SYS-003。
- 本文中の ID 言及（mentions）は補助であり、規範根拠にはしない（SHOULD）。根拠: SPEC-SYS-003。

### READ_NEXT の位置づけ（SHOULD）

- `READ_NEXT` は「読む/参照する順」の **人間・LLM 向け導線**であり、`trace` の代替ではない（SHOULD）。
- pack の `resolved_ids` 決定に `READ_NEXT` を混入させないのが既定（SHOULD）。混入は hints として記録し得る（MAY）。根拠: SPEC-SYS-005。

## LLM_BRIEF の書き方（規範）

### 目的（SHOULD）

`LLM_BRIEF` は、当該 spec を pack として単体で渡したときに、LLM が「何をすべきか」を誤解しないための最短要約である（SHOULD）。

### ガイドライン（SHOULD）

- 対象（kind/テーマ）と達成したいタスク（要件整理、IF 生成、テスト生成、影響分析等）を 2〜4 行で明示する（SHOULD）。
- 詳細要件の列挙ではなく、「このファイルの役割」と「出力してほしい作業」を優先する（SHOULD）。
- 依存する前提（参照すべき STEER/ARCH/REQ 等）がある場合、`READ_NEXT` と併せて明示する（SHOULD）。

## 標準フロー（新規作成・修正・参照）

### 1) 新規作成フロー（SHOULD）

1. `kind/scope` を決め、`id` を採番する。
2. YAML front matter を記入する（最低限の必須キー）。
3. registry/guide（SPEC-SYS-002）に従って H2 見出しを配置し、`LLM_BRIEF` を先に書く。
4. REQ の場合は `trace.satisfied_by`（IF/DATA）と `trace.verified_by`（TEST）で最小条件を満たす（SPEC-SYS-003）。
5. `READ_NEXT` を追加し、局所推論の導線を用意する。
6. ツール（lint/pack）を実行し、違反を修正する（SPEC-SYS-005）。

### 2) 修正フロー（SHOULD）

1. 変更が **修正（同一ID維持）**か **置換（新ID発行）**かを判断する。
   - 置換する場合は `trace.supersedes` を使用する（SPEC-SYS-003）。
2. 変更に伴い `trace`（depends_on / satisfied_by / verified_by 等）を更新する。
3. 影響が大きい場合は、pack（局所コンテキスト）で関係 spec をまとめてレビューする。
4. lint を実行し、重大度に応じて修正する（CI ゲートは SPEC-SYS-005）。

### 3) 参照フロー（SHOULD）

1. 参照したい spec の `id` を起点に、index / pack を生成する（概念として）。
2. `trace` を辿って、成立条件（depends_on）・実装（satisfied_by）・検証（verified_by）を確認する（SPEC-SYS-003）。
3. 必要に応じて `READ_NEXT` を hints として参照し、関連の地図を広げる（SPEC-SYS-005）。

## チェックリスト（PR 前の最小確認）

- front matter に `id/kind/scope/spec_title/status` がある
- registry 定義の H2 見出しが完全一致している（表記ゆれなし）
- REQ は `trace.satisfied_by`（IF 1+）と `trace.verified_by`（TEST 1+）を満たす（DATA 必須なら coverage_hints を含む）
- `READ_NEXT` が局所推論の導線として最低限機能する（関連IDが具体的）
- lint が PASS（またはプロファイルの許容範囲）である

## USAGE

### 想定読者（Who）

- 仕様書の作成者（要件/IF/DATA/TEST/architecture/steering 等の執筆者）
- 仕様書のレビュア（PR レビュー担当、リリース前レビュー担当）
- ツール運用者（lint / pack / CI ゲートを運用・保守する担当）

### 参照タイミング（When）

- **新規作成時**: YAML front matter / 標準セクションの配置 / `LLM_BRIEF` と `READ_NEXT` の作成方針を確認する。
- **修正時**: 「同一 ID の修正」か「新 ID による置換」かを判断し、`trace` と導線が切れないかを確認する。
- **参照時**: pack（局所コンテキスト）を起点に、`trace`（SSOT）→ `READ_NEXT`（導線）で関連 spec を広げる。
- **CI / lint 失敗時**: 違反の意味づけ（規範根拠がどこか）と、修正の手順を確認する。

### 使い方（How）

- 本仕様の「標準フロー（新規作成・修正・参照）」と「チェックリスト」を **テンプレ/チェックリスト**として扱い、PR 単位で運用する。
- 運用上は、次の用途概念を基準にツールを使う:
  - **index**: spec 群の機械処理用 SSOT を生成する（後工程の前提）
  - **lint**: 構造 lint + trace-lint を実行し、違反を検出する
  - **pack**: `include_in: pack` を根拠に局所コンテキスト束を生成する

### セットで読む spec（With）

- 本仕様は SPEC-SYS-002〜005 と組み合わせて参照することを想定する（詳細は `READ_NEXT`）。

## 運用上の目安（LLM / SDD 観点）

### 更新トリガー（いつ更新するか）

- セクション定義（registry/guide）の方針・値域・運用が変わった（例: ordering、unknown section policy、`include_in` の扱い）:
  - Action: 本仕様内の「セクション運用（H2見出し）」および「pack を正とする運用原則」の前提を点検し、矛盾があれば更新する。
  - Action: 必要なら同一 PR で関連する規約（SPEC-SYS-002 側の定義ファイル、テンプレ、運用ドキュメント）も併せて更新する。
- `trace` の意味論／最小カバレッジ要件／rule ID 体系が変わり、「作法」と整合しなくなった:
  - Action: 本仕様の新規作成/修正フローとチェックリスト（`trace` 更新・導線維持）を点検し、期待する作業単位（REQ→IF/TEST 等）が破綻しないよう更新する。
  - Action: 運用上の重大度（ゲート）への影響がある場合は、SPEC-SYS-005 の運用（profile/threshold）と整合するよう記述を調整する。
- 成果物契約（index / pack / lint_report の shape、決定性要件）が変わり、運用フロー（レビューや貼り方）が影響を受ける:
  - Action: 「pack を正として渡す」前提、差分安定性（順序/正規化）に関わる記述を点検し、実務フロー（PR で何を回すか）を更新する。
- ツール実行モデル、CI ゲート、exit code / profile が変わり、PR 前提が変わる:
  - Action: 本仕様の「標準フロー」および「CI / lint 失敗時の参照手順」を更新し、運用者が迷わない導線（どこが SSOT か）を維持する。
- 仕様編集における反復的な破綻が観測され、チェックリストやフローの改善が必要になった（例: 曖昧参照の再発、見出し表記ゆれの頻発、導線断絶）:
  - Action: 破綻パターンをチェックリストへ追加し、「先に直すべき最小違反」を明文化する（差分レビューの安定性を優先）。

### LLM 連携の原則（貼り方・渡し方）

- **全文貼りを常態化させず**、pack（局所コンテキスト）を正として運用する（局所推論の安定）。
- 最小セット（用途別の基本）:
  - **新規作成/大改修**: 本仕様（SPEC-SYS-001）の該当フロー（新規/修正/参照）+ 関連 spec の pack
  - **限定修正**: 対象 spec の pack + 変更差分（diff）+ 影響が及ぶ `trace`/`READ_NEXT` 断片
- 拡張セット（必要時）:
  - 参照 SSOT（SPEC-SYS-002/003/004/005）の該当箇所 + 互換性制約（決定性、contract_version、profile 運用）+ 代表例（移行妥当性確認用）
- 「後でつながるだろう」は破綻しやすい。REQ を書いたら **まず IF と TEST の導線**（satisfied_by / verified_by）を切らさない（SPEC-SYS-003）。

### ツール運用（lint / index / pack）

- PR の単位で `lint`（必要に応じて trace-lint を含む）と `pack` を回し、「違反を直してから次へ進む」を基本とする（ゲート詳細は SPEC-SYS-005）。
- 仕様の差分レビューを安定させるため、見出し順・配列順・正規化は成果物契約（SPEC-SYS-004）の方針に寄せる。
- CI とローカルの差分が運用事故になりやすい。可能な限り同一プロファイル/同一前提（設定）で評価できるよう運用を整える（詳細は SPEC-SYS-005）。

### 更新時の作法（どう更新するか）

- 本仕様を更新する場合は、関連する SSOT（SPEC-SYS-002〜005）との矛盾がないことを確認し、必要なら **同一 PR で併せて更新**する。
- 更新後は、想定プロファイルで lint を実行し、重大度に応じて修正する（CI ゲートは SPEC-SYS-005）。

## READ_NEXT

- SPEC-SYS-002: セクション定義（registry/guide、`include_in`、ordering、unknown section policy）の SSOT。H2 見出し運用を変更するときは必読。
- SPEC-SYS-003: トレーサビリティ（`trace` の意味論・最小条件・ルール ID 体系）の SSOT。作成/修正フローで `trace` を更新する判断根拠。
- SPEC-SYS-004: 成果物契約（index / pack / lint_report の shape・互換性・決定性）の SSOT。pack を正として運用する前提・レビュー安定性に直結。
- SPEC-SYS-005: ツール運用（Run Model、profile、CI ゲート、exit code）の SSOT。`lint` / `pack` を CI でどう止めるかの根拠。
