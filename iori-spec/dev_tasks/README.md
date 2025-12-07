---
kind: reference
scope: dev_tasks
id: REF-121
spec_title: "dev_tasks/ (TASK-xxx) の配置と役割"
status: draft
---
# dev_tasks/ (TASK-xxx) の配置と役割

## LLM_BRIEF
`dev_tasks/` に置く TASK-xxx 仕様の入口。IF/REQ に紐づく作業単位をどう書き、trace グラフへどう載せるかの前提を示す。

## USAGE
- IF/REQ に付随する実装タスクを追加するときに、ID 付与と front matter 記載のルールを確認する。
- TASK は trace カバレッジ評価には含めないが、Graph には載せて impact/context で辿れるようにする方針を共有する。
- LLM に作業タスクの読み方を伝えるときの最初のコンテキストとして使う。

## READ_NEXT
- [impl_notes/dev_tasks_spec.md](../impl_notes/dev_tasks_spec.md)
- [impl_notes/spec_template.md](../impl_notes/spec_template.md)
- [reference/iori_spec_guide.md](../reference/iori_spec_guide.md)

## 1. このドキュメントの役割
- TASK-xxx をどこに置き、どの情報を必須とするかを短くまとめる。
- trace グラフ上での扱い（「カバレッジ評価対象外だがノードとしては保持」）を明示する。
- 具体的なタスク内容や完了条件は各 TASK-xxx が SSOT。

## 2. 範囲（Scope）と前提
- 対象: `dev_tasks/` 配下の TASK-xxx 仕様（`kind: dev_tasks`）。
- 前提: `id: TASK-...` と対応 IF/REQ/TEST を `trace.*` に記載し、`spec_section_schema.yaml` の必須セクションに従う。
- 非対象: 実装手順やコード変更の詳細ログ（必要なら別途 issue tracker 等へ）。

## 3. 運用上の目安（LLM / SDD 観点）
- TASK 追加時は対応する REQ/IF/DATA/TEST と相互参照を記載し、必要なら `trace report` で `artifacts/traceability_map.md` を再生成する。
- LLM へ貼る際は、本書よりも対象 TASK-xxx と親 IF/REQ の LLM_BRIEF を優先して渡す。
- CI の trace lint では TASK 未トレースはエラー扱いしない想定であることを共有する。
