---
kind: interfaces
scope: tooling.cli
id: IF-980
spec_title: "IF-980: show — Spec表示（コンテキスト0ラッパ）"
status: draft
trace:
  req:
    - REQ-800
  if:
    - IF-940
    - IF-960
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
    - interfaces/IF-940_search_specs.md
    - interfaces/IF-960_context_builder.md
  see_also:
    - impl_notes/spec_command.md
---
# IF-980: show — Spec表示（コンテキスト0ラッパ）

## LLM_BRIEF
- role: `iori-spec show` は指定 ID の spec 本体を、コンテキスト抽出なしで表示する簡易ビュー。`context --radius 0` の薄いラッパとして設計する。
- llm_action: search で見つけた ID を「まず一度読む」入口として、この IF を実装・利用する。SpecIndex（DATA-900）を使い、対象 ID の主要セクションだけを整形して出力する。

## USAGE
- `iori-spec show <ID>` で対象 ID の LLM_BRIEF/USAGE/主要セクションを表示する。
- `search` からのパイプラインや、LLM に貼る前の確認用ビューとして使う。
- JSON 出力は不要（MVP）だが、text フォーマットで読みやすさを優先する。

## READ_NEXT
- `interfaces/IF-940_search_specs.md`
- `interfaces/IF-960_context_builder.md`
- `requirements/REQ-800_tooling_cli.md`

## 1. このドキュメントの役割
- `context` のゼロ半径版として、指定 ID の主要セクションを素早く読める CLI 振る舞いを定義する。
- search → show → impact/context の流れを滑らかにするための UX 補助。

## 2. 範囲（Scope）と前提
- 対象: `iori-spec show` コマンドの I/O と簡易表示仕様。
- 前提: SpecIndex（DATA-900）で ID 解決し、Markdown 本文から必要なセクションを抽出する。コンテキストの半径計算や近傍探索は行わない。
- 非対象: 近傍追跡（impact）、局所コンテキスト生成（context）、JSON 出力。

## 3. 入出力（I/O 概要）
- 入力: ID（1件）、root/config/format オプション。
- 内部データ: SpecIndex（DATA-900）、対象ファイル本文。
- 出力: text フォーマットの主要セクション（LLM_BRIEF/USAGE/READ_NEXT/主要本文の要約部）。

## 4. Acceptance 例（MVP）
- ID 解決に失敗した場合は適切なエラーメッセージを返す。
- コンテキストの行番号や周辺抜粋は不要（radius=0 相当）。
- 設定（config/root）の解決は他コマンドと一貫させる。
