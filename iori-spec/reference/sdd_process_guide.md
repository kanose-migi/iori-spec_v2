---
kind: reference
scope: meta
id: REF-103
spec_title: "SDD プロセスガイド"
status: draft
---
# SDD プロセスガイド

## LLM_BRIEF
Specification Driven Development（SDD）を iori-spec で回すための手順書。要求→設計→タスク→実装→検証まで、どのタイミングでどの仕様/コマンド/チェックを使うかを整理し、人間と LLM が同じフローを踏めるようにする。

## USAGE
- 仕様追加・変更を始める前に、どのフェーズで何をやるか確認する。
- LLM に「この手順で進めて」と指示する際の貼り付け用コンテキストとして渡す。
- レビューや合意形成時に、抜け漏れ（lint/trace/index 更新など）がないかのチェックリストとして使う。

## READ_NEXT
- `docs/reference/iori_spec_guide.md`（仕様の書き方・ID/構造ルール）
- `docs/reference/iori_spec_section_schema_guide.md`（必須セクションの意味と書き方）
- `docs/reference/iori_spec_config.yaml`（kind/scope vocabulary）
- `docs/steering/product.md` / `docs/steering/tech.md`（上位方針）
- `docs/requirements/functional.md` / `docs/requirements/nonfunctional.md`

## 1. このドキュメントの役割
- SDD を回すためのフェーズ、成果物、チェックポイント、コマンドを一覧化し、誰が見ても同じ手順で進められるようにする。
- LLM に「どの仕様を、どの順で、どの粒度で渡すか」を明示し、コンテキスト過多/不足を防ぐ。
- lint/trace/index といった品質ゲートをプロセスに組み込み、再現性のある運用を支える。

## 2. 範囲（Scope）と前提
- 対象: iori-spec を使った仕様中心の開発（REQ/IF/DATA/TEST/TASK の追加・変更）。
- 前提: 仕様は `spec_section_schema.yaml` に従い、ID は `REQ/IF/DATA/TEST/TASK/REF/STEER/...` のプロジェクト合意プレフィックスを用いる。SpecIndex（DATA-900）が SSOT。
- 非対象: 一般的なチケット運用やリリース計画は別管理とし、ここでは仕様とその周辺フローに限定する。

## 3. 運用上の目安（LLM / SDD 観点）
- フェーズごとに貼るべき仕様を最小限にする（LLM_BRIEF → USAGE → 目的のセクション順）。全文貼りを避ける。
- lint/trace/index は「仕様変更のたびに回す」ことを原則化し、生成物（artifacts）も更新する。
- kind/scope/ID を増やす・変える場合は、config と lint/loader/ガイドをセットで更新し、合意を取る。

## 4. フェーズ概要（人間/LLM 共通の進め方）
- **Phase 1: 目的と境界の合意**  
  - 読む: steering（product/tech）、関連 REQ/REF。  
  - 決める: スコープ・非ゴール・優先度。  
  - チェック: 既存の REQ が流用できるか確認。
- **Phase 2: 要求/設計の明文化**  
  - 読む: 関連 REQ / IF / DATA / TEST / reference。  
  - 書く: REQ を更新/追加。IF/DATA/TEST の草案（カード/要約）を用意。  
  - チェック: lint（frontmatter/sections/ids）を通す。
- **Phase 3: タスク化と実装準備**  
  - 書く: TASK（dev_tasks）を起こし、Steps/Done Criteria を明記。  
  - 更新: traceability_map（必要なら）。  
  - チェック: trace-lint / spec-index。
- **Phase 4: 実装・検証**  
  - 実装: コード/スクリプトを変更。  
  - 検証: テスト（TEST-xxx）更新/追加、lint/trace/index 再生成。  
  - 出力: artifacts（lint 結果、spec_index など）を更新。
- **Phase 5: 合意・リリース準備**  
  - レビュー: 必須セクションが揃っているか、trace/impact が成立するか確認。  
  - 記録: README_SPEC や reference に運用上の注意を反映（必要なら）。

## 5. LLM へのコンテキスト渡しガイド
- 最小セットの順序: `LLM_BRIEF` → `USAGE` → 目的セクション（Summary/Acceptance/Inputs/Outputs 等）。  
- 複数ファイルを渡す場合は「親→子」の順で貼る（例: REQ → IF → DATA → TEST）。  
- 影響確認は `READ_NEXT` を優先参照し、必要最小限の近傍だけを貼る。

## 6. チェックリスト（抜粋）
- フロントマター: kind/scope/id/spec_title/status は埋まっているか。  
- 必須セクション: `LLM_BRIEF` / `USAGE` / `READ_NEXT` / 1〜3 章＋kind別必須セクション（Summary/Acceptance 等）。  
- ID 形式: ルールに従うか（REQ/IF/DATA/TEST/TASK/REF/STEER/...）。  
- Trace: REQ ⇔ IF ⇔ DATA ⇔ TEST ⇔ TASK のリンクが途切れていないか。  
- 生成物: lint / spec_index が最新か、artifacts を更新したか。

## 7. コマンドとタイミング（目安）
- `iori-spec lint`：仕様を編集したら毎回。  
- `iori-spec trace-lint`：トレースを追加/変更したら。  
- `iori-spec index`：lint/trace 後に再生成し、artifacts を更新。  
- `iori-spec search|impact|context|prompt`：検討・影響調査・コンテキスト生成時に適宜。

## 8. 役割と合意形成（最小限のガイド）
- 仕様作成者：前提/スコープ/要件を明確化し、必須セクションを埋める。  
- レビュワー：lint/trace/index の結果と必須セクションを確認し、欠落を指摘。  
- 合意: 上位 steering（product/tech）に反しないかを確認し、必要なら steering を更新してから下位仕様を確定。

## 9. オープンな論点 / TODO
- フェーズごとの承認基準（誰が承認するか、どの成果物を持って進むか）の細分化。  
- LLM 用のプロンプトテンプレ（貼り方・圧縮ルール）の具体化。  
- CI での自動チェック範囲と頻度（lint/trace/index/impact の実行ポリシー）。  
