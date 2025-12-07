---
kind: interfaces
scope: tooling.cli
id: IF-991
spec_title: "IF-991: graph neighbors — 近傍デバッグビュー"
status: draft
trace:
  req:
    - REQ-800
  if:
    - IF-990
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
    - interfaces/IF-990_graph_export.md
    - requirements/REQ-800_tooling_cli.md
  see_also:
    - impl_notes/spec_command.md
---
# IF-991: graph neighbors — 近傍デバッグビュー

## LLM_BRIEF
- role: `iori-spec graph neighbors` は指定 ID の近傍ノードを列挙するデバッグ用 IF。trace/dp/doc グラフがどう張られているかを局所的に確認する。
- llm_action: 影響範囲やトレースを手早く目視確認したいときに、この IF を実装/利用して近傍を出力する。

## USAGE
- `iori-spec graph neighbors <ID> [--depth 1] [--graph trace|dp|doc|all] [--format text|json]`
- lint/impact の前に、ID 周辺のつながりを人間が確認する用途。

## READ_NEXT
- `interfaces/IF-990_graph_export.md`
- `requirements/REQ-800_tooling_cli.md`

## 1. このドキュメントの役割
- 近傍ノード列挙コマンドの入力/出力と、どのグラフを対象にするかを定義する。
- trace report に頼らず、局所的な接続確認を CLI から簡易に行えるようにする。

## 2. 範囲（Scope）と前提
- 対象: `graph neighbors` コマンドの I/O。trace/dp/doc いずれか（または all）を対象にする。
- 前提: グラフは DATA-900 から構築。`extension: true` を含むノードも出力対象だが、ラベル等で区別してもよい。
- 非対象: 影響範囲探索（impact）、コンテキスト抽出（context）。

## 3. 入出力（I/O 概要）
- 入力: ID、depth、graph 種別、format、root/index。
- 出力: text（人間向け）または JSON（ツール向け）の近傍ノード一覧。

## 4. Acceptance 例（MVP）
- 指定 depth までの到達ノードとエッジ種別を列挙する。
- ID が存在しない場合は明確なエラーを返す。
- format=text では読みやすいリスト、format=json では機械可読な隣接情報を出力する。
