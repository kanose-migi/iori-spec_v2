---
kind: interfaces
scope: tooling.cli
id: IF-990
spec_title: "IF-990: graph export — Trace/DP/Docの可視化エクスポート"
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
    - impl_notes/spec_command.md
  see_also:
    - interfaces/IF-991_graph_neighbors.md
---
# IF-990: graph export — Trace/DP/Docの可視化エクスポート

## LLM_BRIEF
- role: `iori-spec graph export` は G_trace / G_dp / G_doc などの内部グラフを DOT 等でエクスポートし、可視化やデバッグに使うための IF。
- llm_action: SpecIndex（DATA-900）から構築したグラフを DOT/JSON で出力し、人間/ツールが構造を確認できるようにする。

## USAGE
- `iori-spec graph export --graph trace|dp|doc|all --format dot|json --out <PATH>`
- CI/デバッグでグラフ構造を可視化したいときに使う。生成物は artifacts/ 以下に書き出す想定。

## READ_NEXT
- `interfaces/IF-991_graph_neighbors.md`
- `requirements/REQ-800_tooling_cli.md`

## 1. このドキュメントの役割
- 内部グラフの可視化/デバッグ用エクスポートの仕様を定める。
- trace lint の結果だけでは分かりにくい依存構造を、人間が確認できる形で出力する。

## 2. 範囲（Scope）と前提
- 対象: `graph export` コマンドの I/O、サポートするグラフ種別とフォーマット。
- 前提: グラフ構築は DATA-900 を元に行い、手書きのトレースマップには依存しない。
- 非対象: レイアウトやビューア固有の設定（外部ツールに委ねる）。

## 3. 入出力（I/O 概要）
- 入力: graph 種別、フォーマット、出力先、root/index。
- 参照: DATA-900（SpecIndex）から trace/dp/doc を構築。
- 出力: DOT/JSON などのグラフ表現ファイル。

## 4. Acceptance 例（MVP）
- 指定したグラフ種別ごとに適切なノード/エッジを含む DOT/JSON を生成する。
- path/filename の解決は config/root と一貫する。
- 未知の種別やフォーマット指定時はわかりやすいエラーを返す。
