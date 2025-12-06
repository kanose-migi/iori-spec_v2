---
kind: reference
scope: meta
id: REF-102
spec_title: "iori-spec Section Guide"
status: draft
---
# iori-spec Section Guide

## LLM_BRIEF
iori-spec で扱う仕様セクションの意味・粒度・書き分け方をまとめたリファレンス。`spec_section_schema.yaml` の機械可読な定義を、人間と LLM が運用する際の実用的なガイドとして補完する。

## USAGE
- 新しい仕様ファイルを作成する前に、必要なセクションや粒度を確認する。
- 既存仕様を lint で修正するときに、どの heading が何を担うかを素早く参照する。
- LLM へコンテキストを渡す際に、どのセクションから情報を抜き出すべきか判断する材料として使う。

## READ_NEXT
- `docs/reference/iori_spec_section_schema_guide.md`：セクションの必須 heading と属性を定義したスキーマ。
- `docs/reference/iori_spec_guide.md`：仕様全体の書き方・運用ルール。
- `docs/reference/iori_spec_config.yaml`：lint 設定や vocabulary の一覧。

## 1. このドキュメントの役割
- 仕様セクションごとの目的と期待する情報粒度を示し、文書間でのばらつきを減らす。
- lint エラーの解消だけでなく、LLM が適切に読み解ける構造を維持するための指針を提供する。
- スキーマに無い実務的な補足（例: 典型的な記述例、避けるべき書き方）をまとめる。

## 2. 範囲（Scope）と前提
- 対象: core spec 全般（steering / requirements / architecture / interfaces / data_contracts / tests / dev_tasks / reference）。
- 前提: YAML front matter を持ち、`spec_section_schema.yaml` に従うこと。セクションの heading レベルは H2 固定（`##`）。
- 本ガイドは記述スタイルの目安を示すのみで、厳密な構造チェックはスキーマが担う。

## 3. 運用上の目安（LLM / SDD 観点）
- LLM に読み込ませる際は、`LLM_BRIEF` を必ず先に渡し、続いて目的のセクションを順番に与えると誤読を防げる。
- `READ_NEXT` はコンテキスト選択の候補リストとして維持し、リンク切れや陳腐化を防ぐために仕様更新時に同時更新する。
- セクションの削除・統合を行う場合は、スキーマ更新とセットで lint を回し、差分が他の仕様へ波及しないか確認する。



