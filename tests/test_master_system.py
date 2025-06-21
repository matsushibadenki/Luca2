# /tests/test_master_system.py
# タイトル: Master Integration System Tests (Final Fix)
# 役割: リファクタリングされたマスター統合オーケストレーターと各専門クラスの協調動作を検証する。

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock

# 修正: typesからIntegrationConfigをインポート
from llm_api.master_system.types import IntegrationConfig
from llm_api.master_system.orchestrator import MasterIntegrationOrchestrator
from llm_api.providers.base import LLMProvider
from llm_api.super_intelligence.integration_system import SuperIntelligenceOrchestrator
# 修正: initializerのインポートパスを絶対パスに修正
from llm_api.master_system.initializer import SystemInitializer
from llm_api.master_system.solver import IntegratedProblemSolver


@pytest.fixture
def mock_provider():
    """モックのLLMProviderを作成するpytestフィクスチャ"""
    return MagicMock(spec=LLMProvider)

@pytest.fixture
def orchestrator(mock_provider):
    """リファクタリングされたテスト用のOrchestratorインスタンスを作成するフィクスチャ"""
    config = IntegrationConfig(enable_all_systems=True)
    # DI（依存性注入）対応のコンストラクタを使用
    orchestrator_instance = MasterIntegrationOrchestrator(mock_provider, config)
    return orchestrator_instance

@pytest.mark.asyncio
async def test_orchestrator_initialization(orchestrator: MasterIntegrationOrchestrator):
    """オーケストレーターがInitializerを呼び出し、正常に初期化を完了できるかをテストする。"""
    # SystemInitializerのモック化
    with patch('llm_api.master_system.orchestrator.SystemInitializer') as mock_initializer_cls:
        mock_instance = mock_initializer_cls.return_value
        mock_instance.initialize_subsystems.return_value = {
            "superintelligence": MagicMock(spec=SuperIntelligenceOrchestrator)
        }
        mock_instance.get_subsystem_status.return_value = {"superintelligence": {"initialized": True}}

        init_result = await orchestrator.initialize_integrated_system()

        assert orchestrator.integration_status == "operational"
        assert init_result["integration_status"].startswith("🌟 FULLY INTEGRATED")
        assert "subsystem_status" in init_result

@pytest.mark.asyncio
async def test_solve_ultimate_problem_delegation(orchestrator: MasterIntegrationOrchestrator):
    """問題解決がSolver経由でSuperIntelligenceOrchestratorに委譲されるかをテストする。"""
    # まずシステムを初期化
    await orchestrator.initialize_integrated_system()
    orchestrator.integration_status = "operational"

    mock_solution = {"integrated_solution": "Mocked transcendent solution", "transcendence_achieved": True}
    
    # orchestratorに設定されているsuperintelligenceインスタンスのメソッドをモック化
    # このテストは初期化が成功している前提なので、solverとsuperintelligenceは存在する
    superintelligence_mock = orchestrator.subsystems["superintelligence"]
    superintelligence_mock.transcendent_problem_solving = AsyncMock(return_value=mock_solution)
    
    problem = "What is the nature of reality?"
    result = await orchestrator.solve_ultimate_integrated_problem(problem)
    
    superintelligence_mock.transcendent_problem_solving.assert_awaited_once_with(problem, None)
    assert result["integrated_solution"] == mock_solution["integrated_solution"]

@pytest.mark.asyncio
async def test_system_initialization_failure(mock_provider):
    """サブシステムの初期化失敗時にエラーが正しくハンドリングされるかをテストする。"""
    config = IntegrationConfig(enable_all_systems=True)
    orchestrator_with_fail = MasterIntegrationOrchestrator(mock_provider, config)

    with patch('llm_api.master_system.orchestrator.SystemInitializer') as mock_initializer_cls:
        mock_instance = mock_initializer_cls.return_value
        mock_instance.initialize_subsystems.side_effect = ValueError("Init failed")
        
        result = await orchestrator_with_fail.initialize_integrated_system()
        
        assert orchestrator_with_fail.integration_status == "failed"
        assert result["integration_status"] == "❌ INTEGRATION FAILED"
        assert "Init failed" in result["error"]