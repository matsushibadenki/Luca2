# /tests/test_value_evolution.py
# タイトル: Homeostatic Motivation Engine Tests
# 役割: デジタルホメオスタシスに基づき、価値観を自律的に進化させる新エンジンの動作を検証する。

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch

from llm_api.providers.base import LLMProvider
from llm_api.value_evolution.evolution_engine import ValueEvolutionEngine
from llm_api.value_evolution.types import HomeostasisReport, IntellectualWellnessMetrics
from llm_api.meta_cognition.engine import MetaCognitionEngine

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.fixture
def mock_meta_cognition_engine() -> MetaCognitionEngine:
    """モックのMetaCognitionEngineを作成するフィクスチャ"""
    engine = MagicMock(spec=MetaCognitionEngine)
    engine.dialogue_history = []
    return engine

@pytest.fixture
def value_engine(
    mock_provider: LLMProvider,
    mock_meta_cognition_engine: MetaCognitionEngine
) -> ValueEvolutionEngine:
    """テスト用のValueEvolutionEngineインスタンスを作成するフィクスチャ"""
    # 新しいエンジンはMetaCognitionEngineに依存するため、モックを注入する
    return ValueEvolutionEngine(
        provider=mock_provider,
        meta_cognition_engine=mock_meta_cognition_engine
    )

class TestHomeostaticMotivationEngine:
    """新しいValueEvolutionEngine (HomeostaticMotivationEngine) のテストスイート"""

    def test_initialization(self, value_engine: ValueEvolutionEngine):
        """エンジンがデフォルトの価値観フレームワークで正しく初期化されるかをテストする。"""
        assert value_engine.ethical_framework is not None
        assert "logical_coherence" in value_engine.ethical_framework.values
        assert value_engine.homeostasis_monitor is not None

    @pytest.mark.asyncio
    @patch('llm_api.value_evolution.homeostasis_monitor.DigitalHomeostasisMonitor.assess_intellectual_wellness')
    async def test_maintain_homeostasis_in_stable_state(
        self,
        mock_assess_wellness: AsyncMock,
        value_engine: ValueEvolutionEngine,
        mock_provider: LLMProvider
    ):
        """知的健全性が安定している場合に、価値観が変更されないことをテストする。"""
        # 健全な状態のレポートをモック
        stable_report = HomeostasisReport(
            metrics=IntellectualWellnessMetrics(),
            overall_wellness=0.95,
            deviation_from_ideal=-0.05, # 逸脱なし
            recommended_focus=""
        )
        mock_assess_wellness.return_value = stable_report

        initial_values = value_engine.get_current_values().copy()
        result = await value_engine.maintain_homeostasis()

        assert result is not None
        assert result["status"] == "stable"
        # 価値観が変更されていないことを確認
        assert value_engine.get_current_values() == initial_values
        # LLMコールが発生していないことを確認
        mock_provider.call.assert_not_awaited()

    @pytest.mark.asyncio
    @patch('llm_api.value_evolution.homeostasis_monitor.DigitalHomeostasisMonitor.assess_intellectual_wellness')
    async def test_maintain_homeostasis_in_unstable_state(
        self,
        mock_assess_wellness: AsyncMock,
        value_engine: ValueEvolutionEngine,
        mock_provider: LLMProvider
    ):
        """知的健全性が不安定な場合に、自律的な価値観の調整が行われるかをテストする。"""
        # 不健全な状態のレポートをモック
        unstable_report = HomeostasisReport(
            metrics=IntellectualWellnessMetrics(logical_coherence=0.5),
            overall_wellness=0.7,
            deviation_from_ideal=0.2, # 逸脱あり
            recommended_focus="logical_coherence"
        )
        mock_assess_wellness.return_value = unstable_report

        # LLMが返す、調整後の新しい価値観をモック
        adjusted_values = value_engine.get_current_values().copy()
        adjusted_values["logical_coherence"] += 0.05
        mock_provider.call.return_value = {"text": json.dumps(adjusted_values)}

        initial_values = value_engine.get_current_values().copy()
        result = await value_engine.maintain_homeostasis()

        assert result is not None
        assert result["status"] == "adjusted"
        # LLMが1回呼び出されたことを確認
        mock_provider.call.assert_awaited_once()
        # 価値観が変更されたことを確認
        assert value_engine.get_current_values() != initial_values
        assert value_engine.get_current_values()["logical_coherence"] > initial_values["logical_coherence"]

    def test_receive_feedback_adjusts_adherence(self, value_engine: ValueEvolutionEngine):
        """外部からのフィードバックで、関連する価値の重みが微調整されるかをテストする。"""
        initial_adherence = value_engine.ethical_framework.values["user_feedback_adherence"]

        # ポジティブなフィードバック
        value_engine.receive_feedback({"type": "positive"})
        positive_adherence = value_engine.ethical_framework.values["user_feedback_adherence"]
        assert positive_adherence > initial_adherence

        # ネガティブなフィードバック
        value_engine.receive_feedback({"type": "negative"})
        final_adherence = value_engine.ethical_framework.values["user_feedback_adherence"]
        assert final_adherence < positive_adherence