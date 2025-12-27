---
kind: reference
scope: spec_system
id: SPEC-SYS-005
spec_title: "iori-spec Tooling Specification (Index / Lint / Context Pack / CI Gate)"
stability: core # core|extension
status: draft # draft|review|stable|deprecated
---

# SPEC-SYS-005 Tooling Specification (Index / Lint / Context Pack / CI Gate)

## LLM_BRIEF

- kind: reference（scope: spec_system）
- 本仕様は、iori-spec ツールの **実行仕様（Run / Config / Profile / Gate / exit code）**を定義する。
- 成果物契約は SPEC-SYS-004、`trace` の意味論・ルールID/プロファイル例は SPEC-SYS-003、セクション定義は SPEC-SYS-002 を正とし、本仕様はそれらに基づく **手順と運用（プロファイル、ゲート、exit code）**を規範化する。
- 規範（Normative）のSSOT（ルールカタログ／プロファイル／スキーマ等）は **機械可読な外部ファイル**に外部化し、仕様書内の生成スナップショット（DO NOT EDIT）は doc-sync により同期検証できるように運用する。

## このドキュメントの役割

- 何を決めるか（本仕様の SSOT）
  - ツールの実行モデル（Run）、入力（Spec Root）、設定の解決順、既定値
  - プロファイルの指定・保管・優先順位
  - lint の実行範囲（構造lint + trace-lint）、Quality Gate（PASS/FAIL）、exit code
  - doc-sync（外部SSOT→仕様書内 Snapshot 再生成／差分検証）と、その結果の Gate/exit code への接続
  - context pack の生成の起点（seed / lint連携）と “運用としての” 既定挙動
  - index の扱い（pack/lint の前提工程として必須）と最小の運用境界
- 何を決めないか（他仕様へ委譲）
  - 成果物のデータ契約（フィールド、順序、決定性、互換性）: SPEC-SYS-004
  - `trace` の意味論・一般制約・ルールID定義: SPEC-SYS-003
  - セクション定義（H2 heading、section_id、include_in、ordering）: SPEC-SYS-002
- 過剰設計回避
  - CLI 名やサブコマンド体系は **非安定**（例示扱い）。仕様の安定軸は用途概念（index / lint / pack）と設定キーである。
- 本仕様が答える主要な問い（チェックリスト）
  - 1回の Run で、どのフェーズを **必ず**実行し、どの成果物を生成するか（scan → index → lint → pack）
  - 設定はどの順序で解決され、Effective Config はどの値を含むべきか
  - lint の結果は、どのように finding / severity / rule_id として表現され、Gate にどう接続されるか
  - pack は何を根拠に抽出し、`resolved_ids` は何に基づいて決まるか
  - CI は何をもって PASS/FAIL/実行失敗を判定するか（exit code の意味論）

## 範囲（Scope）と前提

### 規範キーワード（本仕様内）

本仕様は RFC 2119 の意味で MUST / MUST NOT / SHOULD / MAY を用いる。

### 用語（本仕様内）

- **Spec Root**: 仕様書群（Markdown）を探索する起点ディレクトリ。
- **Run**: 1 回のツール実行。入力（Spec Root + 有効設定）に対して、index / lint_report / pack を生成し、必要に応じてゲート判定・exit code を返す。
- **Effective Config（有効設定）**: 既定値・設定ファイル・CLI 等を解決して確定した実効設定（後述）。決定性および `config_hash` の対象となる。
- **Severity の順序**: 本仕様における重大度の順序は `error` > `warn` > `info` とする（MUST）。

### 対象（in-scope）

- ツール機能（安定コア）
  - **index**（pack / lint の前提工程として必須）
  - **lint**（構造lint + trace-lint）
  - **pack**（context pack：局所化）
  - **CI ゲート判定**と **exit code**
- 設定・運用
  - 設定ファイル（config）とプロファイル（profile）
  - 設定の解決順・既定値・CI 推奨運用

### 非対象（out-of-scope）

- index / pack / lint_report の出力フォーマット詳細・互換性契約: SPEC-SYS-004
- `trace` の意味論とルールIDの定義: SPEC-SYS-003
- セクション定義・抽出対象の定義（include_in は `{index, render, pack}` のみ）: SPEC-SYS-002
- CI プラットフォーム別の通知・可視化（PR annotations 等）や、人間向けレポート整形（Markdown/HTML）などの UX 最適化（※本仕様では拡張点として扱う）

