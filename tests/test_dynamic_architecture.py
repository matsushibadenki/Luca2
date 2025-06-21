# /tests/test_dynamic_architecture.py
# タイトル: Dynamic Architecture System Tests
# 役割: SystemArchitectと適応コンポーネント群の動作を検証する。

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

# テスト対象のモジュール
from llm_api.dynamic_architecture.architect import SystemArchitect
from llm_api.dynamic_architecture.components import MetaAnalyzer, AdaptiveReasoner
from llm_api.dynamic_architecture.types import ArchitectureBlueprint, ComponentType
from llm_api.providers.base import LLMProvider

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock(return_value={"text": "mocked response"})
    return provider

@pytest.fixture
def system_architect(mock_provider: LLMProvider) -> SystemArchitect:
    """テスト用のSystemArchitectインスタンスを作成するフィクスチャ"""
    return SystemArchitect(mock_provider)

@pytest.mark.asyncio
class TestSystemArchitect:
    """SystemArchitectクラスのテストスイート"""

    async def test_initialization(self, system_architect: SystemArchitect):
        """アーキテクチャが正しく初期化されるかをテストする。"""
        init_result = await system_architect.initialize_adaptive_architecture({})
        
        assert init_result["architecture_initialized"] is True
        assert len(system_architect.components) > 0
        assert "meta_analyzer" in system_architect.components
        assert "adaptive_reasoner" in system_architect.components
        assert isinstance(system_architect.current_architecture, ArchitectureBlueprint)

    async def test_execute_adaptive_pipeline(self, system_architect: SystemArchitect):
        """
        適応型パイプラインが設計図通りにコンポーネントを順次実行するかをテストする。
        各コンポーネントのexecuteメソッドをモック化し、呼び出し順とデータの受け渡しを検証する。
        """
        await system_architect.initialize_adaptive_architecture({})

        # 各コンポーネントのexecuteメソッドをモック化
        mock_analyzer_result = {"analysis_results": {"complexity": 0.5}, "confidence": 0.9}
        mock_reasoner_result = {"reasoning_output": "reasoned solution", "confidence": 0.8}
        mock_synthesizer_result = {"synthesized_output": "synthesized solution", "confidence": 0.85}
        mock_validator_result = {"validation_feedback": "looks good", "confidence": 0.95}
        system_architect.components['meta_analyzer'].execute = AsyncMock(return_value=mock_analyzer_result)
        system_architect.components['adaptive_reasoner'].execute = AsyncMock(return_value=mock_reasoner_result)
        system_architect.components['synthesis_optimizer'].execute = AsyncMock(return_value=mock_synthesizer_result)
        system_architect.components['reflection_validator'].execute = AsyncMock(return_value=mock_validator_result)

        # パイプラインを実行
        initial_input = "initial problem"
        final_result = await system_architect.execute_adaptive_pipeline(initial_input, {})

        # 検証
        execution_flow = system_architect.current_architecture.execution_flow
        
        # 1. MetaAnalyzerが初期入力で呼び出される
        meta_analyzer_args = system_architect.components['meta_analyzer'].execute.await_args
        assert meta_analyzer_args.args[0] == initial_input
        assert meta_analyzer_args.args[1] == {}
        
        # 2. AdaptiveReasonerがAnalyzerの出力で呼び出される
        system_architect.components['adaptive_reasoner'].execute.assert_awaited_once_with(
            mock_analyzer_result, mock_analyzer_result
        )
        
        # 3. SynthesisOptimizerがReasonerの出力で呼び出される
        system_architect.components['synthesis_optimizer'].execute.assert_awaited_once_with(
             mock_reasoner_result, {**mock_analyzer_result, **mock_reasoner_result}
        )
        
        # 4. ReflectionValidatorがSynthesizerの出力で呼び出される
        system_architect.components['reflection_validator'].execute.assert_awaited_once_with(
            mock_synthesizer_result, {**mock_analyzer_result, **mock_reasoner_result, **mock_synthesizer_result}
        )
        
        # 最終的な出力がValidatorの出力と一致する
        assert final_result['final_output'] == mock_validator_result


@pytest.mark.asyncio
class TestAdaptiveComponents:
    async def test_meta_analyzer_execute(self):
        analyzer = MetaAnalyzer("test_analyzer")
        # 修正: インスタンスの辞書に直接モックを代入する
        mock_complexity_analyzer = AsyncMock(return_value={"score": 0.6})
        analyzer.analysis_strategies['complexity'] = mock_complexity_analyzer

        with patch.object(analyzer, '_generate_recommendations', new_callable=AsyncMock, return_value=["rec 1"]):
             result = await analyzer.execute("test data", {"requested_analyses": ["complexity"]})

        mock_complexity_analyzer.assert_awaited_once()
        assert "complexity" in result["analysis_results"]

    async def test_adaptive_reasoner_selects_mode_and_executes(self, mock_provider: LLMProvider):
        reasoner = AdaptiveReasoner("test_reasoner", mock_provider)
        context = {"analysis_results": {"uncertainty": {"epistemic_uncertainty": 0.7}}}
        
        # 修正: 同様に、インスタンスの辞書に直接モックを代入
        mock_creative = AsyncMock(return_value={"output": "creative", "confidence": 0.6})
        reasoner.reasoning_modes['creative'] = mock_creative
        
        result = await reasoner.execute("test data", context)

        assert result["mode_used"] == "creative"
        mock_creative.assert_awaited_once()
