# Spec FAQ (iori-spec 用)

## Q1. 新しいドキュメントを追加したいとき、どのディレクトリに置けばいい？

**A.** まず「そのドキュメントは何についての話か？」を考えるとよいです。

* プロジェクトの目的・スコープ・ビジョン → `steering/`
* ツールとして「何ができる必要があるか」 → `requirements/`
* 全体構造・コンポーネント・依存方向 → `architecture/`
* CLI / API の入口・オプション・戻り値 → `interfaces/`
* JSON やバイナリのスキーマ → `data_contracts/`
* どう検証するか・受け入れ条件 → `tests/`
* 仕様の書き方・命名規則・用語集 → `reference/`
* 設計メモ・ボツ案・検討ログ → `impl_notes/`

迷った場合は、

> 「これは **正本としての仕様**か？
> それとも **考え中のメモ / 実装ガイド**か？」

で判断し、後者ならひとまず `impl_notes/` に置くのがおすすめです。

## Q2. IF（interfaces）にアルゴリズムを書いてもいい？

**A.** 原則は「IF は外から見えるインターフェイス（契約）を書く場所」です。
つまり、

* 入力（引数・オプション）
* 出力（どの DATA-xxx を返すか）
* 正常／異常系の挙動
* 守るべき制約（計算量・メモリ使用など）

を中心に書きます。

ただし例外として、

* パフォーマンス要件やメモリ制約を守るために**アルゴリズム自体が契約になる場合**

は、IF にアルゴリズム的制約を**書いてよい／書くべき**です。

その際は、次のように分けるとスッキリします。

* **Algorithm (normative)**
  → 守らないと仕様違反になる制約（計算量、ストリーミング必須など）
* **Implementation Notes (non-normative)**
  → 実装ガイド・具体手順・LLM 用ヒント（守れなくても仕様違反ではない）

「LLM にこう実装させたい」という細かい手順は、
可能なら `impl_notes/` に「実装ノート」として分離すると、IF が肥大化せずに済みます。

## Q3. LLM に実装をお願いしたいとき、どのドキュメントを見せればいい？

**A.** だいたい次の組み合わせを想定しています。

1. 仕様の前提：

   * `reference/spec_structure_and_traceability.md`
   * 必要なら `reference/iori_spec_guide.md`, `reference/naming_conventions.md`

2. 実装したい機能の正本仕様：

   * 対応する REQ（`requirements/functional.md` 等の該当部分）
   * 対応する IF（`interfaces/...`）
   * 利用する DATA のスキーマ（`data_contracts/...`）

3. 必要に応じて実装ノート：

   * `impl_notes/` 以下の該当ノート
     （例：`impl_notes/IF-100_index_algorithm_notes.md` など）

「契約」は requirements / interfaces / data_contracts で、
「実装のアドバイス」は impl_notes という分担を守っておくと、
LLM に渡すコンテキストも整理しやすくなります。

## Q4. data_contracts と interfaces の違いがよく分からない

**A.** シンプルに言うと：

* `interfaces/`
  → **「どう呼ぶか・どう返るか」**（コマンド名・オプション・返す DATA-xxx の種類）
* `data_contracts/`
  → **「返ってくるデータの中身そのもの」**（JSON/バイナリのフィールドと意味）

例：`iori-spec index` の場合

* interfaces 側：

  * コマンド名、引数、`--format` オプション、終了コードなど
  * 「戻り値は DATA-101（index_json）である」といった宣言

* data_contracts 側：

  * DATA-101 の JSON スキーマ
  * `docs[]` の要素に含まれるフィールド（doc_id, path, kind, scope, …）の意味

## Q5. reference と steering の違いは？

**A.**

* `steering/`
  →「このツールを**なぜ**作るのか／**どこへ**向かうのか」というプロダクトの舵取りの話。

* `reference/`
  →「このツールの仕様を**どう書くか・どう読むか**」というメタ情報・ルール・辞書。

steering は動機や方向性、reference は書式・ルール・言葉の意味、
というイメージで分けると判断しやすいです。

## Q6. impl_notes に書いた内容が“最終仕様”になってきた場合はどうする？

**A.** そのときは、「昇格」を検討します。

* 要件そのものになっている → `requirements/` に移す
* IF の契約になっている → `interfaces/` に反映する
* データ形式の正本になっている → `data_contracts/` に切り出す

impl_notes は「ゴミ箱」ではなく、

> 「まずはここで荒く書いて → 本当に重要になったら正規の spec に昇格させる」

ための**待機場所**と考えるのがよさそうです。



