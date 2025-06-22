# **MetaIntelligence プロジェクトファイル構造 (v1.0)**

Luca/  
├── .env.example                \# 環境変数のテンプレートファイル  
├── README.md                     \# プロジェクト全体の概要、特徴、セットアップ方法  
├── requirements.txt              \# Pythonの依存ライブラリリスト  
├── mypy.ini                      \# 静的型チェックのためのmypy設定ファイル  
├── fetch\_llm\_v2.py               \# CLI（コマンドラインインターフェース）のメインエントリーポイント  
├── fetch\_llm\_autonomous.py       \# 自律学習システム用のCLIエントリーポイント  
├── quick\_test\_v2.py              \# 環境と基本機能の動作を素早く確認する診断スクリプト  
├── test\_all\_v2\_providers.py      \# 全てのプロバイダーとV2モードを対象とした包括的なテストスクリプト  
├── build\_emotion\_space.py        \# 感情マッピングファイル(emotion\_mapping.json)を生成するスクリプト  
│  
├── llm\_api/                      \# AIのコアロジックを格納するメインパッケージ  
│   ├── \_\_init\_\_.py               \# パッケージの初期化、ロギング設定  
│   ├── config.py                 \# APIキーやモデル設定など、プロジェクト全体の設定を集中管理  
│   │  
│   ├── providers/                \# 各LLMプロバイダーとの連携を担当  
│   │   ├── \_\_init\_\_.py           \# プロバイダーの動的読み込みとファクトリー機能  
│   │   ├── base.py               \# 全プロバイダーの抽象基底クラス  
│   │   ├── claude.py             \# (以下、各プロバイダーに対応するファイル)  
│   │   ├── enhanced\_claude\_v2.py  
│   │   ├── gemini.py  
│   │   ├── enhanced\_gemini\_v2.py  
│   │   ├── huggingface.py  
│   │   ├── enhanced\_huggingface\_v2.py  
│   │   ├── llamacpp.py  
│   │   ├── enhanced\_llamacpp\_v2.py  
│   │   ├── ollama.py  
│   │   ├── enhanced\_ollama\_v2.py  
│   │   ├── openai.py  
│   │   └── enhanced\_openai\_v2.py  
│   │  
│   ├── core\_engine/              \# 思考の品質と効率を最適化する推論の中核システム  
│   │   ├── \_\_init\_\_.py           \# コアエンジンパッケージの初期化  
│   │   ├── engine.py             \# 全パイプラインを管理し、モードに応じて処理を振り分けるエンジン  
│   │   ├── analyzer.py           \# プロンプトの複雑性を多言語対応で分析  
│   │   ├── learner.py            \# 過去の実行結果からプロンプトの複雑性を学習  
│   │   ├── reasoner.py           \# 複雑性レジームに応じて推論戦略を呼び分けるディスパッチャ  
│   │   ├── enums.py              \# 複雑性レジームのEnum定義  
│   │   │  
│   │   ├── pipelines/            \# 各推論モードの具体的な処理フローを実装したパイプライン群  
│   │   │   ├── \_\_init\_\_.py  
│   │   │   ├── adaptive.py       \# 適応型推論のオーケストレーター  
│   │   │   ├── parallel.py       \# 並列推論パイプライン  
│   │   │   ├── quantum\_inspired.py \# 量子インスパイアード推論パイプライン  
│   │   │   ├── self\_discover.py  \# 自己発見パイプライン  
│   │   │   └── speculative.py    \# 投機的思考パイプライン  
│   │   │  
│   │   ├── logic/                \# パイプラインから分割された具体的なロジック  
│   │   │   ├── \_\_init\_\_.py  
│   │   │   ├── self\_adjustment.py  \# 自己評価とレジーム再調整のロジック  
│   │   │   └── finalization.py     \# 解の改善と学習記録のロジック  
│   │   │  
│   │   └── reasoning\_strategies/ \# 各複雑性レベルに応じた推論戦略  
│   │       ├── \_\_init\_\_.py  
│   │       ├── low\_complexity.py  
│   │       ├── medium\_complexity.py  
│   │       └── high\_complexity.py  
│   │  
│   ├── rag/                      \# RAG（検索拡張生成）機能  
│   │   ├── \_\_init\_\_.py  
│   │   ├── knowledge\_base.py  
│   │   ├── manager.py  
│   │   └── retriever.py  
│   │  
│   ├── reasoning/                \# 自己発見に基づく推論戦略モジュール (self\_discoverモードで使用)  
│   │   ├── \_\_init\_\_.py  
│   │   ├── atomic\_modules.py     \# 思考の基本単位  
│   │   ├── strategy\_hub.py       \# 思考戦略を管理・選択  
│   │   └── strategy\_hub.json     \# 思考戦略のデータストア  
│   │  
│   ├── emotion\_core/             \# (実験的) 感情分析・制御の中核機能  
│   │   ├── \_\_init\_\_.py  
│   │   ├── emotion\_space.py  
│   │   ├── monitoring\_module.py  
│   │   ├── sae\_manager.py  
│   │   ├── steering\_manager.py  
│   │   └── types.py  
│   │  
│   ├── autonomous\_action/        \# (実験的) 感情トリガーによる自律行動  
│   │   ├── \_\_init\_\_.py  
│   │   ├── orchestrator.py  
│   │   └── trigger.py  
│   │  
│   └── tool\_integrations/        \# Web検索などの外部ツール連携  
│       └── web\_search\_tool.py  
│  
├── cli/                          \# コマンドラインインターフェース関連のコード  
│   ├── \_\_init\_\_.py  
│   ├── handler.py                \# CLIの初期化と処理委譲を行うファサード  
│   ├── main.py                   \# argparseによる引数解析とメイン処理の呼び出し  
│   ├── request\_processor.py      \# V2拡張/標準フォールバックなどのリクエスト処理ロジック  
│   ├── command\_runner.py         \# \--health-checkなどの管理コマンド実行  
│   └── utils.py                  \# CLIで使われるヘルパー関数  
│  
├── doc/                          \# プロジェクトのドキュメント  
│   ├── architecture.md           \# システムアーキテクチャ解説  
│   ├── cli\_guide.md              \# CLIの詳細な使用方法  
│   ├── installation\_guide.md     \# インストールガイド  
│   └── roadmap.md                \# プロジェクトのロードマップ  
│  
└── tests/                        \# 単体テストおよび結合テストコード  
    ├── \_\_init\_\_.py  
    ├── test\_cli.py  
    ├── test\_core\_engine.py  
    └── test\_providers.py  
