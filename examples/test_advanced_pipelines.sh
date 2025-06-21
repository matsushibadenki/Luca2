#!/bin/bash
# /examples/test_advanced_pipelines.sh
# タイトル: Advanced Pipeline Test Script
# 役割: MetaIntelligence V2の高度な推論パイプライン（parallel, self_discover, speculative, quantum_inspired）を体系的にテストし、その動作を実証する。

echo "🧠⚛️ MetaIntelligence V2: Advanced Pipeline Demonstration"
echo "========================================================"
echo "This script will test the parallel, self_discover, speculative_thought, and quantum_inspired modes."
echo "Note: Some of these tests may take several minutes to complete, especially with larger models."
echo "--------------------------------------------------------"

# --- Parallel Mode Test ---
# 複数の思考戦略を並列実行し、最良の解を選択する能力をテストします。
# 哲学的でオープンエンドな問いは、多様な解釈を促し、このモードの長所を引き出します。
echo -e "\n🌐 [1/4] Testing Parallel Mode (Best-of-Breed Selection)..."
echo "Problem: What is the nature of happiness? Discuss from both philosophical and scientific perspectives."
python fetch_llm_v2.py ollama "What is the nature of happiness? Discuss from both philosophical and scientific perspectives." --mode parallel --model gemma3:latest --json

# --- Self-Discover Mode Test ---
# 問題解決のための思考戦略（atomic modules）を自律的に構築する能力をテストします。
# 明確な手順のない計画立案タスクは、このモードの能力を評価するのに適しています。
echo -e "\n🧭 [2/4] Testing Self-Discover Mode (Dynamic Strategy Construction)..."
echo "Problem: Create a step-by-step plan for someone to learn a new programming language effectively in 3 months."
python fetch_llm_v2.py ollama "Create a step-by-step plan for someone to learn a new programming language effectively in 3 months." --mode self_discover --model gemma3:latest --json

# --- Speculative Thought Mode Test ---
# 軽量モデルで高速に多様なアイデアを生成し、高機能モデルで統合・洗練させる能力をテストします。
# このデモでは、Ollamaの軽量モデル（phi3:miniなど）をドラフト生成に使うことを想定しています。
echo -e "\n💡 [3/4] Testing Speculative Thought Mode (Rapid Idea Generation)..."
echo "Problem: Generate three innovative solutions to address the problem of urban food deserts."
python fetch_llm_v2.py ollama "Generate three innovative solutions to address the problem of urban food deserts." --mode speculative_thought --model phi3:mini --json

# --- Quantum-Inspired Mode Test ---
# 多様な視点から仮説を生成（重ね合わせ）し、それを単一の包括的な解へと統合（収縮）する能力をテストします。
# 創造的で発散的な思考が求められるSF的な問いが適しています。
echo -e "\n🌌 [4/4] Testing Quantum-Inspired Mode (Holistic Synthesis)..."
echo "Problem: If humanity could share dreams, how would society, culture, and ethics change? Describe multiple scenarios."
python fetch_llm_v2.py ollama "If humanity could share dreams, how would society, culture, and ethics change? Describe multiple scenarios." --mode quantum_inspired --model gemma3:latest --json

echo -e "\n\n✅ Advanced Pipeline Demonstration Complete!"
echo "Review the JSON outputs to analyze the 'thought_process' of each pipeline."
