---
kind: interfaces
scope: tooling.cli
id: IF-985
spec_title: "IF-985: scaffold/new — Specテンプレ生成"
status: draft
trace:
  req:
    - REQ-800
  if: []
  data:
    - DATA-900
    - DATA-901
  test: []
  task: []
dp:
  produces: []
  produced_by: []
  consumes:
    - DATA-901
    - DATA-900
  inputs: []
doc:
  read_next:
    - requirements/REQ-800_tooling_cli.md
    - data_contracts/DATA-901_spec_section_schema.md
    - impl_notes/spec_template.md
  see_also:
    - impl_notes/spec_command.md
---
# IF-985: scaffold/new — Specテンプレ生成

## LLM_BRIEF
- role: `iori-spec new` / `scaffold` は REQ/IF/DATA/TEST/TASK のテンプレを生成し、SDD で一貫した構造の spec を量産するための IF。
- llm_action: 追加する ID に応じて front matter・必須セクションを自動配置し、LLM は生成されたテンプレを埋めるだけで済むようにする。

## USAGE
- `iori-spec new <kind> --id <ID> --spec_title ... [--scope ...] [--status draft]`
- `spec_section_schema.yaml` と `spec_template` に沿った最小構造を出力する。
- 既存ファイルとの衝突を避け、パス命名規則に従ったファイル名を提示する。

## READ_NEXT
- `impl_notes/spec_template.md`
- `data_contracts/DATA-901_spec_section_schema.md`
- `requirements/REQ-800_tooling_cli.md`

## 1. このドキュメントの役割
- 新規 spec 作成時の型崩れを防ぎ、lint/trace が前提とする形で初期ファイルを生成する。
- LLM/人間がテンプレ埋めに集中できるよう、必須の front matter と heading を自動で整える。

## 2. 範囲（Scope）と前提
- 対象: `new` / `scaffold` コマンドの I/O、テンプレ生成ポリシー。
- 前提: kind ごとの命名規則（ファイル名、ID 形式）、必須セクションは DATA-901 と spec_template に従う。
- 非対象: 既存ファイルへのマージや差分編集（テンプレ生成のみ）。

## 3. 入出力（I/O 概要）
- 入力: kind / id / spec_title / scope / status / root / out。
- 参照: DATA-901（必須セクション）、spec_template（ヘッダ例）、DATA-900（ID 重複確認用）。
- 出力: 新規 Markdown テンプレファイル（dry-runで stdout、通常はファイル書き出し）。

## 4. Acceptance 例（MVP）
- ID/ファイル名の衝突を検出し、エラーまたは上書き防止の確認を行う。
- front matter に必須キー（id/kind/scope/spec_title/status）を含める。
- kind に応じた必須 heading を生成する（DATA-901 準拠）。
