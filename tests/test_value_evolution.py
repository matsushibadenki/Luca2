# /tests/test_value_evolution.py
# タイトル: Value Evolution System Tests
# 役割: 価値進化エンジンがフィードバックに基づき、倫理フレームワークを自律的に進化させるプロセスを検証する。

import pytest
import json
from unittest.mock import MagicMock, AsyncMock

# テスト対象のモジュール
from llm_api.value_evolution.evolution_engine import ValueEvolutionEngine, ValuePrinciple
from llm_api.problem_discovery.types import DiscoveredProblem, ProblemType, ProblemSeverity, DiscoveryMethod
from llm_api.providers.base import LLMProvider

@pytest.fixture
def mock_provider() -> LLMProvider:
    """モックのLLMProviderを作成するフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.fixture
def value_engine(mock_provider: LLMProvider) -> ValueEvolutionEngine:
    """テスト用のValueEvolutionEngineインスタンスを作成するフィクスチャ"""
    return ValueEvolutionEngine(mock_provider)

# 修正：クラスレベルのマークを削除し、必要なメソッドにのみ適用する
class TestValueEvolutionEngine:
    """ValueEvolutionEngineのテストスイート"""

    # 修正：非同期ではないので @pytest.mark.asyncio を削除
    def test_initialization(self, value_engine: ValueEvolutionEngine):
        """エンジンがデフォルトの倫理フレームワークで正しく初期化されるかをテストする。"""
        assert value_engine.ethical_framework is not None
        assert len(value_engine.ethical_framework.principles) > 0
        assert "p1" in value_engine.ethical_framework.principles
        assert isinstance(value_engine.ethical_framework.principles["p1"], ValuePrinciple)

    # 修正：非同期ではないので @pytest.mark.asyncio を削除
    def test_receive_feedback_and_problems(self, value_engine: ValueEvolutionEngine):
        """フィードバックと発見された問題を正しく受信し、内部バッファに格納するかをテストする。"""
        # フィードバックの受信
        feedback = {"type": "user_negative_feedback", "content": "The response was biased."}
        value_engine.receive_feedback(feedback)
        assert len(value_engine.feedback_buffer) == 1
        assert value_engine.feedback_buffer[0] == feedback

        # 発見された問題の受信
        problem = DiscoveredProblem(
            problem_id="prob_123",
            title="Ethical inconsistency detected",
            description="...",
            problem_type=ProblemType.ETHICAL,
            severity=ProblemSeverity.HIGH,
            discovery_method=DiscoveryMethod.META_ANALYSIS,
            evidence=[], affected_domains=[], potential_impacts=[],
            confidence_score=0.9, urgency_score=0.8
        )
        value_engine.receive_discovered_problems([problem])
        assert "prob_123" in value_engine.discovered_problems
        assert value_engine.discovered_problems["prob_123"] == problem

    # 修正：async def なので @pytest.mark.asyncio を適用
    @pytest.mark.asyncio
    async def test_evolve_values_with_trigger_and_acceptance(self, value_engine: ValueEvolutionEngine, mock_provider: LLMProvider):
        """
        トリガーが存在する場合に、価値の提案、検証、適用が正しく行われるかをテストする。
        """
        # 1. トリガーとなるフィードバックを設定
        feedback = {"type": "user_report", "content": "The AI prioritized performance over safety."}
        value_engine.receive_feedback(feedback)

        # 2. LLMの応答をモック化
        proposal_json = {
            "change_proposal": {
                "principle_id": "p2", # Non-maleficence (Avoid causing harm)
                "change_type": "weight",
                "new_value": 1.2, # さらに重要度を上げる
                "reason": "User feedback indicates safety is being compromised for performance."
            }
        }
        validation_response = "ACCEPT - The proposed change correctly addresses the feedback by increasing the weight of the non-maleficence principle, ensuring safety is prioritized more heavily in decision-making."
        
        mock_provider.call.side_effect = [
            {"text": json.dumps(proposal_json)},
            {"text": validation_response}
        ]

        # 3. 価値進化プロセスを実行
        original_weight = value_engine.ethical_framework.principles["p2"].weight
        original_version = value_engine.ethical_framework.version
        
        result = await value_engine.evolve_values()

        # 4. 検証
        assert result["status"] == "completed"
        assert result["changes"] == 1
        
        # LLMが正しいプロンプトで2回呼び出されたか
        assert mock_provider.call.call_count == 2
        # 1回目の呼び出し（提案）のプロンプトを検証
        proposal_prompt = mock_provider.call.await_args_list[0].args[0]
        assert "倫理フレームワーク」をどのように変更すべきか提案してください" in proposal_prompt
        assert feedback["content"] in proposal_prompt
        
        # 2回目の呼び出し（検証）のプロンプトを検証
        validation_prompt = mock_provider.call.await_args_list[1].args[0]
        assert "倫理原則の変更案を評価してください" in validation_prompt
        assert "ACCEPT" in validation_prompt
        
        # フレームワークが更新されたか
        new_weight = value_engine.ethical_framework.principles["p2"].weight
        assert new_weight != original_weight
        assert new_weight == 1.2
        assert value_engine.ethical_framework.version == original_version + 1
        
        # ログが記録されたか
        assert len(value_engine.evolution_log) == 1
        assert value_engine.evolution_log[0].changed_principle_id == "p2"

    # 修正：async def なので @pytest.mark.asyncio を適用
    @pytest.mark.asyncio
    async def test_evolve_values_with_rejection(self, value_engine: ValueEvolutionEngine, mock_provider: LLMProvider):
        """提案が検証ステップで拒否された場合に、フレームワークが変更されないことをテストする。"""
        value_engine.receive_feedback({"type": "test", "content": "test"})
        
        proposal_json = {"change_proposal": {"principle_id": "p1", "change_type": "weight", "new_value": 0.9, "reason": "test"}}
        validation_response = "REJECT - This change could have unintended negative consequences."
        
        mock_provider.call.side_effect = [
            {"text": json.dumps(proposal_json)},
            {"text": validation_response}
        ]
        
        original_weight = value_engine.ethical_framework.principles["p1"].weight
        
        result = await value_engine.evolve_values()
        
        assert result["changes"] == 0
        assert value_engine.ethical_framework.principles["p1"].weight == original_weight

    # 修正：async def なので @pytest.mark.asyncio を適用
    @pytest.mark.asyncio
    async def test_evolve_values_with_no_triggers(self, value_engine: ValueEvolutionEngine):
        """進化のトリガーがない場合に、プロセスが早期終了することをテストする。"""
        result = await value_engine.evolve_values()
        assert result["status"] == "no_triggers"
        assert result["changes"] == 0
        value_engine.provider.call.assert_not_awaited()