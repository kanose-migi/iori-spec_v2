---
kind: data_contracts
scope: tooling.prompt
id: DATA-907
spec_title: "DATA-907: Prompt Bundle — ContextBundle → LLM Prompt Bundle (JSON)"
status: draft

trace:
  req: []        # 例: REQ-8xx_prompt_bundle などを後で紐付け
  if:
    - IF-970     # Prompt Bundle Builder — ContextBundle → LLM Prompt Bundle
  data:
    - DATA-905   # 入力: Context Bundle
  test: []
  task: []

dp:
  produces:
    - DATA-907   # IF-970 が生成する PromptBundle
  produced_by:
    - IF-970
  consumes:
    - DATA-905
  inputs:
    - iori_spec_config.yaml   # preset / language / system テンプレ定義
    - Markdown specs (*.md)

doc:
  read_next:
    - DATA-905_context_bundle.md
    - interfaces/IF-970_prompt_bundle_builder.md
  see_also:
    - interfaces/IF-960_context_builder.md
    - impl_notes/spec_command.md
---

# DATA-907: Prompt Bundle — ContextBundle → LLM Prompt Bundle (JSON)

## LLM_BRIEF

- role: このファイルは、IF-970（Prompt Bundle Builder）が生成する  
  **「LLM にそのまま渡せるプロンプト構造（PromptBundle）」のデータ構造**を定義する data_contract です。
- llm_action: あなた（LLM）は IF-970 を実装するとき、この data_contract を  
  **「prompt コマンドの JSON 出力／Python 戻り値のフォーマット」**として参照し、  
  ここで定義された構造を持つ `PromptBundle` オブジェクトを返すコードを書いてください。  
  `prompt_bundle.json` を手書きするのではなく、「常にこの構造に従う実装」を行うことが目的です。

## USAGE

- コマンド出力（CLI）
  - `iori-spec context REQ-201 --max-tokens 2000 --format json \`  
    `| iori-spec prompt --preset default.codegen --format json`  
    → 標準出力に **PromptBundle（DATA-907 準拠の 1 オブジェクト）** を JSON として出す。
- Python ライブラリとして
  - `build_prompt_bundle(context_bundle=..., preset="default.codegen") -> PromptBundle`
- 上位アプリケーションからの利用
  - OpenAI / Anthropic 等の API クライアントは、PromptBundle を  
    自前の message フォーマットにマッピングして LLM を呼び出す。

## READ_NEXT

- IF-970: Prompt Bundle Builder — ContextBundle → LLM Prompt Bundle
- DATA-905: Context Bundle — Spec IDs → LLM Context Bundle
- IF-960: Context Builder — Spec IDs → LLM Context Bundle

---

## 1. このドキュメントの役割

- **ContextBundle（DATA-905） → PromptBundle** という最後の変換ステップの  
  **出力形式（PromptBundle）の SSOT** を定義する。
- これにより：
  - IF-970 の実装
  - `iori-spec prompt` の CLI 出力
  - LLM 呼び出しを行う上位ツール
  が、同じ前提で PromptBundle を扱えるようにする。

---

## 2. 範囲（Scope）と前提

### 2.1 範囲

- DATA-907 は **1 回の prompt 生成で得られる PromptBundle 1 つ**のフォーマットを定義する。
- トップレベルは **1 つの JSON オブジェクト**（PromptBundle）とする。

```jsonc
{
  "preset": "default.codegen",
  "system": "...",
  "user": "...",
  "context_markdown": "...",
  "context_items": [
    { /* PromptContextItem */ }
  ]
}
````

### 2.2 前提

- PromptBundle は、以下を前提として組み立てられる：

  - ContextBundle（DATA-905）
  - preset / language / extra_instruction など（IF-970 で定義）
- PromptBundle 自体は **LLM サービス非依存**の中立な構造とし、
  各プロバイダ向けの message 形式への変換は別レイヤで扱う。

---

## 3. 運用上の目安（LLM / SDD 観点）

