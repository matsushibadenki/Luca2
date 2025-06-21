# llm_api/autonomous_action/trigger.py
# タイトル: Emotion-based Action Trigger
# 役割: 感情分析結果（特に「興味」スコア）に基づいて、自律的な行動を開始するためのトリガー。

import logging
import time
from typing import Dict, Any, Optional

from ..emotion_core.types import EmotionAnalysisResult, ActionRequest, EmotionCategory

logger = logging.getLogger(__name__)

class EmotionActionTrigger:
    """
    感情スコアを監視し、特定の条件を満たした際に自律行動を誘発するクラス。
    """

    def __init__(self, interest_threshold: float = 0.85, cooldown_period: int = 180):
        """
        EmotionActionTriggerを初期化します。

        Args:
            interest_threshold (float): 行動をトリガーする「興味」スコアの閾値。
            cooldown_period (int): 一度トリガーされた後、再度トリガーされるまでの待機時間（秒）。
                                   連続的なトリガーを防ぐために使用。
        """
        self.interest_threshold = interest_threshold
        self.cooldown_period = cooldown_period
        self.last_triggered_time: float = 0.0
        logger.info(
            f"EmotionActionTrigger initialized. "
            f"Threshold: {self.interest_threshold}, Cooldown: {self.cooldown_period}s"
        )

    def check_and_trigger(
        self,
        analysis_result: EmotionAnalysisResult,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[ActionRequest]:
        """
        与えられた感情分析結果を評価し、行動をトリガーするかどうかを決定します。

        Args:
            analysis_result (EmotionAnalysisResult): EmotionMonitorからの分析結果。
            context (Optional[Dict[str, Any]]): 現在の対話やタスクのコンテキスト情報。

        Returns:
            Optional[ActionRequest]: 条件を満たした場合、ActionRequestオブジェクトを返す。
                                     そうでない場合はNoneを返す。
        """
        # 興味スコアが閾値を超えているか確認
        if analysis_result.interest_score < self.interest_threshold:
            return None

        # クールダウン期間が経過しているか確認
        current_time = time.time()
        if current_time < self.last_triggered_time + self.cooldown_period:
            logger.debug(f"興味スコア ({analysis_result.interest_score}) が閾値を超えましたが、"
                         f"クールダウン期間中のためトリガーを抑制します。")
            return None

        # 条件を満たした場合、行動要求を生成
        logger.info(f"興味スコア ({analysis_result.interest_score:.4f}) が閾値 "
                    f"({self.interest_threshold}) を超えました。自律行動をトリガーします。")

        self.last_triggered_time = current_time

        # 現状では「Web検索」アクションを要求する仕様とする
        action_request = ActionRequest(
            trigger_emotion=EmotionCategory.INTEREST,
            confidence=analysis_result.interest_score,
            context=context or {},
            requested_action="web_search"
        )

        return action_request