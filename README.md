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

> 実装状況は開発フェーズに応じて変わります。最初はサブセットから着手し、徐々に拡張していく想定です。コマンド仕様の正本は `iori-spec/impl_notes/spec_command.md` を参照してください。

### Traceability & Index

- **`iori-spec index`** – 仕様インデックス生成（MUST）  
  - front matter の kind/scope/trace/dp を集約し、`artifacts/spec_index.json` を生成。
  - 他コマンドは SpecIndex を SSOT として参照する。
- **`iori-spec trace lint`** – トレーサビリティチェック（MUST）  
  - REQ / IF / DATA / TEST の `trace.*` を検証し、未トレースや未知 ID 参照を検出する。
- **`iori-spec trace report`** – Traceability Map 生成（SHOULD）  
  - `trace lint` 前提の情報から `artifacts/traceability_map.md` を生成するビュー（手書き禁止）。
- **`iori-spec graph export / graph neighbors`** – グラフの DOT/近傍出力（NICE TO HAVE）。

### Search / Context / Impact

- **`iori-spec search`** – ID / spec_title / scope から候補を探索（MUST）。
- **`iori-spec show`** – 特定 ID の主要セクションを簡易表示（SHOULD、`context --radius 0` 相当）。
- **`iori-spec impact`** – 指定 ID から trace グラフをたどり影響ノードを列挙（MUST）。
- **`iori-spec context`** – 影響ノードの本文抜粋を束ねて LLM 向けコンテキストを生成（MUST）。

### Lint & Scaffold

- **`iori-spec lint`** – front matter / sections / ids の構造チェック（MUST）。
- **`iori-spec new` / `iori-spec scaffold`** – REQ/IF/DATA/TEST/TASK のスケルトン生成（SHOULD）。

### Tasks（運用補助）

- **`iori-spec tasks list` / `report tasks`** – TASK ノードを一覧・レポートする補助コマンド（NICE TO HAVE）。
---

## Installation (planned)

> 実装・公開方法は今後の設計により変わる可能性があります。以下はイメージです。

### Python パッケージとして利用する場合

```bash
# 例: PyPI に公開した場合
pip install iori-spec
# or
pipx install iori-spec
```

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

# 仕様インデックスの生成（SpecIndex を SSOT にする）
iori-spec index

# トレーサビリティチェックと Traceability Map 生成
iori-spec trace lint
iori-spec trace report --out artifacts/traceability_map.md

# 探索とコンテキスト生成
iori-spec search \"traceability\" --kinds requirements,interfaces
iori-spec show REQ-800
iori-spec impact REQ-800 --max-depth 2
iori-spec context REQ-800 --radius 1 > /tmp/context-req-800.md

# スケルトン生成（必要に応じて）
iori-spec new req --id REQ-900 --spec_title \"New requirement skeleton\"
```

---

## Roadmap (draft)

- [ ] `index` / `trace lint` / `trace report` / `lint` のコア実装
- [ ] `search` / `show` / `impact` / `context` の LLM 向け出力強化
- [ ] `graph export / neighbors` などデバッグ用コマンド
- [ ] `new|scaffold` と `tasks list|report` の整備

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
