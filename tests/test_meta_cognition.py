# /tests/test_meta_cognition.py
# タイトル: Meta-Cognition System Tests
# 役割: メタ認知エンジンの思考追跡、自己反省、アーキテクチャ最適化の連携を検証する。

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# テスト対象のモジュール
from llm_api.meta_cognition.engine import MetaCognitionEngine
from llm_api.meta_cognition.types import CognitiveState, ThoughtTrace, MetaCognitiveInsight
from llm_api.providers.base import LLMProvider

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock(return_value={"text": '{"cognitive_complexity": 5}'})
    return provider

@pytest.fixture
def meta_cognition_engine(mock_provider: LLMProvider) -> MetaCognitionEngine:
    """テスト用のMetaCognitionEngineインスタンスを作成するフィクスチャ"""
    return MetaCognitionEngine(mock_provider)

@pytest.mark.asyncio
class TestMetaCognitionEngine:
    """MetaCognitionEngineのテストスイート"""

    async def test_begin_metacognitive_session(self, meta_cognition_engine: MetaCognitionEngine):
        """メタ認知セッションが正しく開始されるかをテストする。"""
        problem_context = "How to solve world hunger?"
        session_info = await meta_cognition_engine.begin_metacognitive_session(problem_context)

        assert "session_id" in session_info
        assert "problem_analysis" in session_info
        assert "cognitive_strategy" in session_info
        assert meta_cognition_engine.cognitive_state == CognitiveState.ANALYZING
        assert len(meta_cognition_engine.current_thought_trace) == 0

    async def test_record_thought_step(self, meta_cognition_engine: MetaCognitionEngine):
        """思考ステップが正しく記録されるかをテストする。"""
        assert len(meta_cognition_engine.current_thought_trace) == 0

        await meta_cognition_engine.record_thought_step(
            cognitive_state=CognitiveState.REASONING,
            context="Initial analysis",
            reasoning="Decomposing the problem",
            confidence=0.8
        )

        assert len(meta_cognition_engine.current_thought_trace) == 1
        trace = meta_cognition_engine.current_thought_trace[0]
        assert isinstance(trace, ThoughtTrace)
        assert trace.cognitive_state == CognitiveState.REASONING
        assert trace.confidence_level == 0.8
        assert meta_cognition_engine.cognitive_state == CognitiveState.REASONING

    async def test_perform_metacognitive_reflection(self, meta_cognition_engine: MetaCognitionEngine):
        """メタ認知的反省が、自己反省エンジンと最適化エンジンを正しく呼び出すかをテストする。"""

        mock_insights = [
            MetaCognitiveInsight(
                insight_type="efficiency_issue",
                description="Too many steps",
                confidence=0.7,
                suggested_improvement="Use shortcuts",
                impact_assessment={}
            )
        ]
        mock_optimizations = {"reasoning_shortcuts_enabled": True}

        with patch.object(meta_cognition_engine.reflection_engine, 'analyze_thought_pattern', new_callable=AsyncMock, return_value=mock_insights) as mock_analyze, \
             patch.object(meta_cognition_engine.architect_optimizer, 'optimize_cognitive_architecture', new_callable=AsyncMock, return_value=mock_optimizations) as mock_optimize:

            await meta_cognition_engine.record_thought_step(CognitiveState.ANALYZING, "ctx1", "rsn1", 0.9)
            await meta_cognition_engine.record_thought_step(CognitiveState.REASONING, "ctx2", "rsn2", 0.8)

            result = await meta_cognition_engine.perform_metacognitive_reflection()

            mock_analyze.assert_awaited_once_with(meta_cognition_engine.current_thought_trace)
            mock_optimize.assert_awaited_once_with(mock_insights)

            assert result["optimizations"]["reasoning_shortcuts_enabled"] is True
            assert meta_cognition_engine.architecture_config["reasoning_shortcuts_enabled"] is True

    async def test_reflection_with_insufficient_trace(self, meta_cognition_engine: MetaCognitionEngine):
        """思考トレースが不十分な場合、反省が実行されないことをテストする。"""
        await meta_cognition_engine.record_thought_step(CognitiveState.ANALYZING, "ctx1", "rsn1", 0.9)

        result = await meta_cognition_engine.perform_metacognitive_reflection()

        assert result["insights"] == []
        assert result["optimizations"] == {}
