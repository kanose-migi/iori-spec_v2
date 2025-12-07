---
kind: requirements
scope: tooling.prompt
id: REQ-810
spec_title: "REQ-810: Prompt Bundle (Extension)"
status: draft
extension: true

trace:
  req: []
  if:
    - IF-970      # Prompt Bundle Builder
  data:
    - DATA-907    # PromptBundle
    - DATA-905    # 入力: ContextBundle
  test: []
  task: []

dp:
  produces:
    - DATA-907
  produced_by: []
  consumes:
    - DATA-905
  inputs: []

doc:
  read_next:
    - interfaces/IF-970_prompt_bundle_builder.md
    - data_contracts/DATA-907_prompt_bundle.md
    - data_contracts/DATA-905_context_bundle.md
  see_also:
    - impl_notes/spec_command.md
---
# REQ-810: Prompt Bundle (Extension)

## LLM_BRIEF

- role: ContextBundle（DATA-905）から LLM へ渡す PromptBundle を組み立てる拡張機能の要求を定義する。
- llm_action: IF-970 / DATA-907 を設計・更新するときに、本要求を満たすこと。コア（index/lint/search/impact/context）とは独立した拡張として扱う。

## USAGE
- prompt 拡張を実装するときの親要求として参照する。
- コア要求（REQ-800）との衝突を避けるため、トレース上は拡張扱いであることを確認する。
- LLM に prompt 機能を説明するときの最小コンテキストとして貼る（LLM_BRIEF と 4/6 セクションを優先）。

## READ_NEXT
- `interfaces/IF-970_prompt_bundle_builder.md`
- `data_contracts/DATA-907_prompt_bundle.md`
- `data_contracts/DATA-905_context_bundle.md`

## 1. このドキュメントの役割
- ContextBundle → PromptBundle 変換を担う拡張機能の要求をまとめ、IF-970 / DATA-907 の上位ゴールを示す。
- コア CLI（index/lint/trace/search/impact/context）とは独立した optional 機能として位置づける。
- トレーサビリティ上、拡張機能であることを明記し、CI でのカバレッジ厳格度を下げる根拠とする。

## 2. 範囲（Scope）と前提
- 対象: PromptBundle 生成に関わる IF-970 / DATA-907 とその設定（DATA-910.prompt）。
- 前提:
  - ContextBundle（DATA-905）を入力とする。
  - LLM サービス非依存の JSON 互換構造を出力する。
  - preset/language は DATA-910 などの設定に従う。
- 非対象: LLM API 呼び出し本体、プロバイダ固有の message 形式。

## 3. 運用上の目安（LLM / SDD 観点）
- ステータスが draft の間は trace lint のカバレッジ判定を厳格にしない（拡張扱い）。
- ContextBundle 抽出ポリシーの変更に合わせて PromptBundle のテキスト量・構造を見直す。
- コア機能と混同しないよう、README/ARCH では拡張タグ付きで案内する。

## 4. 要件の概要（Summary）
- ContextBundle を入力に、preset/language/extra_instruction に基づく PromptBundle を生成できること。
- PromptBundle は system/user/context_markdown/context_items を含み、LLM へそのまま渡せる形であること。
- 構造は DATA-907 に従い、拡張機能としてコアの整合性を壊さないこと。

## 5. Acceptance Criteria
- IF-970 / DATA-907 が本 REQ にトレースされ、`trace report` で拡張として識別できること。
- PromptBundle の JSON 構造が DATA-907 準拠であること。
- preset/language の解決が DATA-910 の定義を尊重していること（将来拡張可）。

## 6. 用語
- **PromptBundle**: LLM に渡す system/user/context をまとめた JSON 互換オブジェクト。
- **preset**: system/user テンプレートや言語を切り替える論理名（DATA-910 で定義）。
