---
kind: interfaces
scope: tooling.lint.trace
id: IF-930
spec_title: "IF-930: Trace Lint — REQ / IF / DATA / TEST Coverage"
status: draft

trace:
  req: []        # 例: REQ-8xy_traceability_coverage などを後で紐付け
  if:
    - IF-910     # Spec Index Builder（spec_index.json を前提として利用）
    - IF-920     # Lint Core（LintIssue 形式などの共通部分を利用）
  data:
    - DATA-900   # Spec Index Catalog（trace lint の唯一の入力 DATA）
  test: []
  task: []

dp:
  produces: []      # trace lint 結果を DATA-903 などとして data_contract 化する場合あり
  produced_by: []
  consumes:
    - DATA-900
  inputs: []

doc:
  read_next:
    - DATA-900
    - interfaces/IF-920_lint_core.md
    - reference/iori_spec_guide.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-930: Trace Lint — REQ / IF / DATA / TEST Coverage

## LLM_BRIEF

- role: この IF は、`spec_index.json`（DATA-900）を入力として、REQ / IF / DATA / TEST / TASK 間の **トレーサビリティ（つながり具合）の健全性を検査する trace lint のコアロジック**を定義します。
- llm_action: あなた（LLM）はこの IF と DATA-900 を読み、`iori-spec trace-lint` コマンドの中核となる **Python モジュール（trace lint コア）** を設計・実装してください。仕様ファイル群を直接読むのではなく、「SpecIndex（DATA-900）を読み込んでトレースグラフを検査し、LintIssue の一覧を返す」コードを書くことが目的です。

## USAGE

- ユースケース（CLI 層から見た想定）
  - `iori-spec trace-lint --index artifacts/spec_index.json --format json`
  - `iori-spec trace-lint --index artifacts/spec_index.json --rules TR-001,TR-003 --format json`
- ユースケース（Python モジュールとしての関数イメージ）
  - `run_trace_lint(index: SpecIndex, enabled_rules: list[str]) -> list[LintIssue]`
  - ここで `SpecIndex` は DATA-900 で定義した構造、`LintIssue` は IF-920 で用いた構造と同じ。

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- IF-920: Lint Core — frontmatter / sections / ids
- reference/iori_spec_guide.md（ID 命名規則・role の定義など）
- impl_notes/spec_command.md（lint / trace-lint コマンドの位置づけ）

---

## 1. このドキュメントの役割

- `spec_index.json` に基づき、`REQ-xxx ↔ IF-xxx / DATA-xxx / TEST-xxx / TASK-xxx` の **トレーサビリティが過不足なく張られているか**を lint するためのインターフェイスを定義する。
- 具体的には、次のような問題を検出する：
  - 実装やテストでカバーされていない REQ（孤立した REQ）
  - どの REQ にも紐づいていない IF / DATA / TEST / TASK（浮いた実装・テスト・タスク）
  - `trace.*` が参照している ID が index に存在しない（壊れたリンク）
- コマンドライン（`iori-spec trace-lint`）と実装（Python モジュール）・テスト・LLM から見た  
  「入力・ルール・出力（LintIssue）」の契約を明確にする。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- 対象：
  - DATA-900（`spec_index.json`）に含まれるすべての SpecNode。
- 検査対象の関係：
  - REQ ↔ IF / DATA / TEST / TASK
  - trace の参照整合性（存在しない ID を参照していないか）
  - 必要に応じて、トレースグラフの構造（孤立ノード・自己参照・循環など）

### 2.2 前提

- `spec_index.json` は IF-910（Spec Index Builder）により 最新の状態に生成されている。
- 各 SpecNode は少なくとも：
  - `id`, `kind`, `scope`, `status`, `spec_title`, `role`, `file`
  - `trace`（存在すれば）
  を持つ。
- `role` は ID プレフィックスに基づいて `req` / `if` / `data` / `test` / `task` 等に分類されている。
- LintIssue の構造は IF-920 のものを再利用する（可能であれば DATA-902 として共通 data_contract 化する）。

---

## 3. 運用上の目安（LLM / SDD 観点）

- 入力となる SpecIndex（DATA-900）は config の `paths.ignore_dirs` を適用して最新化しておく。
- coverage 不足（REQ に IF/DATA/TEST が無い等）は CI でブロックするエラー、孤立 TASK は警告扱いとする運用を想定。
- 出力は DATA-902 相当の Issue リストとして json/text で保存・通知し、trace report などの派生処理に渡せる形式を維持する。

---

## 4. Summary

- SpecIndex から G_trace を構築し、REQ ⇔ IF/DATA/TEST のリンク不足・存在しない ID 参照・孤立ノードを検出する lint を定義する。
- TASK は coverage 判定の対象外（警告のみ）とし、開発タスクの参考情報として扱う。

---

## 5. Inputs

