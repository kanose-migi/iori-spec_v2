---
kind: data_contracts
scope: tooling.section_schema
id: DATA-901
spec_title: "DATA-901: Spec Section Schema — spec_section_schema.yaml"
status: draft

# ---- 要求トレースグラフ（G_trace）用の情報 ----
trace:
  req: []        # セクション構造に関する要件 REQ-xxx があれば追記
  if: []         # この DATA を消費する IF（lint/context 等）を将来的に紐付けてもよい
  data:
    - DATA-900   # 同じ tooling 系 DATA として論理的に関連
  test: []       
  task: []       

# ---- Data–Process グラフ（G_dp）用の情報 ----
dp:
  produces: []      
  produced_by: []   
  consumes:
    - DATA-900      # セクションスキーマは index と合わせて利用される
  inputs: []        

# ---- ドキュメント依存グラフ（G_doc）用の情報 ----
doc:
  read_next:
    - DATA-900
  see_also:
    - reference/iori_spec_guide.md
    - impl_notes/spec_template.md
---

# DATA-901: Spec Section Schema — spec_section_schema.yaml

## LLM_BRIEF

- role: このファイルは、`kind` ごとに「どのセクション見出しを必須とするか」「どのセクションを LLM 用コンテキストとして抽出するか」に加えて、**各セクションの意図・記載内容・LLM への指示（ヒント）** を定義するセクションスキーマの data_contract です。
- llm_action: `iori-spec lint` や `iori-spec context` など、仕様書の構造チェックやコンテキスト抽出を行うモジュール、あるいは将来の scaffold/prompt 系モジュールを **設計・実装・変更するとき**に、このスキーマを参照してください。`spec_section_schema.yaml` 自体を生成するのではなく、「ここに定義されたルール（構造 + 意味）を読み取り適用するコード」を書くことが目的です。

## USAGE

- この data_contract を参照する主なユースケース
  - `iori-spec lint` が、kind ごとに必須セクションが揃っているか・重複していないかなどを検査する。
  - `iori-spec context` / `show` が、「LLM に渡すべきセクションだけ」を自動抽出する。
  - `iori-spec scaffold new`（将来）などが、新しい spec のひな型を生成する際に利用する。
  - PromptBundleBuilder（IF-970 など）が、`llm_hint` をもとに各セクションの扱い方を LLM に説明するプロンプトを組み立てる。
- 人間がこのドキュメントを読むタイミング
  - spec テンプレートを増やしたいとき（新しい kind を追加する等）
  - `LLM_BRIEF`, Summary, Acceptance など、「LLM にとって重要なセクション」を整理したいとき
  - 「このセクションには何を書けばよいか」を SSOT として確認したいとき

## READ_NEXT

- DATA-900: Spec Index Catalog — spec_index.json
- reference/iori_spec_guide.md
- impl_notes/spec_template.md

---

## 1. このドキュメントの役割

- 仕様書の Markdown 構造（見出し）に対して、
  - **kind ごとに必須となるセクション**
  - **LLM に渡すべきセクション（tool_source）**
  - **見出しレベルとテキスト**
  - **セクションに書くべき内容の説明（body_hint）**
  - **LLM に対する振る舞い指示（llm_hint）**
  を明示的に定義する。
- これにより、
  - `lint` が構造上の崩れ（必須見出し欠落・重複など）を自動検出できる。
  - `context` / `show` が kind に依存しない共通ロジックでコンテキストを抽出できる。
  - scaffold 系ツールや LLM が、「どのセクションに何を書くべきか」を機械可読な形で理解できる。
- テンプレート（`spec_template.md`）と実データの間に立つ **機械可読な中間レイヤ** として機能する。
- 各 kind に対してどの見出しが存在するか／必須かといった具体的な内容と、その意味・書き方に関するヒントは、
  本 data_contract のインスタンスである `reference/spec_section_schema.yaml` に定義される。
  iori-spec ツールはこの YAML を SSOT として扱い、本ドキュメントはそのスキーマ（型と意味フィールド）の仕様を記述する。

## 2. 範囲（Scope）と前提

- 範囲
  - `spec_section_schema.yaml` という 1 つの YAML ファイルの構造を定義する。
  - kind ごとの「layer1（共通セクション）」および「layer2（kind 固有セクション）」のうち、**ツールが構造的に理解したい見出し**と、**各セクションの意味に関するメタ情報**を対象とする。
- 前提
  - 各 spec は `LLM_BRIEF`, `USAGE`, `READ_NEXT`, `1. このドキュメントの役割` などの layer1 セクションを持つ。
  - data_contract 側で「どの見出しを tool_source とするか」を指定し、本文の抜粋は runtime に Markdown から切り出す。
  - 「このセクションには何を書くべきか」「LLM にどう使わせたいか」は、`short_desc` / `body_hint` / `llm_hint` として YAML に記述される。

