# /tests/test_problem_discovery.py
# タイトル: Problem Discovery System Tests
# 役割: 問題発見エンジンがデータソースから潜在的な問題を正しく発見・分析するプロセスを検証する。

import pytest
import json
from unittest.mock import MagicMock, AsyncMock, patch

# テスト対象のモジュール
from llm_api.problem_discovery.discovery_engine import ProblemDiscoveryEngine
from llm_api.problem_discovery.types import DiscoveredProblem, ProblemType, ProblemSeverity, DiscoveryMethod, DataPattern
import llm_api.problem_discovery.strategies.from_patterns as from_patterns
import llm_api.problem_discovery.utils as discovery_utils
from llm_api.providers.base import LLMProvider

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.fixture
def problem_discovery_engine(mock_provider: LLMProvider) -> ProblemDiscoveryEngine:
    """テスト用のProblemDiscoveryEngineインスタンスを作成するフィクスチャ"""
    return ProblemDiscoveryEngine(mock_provider)

@pytest.mark.asyncio
class TestProblemDiscoveryEngine:
    """ProblemDiscoveryEngineのテストスイート"""

    # 修正：各@patchデコレータに new_callable=AsyncMock を追加
    @patch('llm_api.problem_discovery.strategies.from_patterns.discover_from_patterns', new_callable=AsyncMock)
    @patch('llm_api.problem_discovery.utils.infer_causal_relationships', new_callable=AsyncMock)
    @patch('llm_api.problem_discovery.utils.detect_anomalies', new_callable=AsyncMock)
    @patch('llm_api.problem_discovery.utils.extract_data_patterns', new_callable=AsyncMock)
    async def test_discover_problems_orchestration(
        self,
        mock_extract_patterns,
        mock_detect_anomalies,
        mock_infer_causal,
        mock_discover_from_patterns,
        problem_discovery_engine: ProblemDiscoveryEngine
    ):
        """
        問題発見の主要なオーケストレーションフローが正しく実行されるかをテストする。
        - データ前処理（パターン抽出など）
        - 発見戦略の呼び出し
        - 結果の後処理（重複排除、優先順位付け）
        """
        # 1. モックの設定
        mock_patterns = [DataPattern(pattern_id="p1", description="desc", frequency=0.8, statistical_significance=0.9, anomaly_indicators=[], related_features=[])]
        mock_problem = DiscoveredProblem(
            problem_id="prob_1", title="Test Problem", description="A test problem",
            problem_type=ProblemType.SYSTEMIC, severity=ProblemSeverity.HIGH,
            discovery_method=DiscoveryMethod.PATTERN_ANALYSIS, evidence=[],
            affected_domains=[], potential_impacts=[], confidence_score=0.9, urgency_score=0.8
        )
        
        mock_extract_patterns.return_value = mock_patterns
        mock_detect_anomalies.return_value = []
        mock_infer_causal.return_value = []
        mock_discover_from_patterns.return_value = [mock_problem]

        # 2. 実行
        data_sources = [{"data": "some data"}]
        domain_context = {"domain_description": "test domain"}
        report = await problem_discovery_engine.discover_problems_from_data(data_sources, domain_context)

        # 3. 検証
        # データ前処理関数が呼び出されたか
        mock_extract_patterns.assert_awaited_once_with(problem_discovery_engine.provider, data_sources)
        mock_detect_anomalies.assert_awaited_once_with(problem_discovery_engine.provider, data_sources, mock_patterns)
        
        # 発見戦略が呼び出されたか
        mock_discover_from_patterns.assert_awaited_once_with(problem_discovery_engine.provider, mock_patterns, domain_context)
        
        # 結果がレポートに含まれているか
        assert report["problems_discovered"] == 1
        assert len(report["problem_details"]) == 1
        assert report["problem_details"][0]["id"] == "prob_1"
        assert "high_priority_problems" in report

    @pytest.mark.asyncio
    async def test_analyze_discovery_results(self, problem_discovery_engine: ProblemDiscoveryEngine, mock_provider: LLMProvider):
        """発見された問題群の最終分析がLLMコールを通じて行われるかをテストする。"""
        problems = [
            DiscoveredProblem(
                problem_id="p1", title="T1", description="D1", problem_type=ProblemType.ETHICAL,
                severity=ProblemSeverity.HIGH, discovery_method=DiscoveryMethod.PATTERN_ANALYSIS,
                evidence=[], affected_domains=[], potential_impacts=[], confidence_score=0.9, urgency_score=0.9
            )
        ]
        mock_provider.call.return_value = {"text": '{"overall_health": "Concerns in ethical alignment."}'}
        
        analysis = await problem_discovery_engine._analyze_discovery_results(problems)
        
        mock_provider.call.assert_awaited_once()
        prompt = mock_provider.call.await_args.args[0]
        assert "システム内で自律的に発見された潜在的な問題のリスト" in prompt
        assert "T1" in prompt
        assert analysis["overall_health"] == "Concerns in ethical alignment."

@pytest.mark.asyncio
class TestDiscoveryStrategies:
    """各発見戦略の単体テスト"""

    async def test_discover_from_patterns(self, mock_provider: LLMProvider):
        """データパターンから問題を発見する戦略をテストする。"""
        patterns = [
            DataPattern(pattern_id="p1", description="High error rate after deployment", frequency=0.9, statistical_significance=0.95, anomaly_indicators=[], related_features=[]),
            DataPattern(pattern_id="p2", description="Low significance pattern", frequency=0.1, statistical_significance=0.5, anomaly_indicators=[], related_features=[])
        ]
        
        problem_data_json = {
            "title": "Deployment causing high error rates", "description": "...",
            "problem_type": "operational", "severity": "high", "affected_domains": ["system"],
            "potential_impacts": ["user dissatisfaction"], "urgency": 0.9
        }
        mock_provider.call.return_value = {"text": json.dumps(problem_data_json)}

        # 戦略を実行
        discovered_problems = await from_patterns.discover_from_patterns(mock_provider, patterns, {})
        
        # 検証
        # 統計的優位性の高いパターン(p1)に対してのみLLMが呼ばれる
        mock_provider.call.assert_awaited_once()
        prompt = mock_provider.call.await_args.args[0]
        assert "High error rate after deployment" in prompt

        # 問題が正しく生成されたか
        assert len(discovered_problems) == 1
        problem = discovered_problems[0]
        assert problem.title == "Deployment causing high error rates"
        assert problem.severity == ProblemSeverity.HIGH
        assert problem.confidence_score == 0.95