- `artifacts/spec_index.json`（DATA-900）
- （任意）trace map 等の補助ファイル（将来拡張）

---

## 6. Outputs

- trace lint Issue の一覧（DATA-902 相当、text/json）
- Exit Code（重大 Issue の有無に応じて CLI 側で判定）

---

## 7. Lint ルールセット

本 IF では、トレーサビリティに関する lint ルールを `TR-xxx` という ID で定義する。  
CLI からは `--rules` / `--no-warn-uncovered-task` 等でルールを有効・無効化できる前提。

### 7.1 基本ルール（MUST）

1. **TR-001: REQ のカバレッジ不足**
   - 各 `role == "req"` のノードについて、少なくとも 1 つ以上の
     - IF (`trace.if`)
     - DATA (`trace.data`)
     - TEST (`trace.test`)
   のいずれかが紐づいていることを期待する。
   - いずれも存在しない場合、「未カバーの REQ」としてエラーまたは警告とする。

2. **TR-002: 孤立した IF / DATA / TEST**
   - `role == "if" | "data" | "test"` のノードについて、どの REQ からも参照されていない（`trace.req` が空、かつどの REQ の `trace.if / trace.data / trace.test` にも出てこない）場合、「孤立した実装 / データ定義 / テスト」として警告またはエラーとする。

3. **TR-003: trace 参照の存在チェック**
   - 全ての `nodes[].trace` に含まれる ID について、
     - `spec_index.nodes[].id` に存在しているかを確認する。
   - 存在しない ID を参照している場合、「不正な参照」としてエラーとする。

### 7.2 拡張ルール（SHOULD）

4. **TR-004: TASK の紐付きチェック**
   - `role == "task"` のノードについて、少なくとも 1 つ以上の
     - REQ (`trace.req`)
     - IF (`trace.if`)
   に紐づいていることを推奨する。
   - どの REQ / IF にも紐づいていない場合、「文脈を持たない TASK」として warning とする（エラーにはしない）。

5. **TR-005: 自己参照 / 循環（簡易チェック）**
   - 各ノードの `trace.*` が自ノード自身の ID を含んでいないかをチェックし、含んでいればエラーとする（自己参照の禁止）。
   - （オプション）小規模な循環（2〜3 ノードでの行き止まりのないループ）があれば warning とする。

6. **TR-006: 役割と trace の一貫性**
   - 例：
     - `role == "req"` のノードの `trace.req` に他の REQ を列挙している場合は不正（仕様次第で warning / error）。
     - `role == "test"` のノードが `trace.test` に他 TEST を列挙している場合も不正。
   - `iori_spec_guide` に定義された「どの role がどの role を trace してよいか」のポリシーに従う。

### 7.3 将来拡張ルール（NICE TO HAVE / メモ）

7. **TR-101: ステータスと coverage の整合**
   - 例：`status: stable` の REQ に対して、IF / TEST が存在しない場合はより強い警告とする。
8. **TR-102: 役割別 coverage 指標**
   - lint というより、`req_covered_ratio`・`if_orphan_ratio` など集計値を出すレポート機能として別コマンド化も検討。

---

## 8. 処理フロー（概略）

### 8.1 エントリポイント（コア関数）

1. `spec_index.json`（DATA-900）を読み込み、SpecIndex オブジェクトを構築する。
2. 有効なルール ID / カテゴリ（`enabled_rules`）を決定する。
3. SpecIndex からトレースグラフを構築する（必要に応じて）。

### 8.2 グラフ構築（簡易）

- SpecIndex から、以下のような内部表現を作る：

