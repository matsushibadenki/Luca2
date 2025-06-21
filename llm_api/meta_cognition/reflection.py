# /llm_api/meta_cognition/reflection.py
# タイトル: Self-Reflection Engine
# 役割: 自身の思考プロセス（ThoughtTrace）を分析し、メタ認知的な洞察を生成する。

import asyncio  # ★ 修正: asyncioをインポート
import logging
from collections import defaultdict, deque
from typing import Any, Deque, Dict, List, Optional

from .types import MetaCognitiveInsight, ThoughtTrace

logger = logging.getLogger(__name__)


class SelfReflectionEngine:
    """
    自己反省エンジン。
    過去の思考パターンを分析し、効率、品質、バイアスなどを評価して
    自己改善のためのメタ認知的な洞察を生成する。
    """

    def __init__(self) -> None:
        """自己反省エンジンを初期化します。"""
        self.thought_history: Deque[ThoughtTrace] = deque(maxlen=1000)
        self.pattern_library: Dict[str, Any] = {}
        self.effectiveness_metrics: Dict[str, float] = defaultdict(float)
        logger.info("SelfReflectionEngineが初期化されました。")

    async def analyze_thought_pattern(
        self,
        thought_traces: List[ThoughtTrace]
    ) -> List[MetaCognitiveInsight]:
        """
        与えられた思考の軌跡を分析し、改善に繋がる洞察のリストを返します。

        Args:
            thought_traces: 分析対象の一連の思考トレース。

        Returns:
            メタ認知的な洞察（MetaCognitiveInsight）のリスト。
        """
        if not thought_traces:
            return []

        insights: List[MetaCognitiveInsight] = []

        # 認知効率、推論品質、バイアス、創発パターンの分析を並行して実行
        analysis_tasks = [
            self._analyze_cognitive_efficiency(thought_traces),
            self._analyze_reasoning_quality(thought_traces),
            self._detect_cognitive_biases(thought_traces),
            self._discover_emergent_patterns(thought_traces),
        ]
        results = await asyncio.gather(*analysis_tasks)

        for result in results:
            if isinstance(result, list):
                insights.extend(result)
            elif result:
                insights.append(result)

        return insights

    async def _analyze_cognitive_efficiency(
        self,
        traces: List[ThoughtTrace]
    ) -> Optional[MetaCognitiveInsight]:
        """思考の効率を分析します。"""
        if len(traces) < 3:
            return None

        total_steps = sum(len(trace.intermediate_outputs) for trace in traces)
        avg_steps = total_steps / len(traces)
        avg_confidence = sum(trace.confidence_level for trace in traces) / len(traces)

        if avg_steps > 8 and avg_confidence < 0.75:
            return MetaCognitiveInsight(
                insight_type="efficiency_issue",
                description=f"思考ステップが多い({avg_steps:.1f}ステップ)割に確信度が低い({avg_confidence:.2f})傾向があります。",
                confidence=0.8,
                suggested_improvement="推論の初期段階で目標をより明確化するか、より直接的なアプローチを検討してください。",
                impact_assessment={"efficiency": 0.4, "accuracy": 0.1},
            )
        return None

    async def _analyze_reasoning_quality(
        self,
        traces: List[ThoughtTrace]
    ) -> Optional[MetaCognitiveInsight]:
        """推論の品質（一貫性など）を分析します。"""
        consistency = self._measure_reasoning_consistency(traces)
        if consistency < 0.6:
            return MetaCognitiveInsight(
                insight_type="reasoning_inconsistency",
                description=f"異なる思考ステップ間での推論の一貫性が低いようです（スコア: {consistency:.2f}）。",
                confidence=0.75,
                suggested_improvement="推論の核となる前提条件を明確化し、思考の論理的構造を再確認してください。",
                impact_assessment={"consistency": 0.5, "reliability": 0.3},
            )
        return None

    async def _detect_cognitive_biases(
        self,
        traces: List[ThoughtTrace]
    ) -> List[MetaCognitiveInsight]:
        """思考プロセスにおける認知バイアスの兆候を検出します。"""
        # (この実装は簡略化されています)
        insights: List[MetaCognitiveInsight] = []
        # ここに確証バイアスやアンカリングバイアスなどを検出するロジックを実装
        return insights

    async def _discover_emergent_patterns(
        self,
        traces: List[ThoughtTrace]
    ) -> List[MetaCognitiveInsight]:
        """効果的な思考パターンなど、創発的なパターンを発見します。"""
        # (この実装は簡略化されています)
        insights: List[MetaCognitiveInsight] = []
        # ここに思考状態の遷移などを分析し、成功に繋がりやすいパターンを発見するロジックを実装
        return insights

    def _measure_reasoning_consistency(self, traces: List[ThoughtTrace]) -> float:
        """推論の一貫性を測定します。（簡易版）"""
        if not traces or len(traces) < 2:
            return 1.0
        
        confidences = [trace.confidence_level for trace in traces]
        # 急激な確信度の低下がないかをチェック
        drops = sum(1 for i in range(len(confidences) - 1) if confidences[i] > 0.8 and confidences[i+1] < 0.5)
        
        return 1.0 - (drops / len(traces))