### 前提（必須依存）

- pack の抽出根拠は SPEC-SYS-002 の `include_in: pack` を用いる（抽出対象の SSOT）。
- lint のルールID（FM### / S### / T### 等）と内蔵プロファイル（strict / balanced / exploratory）の割当は、外部SSOT（ルールカタログ／profiles）を正とする。
  - ただし、ルールの意味論（何を違反とみなすか）と適用範囲は SPEC-SYS-006/002/003 を正とする。
- pack / lint_report は `source_index`（index_digest / index_contract_version）を必須とする（SPEC-SYS-004 の要件）。よって **index_digest を得られること**は本仕様の前提となる。

---

## Stable Core と Edge の境界（責務分類）

本仕様は「安定核（Stable Core）＋周辺（Edge）」で運用互換性と改善速度を両立する。

### Stable Core（固定すべき責務）

以下は、下流互換性・再現性・CI 安定性に直結するため Stable Core とする（MUST）。

1. **Run のフェーズ構造**（scan → index → lint → pack）と、pack/lint が index を前提とすること
2. **設定解決順序**と **Effective Config** の定義
3. **プロファイル機構**（profile の指定・解決・未割当時の既定 severity）
4. **Quality Gate（PASS/FAIL）**の意味論（threshold と判定規則）
5. **exit code** の意味論（0/1/2 の固定）
6. **doc-sync**（外部SSOT→仕様書内 Snapshot の再生成／差分検証）と、Gate への接続
7. 成果物契約への準拠（SPEC-SYS-004）
   - lint_report の `run_status` 算出
   - pack/lint_report の `source_index`（index_digest / index_contract_version）の付与

### Edge（拡張点として切り出す責務）

以下は環境・プロジェクト事情で変わりやすく、改善サイクルを阻害しやすいので Edge とする（MAY/SHOULD）。

- CLI 名やサブコマンド体系（例示に留める）
- CI プラットフォーム別の統合（annotations / PR comment / Slack 通知 等）
- 人間向けレポート整形（Markdown/HTML/色付きログ/TUI）
- search / impact のランキング・ヒューリスティクス、表示順の最適化
- pack の seed 自動生成の高度な戦略（学習的/ヒューリスティクス）
- プロジェクト固有ルール（独自 rule_id の追加、独自検査の導入）
  - ただし「未知 rule_id を許容する」「未割当は info」等の互換性原則は Stable Core に従う

---

## 実行モデル（Run Model）

### Run の定義

- Run は、同一の Spec Root と同一の Effective Config（プロファイル含む）を入力として、index / pack / lint_report を生成・評価する 1 回の実行単位である。
- Run は次のフェーズを持つ（MUST）:
  1. **scan**: Spec Root を走査し対象 spec を収集
  2. **index**: SPEC-SYS-004 の index（spec_index.jsonl）を生成し、`index_digest` を算出
  3. **lint**: index（および必要な本文情報）を入力として lint（構造lint + trace-lint + doc-sync（任意））を実行し、lint_report を生成
  4. **pack**（任意）: seed または lint 結果から pack を生成

> NOTE: pack / lint_report が `source_index` を必須とするため、Run から index フェーズを欠落させてはならない（MUST NOT）。

### scan（対象 spec の探索）既定規則（SHOULD）

- 既定では `spec_root` 配下の `**/*.md` を探索対象とする（SHOULD）。
- `output_root`（既定: `<project_root>/artifacts`）配下は探索対象から除外しなければならない（MUST）。
- `.git/**` や `node_modules/**` 等の一般的なビルド/依存ディレクトリは除外することが望ましい（SHOULD）。

> NOTE: 探索規則の差は index_digest / files_hash / lint 結果の差に直結するため、探索規則は Effective Config に含め、`config_hash` の対象とする（MUST）。

### scan の上書き（MAY）

- 実装は以下の config をサポートしてよい（MAY）。
  - `scan.include_globs`
  - `scan.exclude_globs`
- サポートする場合、これらは Effective Config に含め、`config_hash` の対象としなければならない（MUST）。

### index_digest の一貫性（MUST）

- `index_digest` は SPEC-SYS-004 が定義する算出規則に従う（MUST）。
- index をファイルに永続化しない実装であっても、**SPEC-SYS-004 と等価な正規化出力**に対して digest を算出できなければならない（MUST）。

