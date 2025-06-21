# /llm_api/master_system/initializer.py
# タイトル: System Initializer
# 役割: マスター統合システムの全てのサブシステムを初期化する責務を持つ。

import logging
from typing import Any, Dict, Optional

from ..providers.base import LLMProvider
from ..meta_cognition.engine import MetaCognitionEngine
from ..dynamic_architecture.architect import SystemArchitect
from ..super_intelligence.integration_system import SuperIntelligenceOrchestrator
from ..value_evolution.evolution_engine import ValueEvolutionEngine
from ..problem_discovery.discovery_engine import ProblemDiscoveryEngine
from ..memory_consolidation.engine import ConsolidationEngine # 新規追加
from .types import IntegrationConfig

logger = logging.getLogger(__name__)

class SystemInitializer:
    """全てのサブシステムの初期化を担当するクラス。"""

    def __init__(self, primary_provider: LLMProvider, config: IntegrationConfig):
        self.primary_provider = primary_provider
        self.config = config

    def initialize_subsystems(self) -> Dict[str, Any]:
        """設定に基づいて全てのサブシステムをインスタンス化する。"""
        subsystems: Dict[str, Any] = {
            "meta_cognition": None,
            "dynamic_architect": None,
            "superintelligence": None,
            "value_evolution": None,
            "problem_discovery": None,
            "memory_consolidation": None, # 新規追加
        }
        
        if not self.config.enable_all_systems:
            logger.warning("全てのサブシステムが無効化されています。")
            return subsystems

        logger.info("全てのサブシステムの初期化を開始します...")
        
        subsystems["meta_cognition"] = MetaCognitionEngine(self.primary_provider)
        subsystems["dynamic_architect"] = SystemArchitect(self.primary_provider)
        subsystems["superintelligence"] = SuperIntelligenceOrchestrator(self.primary_provider)
        subsystems["value_evolution"] = ValueEvolutionEngine(self.primary_provider)
        subsystems["memory_consolidation"] = ConsolidationEngine(self.primary_provider) # 新規追加
        
        if self.config.problem_discovery_active:
            subsystems["problem_discovery"] = ProblemDiscoveryEngine(self.primary_provider)
        
        # AdaptivePipelineにConsolidationEngineを注入 (後続のコミットでAdaptivePipelineが初期化された後に設定される必要がある)
        # ここでは直接注入せず、Orchestratorで初期化後に設定する方針にする
        
        logger.info("全てのサブシステムの初期化が完了しました。")
        return subsystems

    def get_subsystem_status(self, subsystems: Dict[str, Optional[Any]]) -> Dict[str, Dict[str, bool]]:
        """初期化されたサブシステムのステータスを返す。"""
        return {
            name: {"initialized": instance is not None}
            for name, instance in subsystems.items()
        }