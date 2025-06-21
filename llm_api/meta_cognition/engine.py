# /llm_api/meta_cognition/engine.py
# タイトル: Meta-Cognition Engine
# 役割: メタ認知システムの全体を統合し、思考プロセスの分析、改善、適応のサイクルを調整する。

import asyncio
import json
import logging
import re
import time
from collections import deque
from typing import Any, Deque, Dict, List, Optional, cast  # ★ 修正: castをインポート

from ..providers.base import LLMProvider
from .optimizer import CognitiveArchitectOptimizer
from .reflection import SelfReflectionEngine
from .types import CognitiveState, ThoughtTrace

logger = logging.getLogger(__name__)


class MetaCognitionEngine:
    """
    メタ認知エンジン - 全体統合システム。
    自己反省（SelfReflectionEngine）と認知アーキテクチャ最適化
    （CognitiveArchitectOptimizer）の各コンポーネントを協調させ、
    システム自身の思考プロセスを継続的に改善する。
    """

    def __init__(self, provider: LLMProvider):
        """
        MetaCognitionEngineを初期化します。

        Args:
            provider: LLMプロバイダーのインスタンス。
        """
        self.provider = provider
        self.reflection_engine = SelfReflectionEngine()
        self.architect_optimizer = CognitiveArchitectOptimizer()
        self.current_thought_trace: List[ThoughtTrace] = []
        self.meta_insights_history: Deque[Dict[str, Any]] = deque(maxlen=100)
        self.architecture_config: Dict[str, Any] = {}
        self.cognitive_state = CognitiveState.IDLE
        logger.info("🤔 Meta-Cognition Engine 初期化完了")

    async def begin_metacognitive_session(self, problem_context: str) -> Dict[str, Any]:
        """
        新しい問題解決のためのメタ認知セッションを開始します。

        Args:
            problem_context: 解決すべき問題のコンテキスト。

        Returns:
            セッションID、問題分析、初期戦略などを含むセッション情報。
        """
        logger.info(f"メタ認知セッション開始: {problem_context[:50]}...")
        self.current_thought_trace = []
        self.cognitive_state = CognitiveState.ANALYZING

        problem_analysis = await self._analyze_problem_nature(problem_context)
        cognitive_strategy = await self._select_cognitive_strategy(problem_analysis)

        return {
            "session_id": f"meta_{int(time.time())}",
            "problem_analysis": problem_analysis,
            "cognitive_strategy": cognitive_strategy,
            "meta_config": self.architecture_config,
        }

    async def record_thought_step(
        self,
        cognitive_state: CognitiveState,
        context: str,
        reasoning: str,
        confidence: float,
        outputs: Optional[List[str]] = None
    ) -> None:
        """
        思考プロセスの一つのステップを記録します。

        Args:
            cognitive_state: 現在の認知状態。
            context: このステップの入力コンテキスト。
            reasoning: 実行された推論の内容。
            confidence: このステップの確信度。
            outputs: このステップでの中間出力。
        """
        thought_trace = ThoughtTrace(
            timestamp=time.time(),
            cognitive_state=cognitive_state,
            input_context=context,
            reasoning_step=reasoning,
            confidence_level=confidence,
            resource_usage={"tokens": len(reasoning)},
            intermediate_outputs=outputs or [],
            decision_points=[]
        )
        self.current_thought_trace.append(thought_trace)
        self.reflection_engine.thought_history.append(thought_trace)
        self.cognitive_state = cognitive_state

    async def perform_metacognitive_reflection(self) -> Dict[str, Any]:
        """
        記録された思考トレースに対してメタ認知的な反省を実行し、
        アーキテクチャの最適化案を生成します。

        Returns:
            得られた洞察と最適化案を含む辞書。
        """
        logger.info("メタ認知的反省を実行中...")
        self.cognitive_state = CognitiveState.REFLECTING

        if len(self.current_thought_trace) < 2:
            logger.warning("反省するには思考トレースが短すぎます。")
            return {"insights": [], "optimizations": {}}

        # 自己反省エンジンで思考パターンを分析
        insights = await self.reflection_engine.analyze_thought_pattern(self.current_thought_trace)

        # 最適化エンジンで改善策を立案
        optimizations = await self.architect_optimizer.optimize_cognitive_architecture(insights)

        # 最適化案を現在のアーキテクチャ設定に適用
        self.architecture_config.update(optimizations)
        for insight in insights:
            self.meta_insights_history.append(vars(insight))

        reflection_result = {
            "insights": [vars(i) for i in insights],
            "optimizations": optimizations,
            "thought_trace_length": len(self.current_thought_trace),
        }

        logger.info(f"メタ認知的反省完了: {len(insights)}個の洞察、{len(optimizations)}個の最適化案を生成。")
        self.cognitive_state = CognitiveState.ADAPTING
        return reflection_result

    async def _analyze_problem_nature(self, problem: str) -> Dict[str, Any]:
        """LLMを用いて問題の性質を分析します。"""
        analysis_prompt = f"""
        以下の問題の性質を多角的に分析し、JSON形式で回答してください：
        - cognitive_complexity: 認知的複雑性 (1-10)
        - thinking_type: 必要な思考タイプ (例: logical, creative, strategic)
        - uncertainty_level: 不確実性の程度 (1-10)

        問題: "{problem}"
        """
        response = await self.provider.call(analysis_prompt, "")
        try:
            analysis_text = response.get('text', '{}')
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                # ★ 修正: json.loadsの結果を期待される型にキャスト
                return cast(Dict[str, Any], json.loads(json_match.group(0)))
            return {}
        except Exception:
            logger.warning("問題分析のJSON解析に失敗しました。")
            return {}

    async def _select_cognitive_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """問題分析に基づいて認知戦略を選択します。"""
        complexity = analysis.get("cognitive_complexity", 5)
        uncertainty = analysis.get("uncertainty_level", 5)

        strategy = {"primary_approach": "balanced", "monitoring_frequency": "medium"}

        if complexity >= 8 or uncertainty >= 8:
            strategy["primary_approach"] = "decomposition"
            strategy["monitoring_frequency"] = "high"
        elif analysis.get("thinking_type") == "creative":
            strategy["primary_approach"] = "divergent_convergent"

        return strategy