---

## 設定（Config）とプロファイル（Profile）

### 設定の解決順（MUST）

ツールは設定を以下の優先順位で解決する（上が強い）。

1. CLI 引数（例：`--config` / `--profile` / `--spec-root` / `--out`）
2. 設定ファイル（config）
3. 既定値

環境変数をサポートしてもよい（MAY）。サポートする場合も上記優先順位を乱さない（MUST）。

### Effective Config（有効設定）の確定（MUST）

- ツールは上記の解決順に従い、最終的に **Effective Config** を確定する（MUST）。
- `gate.threshold` が省略されている場合、選択された `profile` の既定 threshold を適用して Effective Config に確定させる（MUST）。
- pack/lint/index の出力に影響する設定値（例：除外パターン、unknown_sections policy、pack limits、follow 設定等）は、Effective Config に含めなければならない（MUST）。

### config_hash の算出対象（MUST）

- SPEC-SYS-004 の `config_hash` は、**Effective Config（既定値適用後）**を正規化した表現を対象としなければならない（MUST）。
- 正規化は少なくとも以下を満たす（MUST）。
  - キー順は辞書順
  - 文字コードは UTF-8、改行は LF
  - パスは `spec_root` 基準の相対表現（区切りは `/` を推奨）
- `config_hash` は少なくとも次の要素を含む（MUST）。
  - `spec_root` / `output_root`
  - `profile` / `gate.threshold`（profile 既定適用後）
  - `scan.include_globs` / `scan.exclude_globs`（サポートする場合）
  - 構造lintに影響する設定（例：unknown_sections policy）
  - `pack.limits` / `pack.follow.*`（サポートする場合）
  - `doc_sync.mode`（サポートする場合）

### 既定の設定ファイル位置（SHOULD）

中小規模での運用安定のため、既定の config パスを固定する（SHOULD）。

- 例: `<project_root>/.iori-spec/config.yaml`

### config の最小スキーマ（MUST）

config は少なくとも次を表現できる（MUST）。

- 設定ファイルは `<project_root>/.iori-spec/config.yaml` を既定とし、**暗黙に他パスを探索しない**（MUST NOT）。
- config は `version` を持つ（MUST）。後方互換のため、未知キーは無視できる実装を推奨（SHOULD）。

推奨の最小 shape（v1）：

```yaml
version: 1

paths:
  spec_root: "spec" # project_root 基準の相対パス（MUST）
  spec_glob: "spec/**/*.md" # 探索対象（MAY）。未指定時は "**/*.md" を既定としてよい
  artifacts_dir: "artifacts" # output_root（MUST）
  ignore_paths: # spec_root 基準の ignore（MAY）
    - "README.md"

runtime:
  profile: "balanced" # strict|balanced|exploratory（MUST）

gate:
  threshold: "error" # error|warn|info（MUST）。未指定時は profile 既定でもよい

doc_sync:
  mode: "off" # off|check|write（MAY）。CI では check を推奨

vocab:
  kinds: # kind の語彙（MAY）。ツール既定 + 追加語彙 = Effective Kinds
    - id: "requirements"
      label: "Requirements"
      dir: "requirements"
  scopes: # scope_root の語彙（SHOULD）。root は enum 検査し、".subpath" は自由
    - id: "spec_system"
      label: "Spec System"
  variants: # kind 内一次分類（MAY）
    requirements: ["functional", "nonfunctional"]
```

#### project taxonomy（MAY）

front matter の検査・テンプレ生成の決定性のため、config は project taxonomy を含めてよい（MAY）。

- `taxonomy.kinds`（MAY）: Effective Kinds の追加語彙（SPEC-SYS-006）
- `taxonomy.scopes`（SHOULD）: `scope_root` の推奨語彙（SPEC-SYS-006）
- `taxonomy.variants`（MAY）: kind 内一次分類（`variant`）の enum（SPEC-SYS-006 / ADR-SPEC-001）
  - `taxonomy.variants[kind]` が存在する kind では、front matter の `variant` を必須（MUST）として lint できる。

#### config 例（参考）

```yaml
spec_root: .
output_root: artifacts
profile: balanced
gate:
  threshold: error
doc_sync:
  mode: check
taxonomy:
  scopes: ["spec_system", "cli", "builder"]
  variants:
    requirements: ["functional", "nonfunctional"]
scan:
  include_globs: ["**/*.md"]
  exclude_globs: ["artifacts/**", ".git/**", "node_modules/**"]
pack:
  limits:
    max_specs: 50
    max_chars: 200000
```

