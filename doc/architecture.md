# **MetaIntelligence V2 アーキテクチャ (v1.0)**

MetaIntelligence V2は、モジュール化されたコンポーネントが協調して動作する洗練されたアーキテクチャを採用しています。これにより、柔軟性、拡張性、そして高いパフォーマンスを両立しています。

## **1\. 全体像：リクエストから応答までの流れ**

ユーザーからのリクエストは、以下のコンポーネントを順に通過します。

graph TD  
    A\[ユーザー\] \--\> B(fetch\_llm\_v2.py);  
    B \--\> C{cli/main.py};  
    C \--\> D\[cli/handler.py\];  
    D \--\> E\[cli/request\_processor.py\];  
    E \--\> F{V2モードか？};  
    F \-- Yes \--\> G\[llm\_api/core\_engine/engine.py\];  
    F \-- No \--\> H\[標準プロバイダー呼び出し\];  
    G \--\> I{推論パイプライン選択};  
    I \--\> J\[各Pipelineクラス\];  
    J \--\> K\[LLM API\];  
    H \--\> K;  
    K \--\> L\[応答\];  
    L \--\> A;

    subgraph CLI Layer  
        B  
        C  
        D  
        E  
    end

    subgraph Core Logic Layer  
        F  
        G  
        H  
        I  
        J  
    end

1. **CLIレイヤー (fetch\_llm\_v2.py, cli/)**:  
   * ユーザーからのコマンドライン引数を解釈します (argparse)。  
   * 管理コマンド（--health-checkなど）を処理します。  
   * 主要な処理をRequestProcessorに委譲します。  
2. **リクエスト処理 (cli/request\_processor.py)**:  
   * \--mode引数に基づき、**V2拡張モード**で処理するか、**標準モード**にフォールバックするかを決定します。  
   * V2拡張モードが選択された場合、MetaIntelligenceEngineを呼び出します。  
3. **コアエンジン (llm\_api/core\_engine/)**:  
   * **engine.py (MetaIntelligenceEngine)**: システムの中核。modeに応じて、5つの主要な**推論パイプライン**（adaptive, parallelなど）の中から適切なものを選択し、処理を委譲します。  
   * **各パイプライン (pipelines/)**: それぞれが特有の思考戦略を実装しています。例えば、AdaptivePipelineはさらに下位のコンポーネントを協調させます。  
   * **AdaptivePipelineの内部動作**:  
     1. **analyzer.py**: プロンプトの言語と複雑性を分析します。  
     2. **logic/self\_adjustment.py**: 推論ループを管理します。  
        * **reasoner.py**: 複雑性レジーム（低・中・高）に応じて、具体的なreasoning\_strategiesを呼び出します。  
        * 最初の推論結果が不十分な場合、レジームを動的に調整し、再度推論を実行します（自己調整）。  
     3. **logic/finalization.py**: 最終的な解を改善し、レスポンスを整形します。  
     4. **learner.py**: 推論結果を学習し、将来の実行に活かします。

## **2\. 主要な推論パイプライン**

MetaIntelligenceEngineは、以下の5つのパイプラインをオーケストレーションします。

* **Adaptive Pipeline**: 最も基本的なパイプライン。複雑性分析、自己調整ループ、学習機能を通じて、単一の思考スレッドで効率的に問題を解決します。他のモードの基盤としても機能します。  
* **Parallel Pipeline**: 3つの複雑性レジーム（低・中・高）でAdaptivePipelineを並列実行し、得られた複数の回答の中から、LLM自身に最も優れたものを選択させます。品質を最大化したい場合に有効です。  
* **Quantum-Inspired Pipeline**: 1つの問題に対し、多様なペルソナ（例：「楽観的な未来学者」「懐疑的なリスクアナリスト」）の視点から複数の仮説を並列生成（重ね合わせ）し、それらを最終的に1つの包括的な回答に統合（収縮）します。発想の飛躍や深い洞察が求められるタスクに適しています。  
* **Speculative Thought Pipeline**: ローカルの軽量モデル（Ollamaなど）で高速に複数の思考ドラフトを生成し、それをクラウドの高機能モデル（GPT-4oなど）が検証・統合するハイブリッドなパイプラインです。コストと品質のバランスを取りつつ、高速な思考を実現します。  
* **Self-Discover Pipeline**: 問題の性質をLLMに分析させ、予め定義された原子的な思考モジュール（DECOMPOSE, CRITICAL\_THINKINGなど）を動的に組み合わせることで、その場に応じたオーダーメイドの解決戦略を自律的に構築します。未知の問題や、定型的な解決策がないタスクに有効です。

## **3\. 補足的なシステム**

* **RAG (検索拡張生成)**: llm\_api/rag/manager.pyが中心となり、プロンプトの内容に応じてWikipediaやローカルファイルを検索し、得られた情報をコンテキストとしてプロンプトに付加します。これにより、LLMが最新の情報や専門知識に基づいた回答を生成できるようになります。  
* **感情コア & 自律行動 (実験的)**: llm\_api/emotion\_core/とllm\_api/autonomous\_action/が連携します。SAE（スパース・オートエンコーダ）を用いてLLMの内部状態から「興味」などの感情を分析し、閾値を超えた場合に自律的にWeb検索などの追加アクションを実行します。

このモジュール化された設計により、MetaIntelligence V2は、特定の機能を追加・修正することが容易でありながら、全体として一貫性のある高度な推論能力を発揮することができます。