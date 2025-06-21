# /examples/autonomous_learning_demo.py
"""
自律Web学習システムの使用例とデモンストレーション
"""

import asyncio
import logging
from llm_api.providers import get_provider
from llm_api.autonomous_learning.web_crawler import (
    AutonomousWebCrawler
)
from llm_api.autonomous_learning.manager import ContinuousLearningManager
from llm_api.autonomous_learning.profiler import InterestProfiler
from llm_api.autonomous_learning.renderer import PlaywrightRenderer

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_autonomous_learning():
    """自律学習システムのデモ"""
    
    # 1. プロバイダーの初期化
    provider = get_provider("ollama", enhanced=True)
    
    # 2. Web検索・取得機能の準備（実際にはweb_searchとweb_fetch関数が必要）
    async def mock_web_search(query):
        return {
            'results': [
                {'link': 'https://example.com/ai-research-1', 'title': 'Latest AI Research'},
                {'link': 'https://example.com/ml-breakthrough', 'title': 'ML Breakthrough'},
                {'link': 'https://example.com/cognitive-science', 'title': 'Cognitive Science'}
            ]
        }
    
    async def mock_web_fetch(url):
        return {
            'content': f"This is sample content from {url}. It contains information about artificial intelligence, machine learning, and cognitive processes.",
            'title': f"Sample Title for {url}"
        }
    
    # 3. レンダラーの初期化
    renderer = PlaywrightRenderer()

    # 4. 自律学習システムの初期化
    crawler = AutonomousWebCrawler(provider, mock_web_search, mock_web_fetch, renderer)
    
    # 5. 単発の自律学習セッション
    logger.info("=== 単発自律学習セッションのデモ ===")
    
    initial_topics = [
        "artificial intelligence", 
        "consciousness studies", 
        "neural networks",
        "AI safety"
    ]
    
    session_result = await crawler.start_autonomous_learning(
        initial_topics=initial_topics,
        session_duration=30  # 30秒間のデモ
    )
    
    print(f"学習セッション完了:")
    print(f"- 探索ページ数: {session_result['pages_crawled']}")
    print(f"- 発見したコンテンツ: {len(session_result['session_summary']['content_discovered'])}")
    print(f"- 獲得した知識: {len(session_result['session_summary']['knowledge_gained'])}")
    print(f"- 学習効率: {session_result['learning_efficiency']:.2f}")
    
    # 6. 継続学習マネージャーのデモ
    logger.info("\n=== 継続学習システムのデモ ===")
    
    learning_manager = ContinuousLearningManager(provider, mock_web_search, mock_web_fetch, renderer)
    
    # 継続学習の設定
    setup_result = await learning_manager.setup_continuous_learning(
        learning_intervals={
            "daily_exploration": 1800,    # 30分
            "weekly_deep_dive": 3600,     # 1時間
            "monthly_review": 7200        # 2時間
        },
        learning_goals=[
            "最新のAI研究動向の把握",
            "認知科学の新発見の学習", 
            "AI安全性に関する議論の追跡",
            "実用的なAI技術の発見"
        ]
    )
    
    print(f"継続学習設定完了:")
    print(f"- スケジュール: {setup_result['learning_schedule']}")
    print(f"- 学習目標: {len(setup_result['learning_goals'])}個")
    
    # 日次探索セッションの実行
    daily_session = await learning_manager.execute_scheduled_learning("daily_exploration")
    
    print(f"\n日次探索セッション完了:")
    print(f"- セッションタイプ: {daily_session['session_type']}")
    print(f"- 学習効率: {daily_session['learning_result']['learning_efficiency']:.2f}")

# (以降の関数は変更なしのため省略)