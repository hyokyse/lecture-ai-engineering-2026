# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：
  search_materials
  glossary_search_glossary
- STEP 2 の [tool call]：
  glossary_search_glossary({'query': '3レベル'})
- STEP 3 の [tool call]：
  fetch_fetch({'url': 'https://modelcontextprotocol.io/'})
- STEP 4 の [tool call]：
  aws_aws___search_documentation({'search_phrase': 'Amazon S3 versioning overview'})
- 気づき・疑問：
　step4のtool callは
aws _ aws___search_documentation
│   │ │
│   │ └─ AWSサーバーが提供する元のツール名
│   └── サーバー名とツール名を分ける区切り
└────── mcp_servers.jsonで設定したサーバー名

　aws___search_documentationの3つの_はaws側でtool名がaws___search_documentationとして定義されているかららしい(by Quri)

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎
- やったこと：mcp_server.pyにget_lecture_summaryを追加
- 結果：mcp_server.pyのみの変更でツールの追加ができている。
- 気づき・疑問：
  server側で知らぬ間にtoolが加えられていた場合、agent側で狙っていたtoolが選択されないことで不都合が生じないのかと思いました(出力をtraceすれば気づくことはできるでしょうが)。

　pytestで過去のlectureで使ったmake_quizでエラーが出てしまいましたが、その時に何をしたのか思い出して後ほどトラシューします。
