---
kind: requirements
scope: tooling.cli
id: REQ-800
spec_title: "REQ-800: iori-spec CLI ? Core Tooling Requirements"
status: draft

trace:
  req: []
  if:
    - IF-910    # index
    - IF-920    # lint
    - IF-930    # trace
    - IF-940    # search
    - IF-950    # impact
    - IF-960    # context
  data:
    - DATA-900  # spec_index
    - DATA-901  # spec_section_schema
    - DATA-904  # search_result
    - DATA-905  # context_bundle
    - DATA-906  # impact_report
    - DATA-910  # iori_spec_config
  test: []
  task: []

dp:
  produces:
    - DATA-900
    - DATA-904
    - DATA-905
    - DATA-906
  produced_by: []
  consumes:
    - DATA-901
    - DATA-910
  inputs: []

doc:
  read_next:
    - dev-plan.md
    - DATA-910_iori_spec_config.md
    - interfaces/IF-910_spec_index_builder.md
    - interfaces/IF-920_lint_core.md
    - interfaces/IF-930_trace_lint.md
    - interfaces/IF-940_search_specs.md
    - interfaces/IF-950_impact_analyzer.md
    - interfaces/IF-960_context_builder.md
  see_also:
    - reference/iori_spec_guide.md
---

# REQ-800: iori-spec CLI ? Core Tooling Requirements

## LLM_BRIEF

- role: このドキュメントは、`iori-spec` CLI ツールが満たすべき **ユーザー視点の要求（Requirements）** を定義します。
- llm_action: あなた（LLM）は、`interfaces/IF-9xx_*.md` や `data_contracts/DATA-9xx_*.md` を実装・修正するとき、この REQ を **上位のゴール** として参照し、ここに書かれた振る舞い・制約を壊さないようにしてください。CLI の細かい I/O 仕様は IF / DATA に委ねられますが、ここで定義された「MUST / SHOULD レベルの要求」を外れない実装を行うことが目的です。

## USAGE
- CLI の上位要求を確認したいときに読む。下位 IF / DATA / TEST を追加・修正する際の親要件。
- lint で requirements の必須 heading を補うときの参照テンプレ。
- LLM へのプロンプトに貼る場合は、`LLM_BRIEF` → 本セクション → `4. 要件の概要` → `6. Acceptance Criteria` の順で渡す。

## READ_NEXT
- `interfaces/IF-910_spec_index_builder.md`（index）
- `interfaces/IF-920_lint_core.md`（lint）
- `interfaces/IF-930_trace_lint.md`（trace）
- `interfaces/IF-940_search_specs.md`（search）
- `interfaces/IF-950_impact_analyzer.md`（impact）
- `interfaces/IF-960_context_builder.md`（context）
- `data_contracts/DATA-900_spec_index.md` / `DATA-901_spec_section_schema.md` ほか

## 1. このドキュメントの役割

- `iori-spec` CLI の **プロダクトとしての要求事項** をまとめる。
- 個別の IF（index / lint / trace / search / impact / context / show / graph / scaffold / tasks）に対して、何のために存在するか、どのレベルまで実用的に動く必要があるかを上位レイヤから規定する。
- Traceability: 本 REQ-800 は、IF-910 / 920 / 930 / 940 / 950 / 960 / 970 の「親」として機能する。

## 2. 範囲（Scope）と前提

### 2.1 対象
- `iori-spec` Python パッケージが提供する **CLI コマンド群**。
- 特に、次のコアコマンドを対象とする：`index` / `trace lint` / `trace report` / `lint` / `search` / `show` / `impact` / `context` / `new|scaffold` / `tasks list|report`（graph export/neighbors は NICE TO HAVE）

### 2.2 非対象
- LLM API の呼び出し自体（OpenAI / Anthropic などのクライアント実装）。
- エディタ拡張 / Web UI など、`iori-spec` CLI の上に乗るアダプタ。
- 仕様そのものの内容（各プロジェクト固有の REQ / IF / DATA / TEST）。

## 3. 運用上の目安（LLM / SDD 観点）
- 下位 IF / DATA / TEST を作成・変更するときは、必ず本 REQ に適合するかを確認する。
- lint エラーが出た場合は、必須 heading（LLM_BRIEF / USAGE / READ_NEXT / 1〜3 / 4 / 6）を優先的に補う。
- CLI コマンドの追加・大幅変更を行う場合は、本 REQ を更新し、対応する IF / DATA / TEST を同期させる。
- トレーサビリティは front matter の `trace.*` を SSOT とし、必要に応じて `trace report` でビューを生成する（手書きしない）。

