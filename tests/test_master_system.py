# /tests/test_master_system.py
# タイトル: Emergent Intelligence and Master System Integration Tests
# 役割: 創発的知能プロセッサと、それを呼び出すマスター統合システムの協調動作を検証する。

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

from llm_api.master_system.types import IntegrationConfig
from llm_api.master_system.orchestrator import MasterIntegrationOrchestrator
from llm_api.providers.base import LLMProvider
from llm_api.emergent_intelligence.processor import EmergentIntelligenceProcessor, AgentOutput, EmergentInsight

@pytest.fixture
def mock_provider():
    """モックのLLMProviderを作成するpytestフィクスチャ"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.fixture
def orchestrator(mock_provider):
    """テスト用のOrchestratorインスタンスを作成するフィクスチャ"""
    config = IntegrationConfig(enable_all_systems=True)
    orchestrator_instance = MasterIntegrationOrchestrator(mock_provider, config)
    return orchestrator_instance

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator: MasterIntegrationOrchestrator):
    """オーケストレーターがInitializerを呼び出し、正常に初期化を完了できるかをテストする。"""
    with patch('llm_api.master_system.orchestrator.SystemInitializer') as mock_initializer_cls:
        mock_instance = mock_initializer_cls.return_value
        mock_instance.initialize_subsystems.return_value = {
            "emergent_intelligence": MagicMock(spec=EmergentIntelligenceProcessor)
        }
        mock_instance.get_subsystem_status.return_value = {"emergent_intelligence": {"initialized": True}}

        init_result = await orchestrator.initialize_integrated_system()
        
        assert orchestrator.integration_status == "operational"
        assert init_result["integration_status"] == "operational"
        assert "subsystem_status" in init_result

@pytest.mark.asyncio
async def test_solve_ultimate_problem_delegation(orchestrator: MasterIntegrationOrchestrator):
    """問題解決がSolver経由でEmergentIntelligenceProcessorに委譲されるかをテストする。"""
    await orchestrator.initialize_integrated_system()
    orchestrator.integration_status = "operational"

    mock_solution = {"emergent_solution": "Mocked emergent solution", "phi_score": 6.0}
    
    emergent_proc_mock = orchestrator.subsystems["emergent_intelligence"]
    emergent_proc_mock.synthesize_emergent_insight = AsyncMock(return_value=mock_solution)
    
    problem = "What is the nature of reality?"
    result = await orchestrator.solve_ultimate_integrated_problem(problem)
    
    emergent_proc_mock.synthesize_emergent_insight.assert_awaited_once_with(problem, None)
    assert result["integrated_solution"] == mock_solution["emergent_solution"]