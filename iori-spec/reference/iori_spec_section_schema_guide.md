---
kind: reference
scope: meta
id: REF-101
spec_title: "Section Schema Guide"
status: review
---
# Section Schema Guide

## LLM_BRIEF
`spec_section_schema.yaml` に書かれたセクション構造ルールを、人間と LLM が理解しやすいように自然言語で説明するガイド。どの kind に何の見出しが必要か、どこを iori-spec が機械的に読むかを素早く把握できる。

## USAGE
- lint や spec 追加で見出し不足を指摘されたら、まず本ガイドを開いて必要セクションを確認する。
- 新しい kind を追加・変更する場合、`spec_section_schema.yaml` を編集しつつ、本ガイドで意図や読み方を補足する。
- LLM に「どの見出しが必須か」「どこを tool が読むか」を説明する際に、このガイドを貼る。

## READ_NEXT
- [reference/spec_section_schema.yaml](./spec_section_schema.yaml)（機械可読な元スキーマ）
- [reference/iori_spec_guide.md](./iori_spec_guide.md)（仕様全体の書き方・ID/構造ルール）
- [reference/iori_spec_config.yaml](./iori_spec_config.yaml)（kind / scope vocabulary）

## 1. このドキュメントの役割
- セクションスキーマの「意図」と「実務上の使い方」を文章で説明し、YAML を読まなくても最低限の判断ができるようにする。
- 必須／推奨セクションや、LLM/ツールが参照する箇所を明示し、lint 修正や新規 spec 追加を迷わず進められるようにする。
- スキーマ変更時に、人間向けの差分説明をここに追記しておく。

## 2. 範囲（Scope）と前提
- 対象: `steering / requirements / architecture / interfaces / data_contracts / tests / dev_tasks / reference` の core spec。
- 前提: 全ファイルは YAML front matter を持ち、kind に応じて決められた H2 見出しを含む（見出しは `spec_section_schema.yaml` で定義）。
- 本ガイドはスキーマの読み方と実務上の運用ヒントを示す。正式なチェックは `spec_section_schema.yaml` を参照。

## 3. 運用上の目安（LLM / SDD 観点）
- LLM に渡す際は `LLM_BRIEF` → 目的のセクションの順で貼ると誤読を防げる。
- lint エラーが出たら、「どの kind でどの見出しが missing か」を本ガイドで確認し、見出しを追加する。
- kind 追加や見出し変更は、ツール実装・既存 docs への影響が大きい。`spec_section_schema.yaml` と本ガイドをセットで更新し、関連 reference も同時に直す。

## 4. スキーマ表の読み方（概要）
- **kinds**: その見出しが適用される kind（requirements / interfaces など）。
- **heading.level/text**: 期待する見出しレベルと文字列（H2 固定）。テキストは lint で完全一致が求められる。
- **required**: true は必須、false は任意（推奨）。
- **multiple**: 同じ見出しを複数置いてよいか。
- **tool_source**: iori-spec が機械的に読むセクションかどうか。true のセクションは context 抽出や index 生成の主な情報源。
- **order**: 推奨の並び順（lint は順序はチェックせず、存在と重複をチェック）。

## 5. 全 kind 共通（core MUST）
`steering / requirements / architecture / interfaces / data_contracts / tests / reference / dev_tasks` すべてで必須の H2 見出し：
- `## LLM_BRIEF`
- `## USAGE`
- `## READ_NEXT`
- `## 1. このドキュメントの役割`
- `## 2. 範囲（Scope）と前提`
- `## 3. 運用上の目安（LLM / SDD 観点）`

## 6. kind 別必須・任意セクション

### requirements
- 必須: `## 4. 要件の概要（Summary）`, `## 6. Acceptance Criteria`
- 任意: `## 5. 背景・コンテキスト（任意）`, `## 7. 非ゴール / 除外事項（任意）`

### interfaces
- 必須: `## 4. Summary`, `## 5. Inputs`, `## 6. Outputs`
- 任意: `## 7. Errors（任意）`, `## 8. Examples（任意）`

### data_contracts
- 必須: `## 4. Summary`, `## 5. Schema`
- 任意: `## 6. Constraints（任意）`, `## 7. 利用箇所の概要（任意）`

### tests
- 必須: `## 4. Summary`, `## 6. Steps`, `## 7. Expected Results`
- 任意: `## 5. Preconditions（任意）`

### dev_tasks
- 必須: `## 4. Summary`, `## 5. Steps`, `## 6. Done Criteria`
- 任意: なし（必要に応じて自由に追加可）

