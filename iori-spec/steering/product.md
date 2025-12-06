---
kind: steering
scope: meta
id: STEER-001
spec_title: "iori-spec プロダクト指針"
status: draft
---
# iori-spec プロダクト指針

## LLM_BRIEF
仕様書を解析・索引化し、lint / trace / impact / context / prompt を行うツールセット「iori-spec」のプロダクト方向性を示す。対象は仕様を書く人と、それを活用して開発・レビュー・プロンプト生成を行う人/LLM。

## USAGE
- iori-spec に関わる開発・改修の前に読み、目的と優先順位を共有する。
- 追加する IF / DATA / TEST / requirements を書く際の「上位の意図」を確認する。
- LLM に iori-spec の全体像を説明するときの冒頭コンテキストとして渡す。

## READ_NEXT
- `docs/steering/tech.md`（技術・非機能方針）
- `docs/reference/iori_spec_guide.md`（仕様の書き方・ID/構造ルール）
- `docs/reference/iori_spec_section_schema_guide.md`（必須セクションの意味と書き方）
- `docs/reference/iori_spec_config.yaml`（kind/scope vocabulary と設定）
- `docs/architecture/overview.md`（アーキテクチャ概要）
- `docs/requirements/functional.md`（機能要件の一覧）

## 1. このドキュメントの役割
- iori-spec のビジョンとプロダクトゴールを示し、個別の requirements / IF / DATA / TEST の上位に位置づける。
- ユーザー（仕様を書く人・読む人・LLM）が得る価値を明文化し、優先順位を揃える。
- 非ゴールや制約を共有し、実装・設計・運用で迷ったときの判断軸を提供する。

## 2. 範囲（Scope）と前提
- 対象: 仕様を中心にした開発フローを支援するツールチェーン（CLI / ライブラリ / スキーマ / 定義ファイル）。
- 利用者: 仕様を書く人、仕様をもとに実装・レビューする人、LLM を活用する人。
- 前提: 仕様は ID を持ち、front matter + セクションスキーマに従う。SpecIndex が SSOT となり、すべての分析はそこから行う。
- 非対象: 一般的なプロジェクト管理（課題管理やリリース管理）やソースコードビルド全般は範囲外。あくまで「仕様とその周辺コンテキスト」にフォーカスする。

## 3. 運用上の目安（LLM / SDD 観点）
- 仕様追加・変更は必ず lint / trace-lint を通し、SpecIndex を再生成して一貫性を保つ。
- LLM へのプロンプトは、最小限の必須セクション（LLM_BRIEF→USAGE→要件概要など）を順序立てて渡す。
- kind/scope/ID のルールは `iori_spec_guide.md` を唯一の参照源とし、逸脱する場合は Steering を更新して合意を取る。
- 新機能（コマンド・スキーマ）の追加は、REQ → IF → DATA → TEST の流れで仕様を先に用意し、実装は後追いする。

## 4. プロダクトゴール
- G1: 仕様セットの構造健全性を自動検証できる（front matter / sections / IDs / trace）。
- G2: SpecIndex を SSOT に、検索・影響分析・コンテキスト生成を高速に行える。
- G3: LLM との協働を前提に、必要なコンテキスト（Sections/IDs）を最小で抽出し、プロンプト化まで一気通貫で支援する。
- G4: 導入コストを下げるため、設定ファイルとスキーマを読めば第三者でも運用開始できる。

## 5. 提供価値
- V1: 仕様駆動（SDD）の実行力向上 — lint/trace/index により「仕様を書く/読む/維持する」負荷を下げる。
- V2: 変更影響の可視化 — REQ/IF/DATA/TEST 間のトレースをグラフで扱い、影響範囲を即座に提示する。
- V3: LLM との連携最適化 — 必要最小のセクションを抽出・圧縮し、プロンプト生成までを自動化する。
- V4: 導入容易性 — スキーマと設定を公開し、別プロジェクトでも転用しやすい形で提供する。

## 6. 非ゴール / 制約
- NG1: 一般的なプロジェクト管理（チケット・リリース計画）は扱わない。
- NG2: ソースコードビルドや実行環境の CI は範囲外（仕様周辺の分析に特化）。
- NG3: LLM モデルの実装やホスティングは行わない（利用は想定）。
- NG4: 仕様以外のドキュメント（設計詳細・API リファレンス以外の一般 docs）は lint/trace の対象外。

## 7. 成功指標（例）
- Lint/trace/index/impact/context/prompt が日常開発で使われ、手作業より早く正確な判断ができる。
- SpecIndex を起点に、影響範囲とコンテキスト生成が一貫して再現可能である。
- 新しい仕様ファイル追加時に、セットアップから lint 通過までの時間が短い（数分〜数十分）。
- 仕様変更時の漏れ（トレース切れ、セクション欠落）が顕著に減る。

