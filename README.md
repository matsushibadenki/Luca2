# **Luca \-MetaIntelligence V2-: 適応型推論エンジン**

MetaIntelligence V2は、LLM（大規模言語モデル）が直面する根本的な課題、特にApple Researchの論文「[The Illusion of Thinking](https://ml-site.cdn-apple.com/papers/the-illusion-of-thinking.pdf)」で指摘された「思考の錯覚」を克服するために設計された、次世代のAI推論フレームワークです。

単なるLLMのラッパーではなく、問題の複雑性を自律的に分析し、最適な思考戦略を動的に選択することで、推論の品質と効率を最大化します。

名称の、LUCA (Last Universal Common Ancestor)は、約30億年から40億年前に存在したと考えられている、地球上のすべての生命の共通の祖先となる単細胞生物が由来です。

## **🌟 主な特徴**

* **適応型複雑性分析**: プロンプトの複雑性を自動で分析し、「低」「中」「高」の3つのレジームに分類。不要な思考（Overthinking）や思考の崩壊（Collapse）を防ぎます。  
* **マルチ推論パイプライン**: 5つの異なる思考パイプラインを搭載し、タスクに応じて最適なものを選択します。  
  * adaptive: 複雑性を自動分析し、リアルタイムで推論戦略を調整する標準モード。  
  * parallel: 複数の戦略を並列実行し、最も優れた解を選択する最高品質モード。  
  * quantum\_inspired: 多様な視点から仮説を生成・統合し、深い洞察を導き出すモード。  
  * speculative\_thought: 軽量モデルで思考のドラフトを生成し、高機能モデルで検証・統合する高速思考モード。  
  * self\_discover: 問題の性質から、原子的な思考モジュールを動的に組み合わせ、未知の問題解決戦略を自律的に構築するモード。  
* **マルチプロバイダー対応**: OpenAI, Anthropic (Claude), Google (Gemini), Ollama, Llama.cpp, HuggingFaceなど、主要なLLMプロバイダーに単一のインターフェースで対応します。  
* **RAG (検索拡張生成)**: Wikipediaやローカルファイルからの情報検索で、回答の精度と鮮度を向上させます。  
* **自己改善学習**: 過去の推論結果やユーザーからのフィードバックを学習し、同じような問題に対して、次回からより最適な戦略を選択します。  
* **（実験的）感情コアシステム**: SAE（スパース・オートエンコーダ）を利用してLLMの内部状態から感情を分析し、自律的なアクション（Web検索など）をトリガーします。

## **🔧 インストールと設定**

### **1\. 依存関係のインストール**

\# リポジトリをクローン  
git clone https://github.com/matsushibadenki/Luca.git  
cd Luca

\# 依存関係をインストール  
pip install \-r requirements.txt

\# spaCyモデルをダウンロード (推奨)  
python \-m spacy download en\_core\_web\_sm  
python \-m spacy download ja\_core\_news\_sm

### **2\. 環境変数の設定**

プロジェクトルートに.envファイルを作成し、APIキーなどを設定します。

\# .envファイル

\# 使用するAPIキー (Ollamaのみの場合は不要)  
OPENAI\_API\_KEY="sk-..."  
CLAUDE\_API\_KEY="sk-ant-..."  
GEMINI\_API\_KEY="AIza..."  
HF\_TOKEN="hf\_..."  
SERPAPI\_API\_KEY="..." \# Web検索機能を使用する場合

\# Ollamaのデフォルトモデル  
OLLAMA\_DEFAULT\_MODEL="gemma3:latest"

\# Llama.cppサーバーの設定  
LLAMACPP\_API\_BASE\_URL="http://localhost:8000"

\# ログレベル (DEBUG, INFO, WARNING, ERROR)  
LOG\_LEVEL="INFO"

### **3\. Ollamaのセットアップ (ローカルモデル使用時)**

\# Ollamaをインストール (macOS/Linux)  
curl \-fsSL https://ollama.ai/install.sh | sh

\# Ollamaサーバーを起動  
ollama serve

\# 推奨モデルをダウンロード  
ollama pull gemma3:latest  
ollama pull llama3.1:latest  
ollama pull phi3:mini

## **🚀 クイックスタート**

### **1\. システムの動作確認**

\# 基本的な診断スクリプトを実行  
python quick\_test\_v2.py

\# 利用可能なプロバイダーとモードを確認  
python fetch\_llm\_v2.py \--system-status

\# Ollamaの接続とモデルを確認  
python fetch\_llm\_v2.py ollama \--health-check

### **2\. 基本的なCLIの使用例**

\# 適応モードで質問 (推奨される基本モード)  
python fetch\_llm\_v2.py ollama "自己認識とは何か、簡潔に教えてください。" \--mode adaptive

\# 複雑な問題を高分解能モードで解決  
python fetch\_llm\_v2.py openai "持続可能な都市交通システムの設計案を考えてください。" \--mode decomposed

\# Wikipediaの知識を使って回答  
python fetch\_llm\_v2.py claude "ジェイムズ・ウェッブ宇宙望遠鏡の最新の発見について教えて。" \--mode balanced \--wikipedia

\# JSON形式で詳細な思考プロセスを確認  
python fetch\_llm\_v2.py ollama "AI倫理の主要な課題を3つ挙げてください。" \--mode balanced \--json

### **3\. 高度なパイプラインのテスト**

より高度な思考パイプライン（parallel, self\_discoverなど）の動作を体系的に確認するには、専用のテストスクリプトを実行します。

\# 各高度パイプラインのデモンストレーションを実行  
bash examples/test\_advanced\_pipelines.sh

## **📖 詳細ガイド**

より詳しい使い方やアーキテクチャについては、docディレクトリ内のドキュメントを参照してください。

* doc/directory\_structure.md: プロジェクト全体のファイル構成  
* doc/cli\_guide.md: 全てのCLIコマンドとオプションの詳細なガイド  
* doc/architecture.md: システムアーキテクチャの解説  
* doc/roadmap.md: プロジェクトの今後の展望