### プロファイル（重大度プロファイル）の定義

- プロファイルは「ルールID（FM### / S### / T### 等）→ severity（error|warn|info）」の割当を持つ運用設定である（MUST）。
- 内蔵プロファイル名は `strict` / `balanced` / `exploratory` を提供する（MUST）。
- 内蔵プロファイルの内容（割当）は、外部SSOTとして配布される **`.iori-spec/profiles/{strict,balanced,exploratory}.yaml`** を正とし、それらと一致しなければならない（MUST）。
- SPEC-SYS-003 に記載される例は参考（Informative）であり、衝突時の正は profiles 側である。
- 内蔵プロファイルの割当を変更することは、CI の挙動を変え得るため **互換性破壊（MAJOR）**として扱う（MUST）。
- 内蔵プロファイルの `gate.threshold` 既定（strict=warn 等）を変更することも同様に **互換性破壊（MAJOR）**として扱う（MUST）。

#### severity の表記

- 本ツールが出力する lint_report の `findings[].severity` は `error|warn|info`（小文字）を用いる（MUST）。

### 未割当ルールIDの扱い（MUST）

- カスタムプロファイル等で、既知のルールIDに割当が存在しない場合、既定 severity は `info` とする（MUST）。

  - 目的: ルール追加時に突然 FAIL が増えることを避け、運用者が明示的にゲートを強化できるようにする。

### 規範ファイル（Normative Artifacts）の解決（SHOULD）

- 内蔵プロファイル（`strict|balanced|exploratory`）は、既定で `.iori-spec/profiles/*.yaml` から解決することを推奨する（SHOULD）。
- doc-sync（Snapshot 同期）で参照するソースは、Snapshot markers が示すパスを **`spec_root` 基準で解決**する（MUST）。
- セキュリティと決定性のため、doc-sync は既定で `spec_root` 外への参照（`..` 等）を拒否すべきである（SHOULD）。

---

## lint の仕様（構造lint + trace-lint + Gate + exit code）

### lint の範囲（MUST）

`lint` は少なくとも次を含む（MUST）。

1. **front matter lint**（SPEC-SYS-006 に基づく）
   - YAML front matter の parse/必須キー/enum 検査等（rule_id: `FM###`）

2. **構造lint**（SPEC-SYS-002 に基づく）
   - 必須セクション欠落、見出し重複、未知セクションの扱い（allow/warn/error）、順序逸脱など

3. **trace-lint**（SPEC-SYS-003 に基づく）
   - ルールID（T001..）に対応する違反検出（例：重複、自己参照、循環、最小カバレッジ 等）

4. **doc-sync**（生成スナップショットの同期検証。外部SSOTと仕様書内 Snapshot の一致）
   - Snapshot markers（BEGIN/END）に基づき、外部ソースを読み、再生成した内容と一致することを検証する
   - 不一致は findings として報告し、Gate の対象となり得る

### front matter lint の rule_id（MUST）

- front matter lint の findings は `rule_id` に `FM###` 形式を用いなければならない（MUST）。
- `FM###` の詳細定義（一覧）は SPEC-SYS-006 を正とする（MUST）。

### 構造lintの rule_id（MUST）

- 構造lintの findings は `rule_id` に `S###` 形式を用いなければならない（MUST）。

  - 例: `S001`（必須セクション欠落）、`S002`（未知セクションの扱い違反）、`S003`（見出し重複）、`S004`（順序逸脱）、`S010`（Snapshot 不一致 / doc-sync）

- `S###` の詳細定義（一覧）は、将来 SPEC-SYS-002 または別途カタログ仕様へ委譲してよい（MAY）。

  - ただし `S###` 形式と「構造lintも findings として出し、Gate の対象になり得る」ことは本仕様の Stable Core とする（MUST）。

### lint_report の生成（MUST）

- lint の結果は SPEC-SYS-004 の lint_report（data）として出力する（MUST）。
- `profile` は **ラベル**であり、report 内にゲート条件（threshold 等）を埋め込んではならない（MUST NOT）。
- `rule_id` は未知でも許容し、Consumer が表示可能であること（MUST）。

