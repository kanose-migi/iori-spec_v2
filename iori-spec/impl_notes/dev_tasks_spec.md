---
kind: reference
scope: dev_tasks
spec_title: "Dev Tasks (TASK-xxx) Spec"
status: draft  # draft / review / stable
---

# Dev Tasks (TASK-xxx) Spec

## 1. このドキュメントの役割

* `docs/dev_tasks/` 以下に置く **開発タスクカード（TASK-xxx）** のルールを定義する。
* 各 IF（IF-xxx）を「弱めの LLM にも安全に投げられる粒度のタスク」に分割し、
  人間／LLM が共通の前提で実装作業を進められるようにする。
* ここで定義する TASK-xxx は、プロダクトとしての挙動（REQ/IF/DATA/TEST）の SSoT ではなく、
  **「実装フローを仕様化した補助レイヤー」**として扱う。

---

## 2. dev_tasks ディレクトリの位置づけ

### 2.1 パスと kind

* ルート: `docs/dev_tasks/`
* 各ファイルの front matter 例:

```yaml
---
kind: dev_tasks
scope: IF-100               # 対象となる IF-xxx
spec_title: "Dev Tasks for IF-100 (index)"
status: draft | review | stable
---
```

### 2.2 1 IF = 1 dev_tasks ファイル

* 原則として、**1 つの IF-xxx につき 1 つの dev_tasks ファイル**を用意する。

  * 例:

    * `docs/interfaces/cli/IF-001_index_cli_spec.md`
    * `docs/dev_tasks/IF-001_index_tasks.md`

* このファイル内に、その IF を実装するための TASK-xxx を複数定義する。

---

## 3. TASK ID 体系

### 3.1 形式

* 開発タスク ID は次の形式とする:

`TASK-IF-<nnn>-<mm>`

* 例:

  * `TASK-IF-001-01` … IF-001 を実装するための 1 つ目のタスク
  * `TASK-IF-001-02` … 同じく 2 つ目のタスク

* `<nnn>` は IF 番号（`IF-001` なら `001`）、`<mm>` はその IF 内での連番（01, 02, ...）とする。

### 3.2 ID の扱い

* TASK-xxx は **ID として index 対象**とする。

* ただし、

  * `requirements/traceability_map.md` の REQ↔IF/DATA/TEST のトレーサビリティには **含めない**。
  * `trace` コマンドの「未トレース ID チェック」の対象にも **含めない**。

* つまり、TASK-xxx は

  * `index` では通常の ID と同様に抽出・列挙されるが、
  * `trace` の整合性チェックの「正本」には関与しない。

---

## 4. dev_tasks ファイルの構造

### 4.1 全体構成（1 IF = 1 ファイル）

ファイル名の例:

* `docs/dev_tasks/IF-001_index_tasks.md`

中身のテンプレート例:

```markdown
---
kind: dev_tasks
scope: IF-001
spec_title: "Dev Tasks for IF-001 (index)"
status: draft
---

# Dev Tasks for IF-001 (index)

## 1. Overview

- 対象 IF: IF-001 (`interfaces/cli/IF-001_index_cli_spec.md`)
- カバーする REQ:
  - REQ-101, REQ-102
- 目的:
  - IF-001 の実装を、低コスト LLM にも任せやすい粒度のタスクに分割する。

## 2. Task List

| TASK ID         | 概要                              |
|-----------------|-----------------------------------|
| TASK-IF-001-01  | CLI スケルトンの作成             |
| TASK-IF-001-02  | spec_loader 呼び出しの組み込み    |
| TASK-IF-001-03  | index.json 出力ロジックの実装     |

## 3. TASK-IF-001-01: CLI スケルトンの作成

- **目的**:
  - `iori-spec index <root> [--format json]` の CLI エントリポイントを実装する。
- **関連仕様**:
  - IF-001: CLI 仕様 (`interfaces/cli/IF-001_index_cli_spec.md`)
- **入力**:
  - コマンドライン引数
- **出力**:
  - `index` コマンドのエントリ関数（まだビジネスロジックなし）
- **制約**:
  - 標準ライブラリのみ使用する。
  - まだファイル走査や ID 抽出は実装しない。
- **推奨手順（LLM に渡す想定の粒度）**:
  1. 既存の CLI エントリのスケルトンを確認する。
  2. `index` サブコマンドを追加し、`root` 引数を必須にする。
  3. `--format` オプション（`json` のみサポート）を追加する。
  4. `main()` から `run_index_cli()` 的な関数を呼び出す構造にする。

## 4. TASK-IF-001-02: spec_loader 呼び出しの組み込み

... 以下同様 ...
```

### 4.2 セクションの役割

* `Overview`:

  * 対象 IF, 関連 REQ, 目的を簡潔に示す。
* `Task List`:

  * TASK-xxx の一覧と一言概要。
    LLM に見せる前に人間が全体像を把握しやすくするためのテーブル。
* 各 `TASK-IF-xxx-nn` セクション:

  * LLM にそのままプロンプトとして渡せるレベルまで具体化してよい。
  * ただし、**仕様の SSOT ではない**ことを意識し、IF / DATA / TEST 側からの逆参照に依存しすぎないようにする。

---

## 5. iori-spec コマンドとの関係

### 5.1 index

* `iori-spec index` は、TASK-xxx を含むすべての ID を通常どおり抽出・集計する。
* 出力 JSON の `ids` セクションには、`"prefix": "TASK"` のエントリが追加されうる。

### 5.2 trace

* `trace` コマンドは、当面は **REQ/IF/DATA/TEST のみを対象**とする。
* TASK-xxx は「トレーサビリティの網羅性チェックの対象外」であり、
  未トレースであってもエラー・警告にはならない。

### 5.3 impact / context（将来の拡張）

* 将来的には、`impact` や `context` のオプションとして

  * `--include TASK`
  * `--seed TASK-IF-001-01`
    等をサポートし、
    ある TASK から関連する IF/REQ/DATA/TEST や doc へ辿る用途を想定している。

---

## 6. 運用上の考え方

* dev_tasks は、**「弱めの LLM にも安心して任せられるタスク設計」**を仕様化したレイヤーと位置づける。
* TASK-xxx は仕様の SSoT ではないが、

  * タスク設計そのものをバージョン管理・レビュー可能にし、
  * 人間と LLM の間で共通の「作業カード」として扱えるようにするためのもの。
* ある TASK-xxx が事実上仕様の一部（たとえば IF の挙動に関する新たな制約）になってきた場合は、

  * requirements / interfaces / data_contracts / tests のいずれかへ「昇格」させることを検討する。

---