- ContextBundle から取得したコンテキストはトークン上限を意識し、不要なセクションは含めない。
- preset / language などのプリセット解決は IF-970 側で一元管理し、PromptBundle では結果のみを保持する。
- PromptBundle は provider 非依存の形を保ち、実際の API 呼び出し用メッセージ変換は別 IF に委ねる。

---

## 4. Summary

- **PromptBundle** は「どの preset で、どんな system / user メッセージと、
  どの spec コンテキスト（Markdown）を LLM に渡すか」を表現する。
- 構造は：

  - `PromptBundle` … 全体のメタ情報＋ system / user / context_markdown / context_items
  - `PromptContextItem` … context_markdown 内のどの部分がどの spec / セクションに対応するか
    という 2 層で構成される。

---

## 5. Schema

### 5.1 PromptBundle（トップレベル）

#### 5.1.1 フィールド一覧

| フィールド              | 型                   | 必須  | 説明                                               |
| ------------------ | ------------------- | --- | ------------------------------------------------ |
| `preset`           | string              | Yes | 使用したプリセット名（例: `"default.codegen"`）。              |
| `system`           | string              | Yes | LLM 用 system メッセージ。                              |
| `user`             | string              | Yes | LLM 用 user メッセージ（主命令＋補足）。                        |
| `context_markdown` | string              | Yes | ContextBundle から生成した Markdown テキスト（1 本の長い文字列）。   |
| `context_items`    | PromptContextItem[] | Yes | context_markdown に含めた spec / セクション情報。            |
| `language`         | string \| null       | No  | プロンプトの主要言語（例: `"ja"`, `"en"`）。未指定時は `null`。      |
| `metadata`         | object \| null       | No  | 任意のメタ情報（generator 情報や timestamp 等）。未使用なら `null`。 |

#### 5.1.2 フィールド詳細

- `preset`

  - IF-970 で指定／解決されたプリセットの論理名。
  - 例：

    - `"default.codegen"`
    - `"default.review"`
    - `"default.summarize"`
- `system`

  - LLM の role / 振る舞いを決めるメッセージ。
  - 例：
    「あなたはソフトウェアエンジニアリングと仕様設計に精通したアシスタントです。…」
- `user`

  - ユーザーからの主命令を表すメッセージ。
  - 例：
    「次の仕様コンテキストを読み、この IF を Python で実装してください。…」
  - IF-970 では `extra_instruction` を末尾に追記するなどの処理を行う。
- `context_markdown`

  - ContextBundle.items[].sections[].body を元に組み立てた Markdown。
  - 人間が読んでも spec の構造が分かるよう、
    spec ごとのヘッダや区切りコメントを含めてよい（IF-970 参照）。
- `context_items`

  - context_markdown 内のどの範囲がどの spec / セクションに対応するかを記録する配列。
  - 後から特定の spec / セクションだけを LLM に抽出したり、
    ハイライト表示したりする用途に使える。
- `language`

  - `"ja"` / `"en"` 等の言語コードを想定。
  - `null` の場合、「preset 側のデフォルト言語に従う」と解釈してよい。
- `metadata`

  - 任意の追加メタ情報を格納するための object。
  - 例：

    - `{ "generated_at": "2025-12-04T12:34:56Z", "generator": "iori-spec 0.1.0" }`
  - 使用しない場合は `null` または省略可（MVP では `null` 推奨）。

---

### 5.2 PromptContextItem（context_items 要素）

#### 5.2.1 構造（一覧）

| フィールド          | 型      | 必須  | 説明                                                |
| -------------- | ------ | --- | ------------------------------------------------- |
| `id`           | string | Yes | 対象 spec の ID。                                     |
| `file`         | string | Yes | spec ファイルの相対パス。                                   |
| `role`         | string | Yes | spec の role（req / if / data / test / task / ...）。 |
| `scope`        | string | Yes | spec の scope。                                     |
| `kind`         | string | Yes | spec の kind（requirements / interfaces / ...）。     |
| `rule_id`      | string | Yes | 対応する SectionSnippet.rule_id（例: `"llm_brief"`）。    |
| `heading`      | string | Yes | セクション見出しテキスト（例: `"## LLM_BRIEF"`）。                |
| `start_offset` | int    | Yes | context_markdown 内での開始位置（文字オフセット、0-origin）。       |
| `end_offset`   | int    | Yes | context_markdown 内での終了位置（文字オフセット、end-exclusive）。  |