> NOTE: デバッグ目的で threshold 等を残したい場合は、規範ではない情報として `extensions` 配下に格納してよい（MAY）。
> ただし Consumer がそれに依存してゲート判定することを前提にしてはならない（MUST NOT）。

### run_status（MUST）

- `run_status` は SPEC-SYS-004 の定義に従い算出する（MUST）。

  - `complete=false` の場合は `fatal`（MUST）
  - `complete=true` の場合は findings の集計により `success|warning|error` を決定（MUST）

### Quality Gate（PASS/FAIL）の定義（MUST）

- ツールは lint 実行結果に対して Quality Gate（PASS/FAIL）を判定する（MUST）。
- `gate.threshold` は `error|warn|info` のいずれか（MUST）。

判定規則（MUST）:

- findings のうち、severity が threshold 以上のものが 1 件でもあれば **FAIL**
- そうでなければ **PASS**

プロファイル既定（SHOULD）:

- `strict`: threshold = `warn`
- `balanced`: threshold = `error`
- `exploratory`: threshold = `error`

### ゲート判定と findings の整合（MUST）

- Gate は **lint_report に出力される findings（同一 Run の同一 profile 適用後）**を入力として判定しなければならない（MUST）。

  - 目的: 「レポートとゲートの不一致」による運用事故を防ぐ（テスト容易性・運用）。

### `run_status=fatal` 時の Gate 扱い（MUST）

- `run_status=fatal` の場合、Gate は評価しない（N/A）ものとし、exit code=2 を返さなければならない（MUST）。

  - 目的: “品質のFAIL” と “実行失敗” を明確に分離する（運用）。

### exit code（MUST）

- exit code は **運用の安定性**のため最小の 3 値に固定する（MUST）。

| exit code | 条件                                      | 意味                        |
| --------: | ----------------------------------------- | --------------------------- |
|         0 | `run_status != fatal` かつ Gate = PASS    | 正常終了（品質ゲート通過）  |
|         1 | `run_status != fatal` かつ Gate = FAIL    | 正常終了（品質ゲート失敗）  |
|         2 | `run_status = fatal` または実行が信頼不可 | 実行失敗（入力不正/例外等） |

#### exit code=2（実行失敗）の代表例（SHOULD）

実装は以下を exit code=2 の代表例として扱うことが望ましい（SHOULD）。

- config の読み込み/パース失敗
- Spec Root の走査失敗（権限/IO）
- index 生成不能（必須情報欠落、内部例外）
- 予期しない例外により lint_report を `complete=true` で生成できない

---

## context pack（局所化）の仕様（運用）

### 抽出根拠（MUST）

- pack は SPEC-SYS-002 の `include_in: pack` を抽出根拠とする（MUST）。
- pack の manifest / resolved_ids / hints の shape と決定規則は SPEC-SYS-004 を正とする（MUST）。

### resolved_ids と READ_NEXT（MUST）

- `resolved_ids` は **seed_ids + trace traversal（指定 edge_type のみ）**で決定する（MUST）。
- `READ_NEXT` は既定では `resolved_ids` の決定に用いない（SHOULD）。

  - `READ_NEXT` 由来は `selection.hints.read_next_ids` 等の **hints**として記録してよい（MAY）。
  - `resolved_ids` に `READ_NEXT` 由来を混入する挙動は、明示設定がある場合に限る（SHOULD）。

### pack の入力モード（SHOULD）

中小規模で有用な最小セットとして、以下を推奨する（SHOULD）。

- **seed 指定**: ID またはファイルパスを seed として pack を生成
- **lint 連携**: Gate FAIL を引き起こした findings を入力として、その周辺（対象 spec + 参照先）を seed にして pack を生成

> NOTE: lint 連携における seed の作り方（例：`finding.spec_id` と `finding.related_ids` の和集合を seed_ids とする等）は Edge として改善余地が大きい。
> ただし最終的な selection は pack manifest に必ず記録され、再現可能でなければならない（MUST）。

---

## テンプレート生成（Skeleton / Template）（拡張・運用）

> NOTE: 本節は Edge（拡張点）として定義する。CLI 名・出力形式は例示であり、安定軸は「入力（kind/variant）→ セクション集合の決定規則」である。

### 目的（Why）

- LLM / 人間が新規 spec（例: `REQ-*.md`）を作成する際に、`kind + variant` に応じた **最小の骨組み（front matter + H2 見出し）**を決定的に提供する。

