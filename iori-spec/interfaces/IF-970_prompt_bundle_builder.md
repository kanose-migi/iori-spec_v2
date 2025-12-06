---
kind: interfaces
scope: tooling.prompt
id: IF-970
spec_title: "IF-970: Prompt Bundle Builder — ContextBundle → LLM Prompt Bundle"
status: draft

trace:
  req: []        # 例: REQ-8xx_prompt_bundle などを後で紐付け
  if:
    - IF-960     # Context Builder — Spec IDs → LLM Context Bundle
  data:
    - DATA-905   # 入力: Context Bundle
  test: []
  task: []

dp:
  produces:
    # 将来的に DATA-907_prompt_bundle として data_contract 化するが、
    # 本 IF 時点では「論理的な PromptBundle」を定義する。
  produced_by:
    - IF-970
  consumes:
    - DATA-905
  inputs:
    - iori_spec_config.yaml   # プロンプトテンプレート／プリセット設定

doc:
  read_next:
    - DATA-905_context_bundle.md
    - interfaces/IF-960_context_builder.md
    - reference/iori_spec_guide.md
  see_also:
    - impl_notes/spec_command.md
---

# IF-970: Prompt Bundle Builder — ContextBundle → LLM Prompt Bundle

## LLM_BRIEF

- role: この IF は、ContextBundle（DATA-905）を入力として、  
  **「LLM にそのまま投げられるプロンプト構造（PromptBundle）」** を組み立てる  
  Prompt Builder の振る舞いを定義します。
- llm_action: あなた（LLM）はこの IF と DATA-905 を読み、  
  `build_prompt_bundle(context_bundle, preset=...) -> PromptBundle` のような  
  **Python モジュール（prompt コア）** を設計・実装してください。  
  ここでいう PromptBundle は、`system` / `user` / `context_markdown` などを含む  
  JSON 互換の構造体であり、将来的に DATA-907 として data_contract 化されます。

## USAGE

- 典型ユースケース（CLI or 上位ツールからの利用イメージ）

  - コンテキスト＋テンプレートから LLM プロンプトを組み立てる：

    ```bash
    # REQ-201 を seed に context を構築した結果から、そのまま LLM プロンプトにしたい
    iori-spec context REQ-201 --max-tokens 2000 --format json \
      | iori-spec prompt --preset default.codegen --format json
    ```

  - 上位アプリケーションから Python ライブラリとして利用：

    ```python
    ctx = build_context(index, section_schema, seed_ids=["REQ-201"], max_tokens=2000)
    prompt = build_prompt_bundle(
        context_bundle=ctx,
        preset="default.codegen",
        extra_instruction="この IF を Python で実装してください。",
    )
    ```

