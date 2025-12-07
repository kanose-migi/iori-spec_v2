# iori-spec

> **Specification static analysis toolkit** — SSoT, traceability, and vocabulary consistency for your specs.  
> 仕様書を「コード並み」に扱うための静的解析ツールセット。

---

## What is iori-spec?

**iori-spec** は、ソフトウェア仕様書や設計ドキュメントを対象にした **静的解析ツール群** です。

- SSoT（Single Source of Truth）
- REQ / IF / DATA / TEST の **トレーサビリティ**
- 用語・ラベル・フォーマットの一貫性

といった観点を、**機械的にチェック・整形**することを目的としています。

CLI から直接使えることはもちろん、  
CI や LLM ツール（例: codex cli）からも呼び出して使えるように設計されています。

 The spec set for this project lives under `iori-spec/`. 新しく仕様を読むときは `iori-spec/README_SPEC.md` から入り、CLI は標準配置なら `--config` 省略可（カスタム配置のみ `--config iori-spec/reference/iori_spec_config.yaml` などを指定）。

---

## Goals / Philosophy

- **仕様書を「設計仕様」として扱う**
  - コードと同様に、Lint・テスト・トレーサビリティを維持可能にする。
- **SSoT を守る**
  - ID とラベル、要件の “正本” を1ヶ所に集約し、それ以外は機械的に同期する。
- **トレーサビリティを可視化する**
  - `REQ ↔ IF ↔ DATA ↔ TEST` の対応関係をグラフとして扱い、穴や矛盾を検出する。
- **LLM/CIフレンドリー**
  - JSON 出力・IDベースのフィルタ・コンテキストパッカーなど、  
    ツール連携を前提にしたインターフェースを提供する。

---

## Features (planned)

> 実装状況は開発フェーズに応じて変わります。最初はサブセットから着手し、徐々に拡張していく想定です。

### Traceability & Index

- **`iori-spec trace`** – トレーサビリティチェック  
  - REQ / IF / DATA / TEST などの ID を走査し、
    - 未実装要件（IFが紐付いていない REQ）
    - 未テスト要件（TESTが紐付いていない REQ）
    - 未使用 DATA（どの IF からも参照されない DATA）
    を検出します。
  - Traceability Map と実際の spec のズレも検知可能にする予定です。

- **`iori-spec index`** – 仕様インデックス生成  
  - 全 Markdown から `kind` / `scope` / ID / tags を集約し、
    機械可読な `spec_index.json` を生成します。
  - 「この ID はどのファイル・どのセクションで定義されているか？」を素早く引けるようにします。

---

### SSoT & Label Management

- **`iori-spec labels`** – ID ↔ ラベル SSoT 同期  
  - 定義元（front matter や見出し）から `id` とラベル（例: `REQ-005: レイテンシ（p95）`）を抽出し、  
    それを SSoT として登録します。
  - 他ファイル内の `REQ-005: ...` / `[REQ-005: ...](` を自動書き換えし、  
    ラベル表記のズレを機械的に解消します。
  - `--check` モードでは、「ラベルがSSoTと一致していない箇所」をLintとして報告します。

- **`iori-spec vocab`** – 用語／正準語彙Lint  
  - `naming_conventions.md` や `glossary_jp_en.md` から
    - 正準語
    - 禁止別名・避けるべき表現
    を読み込み、仕様書全体をスキャンします。
  - 「ゴロ → 語呂合わせ」のように、正準語への置き換え候補や混在表記をレポートします。

---

### Context Tools for LLM

- **`iori-spec context`** – LLM向けコンテキストパッカー  
  - 指定したファイルや ID に対応するセクションを抽出し、
    - `=== FILE: path ===`
    - 行番号付き
    の形式で1つのテキストにまとめます。
  - LLM に「この周辺だけレビューしてほしい」ときに、  
    必要なコンテキストだけをコンパクトに渡す用途を想定しています。

- **`iori-spec impact`** – 影響範囲コンテキスト抽出  
  - `spec_index` や依存情報をもとに、
    - 例: `iori-spec impact REQ-005 --radius 1`
  - 該当 ID と、直接依存している IF / DATA / TEST などを辿り、  
    関連セクションをまとめて出力します。
  - 「REQ-005 を変えるときに一緒に見ておくべき仕様」を自動で束ねます。