### 入力（What）

- `kind`（MUST）
- `variant`（MAY / kind により MUST）

  - `taxonomy.variants[kind]` が定義されている場合、`variant` は必須（MUST）。
- セクション定義 SSOT:
  - `spec_sections_registry.yaml` / `spec_sections_guide.yaml`（SPEC-SYS-002）

### セクション集合の決定規則（How, MUST）

- 対象ファイルの **Effective Section Rules** は以下で決定する（MUST）。

  1. `applies_to_kinds` が `kind` に一致する（または `*` を含む）
  2. かつ `applies_to_variants` が未指定、または `variant` がその列挙に含まれる

- その後、Effective Section Rules を `priority` 昇順（同値は `section_id` 昇順）で並べ、H2 見出し（`heading`）を出力する（MUST）。

### 生成物（例）

- 生成するテンプレートは、少なくとも以下を含むこと（SHOULD）。
  - YAML front matter（SPEC-SYS-006 に準拠、必要なら `variant` を含む）
  - `##` 見出し列（SPEC-SYS-002 の ordering に準拠）
  - Guide 由来の短いプレースホルダ（purpose/guidelines の抜粋）を含めてもよい（MAY）

---

## index の仕様（運用）

### index は前提工程（MUST）

- pack / lint_report の `source_index` 要件を満たすため、ツールは Run の一部として index を生成できなければならない（MUST）。
- index のデータ契約（spec_index.jsonl の record 構造・順序・digest）は SPEC-SYS-004 を正とする（MUST）。

### `index_contract_version` の取り扱い（MUST）

- `source_index.index_contract_version` は、生成した index の `meta.contract_version` を用いなければならない（MUST）。

### persist（ファイル出力）の扱い（SHOULD）

- 中小規模の運用安定のため、既定では index をファイルとして出力する（SHOULD）。

  - ただし、ファイル出力を行わない実装であっても、`index_digest` を算出し pack/lint_report の `source_index` に埋め込めること（MUST）。

---

## 既定の出力配置（推奨）

- 既定の `output_root` は `<project_root>/artifacts`（SHOULD）。
- 既定の出力レイアウトは SPEC-SYS-004 の FS Layout v1（SHOULD）。

  - `artifacts/spec_index.jsonl`
  - `artifacts/packs/<pack_id>/manifest.json`（必須）
  - `artifacts/reports/lint_report.json`

---

## USAGE

### 想定読者（Who）

- ツール実装者（iori-spec CLI / ライブラリ）
- 仕様書群の運用者（リポジトリオーナー、レビュア、CI 管理者）
- 仕様を用いて実装・レビューする開発者（必要に応じて）

### 参照トリガー（When）

- ツールの実行モデル（Run フェーズ）、Gate/exit code の挙動を変更するとき
- 設定キーや設定解決順、既定値を追加・変更するとき
- プロファイル（severity 割当／threshold 既定）を追加・変更するとき
- pack の抽出根拠（seed／lint連携／follow 設定）を追加・変更するとき
- CI で「どの条件で止めるか」を見直すとき（プロファイル移行、厳格化、例外運用）

### 使い方（How）

- ローカル運用（推奨）
  - 既定は `balanced`（threshold=error）で回し、ERROR のみで止める運用が扱いやすい。
  - 初期移行期は `exploratory` を使い、WARN/INFO を蓄積して整備計画に落とす。
  - 成熟後に `strict`（threshold=warn）へ引き上げる。
- CI 運用（推奨）
  - CI では exit code により機械判定する（`0`: PASS / `1`: FAIL（品質ゲート違反） / `2`: 実行失敗）。
  - 仕様書内に Snapshot（生成スナップショット）を運用する場合、CI では `doc_sync.mode=check` を有効化し、外部SSOTとの不一致を FAIL として止めることを推奨する。
  - CI の既定プロファイルは `balanced`（threshold=error）を推奨する。
  - CI とローカルの差分を減らすため、CI でも config を読み、Effective Config を固定する運用を推奨する（SHOULD）。
- 設定運用（推奨）
  - プロファイルと `gate.threshold` は、原則として config に固定し、CI/ローカルの差分を減らす。
  - カスタムプロファイルを導入する場合、未割当ルールが `info` になる点を前提に、段階的に強化する。

### セット読み（With）

