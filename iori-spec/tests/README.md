---
kind: reference
scope: tests
id: REF-120
spec_title: "TEST specs の配置と役割"
status: draft
---
# TEST specs の配置と役割

## LLM_BRIEF
`tests/` ディレクトリの入口。TEST-xxx 仕様をどこに置き、どのように trace へ参加させるかを示す。受入条件やケースは各 TEST-xxx が SSOT。

## USAGE
- 受入・検証仕様（TEST-xxx）を追加するときに、必須セクションや配置を確認する。
- `trace report` で生成する Traceability Map に TEST を載せるための前提（front matter の `trace.*` が SSOTで、生成物は `artifacts/traceability_map.md`）を共有する。
- LLM にテスト仕様の読み方を伝えるときの最初のコンテキストとして添付する。

## READ_NEXT
- [reference/iori_spec_guide.md](../reference/iori_spec_guide.md)
- [impl_notes/spec_template.md](../impl_notes/spec_template.md)
- [impl_notes/spec_structure_and_traceability.md](../impl_notes/spec_structure_and_traceability.md)

## 1. このドキュメントの役割
- TEST-xxx 仕様の置き場所と、trace/lint で期待される形を示す。
- テスト仕様を新規追加するときの「最低限の道標」として機能する。
- 本文は概要のみで、テストケースの正本は各 TEST-xxx に委ねる。

## 2. 範囲（Scope）と前提
- 対象: `tests/` 配下に置く TEST-xxx 仕様。
- 前提: front matter に `kind: tests`、`id: TEST-xxx`、`trace.*` を記載し、`spec_section_schema.yaml` の必須セクションに従う。
- 非対象: 実装コードや自動テストスクリプトの詳細。

## 3. 運用上の目安（LLM / SDD 観点）
- TEST-xxx 追加時は対応する REQ/IF/DATA の `trace.*` を相互に更新し、`trace report` で `artifacts/traceability_map.md` を再生成する。
- LLM へ貼るときは、本書の代わりに対象 TEST-xxx の LLM_BRIEF と Acceptance/ケース部分を優先して渡す。
- CI で lint/trace を回す前に、tests 配下のファイルが必須セクションを満たしているか確認する。