### steering / architecture / reference / impl_notes
- 共通必須の 6 見出しのみをスキーマで強制。それ以外の見出しは自由に追加してよい。

## 7. 追加セクションの扱い
- `allow_extra_sections: true` により、スキーマにない追加見出し（自由セクション）は許可される。
- ただし必須見出しの欠落や重複は lint で検出されるため、まず必須を満たしたうえで任意の拡張を行う。

## 8. よくある確認ポイント
- 見出しの表記ゆれ（全角／半角・句読点違い）があると lint で missing 扱いになる。YAML の `text` と完全一致させる。
- kind を追加・変更したら、YAML と本ガイドを両方更新し、関連 reference（`iori_spec_guide.md` など）も揃える。
- ツールが読むのは H2 見出しの本文のみ。H3 以下は自由に使えるが、構造チェックはされない。

## 9. セクション別記載ガイド（役割と書き方の目安）

### 9.1 全 kind 共通
- `## LLM_BRIEF`: このファイルの役割と、LLM に何をさせたいかを2〜4行で端的に書く。ツールはここを最優先で読む。
- `## USAGE`: 人間向けの使い方・読み方。操作手順や参照順のヒントを具体的に。
- `## READ_NEXT`: 併読すべき spec のリスト。ID またはパスで列挙（箇条書き）。
- `## 1. このドキュメントの役割`: 何を解決するための文書か、期待するアウトプットは何かを説明。
- `## 2. 範囲（Scope）と前提`: 対象領域・前提条件・含めないもの（非対象）を明記。
- `## 3. 運用上の目安（LLM / SDD 観点）`: LLM への貼り方、lint 修正時のコツ、更新タイミングなどの運用ノウハウ。

### 9.2 requirements
- `## 4. 要件の概要（Summary）`: 何を実現するかを短く。入力/出力/制約があれば要点のみ触れる。
- `## 5. 背景・コンテキスト（任意）`: なぜ必要か、既存課題やシナリオを補足。
- `## 6. Acceptance Criteria`: 受け入れ条件を箇条書きで。観測可能な条件・境界値が望ましい。
- `## 7. 非ゴール / 除外事項（任意）`: 明示的に対象外とする範囲を列挙。

### 9.3 interfaces
- `## 4. Summary`: IF の役割を1〜3行で要約（どの入力をどの出力にするか）。
- `## 5. Inputs`: 受け取るデータ/パラメータと前提条件を具体的に。型や必須/任意を明記。
- `## 6. Outputs`: 返すデータ/副作用を具体的に。正常系の想定形を示す。
- `## 7. Errors（任意）`: 代表的な異常系、エラーコード、再送/リトライ可否など。
- `## 8. Examples（任意）`: 典型的な I/O 例や呼び出し例。LLM に貼りやすい最小セットで。

### 9.4 data_contracts
- `## 4. Summary`: このデータが何のためにあるか、生成/利用側の簡単な説明。
- `## 5. Schema`: フィールド一覧、型、必須/任意、制約（長さ/enum/正規表現など）。テーブルなら列定義を表形式で。
- `## 6. Constraints（任意）`: 整合性制約、ユニークキー、検証ロジック、性能上の制約などを詳述。
- `## 7. 利用箇所の概要（任意）`: 主な生成元/利用先の IF やバッチを自然文で補足（トレースは別途）。

### 9.5 tests
- `## 4. Summary`: テストの目的と対象範囲を1〜2行で。
- `## 5. Preconditions（任意）`: 前提環境・初期データ・前段タスクなど。
- `## 6. Steps`: 手順を箇条書きで。入力値や実行コマンドを具体的に。
- `## 7. Expected Results`: 期待結果を観測可能な形で列挙。出力値・ログ・ステータスなど。

### 9.6 dev_tasks
- `## 4. Summary`: タスクの目的と成果物を一言で。
- `## 5. Steps`: 実装/作業手順を箇条書きで。順序がある場合は明記。
- `## 6. Done Criteria`: 完了判定の条件（テストが通る、lint ノーエラー、ドキュメント更新完了など）。

### 9.7 steering / architecture / reference / impl_notes
- 共通 6 見出しのみがスキーマ必須。追加で記載する場合の例：
  - プロダクト概要、課題/価値、想定ユーザ、非ゴール、成功指標など（steering）
  - コンポーネント一覧、データフロー、依存ルール、設計方針など（architecture）
  - 用語集、命名規約、運用手順など（reference）
  - 調査メモ、検討ログ、作業メモなど（impl_notes）