#### 5.2.2 フィールド詳細

- `id`

  - ContextBundle.items[].id と一致する spec ID。
- `file`

  - ContextBundle.items[].file と一致する相対パス。
- `role`

  - ContextBundle.items[].role と一致。
  - 例：`"req"`, `"if"`, `"data"`, `"test"`, `"task"` 等。
- `scope`

  - ContextBundle.items[].scope と一致。
- `kind`

  - ContextBundle.items[].kind と一致。
- `rule_id`

  - 対象 SectionSnippet.rule_id（DATA-905 参照）。
  - 例：`"llm_brief"`, `"summary"`, `"acceptance_criteria"`。
- `heading`

  - 実際の Markdown 見出しテキスト。
  - 例：`"## LLM_BRIEF"`, `"## 4. Summary"`。
- `start_offset` / `end_offset`

  - context_markdown 文字列に対するオフセット。
  - `context_markdown[start_offset:end_offset]` が、この PromptContextItem に対応する本文になるようにする。
  - 改行・区切りコメントも含めるかどうかは IF-970 側で統一する（MVP では本文＋その heading の直後からを対象としてよい）。

---

## 6. 例

簡易な PromptBundle の例：

```jsonc
{
  "preset": "default.codegen",
  "system": "You are an assistant that reads iori-spec specifications and writes Python code...",
  "user": "次の仕様コンテキストを読み、この IF を Python で実装してください。",
  "context_markdown": "<!-- REQ-201 -->\n# [REQ-201] digits segmentation rules\n\n## LLM_BRIEF\n...\n",
  "context_items": [
    {
      "id": "REQ-201",
      "file": "requirements/REQ-201_digits_segments.md",
      "role": "req",
      "scope": "client.query_engine",
      "kind": "requirements",
      "rule_id": "llm_brief",
      "heading": "## LLM_BRIEF",
      "start_offset": 54,
      "end_offset": 120
    }
  ],
  "language": "ja",
  "metadata": {
    "generated_at": "2025-12-04T12:34:56Z",
    "generator": "iori-spec 0.1.0"
  }
}
```

---

## 7. Constraints（制約）

- トップレベルは常に **1 オブジェクト**（配列ではない）。
- `preset` / `system` / `user` / `context_markdown` / `context_items` は必須。
- `context_items` は配列であり、空の場合は `[]`（context_markdown が空でない場合でも構わない）。
- `start_offset` / `end_offset` は 0 以上の整数で、`start_offset <= end_offset` を満たす。
- `context_markdown.length >= end_offset` でなければならない。
- `language` / `metadata` は省略可能だが、存在する場合は上記スキーマに従う。

---

## 8. IF-970 との関係

- IF-970（Prompt Bundle Builder）は、この DATA-907 を

  - Python 戻り値の型
  - CLI `--format json` の出力フォーマット
    として採用する。
- IF-970 側では、ContextBundle（DATA-905）から抽出したセクションを
  context_markdown に連結し、その上に PromptContextItem の `start_offset` / `end_offset` を計算して
  PromptBundle を構築する。

---

## 9. 今後の拡張（メモ）

- `metadata` 配下に、以下のようなフィールドを追加する案：

  - `context_summary` … context_markdown 全体の要約（数百文字）。
  - `seed_ids` … 元の ContextBundle.seed_ids のコピー。
  - `index_version` … SpecIndex のバージョン（コミットハッシュ等）。
- PromptBundle から OpenAI などの message 形式に変換する
  **IF-975: provider_prompt_adapter** のような IF を定義し、
  「PromptBundle → model-specific messages」の責務を切り分ける。



