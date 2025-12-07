---
kind: steering
scope: meta
id: STEER-002
spec_title: "iori-spec 技術方針"
status: draft
---
# iori-spec 技術方針

## LLM_BRIEF
仕様解析・索引・lint・trace・impact・context・prompt を行うツールチェーン「iori-spec」の技術方針をまとめる。Python を中核に、SpecIndex を SSOT とした CLI/ライブラリ群を安定運用し、LLM 連携を前提にした拡張性・再現性を確保する。

## USAGE
- iori-spec の実装・改修前に技術上の原則と優先順位を確認する。
- requirements / interfaces / data_contracts / tests を追加・変更するときの前提条件として参照する。
- LLM に iori-spec の技術スタックや品質方針を説明するときの最初のコンテキストとして渡す。

## READ_NEXT
- [reference/iori_spec_guide.md](../reference/iori_spec_guide.md)（仕様の書き方・ID/構造ルール）
- [reference/iori_spec_section_schema_guide.md](../reference/iori_spec_section_schema_guide.md)（必須セクションの意味と書き方）
- [reference/iori_spec_config.yaml](../reference/iori_spec_config.yaml)（kind/scope vocabulary と設定）
- [architecture/ARCH-900_tooling_core.md](../architecture/ARCH-900_tooling_core.md)（アーキテクチャ概要）
- [requirements/REQ-800_tooling_cli.md](../requirements/REQ-800_tooling_cli.md)（機能要件の一覧）

## 1. このドキュメントの役割
- iori-spec を実装・運用する際の技術方針と非機能の軸を示す。
- SpecIndex を中心にしたデータフロー、開発プロセス、品質ゲートの原則を共有する。
- 技術選択や設計で迷ったときの判断基準を提供し、個別仕様との整合性を担保する。

## 2. 範囲（Scope）と前提
- 対象: iori-spec の CLI / ライブラリ / スキーマ / 設定ファイル。主に仕様解析・索引・lint・trace・impact・context・prompt 機能。
- 利用者: 仕様を書く人、iori-spec を使って実装/レビューする人、LLM を利用して開発を支援する人。
- 前提: SpecIndex（DATA-900）を SSOT とし、セクション構造は `spec_section_schema.yaml` に従う。ID は `REQ/IF/DATA/TEST/TASK/REF/STEER/...` などプロジェクト合意のプレフィックスを用いる。
- 非対象: ソースコードビルド全般や一般的なプロジェクト管理は扱わない。LLM モデル実装やホスティングは対象外（利用は想定）。

## 3. 運用上の目安（LLM / SDD 観点）
- 仕様変更は lint / trace-lint / spec_index の再生成をセットで行い、差分を確認する。
- LLM へのコンテキストは `LLM_BRIEF` → `USAGE` → 目的のセクション（Summary / Acceptance など）の順で最小限を渡す。
- kind/scope/ID ルールは `iori_spec_guide.md` を唯一の参照源とし、逸脱する場合は Steering を更新して合意を取る。
- ツール拡張は REQ → IF → DATA → TEST の順で仕様を追加し、実装はその後に行う。

## 4. アーキテクチャ原則
- **SSOT: SpecIndex** — 仕様一覧・メタ情報・トレースは DATA-900 を唯一のソースとして扱う。再スキャンを避け、一貫性を担保する。
- **Schema-first** — セクション構造（DATA-901）と設定（DATA-910）を先に定義し、それに従ってパーサ/CLI/生成物を実装する。
- **拡張可能な CLI** — `index / lint / trace-lint / search / impact / context / prompt` をコアとし、サブコマンド追加は IF/DATA で拡張可能に設計する。
- **ツール/データの分離** — 実装コードは `src/`、スキーマと仕様は `iori-spec/`、生成物は `artifacts/` に分離し、ロケールやプロジェクト差分は config で切り替える。

## 5. 技術スタック
- **言語**: Python 3.x（CLI/解析）、TypeScript（将来の UI/拡張用）。  
- **CLI/パーサ**: pathlib / yaml / json / re を中心に軽量実装。依存は最小限を維持。  
- **テスト/品質**: Python 単体テスト（pytest 想定）、lint（ruff 等）を適用。  
- **ビルド/配布**: パッケージングは pyproject ベース。生成物（SpecIndex, lint 結果など）は `artifacts/` に出力。  
- **データ契約**: DATA-9xx で定義された JSON/構造体を遵守し、出力互換性を優先（フィールド削除や意味変更は慎重に）。  
- **パフォーマンス/スケール**: 数百〜数千ファイルの仕様セットで実用的な応答時間を目標（詳細は非機能要件を参照）。  

## 6. 非機能・品質方針
- **再現性**: 同じ入力（`iori-spec/` + config）から同じ SpecIndex / lint 結果が得られること。  
- **透明性**: lint/trace/impact の結果は JSON と human-friendly 出力を両立。  
- **堅牢性**: 必須メタ情報欠落や不正 ID 形式を検出し、明確なメッセージとヒントを返す。  
- **移植性**: OS 依存を最小化し、クロスプラットフォームで動く CLI を目指す。  
- **拡張性**: 新しい kind/scope/ID プレフィックスを追加する場合は、config と lint/loader を同期させる手順を明確にする。  

## 7. リスクと対応策
- **ID/スキーマのズレ**: スキーマ更新とガイド更新がずれると lint が混乱する → スキーマ変更時は `iori_spec_guide.md` / `iori_spec_section_schema_guide.md` を同時更新し、CLI も追従する。
- **出力互換性の破綻**: DATA-9xx のフィールド変更で下位ツールが壊れる → 互換性ポリシーを明示し、重大変更はメジャーバージョンで行う。
- **パフォーマンス劣化**: 大規模 spec セットで CLI が遅い → SpecIndex をキャッシュし、section 抽出は tool_source セクションに限定する。
- **環境差異**: Python/パッケージバージョン差による結果不一致 → サポートバージョンを限定し、pyproject/lock で固定する。

## 8. オープンな論点 / TODO
- trace/impact/context のアルゴリズム最適化（大規模プロジェクト向けの性能検証）。
- UI/可視化ツール（graph viewer, lint report viewer）の範囲と優先度。
- LLM へのプロンプト最適化（圧縮戦略、セクション抽出ルールのチューニング）。
- 新しい ID プレフィックス（例: DOC-, OPS-）の追加要否と lint 実装方針。