## 3. 運用上の目安（LLM / SDD 観点）

- LLM 観点
  - LLM には `spec_section_schema.yaml` 自体をコンテキストとして渡すことで、
    - 「どのセクションを抽出すべきか」
    - 「各セクションには何が書かれているべきか」
    - 「LLM はどう振る舞うべきか（llm_hint）」
    を理解させることができる。
- SDD 観点
  - 新しい kind を追加する際、テンプレート（`spec_template.md`）の整備と同時に、このスキーマに対応する `rules` を追加する。
  - 既存セクション名を変更する場合は、まずこの data_contract を更新し、その後テンプレ・既存 spec を順次追従させる。
  - `body_hint` / `llm_hint` は、**「仕様の書き方ガイド」を別ファイルで重複管理するのではなく、できるだけここに一元化する** ことを推奨する。

---

## 4. Summary

- `spec_section_schema.yaml` は、kind ごとに **「どの見出しが必須か」「どの見出しを LLM に渡すか」** に加え、
  **「各セクションの意図・記載すべき内容・LLM への指示」** を定義するための YAML ファイルである。
- `rules[]` にセクションルールを 1 件ずつ定義し、
  - `heading.level` / `heading.text` で見出しを特定し、
  - `required` / `multiple` / `tool_source` / `order` で振る舞いを指定し、
  - `short_desc` / `body_hint` / `llm_hint` で意味とガイドを与える。
- `options` に、スキーマ全体に関するポリシー（未知の見出しを許可するか等）を記述する。

---

## 5. Schema

### 5.1 トップレベル構造

```yaml
version: 0.2

rules:
  - id: llm_brief
    kinds: ["*"]
    heading:
      level: 2
      text: "LLM_BRIEF"
    required: true
    multiple: false
    tool_source: true
    order: 10
    short_desc: >
      LLM に向けて、この仕様が「何をしたいのか」を手短に伝えるための要約セクション。
    body_hint: |
      - この spec の役割（何を決める／何は決めないか）
      - LLM に期待する振る舞い（コード生成・レビュー・設計補助 など）
      - 注意してほしい制約（破ってはいけない前提・既存設計との整合性）
      を 3〜7 行程度で bullet / paragraph で書く。
    llm_hint: >
      ここに書かれた内容は LLM にとって「指示の上位メタ」となる。
      あなたはまず LLM_BRIEF を読み、この意図に沿って USAGE や本文の解釈・出力方針を決めること。

options:
  allow_extra_sections: true
  default_tool_source: false
````

| フィールド     | 型             | 必須  | 説明                  |
| --------- | ------------- | --- | ------------------- |
| `version` | number\|string | Yes | このスキーマファイル自体のバージョン。 |
| `rules`   | SectionRule[] | Yes | セクションごとのルール定義の配列。   |
| `options` | object        | No  | スキーマ全体に対するオプション設定。  |

### 5.2 SectionRule オブジェクト

```yaml
- id: req_summary
  kinds: ["requirements"]
  heading:
    level: 2
    text: "4. 要件の概要（Summary）"
    match: exact
  required: true
  multiple: false
  tool_source: true
  order: 100

  short_desc: >
    対象となる要件の概要を、1〜3 段落程度で説明するセクション。
  body_hint: |
    - この REQ が解決しようとしている問題
    - 高レベルなゴール（ユーザー視点／システム視点）
    - 他の REQ や ARCH との関係（ざっくりでよい）
    を簡潔にまとめる。
  llm_hint: >
    あなたは req_summary を読むことで、この REQ が何を目的としているかを把握し、
    Acceptance Criteria や IF/DATA との整合性をチェックする。