```python
nodes_by_id: dict[str, SpecNode]
role_by_id: dict[str, SpecRole]      # req / if / data / test / task / ...
trace_refs: dict[str, set[str]]      # from_id -> {to_id1, to_id2, ...}
reverse_refs: dict[str, set[str]]    # to_id -> {from_id1, from_id2, ...}
````

- `trace_refs` には全ての `trace.req / trace.if / trace.data / trace.test / trace.task` をマージして入れてよい
  （role 別に細かく保持したい場合は別マップを用意）。

### 8.3 ルール適用

1. **TR-003: 参照存在チェック**

   - `trace_refs` の値として現れるすべての ID について `nodes_by_id` に存在することを確認。
   - 見つからない場合、ID ごとに LintIssue を生成。

2. **TR-001: REQ coverage**

   - `role == "req"` のノードについて：

     - そのノードの `trace.if / trace.data / trace.test` を取り出す。
     - さらに `reverse_refs` を使って、他ノードから参照されているか（実装側から逆リンクされているか）も考慮してよい。
     - いずれも空であれば LintIssue（未カバーの REQ）を生成。

3. **TR-002: 孤立した IF / DATA / TEST**

   - `role in {"if", "data", "test"}` のノードについて：

     - そのノードがどの REQ の `trace.*` からも参照されていないか、
       また自身の `trace.req` も空かを調べる。
     - 真であれば LintIssue（孤立ノード）を生成。

4. **TR-004: TASK の紐付き**

   - `role == "task"` のノードについて：

     - `trace.req` / `trace.if` が空であり、かつどの REQ / IF からも参照されていなければ warning を生成。

5. **TR-005: 自己参照 / 簡易循環**

   - 各ノード ID `nid` について：

     - `trace_refs[nid]` に `nid` が含まれていれば自己参照としてエラー。
   - 簡易循環チェックは、深さ制限付き DFS / BFS により実装してもよい（MVP では自己参照のみで可）。

6. **TR-006: 役割と trace ターゲットの整合**

   - 各ノードについて：

     - `role == "req"` のノードが `trace.req` を持っていないか？
     - `role == "test"` のノードが `trace.test` で他 TEST を列挙していないか？
   - 不整合があれば LintIssue を生成。

---

## 9. Acceptance Criteria（受け入れ条件）

1. **必須ルールの実装**

   - 少なくとも `TR-001`, `TR-002`, `TR-003` が実装されていること。
2. **一意性・存在チェック**

   - `TR-003` により、`trace.*` に書かれた ID で index に存在しないものがあれば必ず検出されること。
3. **孤立ノードの検出**

   - `TR-001` / `TR-002` により、

     - 未カバー REQ
     - 孤立 IF / DATA / TEST
       が漏れなく検出されること。
4. **ルールフィルタリング**

   - `enabled_rules` で特定ルールのみを有効化した場合、そのルールに対応する Issue のみが返されること。
5. **フォーマット互換性**

   - IF-920 で定義された `LintIssue` と同じ構造で Issue が返されること。
   - CLI レイヤで `--format json` を指定したとき、stdout には JSON のみが出力されること。

---

## 10. Inputs / Outputs

### 10.1 Inputs（コア関数）

| 名前              | 型         | 必須  | 説明                                                       |
| --------------- | --------- | --- | -------------------------------------------------------- |
| `index`         | SpecIndex | Yes | DATA-900 で定義された構造を持つ SpecIndex オブジェクト。                   |
| `enabled_rules` | list[str] | No  | 有効化するルール ID / カテゴリ（例: `["TR-001", "TR-002"]` や `"all"`）。 |

※ CLI 実装では `index_path: Path` を引数とし、内部で JSON を読み込んで `SpecIndex` に変換する形になる。

### 10.2 Outputs（コア関数）

- 戻り値：`list[LintIssue]`

  - IF-920 で定義された構造を再利用する。
  - `rule_id` は `"TR-001"` など trace lint のルール ID を用いる。

LintIssue の再掲（参考）：

| フィールド      | 型             | 説明                                        |
| ---------- | ------------- | ----------------------------------------- |
| `rule_id`  | string        | どのルールに違反したか（例: `"TR-001"`）。               |
| `severity` | string        | `"error"` / `"warning"` / `"info"` のいずれか。 |
| `file`     | string        | 問題が関連する spec のファイルパス（可能ならノードの `file`）。    |
| `line`     | int \| null    | 行番号不明の場合は null でよい（index ベースなので必須ではない）。   |
| `message`  | string        | 人間が読める説明。                                 |
| `hint`     | string \| null | 修正のヒント（どう trace を張るべきか等）。                 |
| `extra`    | object \| null | 追加情報（対象 ID・関連ノード一覧など）。                    |

---

## 11. 非機能要件（簡易）

- **パフォーマンス**

  - SpecIndex に含まれるノード数 N に対して、トレースグラフ構築と lint は O(N + E) 程度（E は trace リンク数）となるよう実装する。
  - 数百〜数千ノード規模でも数秒以内に完了することを目安とする。
- **拡張性**

  - `TR-1xx` / `TR-2xx` などルールを増やしても、既存コードが壊れないようにする（未知の `enabled_rules` は無視する、など）。
- **LLM フレンドリ**

  - ルール ID と内容は 1:1 対応で意味がわかる命名にする（例: `TR-001_REQ_uncovered` のように suffix を付ける案もあり）。
  - 内部のデータ構造（SpecIndex, SpecNode, LintIssue）は、IF-910 / IF-920 / DATA-900 との整合性を保ち、フィールド名も素直な英単語に揃える。

---

## 12. 今後の拡張（メモ）

- trace lint の結果を集計した **Traceability Report（coverage サマリ）** を別 IF / DATA（例: DATA-903_trace_report）として定義し、`iori-spec trace-report` コマンドを追加する。
- REQ の重要度（優先度 / レベル）を導入し、重要度に応じて未カバー REQ の severity を変える（critical な REQ は error、それ以外は warning など）。
- IF-920 と共通する LintIssue 定義・ルールの有効/無効ロジックを専用モジュールに切



