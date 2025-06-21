# /llm_api/autonomous_learning/manager.py
# タイトル: Continuous Learning Manager
# 役割: 継続的な自律学習セッションのスケジューリングと実行を管理する。

import asyncio
import logging
import time
from collections import deque
from typing import Any, Dict, List, Optional

from .crawler import AutonomousWebCrawler
from .renderer import PlaywrightRenderer

logger = logging.getLogger(__name__)


class ContinuousLearningManager:
    """継続学習マネージャー"""

    def __init__(self, provider: Any, web_search_func: Any, web_fetch_func: Any, renderer: Any):
        """
        継続学習マネージャーを初期化します。

        Args:
            provider: LLMプロバイダーのインスタンス。
            web_search_func: Web検索を実行する非同期関数。
            web_fetch_func: Webコンテンツを取得する非同期関数。
            renderer: Webページのレンダリングを担当するレンダラーのインスタンス。
        """
        self.crawler = AutonomousWebCrawler(provider, web_search_func, web_fetch_func, renderer)
        self.learning_schedule: Dict[str, int] = {}
        self.learning_sessions: deque[Dict[str, Any]] = deque(maxlen=100)
        logger.info("ContinuousLearningManagerが初期化されました。")

    async def setup_continuous_learning(
        self,
        learning_intervals: Optional[Dict[str, int]] = None,
        learning_goals: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        継続学習のスケジュールと目標を設定します。

        Args:
            learning_intervals: セッションタイプごとの学習時間（秒）の辞書。
            learning_goals: 学習目標のリスト。

        Returns:
            設定結果を含む辞書。
        """
        default_intervals = {
            "daily_exploration": 3600,      # 1時間
            "weekly_deep_dive": 7200,       # 2時間
            "monthly_review": 14400         # 4時間
        }
        self.learning_schedule = learning_intervals or default_intervals

        default_goals = [
            "最新のAI研究動向の把握",
            "新しい技術手法の学習",
            "関連分野の知識拡張",
            "実用的な応用例の発見"
        ]
        final_learning_goals = learning_goals or default_goals
        
        # クローラーの学習目標にも設定
        # self.crawler.set_learning_goals(final_learning_goals) # 将来的な実装

        logger.info(f"継続学習が設定されました。スケジュール: {self.learning_schedule}, 目標数: {len(final_learning_goals)}")

        return {
            "continuous_learning_setup": True,
            "learning_schedule": self.learning_schedule,
            "learning_goals": final_learning_goals,
            "next_session": "manual_trigger_required"
        }

    async def execute_scheduled_learning(self, session_type: str) -> Dict[str, Any]:
        """
        スケジュールされた学習セッションを実行します。

        Args:
            session_type: 実行するセッションのタイプ（例: "daily_exploration"）。

        Returns:
            学習セッションの結果を含む辞書。
        """
        if session_type not in self.learning_schedule:
            logger.error(f"未知のセッションタイプ: {session_type}")
            return {"error": f"Unknown session type: {session_type}"}

        duration = self.learning_schedule[session_type]
        logger.info(f"スケジュール学習セッション '{session_type}' を {duration}秒間実行します。")

        session_topics = await self._get_session_topics(session_type)

        # クローラーを使って自律学習を実行
        learning_result = await self.crawler.start_autonomous_learning(
            initial_topics=session_topics,
            session_duration=duration
        )

        # セッション結果を記録
        session_record = {
            "session_type": session_type,
            "timestamp": time.time(),
            "duration": duration,
            "result": learning_result,
            "session_id": learning_result.get("session_summary", {}).get("session_id")
        }
        self.learning_sessions.append(session_record)

        logger.info(f"セッション '{session_type}' が完了しました。")

        return {
            "session_completed": True,
            "session_type": session_type,
            "learning_result": learning_result,
            "session_id": session_record.get("session_id")
        }

    async def _get_session_topics(self, session_type: str) -> List[str]:
        """
        セッションタイプに応じた探索トピックのリストを取得します。

        Args:
            session_type: セッションのタイプ。

        Returns:
            トピックのリスト。
        """
        topic_sets = {
            "daily_exploration": [
                "AI news", "machine learning updates", "tech breakthroughs"
            ],
            "weekly_deep_dive": [
                "AI research papers", "cognitive science", "consciousness studies",
                "neural networks", "deep learning"
            ],
            "monthly_review": [
                "AI safety", "future of AI", "ethical AI", "AI governance",
                "technological singularity", "human-AI collaboration"
            ]
        }
        return topic_sets.get(session_type, ["artificial intelligence"])