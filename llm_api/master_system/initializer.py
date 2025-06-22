# /llm_api/master_system/initializer.py
# タイトル: System Initializer
# 役割: マスター統合システムの全てのサブシステムを初期化する責務を持つ。

import logging
from typing import Any, Dict, Optional

from ..providers.base import LLMProvider
from ..meta_cognition.engine import MetaCognitionEngine
from ..dynamic_architecture.architect import SystemArchitect
from ..emergent_intelligence.processor import EmergentIntelligenceProcessor
from ..value_evolution.evolution_engine import ValueEvolutionEngine
from ..problem_discovery.discovery_engine import ProblemDiscoveryEngine
from ..memory_consolidation.engine import ConsolidationEngine
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
            "emergent_intelligence": None,
            "value_evolution": None,
            "problem_discovery": None,
            "memory_consolidation": None,
        }
        
        if not self.config.enable_all_systems:
            logger.warning("全てのサブシステムが無効化されています。")
            return subsystems

        logger.info("全てのサブシステムの初期化を開始します...")
        
        # 依存関係のため、MetaCognitionEngine を先に初期化
        meta_cognition_engine = MetaCognitionEngine(self.primary_provider)
        subsystems["meta_cognition"] = meta_cognition_engine
        
        subsystems["dynamic_architect"] = SystemArchitect(self.primary_provider)
        subsystems["emergent_intelligence"] = EmergentIntelligenceProcessor(self.primary_provider)
        
        # ValueEvolutionEngine に meta_cognition_engine を注入
        value_evolution_engine = ValueEvolutionEngine(
            self.primary_provider, 
            meta_cognition_engine=meta_cognition_engine
        )
        subsystems["value_evolution"] = value_evolution_engine
        
        subsystems["memory_consolidation"] = ConsolidationEngine(self.primary_provider)
        
        if self.config.problem_discovery_active:
            problem_discovery_engine = ProblemDiscoveryEngine(self.primary_provider)
            subsystems["problem_discovery"] = problem_discovery_engine
        
        logger.info("全てのサブシステムの初期化が完了しました。")
        return subsystems

    def get_subsystem_status(self, subsystems: Dict[str, Optional[Any]]) -> Dict[str, Dict[str, bool]]:
        """初期化されたサブシステムのステータスを返す。"""
        return {
            name: {"initialized": instance is not None}
            for name, instance in subsystems.items()
        }