```

| フィールド         | 型           | 必須  | 説明                                                                        |
| ------------- | ----------- | --- | ------------------------------------------------------------------------- |
| `id`          | string      | Yes | 内部識別子（例: `llm_brief`, `req_summary`, `data_schema`）。スキーマ内でユニークであることが望ましい。 |
| `kinds`       | string[]    | Yes | 適用対象の `kind` 一覧。`"*"` を含む場合は全 kind 共通ルールとして扱う。                            |
| `heading`     | HeadingSpec | Yes | 見出しの指定方法。後述。                                                              |
| `required`    | boolean     | Yes | 対象 kind において、このセクションが必須かどうか。                                              |
| `multiple`    | boolean     | Yes | 同じ見出しが複数存在することを許可するか。                                                     |
| `tool_source` | boolean     | Yes | `context` / `show` で LLM に渡す本文として含めるかどうか。                                 |
| `order`       | number      | Yes | kind 内での論理順序。lint で並び順をチェックしたり、context 出力の順番を決める際に利用。                     |
| `short_desc`  | string      | No  | （任意）このセクションの一言説明。UI やドキュメント生成で「セクション一覧」を表示する際に利用することを想定。                  |
| `body_hint`   | string      | No  | （任意）このセクションに**何を書けばよいか**を説明するテキスト。複数行の Markdown（箇条書きなど）をそのまま埋め込んでよい。      |
| `llm_hint`    | string      | No  | （任意）LLM 向けの指示・ヒント。このセクションをどのように解釈し、どのような場面でどう使うべきかを LLM に伝えるためのテキスト。      |
| `notes`       | string      | No  | （任意）人間向けのメモや備考。ツールが直接使わない補足情報を置く場所として利用してよい。                              |

- `short_desc` / `body_hint` / `llm_hint` / `notes` はすべて任意フィールドだが、
  **標準の kind / セクションについてはできるだけ `short_desc` と `body_hint` を埋める**ことを推奨する。
- LLM を強く活用するプロジェクトでは、`llm_hint` を積極的に活用することで、
  「仕様の書き方」と「LLM の使い方」を 1 つの SSOT にまとめることができる。

### 5.3 HeadingSpec オブジェクト

```yaml
heading:
  level: 2
  text: "LLM_BRIEF"
  match: exact      # 省略時は exact
```

| フィールド   | 型      | 必須  | 説明                                                              |
| ------- | ------ | --- | --------------------------------------------------------------- |
| `level` | number | Yes | Markdown 見出しレベル（`##` → 2, `###` → 3 など）。                        |
| `text`  | string | Yes | 見出しのテキスト。デフォルトでは完全一致でマッチさせる。                                    |
| `match` | string | No  | `"exact"`（完全一致）または `"prefix"`（先頭一致）を指定可能（v1 では `exact` 前提でもよい）。 |

### 5.4 options

```yaml
options:
  allow_extra_sections: true
  default_tool_source: false
```

| フィールド                  | 型       | 必須 | 説明                                                                         |
| ---------------------- | ------- | -- | -------------------------------------------------------------------------- |
| `allow_extra_sections` | boolean | No | `rules` に定義されていない見出しを許可するか。`false` の場合、未知の見出しは lint の警告またはエラー対象とする。        |
| `default_tool_source`  | boolean | No | `rules` に定義されていない見出しを、デフォルトで `tool_source: true` とみなすかどうか。通常は `false` を推奨。 |

---

## 6. Constraints（任意）

- `rules[].id` はスキーマ内で一意であることが望ましい。
- 同じ `(kinds, heading.level, heading.text)` 組を複数定義しない。
- `order` はその kind 内で昇順になるように割り当てる（lint で順序チェックを行う場合の前提）。
- `"*"` を含むルールと、具体的な kind を指定したルールが衝突する場合の優先順位は、

  - 「より具体的な kind を持つルール」が優先される実装とする。
- `short_desc` / `body_hint` / `llm_hint` / `notes` は optional だが、

  - `llm_hint` には LLM が読んでも意味がわかる文体で記述すること。
  - `body_hint` には「何を書くべきか」が分かる具体的な bullet や例示を含めることを推奨する。
- `body_hint` / `llm_hint` に長大なテキストを入れすぎると、
  ContextBundle / PromptBundle のトークン消費が増えるため、プロジェクトポリシーに応じて適度な粒度を保つ。

---

## 7. 利用箇所の概要（任意）

- コマンド

  - `iori-spec lint`

    - `rules` に基づき、kind ごとの必須セクション・重複・順序などを検査する。
  - `iori-spec context` / `show`

    - `tool_source: true` なセクションだけを抽出して LLM 用コンテキストを構成する。
  - `iori-spec scaffold new`（将来）

    - `rules` を参照して、新規 spec のひな型を自動生成する。
    - `body_hint` をコメントとして埋め込んだ scaffold を作ることもできる。
  - `iori-spec prompt` / PromptBundleBuilder（将来）

    - `llm_hint` をもとに、「各セクションをどう解釈しどう使うか」を LLM に説明するための system / user プロンプトを構成する。
- その他

  - テンプレートファイル（`spec_template.md`）を編集する際に、「どの見出しがツール的に意味を持っているか」「何を書くべきか」を確認するためにも利用できる。
  - 将来的には `spec_template.md` 自体を `spec_section_schema.yaml` から自動生成することも想定し、その場合も本 data_contract が SSOT となる。