- PromptBundle の典型形（イメージ）：

  ```jsonc
  {
    "preset": "default.codegen",
    "system": "You are an assistant that reads iori-spec specs and writes Python code ...",
    "user": "次の仕様に従ってモジュールを実装してください。",
    "context_markdown": "# REQ-201 ...\n## IF-200 ...\n...",
    "context_items": [
      { "id": "REQ-201", "heading": "## LLM_BRIEF", "body": "..." }
    ]
  }
  ````

## READ_NEXT

- DATA-905: Context Bundle — Spec IDs → LLM Context Bundle
- IF-960: Context Builder — Spec IDs → LLM Context Bundle
- reference/iori_spec_guide.md（role / kind / scope の意味づけ）

---

## 1. このドキュメントの役割

- 「index / lint / search / impact / context」に続く
  **「最後の 1 ステップ（Context → Prompt）」** の IF を定義する。
- 具体的には：

  - 入力：ContextBundle（DATA-905）＋ preset 名＋追加指示など
  - 出力：PromptBundle（system / user / context_markdown などを含む構造体）
  - 振る舞い：preset ごとに

    - system メッセージのテンプレート
    - user メッセージのベース文
    - context のマージ方法・並べ方
      を切り替えられるようにする。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- 本 IF の責務は **構造化された ContextBundle → LLM 向けプロンプト構造** の変換であり、

  - LLM 呼び出し（API クライアント実装）
  - 実際の応答処理
    は範囲外とする。
- PromptBundle の構造は「シンプルな JSON 互換オブジェクト」であり、

  - ChatGPT や OpenAI API の message 形式
  - それ以外の LLM サービス
    にもマッピングしやすい形を意図する。

### 2.2 前提

- ContextBundle は IF-960 / DATA-905 準拠であり、

  - `items[].sections[].body` に LLM に渡したい Markdown テキストが含まれている。
- プロンプトテンプレートや preset の設定は `iori_spec_config.yaml` 等に保持する想定だが、

  - MVP ではコード内の定数（組み込みプリセット）でもよい。

---

## 3. 運用上の目安（LLM / SDD 観点）

- ContextBundle（DATA-905）は `paths.ignore_dirs` を適用した最新の SpecIndex から生成されたものを使用する。
- preset/language などの切替は config（DATA-910）の定義に従い、`--format json` 出力（DATA-907 相当）はログと分離して保存する。
- LLM への入力サイズを抑えるため、context_markdown の長さやセクション抽出ポリシーを定期的に見直す。

---

## 4. Summary

- ContextBundle を入力に、preset/language/extra_instruction に応じた PromptBundle（DATA-907）を構築する。
- system/user/context_markdown を組み立て、LLM 呼び出しに直接渡せる形を定義する。

---

## 5. Inputs

- ContextBundle（DATA-905、json）
- `reference/iori_spec_config.yaml` の prompt セクション（DATA-910）
- preset 名、language、extra_instruction などのパラメータ

---

## 6. Outputs

- PromptBundle（DATA-907、json）
- Exit Code（生成可否で判断）

---

## 7. PromptBundle の設計方針

### 7.1 目的

- LLM 呼び出し側にとって：

  - **「この PromptBundle をそのまま LLM に渡せばいい」**
  - という状態を作ることが目的。

- iori-spec としては：

  - ContextBundle という「仕様・trace ベースの構造化コンテキスト」と
  - 実際の LLM プロンプト形式
    を疎結合に保つための「変換レイヤ」として位置づける。

### 7.2 必須要素（MVP）

PromptBundle（論理構造）は最低限、以下を持つ：

- `preset`：使用したプリセット名（例: `"default.codegen"`）
- `system`：LLM の role・ふるまいを決める system メッセージ
- `user`：ユーザーからの主命令（例: 「次の仕様に従ってコードを書いてください」）
- `context_markdown`：ContextBundle から組み立てた Markdown テキスト（1 本の長い文字列）
- `context_items`：どの spec / セクションが context_markdown に含まれているかのメタ情報

> この構造は後続の DATA-907_prompt_bundle で正式な data_contract として定義される予定。

---

## 8. Inputs / Outputs

### 8.1 Inputs（コア関数）

コア関数の想定シグネチャ：

```python
build_prompt_bundle(
    context_bundle: ContextBundle,
    *,
    preset: str = "default.codegen",
    extra_instruction: str | None = None,
    language: str | None = None,   # "ja" / "en" など
) -> PromptBundle
```

| 名前                  | 型             | 必須  | 説明                                                  |
| ------------------- | ------------- | --- | --------------------------------------------------- |
| `context_bundle`    | ContextBundle | Yes | DATA-905 準拠の ContextBundle。                         |
| `preset`            | string        | No  | 使用するプリセット名。デフォルト `"default.codegen"`。               |
| `extra_instruction` | string \| None | No  | user メッセージ末尾に追記する追加指示。                              |
| `language`          | string \| None | No  | プロンプトの言語設定（"ja" / "en" など）。未指定時は preset 側のデフォルトに従う。 |

### 8.2 Outputs（コア関数）

戻り値：`PromptBundle`

PromptBundle の論理構造（MVP）は以下の通り：

| フィールド              | 型                   | 必須  | 説明                                    |
| ------------------ | ------------------- | --- | ------------------------------------- |
| `preset`           | string              | Yes | 使用したプリセット名。                           |
| `system`           | string              | Yes | LLM 用 system メッセージ。                   |
| `user`             | string              | Yes | LLM 用 user メッセージ（主命令＋補足）。             |
| `context_markdown` | string              | Yes | ContextBundle から生成した Markdown。        |
| `context_items`    | PromptContextItem[] | Yes | context_markdown に含めた spec / セクション情報。 |

PromptContextItem の構造：

| フィールド          | 型      | 必須  | 説明                                                |
| -------------- | ------ | --- | ------------------------------------------------- |
| `id`           | string | Yes | 対象 spec の ID。                                     |
| `file`         | string | Yes | spec ファイルパス。                                      |
| `role`         | string | Yes | spec の role（req / if / data / test / task / ...）。 |
| `scope`        | string | Yes | spec の scope。                                     |
| `rule_id`      | string | Yes | 対応する SectionSnippet.rule_id（例: "llm_brief"）。      |
| `heading`      | string | Yes | セクション見出しテキスト。                                     |
| `start_offset` | int    | Yes | context_markdown 内での開始位置（文字オフセット、0-origin）。       |
| `end_offset`   | int    | Yes | context_markdown 内での終了位置（文字オフセット、end-exclusive）。  |

> `start_offset` / `end_offset` は、後から「特定の spec / セクションだけを LLM に抜き出したい」
> という用途に備えたオプションだが、MVP でも持っておくと便利なので最初から定義しておく。

---

## 9. テンプレート・プリセットの振る舞い

### 9.1 preset の役割

- `preset` は「どのような LLM ロール・タスクで使うか」を表す論理名。
- 例：

  - `"default.codegen"` … 仕様からコードを生成する用途。
  - `"default.review"` … 仕様やコードをレビューする用途。
  - `"default.summarize"` … 仕様を要約する用途。

### 9.2 system / user のテンプレート

- 各 preset は少なくとも以下を定義する：

  - `system_template(language)`
    → 言語に応じた system メッセージ。
  - `user_template(language)`
    → 主命令のベース。`extra_instruction` があれば末尾に追記。

- 例（イメージ：default.codegen / language="ja"）：

  - system:

    > あなたはソフトウェアエンジニアリングと仕様設計に精通したアシスタントです。
    > iori-spec 形式の仕様を読み取り、その意図を尊重しながらコードを実装します。…

  - user:

    > 次の仕様コンテキストを読み、指示に従ってモジュールを実装してください。
    > 実装言語や入出力形式は仕様に従います。…

### 9.3 context_markdown の組み立て

- 基本方針（MVP）：

  - ContextBundle.items[].sections[] を、優先度順に並べて、
  - シンプルな Markdown として連結する。

- 連結フォーマット例：

  ```markdown
  <!-- REQ-201 -->
  # [REQ-201] digits segmentation rules

  ## LLM_BRIEF
  ...

  ## 4. Summary
  ...

  <!-- IF-200 -->
  # [IF-200] Query Engine — digits → Segmented Candidates
  ...
  ```

- これにより、人間が読んでもある程度わかりやすく、
  かつ LLM が spec の区切りを理解しやすい構造になる。

---

## 10. 処理フロー（概略）

1. **ContextBundle の受け取り**

   - DATA-905 準拠の ContextBundle を引数で受け取る。
2. **Preset の解決**

   - `preset` 名と `language` から、使用するテンプレート群を決定。
3. **context_markdown の生成**

   - ContextBundle.items を順番に処理し、

     - spec ごとにヘッダ行
     - SectionSnippet ごとに heading & body
       を連結して 1 本の Markdown にする。
   - 連結時に各セクションの `start_offset` / `end_offset` を計算し、PromptContextItem に格納。
4. **system / user メッセージの生成**

   - `system_template(language)` と `user_template(language)` を呼び出して base 文を生成。
   - `extra_instruction` があれば user の末尾に追記。
5. **PromptBundle の組み立て**

   - 上記で得られた system / user / context_markdown / context_items をまとめて PromptBundle を返す。

---

## 11. Acceptance Criteria（受け入れ条件）

1. **ContextBundle → context_markdown の正しさ**

   - ContextBundle に含まれる SectionSnippet の `body` が、
     期待された順序・階層で context_markdown に連結されている。
2. **PromptContextItem の整合性**

   - 各 PromptContextItem の `start_offset` / `end_offset` が
     context_markdown から該当セクション本文を切り出したときに一致する。
3. **preset の切り替え**

   - `preset="default.codegen"` と `"default.summarize"` で
     少なくとも system / user のメッセージ内容が変化する。
4. **言語設定**

   - `language="ja"` と `"en"` で、system / user の言語が切り替わる（MVP ではベース文の言語だけでよい）。
5. **拡張に優しい構造**

   - PromptBundle は JSON シリアライズ可能なフラット構造であり、
     DATA-907 として data_contract 化したときに大きな変更を必要としない。

---

## 12. 非機能要件（簡易）

- **シンプルさ**

  - PromptBundle は「LLM クライアント層から見て分かりやすい」構造であること。
  - 必須フィールドを最小限に保ち、`extra` 等の拡張ポイントは後付けできるようにする。
- **LLM フレンドリ**

  - context_markdown は人間が見ても読める Markdown とし、
    ID / heading による区切りが明確であること。
- **再現性**

  - 同じ ContextBundle / preset / language / extra_instruction に対して、
    常に同じ PromptBundle が生成される（非決定的な並び順にならない）。

---

## 13. 今後の拡張（メモ）

- PromptBundle を正式な data_contract として **DATA-907_prompt_bundle** として切り出す。
- OpenAI / Anthropic など特定プロバイダ向けに、

  - PromptBundle → model-specific messages への変換 IF を別途定義する。
- `preset` を外部 YAML / JSON で定義し、

  - iori-spec のユーザーが自分好みのプロンプトテンプレートを追加・差し替えできるようにする。



