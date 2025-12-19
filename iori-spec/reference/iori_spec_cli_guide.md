---
kind: reference
scope: iori-spec
id: REF-105
spec_title: "iori-spec CLI 利用ガイド"
status: draft
---
# iori-spec CLI 利用ガイド

## LLM_BRIEF
iori-spec CLI の全コマンドを、初めて使う人／LLM にもわかるようにまとめた利用ガイド。セットアップからコアコマンド（index / trace lint|report / lint / search / show / impact / context）と拡張コマンド（prompt / graph / scaffold / tasks）までを網羅し、主要オプションと典型的な使い方を示す。

## USAGE
- iori-spec を初めて使う人・LLM に渡す最初の CLI リファレンスとして利用する。
- CI や自動化でコマンドを呼ぶ前に、必要な前提（config / root / extension ノードの扱いなど）を確認する。
- 詳細仕様は対応する REQ/IF/DATA（例: REQ-800, IF-910…）を参照する。

## READ_NEXT
- [README_SPEC.md](../README_SPEC.md) — 仕様全体の地図
- [requirements/REQ-800_tooling_cli.md](../requirements/REQ-800_tooling_cli.md) — コア要求
- [interfaces/](../interfaces/) — 各コマンドの IF 詳細
- [impl_notes/spec_command.md](../impl_notes/spec_command.md) — コマンド設計メモ

## 1. セットアップ
- 推奨: 仮想環境を作成し、編集インストールする
  - `python3 -m venv .venv`
  - `. .venv/bin/activate`
  - `pip install -e .`
- 標準配置なら `--config` は省略可（`iori-spec/reference/iori_spec_config.yaml` を自動検出）。
- 非標準配置や別プロジェクトで使う場合は `--config <path>` を指定。

## 2. 共通オプションと前提
- `--config`: `iori_spec_config.yaml` へのパス。未指定時はカレントディレクトリから上位を探索。
- `--root`: プロジェクトルートのオーバーライド。config 探索やパス解決に使用。
- `--glob`: 対象 spec のグロブパターンを上書き（必要な場合のみ）。
- `extension: true`: front matter に付いているノードは「拡張扱い」。trace lint では未トレース/孤立が WARN、無しはコア扱いで ERROR。

## 3. コアコマンド（MUST/SHOULD）

### 3.1 index（IF-910, DATA-900）
- 役割: SpecIndex（DATA-900）を再生成。すべてのコマンドの SSOT。
- 例: `iori-spec index`
- 主なオプション: `--glob`、`--output`、`--no-write`、`--format text|json`
- 出力先: デフォルト `artifacts/spec_index.json`

### 3.2 trace lint / trace report（IF-930, DATA-900）
- 役割: `trace.*` の健全性チェック（lint）と Traceability Map の生成（report）。
- 例: `iori-spec trace lint` / `iori-spec trace report --out artifacts/traceability_map.md`
- 特記事項: `extension: true` ノードは未トレース/孤立を WARN 緩和。コアは ERROR。

### 3.3 lint（IF-920）
- 役割: front matter / sections / ids の構造チェック。
- 例: `iori-spec lint --format text`
- 前提: `spec_section_schema.yaml` に定義された必須セクション。

### 3.4 search（IF-940）
- 役割: ID / spec_title / scope から候補を検索。
- 例: `iori-spec search "traceability" --kinds requirements,interfaces`
- 出力: text / json（DATA-904 相当）。

### 3.5 show（IF-980）
- 役割: 指定 ID の主要セクションを簡易表示（`context --radius 0` 相当）。
- 例: `iori-spec show REQ-800`
- 用途: search 後に「まず読む」ための入口。

### 3.6 impact（IF-950, DATA-906）
- 役割: 指定 ID から trace グラフをたどり影響ノードを列挙。
- 例: `iori-spec impact REQ-800 --max-depth 2 --include-roles req,if,data,test`
- 出力: text / json（ImpactReport, DATA-906）。

### 3.7 context（IF-960, DATA-905）
- 役割: 影響ノードの本文抜粋を束ねて LLM 用の ContextBundle を生成。
- 例: `iori-spec context REQ-800 --radius 1 --format text`
- 前提: section 抽出は `spec_section_schema.yaml` の `tool_source=true` を利用。

### 3.8 prompt（IF-970, DATA-907, 拡張）
- 役割: ContextBundle を入力に PromptBundle を生成（拡張機能）。
- 例: `iori-spec prompt --preset default.codegen --format json`
- 拡張扱い: `extension: true` が付いたノード（REQ-810/IF-970/DATA-907）。

## 4. 補助・運用コマンド（NICE TO HAVE）

### 4.1 graph export / graph neighbors（IF-990/IF-991）
- 役割: trace/dp/doc グラフを DOT/JSON でエクスポート、近傍を列挙。
- 例: `iori-spec graph export --graph trace --format dot --out artifacts/trace.dot`
- 例: `iori-spec graph neighbors REQ-800 --depth 1`

### 4.2 new / scaffold（IF-985）
- 役割: REQ/IF/DATA/TEST/TASK のテンプレ生成。
- 例: `iori-spec new req --id REQ-900 --spec_title "New requirement"`
- 前提: DATA-901（spec_section_schema）と spec_template を参照。

### 4.3 tasks list / report (IF-995)
- 役割: TASK-xxx の一覧・レポート（IF/REQ/DATA/TEST に紐づくタスク把握）。
- 例: `iori-spec tasks list --if IF-900`
- 注意: TASK は trace lint のカバレッジ対象外だが、一覧には出す。

## 5. 典型フロー（初めて触るとき）
1. `python -m venv .venv && . .venv/bin/activate && pip install -e .`
2. `iori-spec index` で SpecIndex を生成。
3. `iori-spec trace lint` / `lint` で構造・トレースの健全性を確認。
4. 仕様を読む: `search` → `show`（→必要なら `impact` / `context`）。
5. 変更を進めるときは `impact` で影響範囲を見てから `context` を LLM に渡す。
6. テンプレ追加は `new` / `scaffold`、タスク把握は `tasks list/report`。

## 6. エラーハンドリングと拡張ノード
- すべてのコマンドは config/root 解決に失敗した場合、エラーコード 2 で終了。
- trace lint: `extension: true` ノードの未トレース/孤立は WARN、その他は ERROR。
- コア/拡張の線引きを明示することで、CI での厳しさをコントロールする。

## 7. よくある質問（抜粋）
- Q: config を省略しても動く？  
  A: 標準配置なら自動検出。カスタム配置は `--config` を指定。
- Q: Traceability Map はどこにできる？  
  A: `trace report` が `artifacts/traceability_map.md` を生成（手書き禁止）。
- Q: prompt は必須？  
  A: 拡張機能。`extension: true` ノードとして扱い、未実装でもコア運用に影響しない。

## 8. 参考リンク
- REQ: [requirements/REQ-800_tooling_cli.md](../requirements/REQ-800_tooling_cli.md), [requirements/REQ-810_prompt_bundle.md](../requirements/REQ-810_prompt_bundle.md)
- IF: [interfaces/](../interfaces/)
- DATA: [data_contracts/](../data_contracts/)
- Config: [reference/iori_spec_config.yaml](./iori_spec_config.yaml)