- SPEC-SYS-004 — 成果物（index / pack / lint_report）の形・決定性・互換性
- SPEC-SYS-006 — YAML front matter（`variant`/taxonomy を含む）
- SPEC-SYS-003 — `trace` の意味論・ルールID（T001..）・プロファイル例
- SPEC-SYS-002 — セクション定義（include_in / ordering / unknown_sections 等）

## 運用上の目安（LLM / SDD 観点）

### 更新トリガー（Trigger → Action）

- 成果物契約（SPEC-SYS-004）が変更された場合（contract_version 更新、必須フィールド追加、digest/正規化変更など）
  - Action: 本仕様の該当箇所（Run/Effective Config/出力配置/pack/lint_report 連携）を更新し、準拠テスト（Conformance Fixtures）のスナップショットも更新する。
- trace ルール（SPEC-SYS-003）が変更された場合（ルール追加、意味論変更、プロファイル例更新など）
  - Action: lint（trace-lint）の参照・前提（rule_id / severity / profile 既定）を更新し、CI ゲート（threshold）への影響を明記する。
- セクション定義（SPEC-SYS-002）が変更された場合（include_in の意味変更、ordering/unknown_sections の変更など）
  - Action: 構造lint（S###）の対象・判定・既定挙動（allow/warn/error）を更新し、Gate への接続可否を点検する。
- 規範ファイル（ルールカタログ／profiles／schemas）を更新した場合
  - Action: doc-sync（check/write）の運用と、Snapshot の配置（SPEC-SYS-002）を点検し、CI で差分が残らないことを確認する。
- 設定・既定値を変更した場合（新しい config key の追加、解決順の変更、既定値の変更）
  - Action: Effective Config の定義と `config_hash` の算出対象を更新し、「出力に影響する設定」が漏れていないか確認する。
- Gate/exit code の意味論を変更した場合
  - Action: 互換性影響（breaking/deprecation）を評価し、CI 運用への影響と移行方針を明記する（必要なら段階導入）。

### LLM 連携（貼り方）

- 最小セット:
  - 本 spec の LLM_BRIEF + 変更対象セクション（diff）+ 期待成果物（例: 仕様追記案、テスト/フィクスチャ更新案）
- 拡張セット（必要時）:
  - 参照 SSOT（SPEC-SYS-002/003/004）の該当箇所 + 互換性制約（決定性、contract_version、profile 互換性）

### ツール運用（Gate の運用方針）

- PR 時:
  - 仕様変更が Run/設定/ゲート/出力に影響する場合、準拠テスト（Conformance Fixtures）の更新を同一 PR で行う。
- リリース前:
  - `index_digest` / `lint_report` / `pack manifest` が「同一入力 → 同一出力」になること（決定性）を点検し、意図しない差分がないことを確認する。
- 準拠テスト（Conformance Fixtures）（SHOULD）:
  - 実装は小さな `spec_root` フィクスチャに対して、以下がスナップショット一致することを確認する準拠テストを用意することが望ましい（SHOULD）。
    - `index_digest`（および spec_index.jsonl の正規化出力）
    - `lint_report`（findings と run_status）
    - `pack` の `manifest`（selection と resolved_ids）

### 更新時の作法（どう更新するか）

- CLI 名やサブコマンド体系は非安定（例示扱い）とし、安定軸は用途概念（index / lint / pack）と設定キーに置く。
- 互換性影響がある変更（プロファイル既定や threshold 既定、Gate/exit code の意味論、決定性に関わる変更）は、CI 運用への影響と移行方針を必ず併記する。
- 参照 SSOT（SPEC-SYS-002/003/004）と本仕様の間に齟齬が出る変更は、該当箇所を点検し、必要なら同一 PR で追随させる。

## READ_NEXT

- SPEC-SYS-004（安定契約: index / pack / lint_report のデータ契約・決定性・互換性）— 本仕様の成果物要件の根拠
- SPEC-SYS-006（front matter: kind/scope/variant/taxonomy）— front matter lint と分類軸の根拠
- SPEC-SYS-003（トレーサビリティ: `trace` の意味論、ルールID、プロファイル例）— trace-lint とプロファイル運用の根拠
- SPEC-SYS-002（セクション定義: include_in / ordering / unknown_sections）— 構造lint と pack 抽出根拠の前提
- SPEC-SYS-001（運用ガイド: 新規作成/修正/参照フロー）— 仕様書運用全体の中でのツール位置づけ
