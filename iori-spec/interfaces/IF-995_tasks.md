---
kind: interfaces
scope: tooling.cli
id: IF-995
spec_title: "IF-995: tasks list/report — TASKビュー補助"
status: draft
trace:
  req:
    - REQ-800
  if: []
  data:
    - DATA-900
  test: []
  task: []
dp:
  produces: []
  produced_by: []
  consumes:
    - DATA-900
  inputs: []
doc:
  read_next:
    - requirements/REQ-800_tooling_cli.md
    - impl_notes/dev_tasks_spec.md
    - impl_notes/spec_command.md
  see_also: []
---
# IF-995: tasks list/report — TASKビュー補助

## LLM_BRIEF
- role: `tasks list` / `tasks report` は TASK-xxx と他 ID の紐づきを一覧・レポートする運用補助 IF。impact/context だけでは見づらい作業タスクの把握を支える。
- llm_action: TASK ノードを一覧・集計し、関連する IF/REQ/DATA/TEST を表示する CLI を実装する。

## USAGE
- `iori-spec tasks list --if IF-900` などで関連 TASK を抽出。
- `iori-spec report tasks --by if` で IF ごとの TASK 一覧を表形式で出力。
- JSON / table いずれの形式でも読みやすさを優先する。

## READ_NEXT
- `impl_notes/dev_tasks_spec.md`
- `requirements/REQ-800_tooling_cli.md`

## 1. このドキュメントの役割
- TASK ノードを中心にしたビュー/レポートを提供する CLI 振る舞いを定義する。
- 実装計画や進捗確認で TASK を素早く引ける入口として機能させる。

## 2. 範囲（Scope）と前提
- 対象: `tasks list` / `tasks report` の I/O と出力形式。
- 前提: SpecIndex（DATA-900）に TASK ノードが含まれていること。trace lint のカバレッジ対象外である点を尊重する。
- 非対象: TASK の編集や作成。

## 3. 入出力（I/O 概要）
- 入力: seed（IF/REQ/DATA/TEST/TASK）、フィルタ、format、root/index。
- 参照: DATA-900 の nodes/edges を用いて TASK 関連を抽出。
- 出力: text/table/json で TASK 一覧または IF/REQ 別レポート。

## 4. Acceptance 例（MVP）
- 指定 seed に関連する TASK を漏れなく列挙できる。
- 出力形式が選べる（table/json）。存在しない場合はわかりやすいメッセージを返す。
- config/root の解決は他コマンドと一貫させる。
