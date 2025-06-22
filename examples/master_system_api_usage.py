# examples/master_system_api_usage.py
# Title: Master System API Usage Example
# Role: Demonstrates how to use the MetaIntelligence Master Integration System directly in Python.

import asyncio
import logging
from llm_api.providers import get_provider
from llm_api.master_system.integration_orchestrator import MasterIntegrationOrchestrator, IntegrationConfig

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def use_master_system():
    """
    MetaIntelligenceの全機能を統合したマスターシステムを呼び出し、
    協調的な問題解決と集合的推論を実行するデモ。
    """
    logger.info("🌟 MetaIntelligence Master System Demo 開始")
    
    try:
        # 1. プライマリLLMプロバイダーを初期化
        # ここではOllamaを検証役として使用するが、OpenAIやClaudeなど高機能なモデルを推奨
        primary_provider = get_provider("ollama", enhanced=True)
        
        # 2. 統合オーケストレーターの作成と設定
        # 全てのサブシステム（メタ認知、価値進化など）を有効にする
        integration_config = IntegrationConfig(enable_all_systems=True)
        orchestrator = MasterIntegrationOrchestrator(primary_provider, integration_config)
        
        # 3. 統合システムの完全初期化
        logger.info("🚀 統合システムを初期化中... (全てのサブシステムを起動します)")
        init_result = await orchestrator.initialize_integrated_system()
        
        if not init_result.get("integration_status", "").startswith("🌟"):
            logger.error(f"統合システムの初期化に失敗しました: {init_result.get('error')}")
            return
            
        logger.info("✅ 統合システム初期化完了!")
        logger.info(f"システムハーモニー: {init_result.get('integration_harmony', 0):.2f}")
        logger.info(f"解放された統合能力の数: {len(init_result.get('unified_capabilities', []))}")

        # 4. 究極統合問題の解決
        # このプロセスでは、システムが内部で複数の機能とモデルを協調させて回答を生成します。
        problem_statement = "人工知能が人類の知性を超えたとき、人類はどのようにしてその価値と目的を維持し続けるべきか？"
        logger.info(f"\n🎯 究極問題解決を開始: 「{problem_statement}」")
        
        solution = await orchestrator.solve_ultimate_integrated_problem(
            problem_statement,
            context={"urgency": "high", "domain": "philosophy_and_ethics"},
            use_full_integration=True
        )
        
        logger.info("\n✨ 究極問題解決完了!")
        logger.info(f"✔️ 超越達成: {solution.get('transcendence_achieved', False)}")
        logger.info(f"🧠 自己進化発生: {solution.get('self_evolution_triggered', False)}")
        logger.info(f"🤝 価値整合スコア: {solution.get('value_alignment_score', 0):.2f}")
        
        print("\n" + "="*25 + " 統合解決策 " + "="*25)
        print(solution.get('integrated_solution', '解決策の生成に失敗しました。'))
        print("="*62)
        
        wisdom = solution.get('wisdom_distillation')
        if wisdom:
            print(f"\n💎 蒸留された知恵:\n{wisdom}")

    except Exception as e:
        logger.error(f"❌ デモ実行中に致命的なエラーが発生しました: {e}", exc_info=True)

if __name__ == "__main__":
    # Windowsでasyncioを使用する際のおまじない
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(use_master_system())