# 第3回 解答

## 演習

- 第1回（素のLLM）とエージェントの回答の違い：
  以前は一般論的な回答だったが、今回はglossary.jsonに従っていた。

- `--trace` で見えたツール呼び出し（ツール名と引数）：
--- trace ---
[tool call]   search_glossary({'query': 'LoRA'})
[tool call]   search_glossary({'query': 'QLoRA'})
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
[tool return] search_glossary -> [{"term": "QLoRA", "lecture": 2, "definition": "ベースモデルの重みを4ビットなどに量子化してメモリを節約したうえで、LoRAで学習する手法。より大きなモデルを小さなGPUで扱える。本講座の第2…
[usage] RunUsage(cost=Decimal('0.0008113'), details={'text_prompt_tokens': 1196}, input_text_tokens=1196, input_tokens=1196, output_tokens=181, requests=2, tool_calls=2)
search_glossaryをLoRAとQLoRA用で呼んだ。

- 1つの質問での LLM 呼び出し回数（`requests`）：2回
- 追加したツールと、docstring に書いた説明：
  make_quiz(copilot作)
  指定した回の用語から1つを選び、確認問題と答えを返す。
 「第2回の確認問題を出して」のように、復習用の問題を求められたときに使う。

 [tool call]   make_quiz({'lecture': 2})
 [tool return] make_quiz -> {"question": "次の説明に当てはまる用語は何でしょう？\n事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラメータが少なく、学習結果…
 [usage] RunUsage(cost=Decimal('0.0006148'), details={'text_prompt_tokens': 916}, input_text_tokens=916, input_tokens=916, output_tokens=136, requests=2, tool_calls=1)

## 宿題

- 取り組んだレベル：基礎
- やったこと：
　1.「- 回答の最後に、関係する回（第N回）を示す。」の行をagent.pyのINSTRUCTIONSから削除した
　2. docstringの「1つだけ」を「まとめて」にかえた

- 結果：
　1. 回答の最後から「第2回」等の記述が消えた。
  2. [tool call]   search_glossary({'query': 'LoRA QLoRA'}) とtool callが当然1回になっていて、
[tool return] search_glossary -> [{"term": "LoRA", "lecture": 2, "definition": "事前学習済みの重みは固定したまま、重みの更新分を2つの小さな行列の積（低ランク行列）で表し、その小さな行列だけを学習するPEFT手法。学習するパラ…
　　　と[tool return]はLoRAのものだけが見えていたが、回答ではQLoRAに関する回答も含まれていた。
- 気づき・疑問：
　1.
  回答の末尾が「関係する回：第2回」だったり、「（関係する回：第2回）」だったり、「第2回</code>」だったり、
  第2回

　（参考：第2回では、LoRAの仕組みやQLoRAによるメモリ削減、量子化について詳しく学びます
　だったりとどうも一致しないようです。

  2. QLoRAの回答も含まれていたのはgeminiが外を見たのか何なのかよくわかっていません。