## 4. 要件の概要（Summary）
- `iori-spec` CLI は、仕様の一覧・検索・Lint・トレース・影響分析・コンテキスト生成・プロンプト生成を統一的に提供し、仕様駆動開発を支援する。
- すべてのコマンドは `DATA-910_iori_spec_config` を基に動作し、`DATA-900_spec_index` を SSOT として利用する。
- JSON 出力は対応する DATA-9xx schema に準拠し（未定義の schema は今後追加検討）、CI / 自動化で再現性を担保する。

## 5. 背景・コンテキスト（任意）
- 仕様セットの健全性（構造・トレース）と、LLM への適切なコンテキスト供給を CLI で支援するための要求をまとめる。

## 6. Acceptance Criteria
- 必須 heading（LLM_BRIEF / USAGE / READ_NEXT / 1〜3 / 4 / 6）が存在し、requirements 用スキーマの lint に通ること。
- コアコマンド（index / trace lint / trace report / lint / search / show / impact / context / new|scaffold / tasks）が本 REQ の機能要件を満たし、対応 IF / DATA / TEST と整合すること。
- JSON 出力が対応する DATA-9xx schema に準拠し、CI で安定的に扱えること。
- front matter の `trace.*` で、本 REQ が対象 IF / DATA から参照されること（必要に応じて trace report でビューを生成）。

## 7. 用語

- **spec**: `kind: requirements / interfaces / data_contracts / ...` を持つ 1 ファイルの仕様。
- **SpecIndex**: `DATA-900`。全 spec のメタ情報カタログ。
- **ContextBundle**: `DATA-905`。LLM に渡す前段階の局所コンテキスト。
- **PromptBundle**: `DATA-907`。LLM にそのまま渡せるプロンプト構造。
- **project root**: `iori_spec_config.yaml` の置かれたリポジトリルート、または CLI 実行時に指定された root。

## 8. ユースケース概要

### 8.1 UC-1: 仕様セットの状態を把握したい
- どの kind / scope / ID の spec があるか、trace がつながっているか、lint 的に破綻していないかを素早く確認したい。

### 8.2 UC-2: 仕様変更の影響範囲を知りたい
- ある REQ / IF / DATA / TEST を変更したときに、どの spec / test / task を一緒に見直すべきかをコマンド 1 本で可視化したい。

### 8.3 UC-3: LLM に渡すコンテキストを自動生成したい
- 「この IF を実装させたい」など、LLM にタスクを投げる際に、周辺の REQ / DATA / TEST を含めた **適切なコンテキストパック** を自動生成したい。

### 8.4 UC-4: CI で仕様の健全性をチェックしたい
- GitHub Actions などから CLI を呼び出し、lint エラーや trace 崩れがあればビルドを落とす／問題がなければ 0 で終了、といった単純なルールを実現したい。

## 9. 機能要件（Functional Requirements）

### 9.1 共通 CLI 要件

1. **R-CLI-01**: サブコマンド形式  
   - `iori-spec <command> [options]` 形式でコマンドを提供すること。
2. **R-CLI-02**: プロジェクトローカルな動作  
   - デフォルトではカレントディレクトリ配下の `iori_spec_config.yaml` を起点とし、そこから相対パスで spec / artifacts を解決すること。
3. **R-CLI-03**: 設定ファイルの利用  
   - 仕様の root / artifacts 出力先 / section schema パスなどは `DATA-910 (iori_spec_config)` の内容に従うこと。
4. **R-CLI-04**: 出力形式の切り替え  
   - 各コマンドは `--format` オプションで少なくとも `text`（human-friendly）/`json` を切り替えられること（実装現状に合わせる）。  
   - `json` は対応する DATA-9xx の schema に準拠すること（未定義のものは将来の拡張）。

### 9.2 index コマンド（REQ → IF-910 / DATA-900）

1. **R-INDEX-01**: SpecIndex の生成  
   - `iori-spec index` は `DATA-910` で指定された `spec_root` / `spec_glob` に従って仕様ファイルを列挙し、`DATA-900_spec_index` を生成すること。
2. **R-INDEX-02**: SSOT としての位置づけ  
   - `search` / `impact` / `context` / `trace` など、他のコマンドは SpecIndex を唯一のソースとして参照すること（直接 Markdown を再走査しないこと）。

### 9.3 lint / trace コマンド（REQ → IF-920 / IF-930）

1. **R-LINT-01**: 構造・メタ情報チェック  
   - `iori-spec lint` は front matter / sections / ids を対象に、`DATA-901` と `DATA-910` の定義に沿って構造的な問題を検出すること。
2. **R-LINT-02**: ルール種別の区別  
   - lint/trace の結果には、少なくともルールカテゴリ（frontmatter / sections / ids / trace）が識別できる情報を含めること（出力スキーマは今後定義）。
