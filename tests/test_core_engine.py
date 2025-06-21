# /tests/test_core_engine.py
# タイトル: MetaIntelligence Core Engine Tests
# 役割: MetaIntelligenceの中核エンジンとその関連コンポーネントの動作を検証する。

import pytest
from unittest.mock import MagicMock, patch, call, AsyncMock # 修正: AsyncMockをインポート
import asyncio


# --- Test target modules (Refactored) ---
from llm_api.core_engine.engine import MetaIntelligenceEngine
from llm_api.core_engine.enums import ComplexityRegime
from llm_api.core_engine.analyzer import AdaptiveComplexityAnalyzer
from llm_api.core_engine.reasoner import EnhancedReasoningEngine
from llm_api.providers.base import LLMProvider, EnhancedLLMProvider, ProviderCapability

# --- Test Fixtures ---

@pytest.fixture
def mock_standard_provider():
    """A pytest fixture that creates a mock LLMProvider (standard)."""
    provider = MagicMock(spec=LLMProvider)
    # 修正: 非同期メソッドにはAsyncMockを使用する
    provider.call = AsyncMock()
    provider.provider_name = "mock_standard_provider"
    provider.get_capabilities.return_value = {
        ProviderCapability.STANDARD_CALL: True
    }
    return provider

@pytest.fixture
def mock_enhanced_provider(mock_standard_provider):
    """A pytest fixture that creates a mock EnhancedLLMProvider."""
    enhanced_provider = MagicMock(spec=EnhancedLLMProvider)
    enhanced_provider.standard_provider = mock_standard_provider
    enhanced_provider.provider_name = mock_standard_provider.provider_name
    # 修正: 非同期メソッドにはAsyncMockを使用する
    enhanced_provider.call = AsyncMock()
    enhanced_provider.get_capabilities.return_value = {
        ProviderCapability.STANDARD_CALL: True,
        ProviderCapability.ENHANCED_CALL: True,
    }
    return enhanced_provider


@pytest.fixture
def engine_system(mock_enhanced_provider):
    """
    A pytest fixture that creates an instance of MetaIntelligenceEngine
    with a mock enhanced provider.
    """
    return MetaIntelligenceEngine(provider=mock_enhanced_provider, base_model_kwargs={})

# --- Test Cases ---

class TestAdaptiveComplexityAnalyzer:
    """Tests for the AdaptiveComplexityAnalyzer class."""

    @pytest.mark.asyncio
    async def test_analyze_complexity(self):
        """Test the prompt complexity analysis."""
        analyzer = AdaptiveComplexityAnalyzer()
        with patch.object(analyzer, '_keyword_based_analysis', return_value=10):
            with patch.object(analyzer, '_get_spacy_model', return_value=None):
                score, regime = analyzer.analyze_complexity("Simple question")
                assert regime == ComplexityRegime.LOW
                assert score == 10

        with patch.object(analyzer, '_keyword_based_analysis', return_value=50):
            with patch.object(analyzer, '_get_spacy_model', return_value=None):
                score, regime = analyzer.analyze_complexity("Medium question")
                assert regime == ComplexityRegime.MEDIUM
                assert score == 50

        with patch.object(analyzer, '_keyword_based_analysis', return_value=80):
            with patch.object(analyzer, '_get_spacy_model', return_value=None):
                score, regime = analyzer.analyze_complexity("Very complex question")
                assert regime == ComplexityRegime.HIGH
                assert score == 80

    @pytest.mark.asyncio
    async def test_nlp_enhanced_analysis_fallback(self):
        """Test that NLP analysis falls back to keyword-based if spacy fails."""
        analyzer = AdaptiveComplexityAnalyzer()
        with patch('spacy.load', side_effect=OSError("Spacy model not found")):
            with patch.object(analyzer, '_keyword_based_analysis', return_value=50) as mock_keyword:
                score, regime = analyzer.analyze_complexity("This is a test.")
                mock_keyword.assert_called_once()
                assert regime == ComplexityRegime.MEDIUM
                assert score == 50


class TestMetaIntelligenceEngine:
    """Tests for the main MetaIntelligenceEngine class and its dispatch logic."""

    @pytest.mark.asyncio
    async def test_solve_problem_mode_dispatch(self, engine_system):
        """Test that solve_problem correctly dispatches to the right pipeline based on the mode."""
        prompt = "test prompt"

        # AdaptivePipeline
        with patch.object(engine_system.adaptive_pipeline, 'execute') as mock_adaptive:
            mock_adaptive.return_value = {"success": True, "final_solution": "Adaptive"}
            await engine_system.solve_problem(prompt, mode='adaptive')
            mock_adaptive.assert_called_once()

        # ParallelPipeline
        with patch.object(engine_system.parallel_pipeline, 'execute') as mock_parallel:
            mock_parallel.return_value = {"success": True, "final_solution": "Parallel"}
            await engine_system.solve_problem(prompt, mode='parallel')
            mock_parallel.assert_called_once()

        # QuantumInspiredPipeline
        with patch.object(engine_system.quantum_pipeline, 'execute') as mock_quantum:
            mock_quantum.return_value = {"success": True, "final_solution": "Quantum"}
            await engine_system.solve_problem(prompt, mode='quantum_inspired')
            mock_quantum.assert_called_once()

        # SpeculativePipeline
        with patch.object(engine_system.speculative_pipeline, 'execute') as mock_speculative:
            mock_speculative.return_value = {"success": True, "final_solution": "Speculative"}
            await engine_system.solve_problem(prompt, mode='speculative_thought')
            mock_speculative.assert_called_once()


class TestEnhancedReasoningEngine:
    """Tests for the core reasoning logic in EnhancedReasoningEngine."""

    @pytest.mark.asyncio
    async def test_high_complexity_decomposes_and_integrates(self, mock_standard_provider):
        """Verify the high complexity flow: decompose -> solve sub-problems -> integrate."""
        engine = EnhancedReasoningEngine(provider=mock_standard_provider, base_model_kwargs={})
        complex_prompt = "Explain quantum computing and its impact on cryptography."

        mock_standard_provider.call.side_effect = [
            {"text": '{"sub_problems": ["Explain qubits.", "Explain Shor\'s algorithm."]}', "error": None},
            {"text": "Qubits are quantum bits.", "error": None},
            {"text": "Shor's algorithm breaks RSA.", "error": None},
            {"text": "Integrated: Qubits and Shor's algorithm.", "error": None},
            {"text": "Final polished answer.", "error": None}
        ]

        result_dict = await engine.execute_reasoning(
            complex_prompt,
            system_prompt="",
            complexity_score=90.0,
            regime=ComplexityRegime.HIGH
        )

        assert result_dict['solution'] == "Final polished answer."
        assert not result_dict['error']
        assert result_dict['complexity_regime'] == ComplexityRegime.HIGH.value
        assert "decomposition" in result_dict
        assert "sub_solutions" in result_dict

        assert mock_standard_provider.call.call_count == 5
        actual_calls = mock_standard_provider.call.await_args_list # 修正: .call -> .await_args_list
        assert "Decompose the following complex problem" in actual_calls[0].kwargs['prompt'] # 修正: args[0] -> kwargs['prompt']
        assert "Explain qubits." in actual_calls[1].kwargs['prompt']
        assert "Explain Shor's algorithm." in actual_calls[2].kwargs['prompt']
        assert "Integrate the 'New Information' into the 'Previous Integrated Result'" in actual_calls[3].kwargs['prompt']
        assert "Polish the following integrated text" in actual_calls[4].kwargs['prompt']