---

### Format & Structure

- **`iori-spec format`** – 仕様テンプレ／フォーマットLint  
  - `kind: requirements` なら必須セクション（目的・ID・Acceptanceなど）が揃っているか、  
    `kind: data_contracts` ならスキーマ定義が存在するか、といったルールをチェックします。
  - `iori_spec_guide.md` で定義されたフォーマット／テンプレートから外れている spec を検知します。

- **`iori-spec xref`** – クロスリファレンス検索  
  - `iori-spec xref REQ-005` のように呼び出すと、
    - ID が定義されている場所
    - README / Traceability Map / 他 spec から参照されている箇所
    を一覧表示します。
  - ID の影響範囲を人の目で確認するときのナビゲーションツールとして使えます。

---

### External Lint Integration

- **`iori-spec textlint`** – textlint 連携ラッパー  
  - Node ベースの [textlint](https://textlint.github.io/) をラップし、
    - `iori-spec textlint docs/requirements/functional.md`
    のように Python ベースの CLI から一貫したインターフェースで呼び出せるようにします。
  - JSON 出力で、日本語文章のスタイル・表記ゆれ・誤字情報を  
    他の Lint 結果と統合しやすくします。

---

### Cleanup & Maintenance (Future)

- **`iori-spec orphan`** – 孤立spec／未参照ID検出  
  - README_SPEC や steering docs などの「エントリポイント」から辿れない spec ファイルを検出します。
  - 定義されているがどこからも参照されていない REQ / IF / DATA / TEST を列挙し、  
    削除・統合候補として報告します。

---

## Installation (planned)

> 実装・公開方法は今後の設計により変わる可能性があります。以下はイメージです。

### Python パッケージとして利用する場合

```bash
# 例: PyPI に公開した場合
pip install iori-spec
# or
pipx install iori-spec
````

### textlint 連携（オプション）

```bash
# Node / npm が必要
npm install --save-dev textlint
# 必要な textlint ルールもここで追加
```

---

## Example Usage (concept)

```bash
# セットアップ（ローカル開発用）
python -m pip install -e .

# REQ/IF/DATA/TEST のトレーサビリティチェック（標準配置なら --config 省略可）
iori-spec trace

# 仕様インデックスの生成
iori-spec index

# ラベル（IDのタイトル）をSSoTに同期
iori-spec labels --sync iori-spec/

# 用語Lint（禁止別名・正準語彙チェック）
iori-spec vocab iori-spec/

# LLM向けに、あるIDまわりのコンテキストを束ねる
iori-spec impact REQ-800 --radius 1 > /tmp/context-req-800.txt

# textlint を経由した日本語Lint
iori-spec textlint iori-spec/requirements/REQ-800_tooling_cli.md --format json
```

---

## Roadmap (draft)

- [ ] `trace` / `index` / `labels` のコア実装
- [ ] `vocab`（用語Lint）と `format`（テンプレLint）の基本ルール実装
- [ ] `context` / `impact` の LLM 向けコンテキスト出力
- [ ] `textlint` ラッパーの実装と統合レポート形式の検討
- [ ] `orphan` などメンテナンス系コマンドの追加

## TODO

- [ ] `spec_title` フィールドの最終方針を決定する  
      - 現状: ID（REQ/IF/DATA/TEST）の認知負荷を下げるための補助ラベルとして、
        各 spec の front matter に `spec_title`（人間向けタイトル）を定義し、
        index / impact などの出力で利用する暫定仕様。
      - ただし、`kind` + `scope`（= パス構造）からタイトルを構成できる可能性もあり、
        `spec_title` フィールド自体が冗長／不要となる設計もあり得る。
      - 見直しタイミング: 全 spec ファイルとその役割が確定し、
        `kind + scope` 命名規則が固まった段階。
      - 選択肢:
        - a) `spec_title` を正式採用（人間向けラベルとして維持）
        - b) `kind + scope` からタイトルを自動生成し、`spec_title` を撤廃

---

## License

TBD

（ライセンス方針が決まり次第、ここに追記してください）