3. **R-TRACE-01**: トレーサビリティ健全性  
   - `iori-spec trace` は SpecIndex（DATA-900）と front matter の `trace.*` を用いて G_trace を構築し、トレーサビリティの欠落や孤立ノードを検出すること。

### 9.4 search コマンド（REQ → IF-940 / DATA-904）

1. **R-SEARCH-01**: SpecIndex ベース検索  
   - `iori-spec search <query>` は、SpecIndex（DATA-900）を用いて `id` / `spec_title` / `scope` を対象に検索を行うこと。
2. **R-SEARCH-02**: JSON 出力  
   - `--format json` 指定時は、DATA-904（SearchHit[]）の schema に従うこと。
3. **R-SEARCH-03**: フィルタ・制限  
   - 少なくとも `--kinds` / `--limit` で kind フィルタと最大件数を制御できること。

### 9.5 impact コマンド（REQ → IF-950 / DATA-906）

1. **R-IMPACT-01**: 影響範囲の列挙  
   - `iori-spec impact <ID...>` は、指定した ID 群を起点として trace グラフ上の到達ノードを列挙できること。
2. **R-IMPACT-02**: 探索の制御  
   - 少なくとも `--mode`（forward/backward/both）と `--max-distance` を指定して探索範囲を制限できること。
3. **R-IMPACT-03**: JSON 出力  
   - `--format json` 指定時は、DATA-906（ImpactReport）の schema に従うこと。

### 9.6 context コマンド（REQ → IF-960 / DATA-905）

1. **R-CONTEXT-01**: 局所コンテキストの構築  
   - `iori-spec context <ID...>` は、seed ID 群とその近傍から LLM に渡しやすい ContextBundle（DATA-905）を構築できること。
2. **R-CONTEXT-02**: section schema の利用  
   - 抽出するセクションは DATA-901（spec_section_schema）の `tool_source=true` なルールに従うこと。
3. **R-CONTEXT-03**: トークン上限の目安  
   - `--max-tokens` を指定した場合、ざっくりとしたトークン見積もりによって過剰なコンテキストを避ける努力をすること（厳密でなくてよい）。


## 10. 非機能要件（Non-Functional Requirements）

### 10.1 操作性・UX

1. **RNF-UX-01**: 人間が読めるデフォルト出力  
   - `--format` 未指定時は、人間が CLI 上で読みやすいテーブルまたは Markdown 形式を採用すること。
2. **RNF-UX-02**: ヘルプの充実  
   - `iori-spec --help` および `iori-spec <command> --help` が利用可能なオプションと簡単な説明を表示すること。

### 10.2 CI / スクリプト連携

1. **RNF-CI-01**: 安定した JSON 形式  
   - `--format json` の出力は、対応する DATA-9xx schema を変えない限り互換性が保たれるよう配慮すること（フィールド追加は可、削除・意味変更は慎重に）。
2. **RNF-CI-02**: Exit Code  
   - コマンドは少なくとも次を満たすこと：正常終了: `0`、lint / trace で重大な問題がある場合: `>0`、使用方法エラーなども `>0` だが種別を区別できる余地を残すこと。

### 10.3 パフォーマンス・スケーラビリティ

1. **RNF-PF-01**: 中規模までの spec セットで実用的  
   - 数百〜数千ファイル程度の仕様セットで、index / lint / search / impact / context が日常的に使える応答時間を目指すこと（具体値は別途調整、MVP では数秒〜十数秒レベルでよい）。

## 11. I/O とフォーマット要件

1. **R-IO-01**: DATA-910 準拠  
   - すべてのコマンドは `DATA-910_iori_spec_config` を通じて spec / artifacts のパスを解決すること。
2. **R-IO-02**: DATA-900 を SSOT に  
   - trace / impact / context / search など、Spec の一覧・関係を必要とする処理は SpecIndex（DATA-900）のみを参照し、直接 Markdown を再走査しないこと（再現性と一貫性のため）。
3. **R-IO-03**: DATA-9xx の遵守  
   - `--format json` 出力を持つコマンドは、それぞれ対応する DATA-9xx schema を遵守すること。

## 12. トレーサビリティ・メタ要件

1. **R-TRACE-META-01**: IF / DATA との対応  
   - 本 REQ-800 は、`trace.if` / `trace.data` に列挙した IF / DATA から明示的に参照されること（双方向トレースの確立）。
2. **R-TRACE-META-02**: 拡張余地の確保  
   - 新しい CLI コマンド（`show` / `scaffold` / `graph` など）を追加する場合、必要に応じて REQ-8xx を拡張するか、新規 REQ を追加すること。
