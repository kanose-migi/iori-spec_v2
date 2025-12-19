# TODO

- [ ] `spec_section_content.yaml` と `spec_section_schema.yaml` からテンプレートを生成する機能の仕様策定
- [ ] `spec_section_content.yaml` と `spec_section_schema.yaml` から、各セクションの目的・概要、および kind 別（共通含む）の記載ガイド（役割と書き方の目安）を提示するガイドファイルを生成する機能の仕様策定
- [x] spec_command.md に上記コマンドの転記完了

- 仕様の「粒度」を自動で促す機能：参照の密集点検出（境界崩壊の兆候）
- LLM向けの安全装置：仕様の「根拠リンク」（ADRへの参照）を必須化（高リスク領域）

- front format のとる値は設定ファイル iori_spec_config で定義するのだから、そこに仕様を記載すべき？

## section の定義

- [x] A. “構造に収束させる圧”が、要求・IF・DATA に対して弱い
  **interfaces：Errors が任意**
  現場ではエラーモデル（失敗条件、再試行可否、ステータスコード等）は downstream 設計・テスト設計の基礎です（ここが欠けると “暗黙知” 化しやすい）。
  `if_errors` の purpose/guidelines 自体は良いので 、**任意のままにするなら lint で強い WARNING を出す**（例：外部公開IFは Errors を推奨）などの「収束圧」が欲しいです。

- [x] A. “構造に収束させる圧”が、要求・IF・DATA に対して弱い
  **data_contracts：互換性/バージョニングの置き場が無い**
  `Schema / Constraints / 利用箇所` は揃っていますが 、Stable Core 観点だと **互換性（破壊的変更の扱い、移行手順の型）**が “自由セクション任せ” になりやすいです。
  汎用テンプレとしては、`## Compatibility`（必須 or 強推奨）を **data_contracts と interfaces に追加**するのが、長期運用で効きます。

- [x] A. “構造に収束させる圧”が、要求・IF・DATA に対して弱い
  **requirements：不変条件/境界条件の“専用置き場”が薄い**
  現行でも Scope/非ゴール/Acceptance はあるため最低限は回ります 。
  ただし「責務分割が促される」方向に収束させるには、**境界条件（Edge cases）や不変条件（Invariants）**を“任意の自由セクション”にせず、（必須にしないまでも）**標準セクションとして用意**した方が、品質が安定します。

- [x] B. “汎用テンプレ”としての kind 覆いが一部足りない
  REF-101 の core MUST には `impl_notes` が含まれていますが 、一方で **nonfunctional_requirements（NFR）kind が明示されていません**。
  どのプロジェクトでも品質要件（性能、信頼性、セキュリティ、運用性）は必ず出るので、汎用テンプレとしては NFR を “正式な kind” として持つのが自然です（section schema を用意するか、requirements に quality subtype を持たせるかのいずれか）。

- [x] C. “全ファイルで USAGE / 運用ノウハウ必須”は、コンテキスト量を押し上げやすい
  `tool_source=true` は context 抽出や index 生成の主要ソースという定義なので 、実装次第では **USAGE/運用ノウハウが毎回コンテキストに混入**し、局所性（短く貼る）を阻害します。
  実際 `show/context` は `tool_source=true` のセクションだけを抽出する想定が書かれています。

  対策（セクション定義を壊さずにできる）：
  - `tool_source` を二段階にする（例：`tool_source: index|context|both`）
  もしくは
  - schema に `tags: [context_core]` を導入して、context builder がタグで絞る

  いずれも「LLMに貼りやすい局所パック」を最優先するあなたの目的に合います。

- [x] D. 見出し番号（“4.” “5.” …）は将来的な拡張で摩擦になりやすい
  番号付き見出しは、人間には親切ですが、**途中に標準セクションを追加したくなったとき**に「番号を振り直すか／振り直さずに不自然な順番で追加するか」の二択になります。さらに “完全一致” 制約とも相性が悪いです。
  （今すぐ問題ではないが、Stable Core ほど変更しづらい領域なので早期に判断したい論点です。）

現行案は **「テンプレ生成・lint・context抽出の“動く最小核”」としては過不足ほぼ無し**です（REF-101 と content YAML と整合しているのが強い）。
ただし、あなたの“上位目的”まで最大適合させるなら、次を推奨します（影響が小さい順）：

1. **context 抽出のプロファイル化**（tool_source を二値のままにしない）
2. **Compatibility セクションの標準化**（interfaces / data_contracts）
3. **Errors を強推奨（できれば必須寄り）**にする運用ルール（lint warning）
4. **NFR の kind 方針**を決め、テンプレに反映する
5. **番号付き見出しを維持するか**（将来の拡張摩擦を許容するか）を Stable Core 判断として確定する

### SPEC-SYS-002_section_schema.md

- [ ] kind 別の必須セクションの SSOT は spec_sections_registry.yaml としたい。セクション別 kind の形式で保持している registry.yaml に基づいて、kind 別の必須セクションを  View として生成する。
  なので、SPEC-SYS-002 には kind 別の必須セクション を記載せず、View へのリンク/参照を保持させたい。

### その他

- text lint の導入 <https://zenn.dev/acha_n/articles/textlint-setup-guide>
