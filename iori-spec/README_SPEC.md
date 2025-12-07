---
kind: reference
scope: meta
id: REF-104
spec_title: "iori-spec 仕様セットの読み方"
status: draft
---
# iori-spec 仕様セットの読み方

## LLM_BRIEF
iori-spec の仕様ツリー全体の「入口」。どこに何があるか、何から読むか、LLM に何を渡すかを示す地図。詳細のSSOTは各 spec に委ね、本書はガイドとして機能する。

## USAGE
- はじめて iori-spec の仕様に触れる人／LLM へ渡す最初のコンテキストとして使う。
- 参照順と主要ファイルを確認し、必要な spec だけ深掘りする。
- lint/trace/index を回す前に、対象ファイルと関係ファイルを把握するチェックリストとしても使う。

## READ_NEXT
- [steering/product.md](./steering/product.md) / [steering/tech.md](./steering/tech.md)
- [reference/iori_spec_guide.md](./reference/iori_spec_guide.md) — 書き方・ID/構造ルール
- [reference/iori_spec_section_schema_guide.md](./reference/iori_spec_section_schema_guide.md) — 必須セクションの意味と書き方
- [reference/sdd_process_guide.md](./reference/sdd_process_guide.md) — SDD の回し方
- [requirements/REQ-800_tooling_cli.md](./requirements/REQ-800_tooling_cli.md) — 現行の要求セット
- [architecture/ARCH-900_tooling_core.md](./architecture/ARCH-900_tooling_core.md) — 仕様ツールの全体構成

## 1. このドキュメントの役割
- 仕様セット全体の地図として、主要ディレクトリと読む順番を示す。
- 人間と LLM が同じ前提で仕様を参照できるよう、最小限のナビゲーションを提供する。
- 詳細は各 spec（REQ/IF/DATA/TEST/REF など）が SSOT であり、本書は導線と参照順のガイドに徹する。

## 2. 範囲（Scope）と前提
- 対象: `iori-spec/` 配下のすべての仕様（steering / requirements / architecture / interfaces / data_contracts / tests / dev_tasks / reference）。
- 前提: YAML front matter と `spec_section_schema.yaml` に従うセクション構造を持つ。ID は合意済みプレフィックス（REQ/IF/DATA/TEST/TASK/REF/STEER/...）を用いる。
- 非対象: ソースコードやビルド設定の詳細は含まない。仕様の地図と参照順に特化する。

## 3. 運用上の目安（LLM / SDD 観点）
- 参照順は「上位→下位」。まず steering / reference を掴み、次に requirements、必要に応じて interfaces / data_contracts / tests を読む。
- LLM に渡すときは、`LLM_BRIEF` → `USAGE` → 関連する REQ/IF/DATA/TEST を最小限で貼る。全文貼りは避ける。
- lint/trace/index を回す前に、対象ファイルの READ_NEXT を確認し、近傍を補足する。
- CLI は標準配置（このリポジトリ: `iori-spec/reference/iori_spec_config.yaml`）なら `--config` 省略可。カスタム配置のときだけ `--config` で明示指定する。

## 4. 仕様ツリーの概要
- `steering/` — プロダクト・技術の方針（Why/Goals/非ゴール）。  
- `architecture/` — 全体構成と主要フロー。  
- `requirements/` — 機能・非機能要件（REQ-xxx）とトレースマップ。  
- `interfaces/` — 処理ユニット/ステージの IF-xxx（spec と card）。  
- `data_contracts/` — データ構造の SSoT（DATA-xxx）。  
- `tests/` — 受入・検証（TEST-xxx）。  
- `dev_tasks/` — 実装タスク（TASK-xxx）。  
- `reference/` — 書き方・スキーマ・運用ガイド（REF-xxx）。

## 5. 推奨参照順（初学者・大きな変更時）
1. `steering/product.md`（Why / ゴール / 非ゴール）  
2. `steering/tech.md`（技術方針・非機能の方向性）  
3. `reference/iori_spec_guide.md`（書き方・ID ルール）  
4. `reference/iori_spec_section_schema_guide.md`（必須セクションの意味）  
5. `reference/sdd_process_guide.md`（SDD の手順）  
6. `requirements/REQ-800_tooling_cli.md`（現行の要件セット）  
7. `architecture/ARCH-900_tooling_core.md`（仕様ツール全体の構成）  
8. 目的に応じて interfaces / data_contracts / tests / dev_tasks を参照（show/graph/scaffold/tasks など補助 IF もここで確認）。

## 6. LLM への貼り方（最小セット例）
- 背景共有: `steering/product.md` の LLM_BRIEF と 1章を短く貼る。  
- 書式/運用: `reference/iori_spec_guide.md` の LLM_BRIEF と該当セクションのみ。  
- SSOT/設定: `reference/iori_spec_config.yaml` と `reference/spec_section_schema.yaml`（セクション構造）を必要箇所だけ添付し、kind/scope と必須 heading を共有する。  
- 仕様インデックス: `iori-spec index`（標準配置なら config 自動検出）で生成した `artifacts/spec_index.json` を貼ると ID ↔ ファイルがすぐ引ける。  
- 実装タスク: 対象 REQ → 関連 IF（カード可）→ 必要 DATA → TEST を順に。

## 7. よく使うコマンド（概要）
- セットアップ: `python -m pip install -e .`（リポジトリ直下で実行し、CLI を有効化）。  
- index: `iori-spec index` — SpecIndex（DATA-900）を再生成（デフォルトで `artifacts/spec_index.json`）。  
- trace lint / report: `iori-spec trace lint` で `trace.*` を検証し、必要に応じて `trace report` で `artifacts/traceability_map.md` を再生成（ビュー、手書き禁止）。  
- lint: `iori-spec lint` — front matter / sections / ids の構造チェック。  
- search / show: `iori-spec search "<query>"` で候補 ID を探索し、`show <ID>` で主要セクションを短く確認。  
- impact / context: `iori-spec impact REQ-800 --max-depth 2` で近傍 ID を列挙し、`context REQ-800 --radius 1` で LLM 用コンテキストを束ねる。  
- scaffold: `iori-spec new <kind> --id ...` で REQ/IF/DATA/TEST/TASK のスケルトンを生成（必要に応じて活用）。  
- 共通オプション: 標準配置でない場合は `--config <path>` を明示。`--root` でプロジェクトルート、`--glob` で対象ファイルのパターンを上書きできる。
