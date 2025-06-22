# /llm_api/master_system/orchestrator.py
# タイトル: Master Integration Orchestrator (Refactored)
# 役割: 全システムの統合と協調を管理する。責務を専門クラスに委譲。

import logging
import asyncio
from typing import Any, Dict, List, Optional, cast, TYPE_CHECKING

from ..providers.base import LLMProvider
from .types import IntegrationConfig
from .initializer import SystemInitializer
from .solver import IntegratedProblemSolver
from .health import SystemHealthMonitor

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from ..core_engine.engine import MetaIntelligenceEngine
    from ..memory_consolidation.engine import ConsolidationEngine

class MasterIntegrationOrchestrator:
    """マスター統合オーケストレーター - 全システムの統合と協調を管理"""
    
    def __init__(self, primary_provider: LLMProvider, config: Optional[IntegrationConfig] = None):
        self.primary_provider = primary_provider
        self.config = config or IntegrationConfig()
        
        self.initializer = SystemInitializer(self.primary_provider, self.config)
        self.health_monitor = SystemHealthMonitor(self)
        
        self.subsystems: Dict[str, Any] = {}
        self.meta_intelligence_engine: Optional['MetaIntelligenceEngine'] = None
        self.solver: Optional[IntegratedProblemSolver] = None
        
        self.integration_status = "uninitialized"
        self._initialization_errors: List[str] = []
        self._health_metrics: Dict[str, Any] = {}
        logger.info("🌟 マスター統合オーケストレーター(リファクタリング版)インスタンス作成")

    async def initialize_integrated_system(self) -> Dict[str, Any]:
        """統合システムの完全初期化"""
        self.integration_status = "initializing"
        self._initialization_errors.clear()
        logger.info("🚀 統合システム完全初期化プロセスを呼び出します...")

        try:
            from ..core_engine.engine import MetaIntelligenceEngine
            self.subsystems = self.initializer.initialize_subsystems()
            
            consolidation_engine = self.subsystems.get("memory_consolidation")
            self.meta_intelligence_engine = MetaIntelligenceEngine(
                self.primary_provider, 
                base_model_kwargs={},
                consolidation_engine=consolidation_engine
            )
            
            self._setup_dependencies()
            
            emergent_intelligence_system = self.subsystems.get("emergent_intelligence")
            if emergent_intelligence_system:
                self.solver = IntegratedProblemSolver(emergent_intelligence_system)
            else:
                 self._initialization_errors.append("Emergent Intelligence system not found.")

            validation_result = self._validate_initialization()
            
            if validation_result["valid"]:
                self.integration_status = "operational"
            elif self.subsystems.get("emergent_intelligence"):
                 self.integration_status = "partially_operational"
            else:
                 self.integration_status = "degraded"

            logger.info(f"✨ 統合システム初期化完了! (状態: {self.integration_status})")
            return {
                "integration_status": self.integration_status,
                "subsystem_status": validation_result["subsystem_status"],
                "integration_harmony": validation_result.get("harmony_score", 0.0),
                "unified_capabilities": validation_result.get("capabilities", [])
            }

        except Exception as e:
            self.integration_status = "failed"
            logger.error(f"❌ 統合システム初期化エラー: {e}", exc_info=True)
            return {"integration_status": "failed", "error": str(e)}
            
    def _setup_dependencies(self) -> None:
        """サブシステム間の依存関係を設定"""
        if self.meta_intelligence_engine and self.meta_intelligence_engine.adaptive_pipeline.consolidation_engine:
            logger.info("ConsolidationEngineがAdaptivePipelineに注入されていることを確認しました。")

    def _validate_initialization(self) -> Dict[str, Any]:
        """初期化後の検証"""
        failed_components = [name for name, instance in self.subsystems.items() if instance is None]
        critical_failures = [c for c in ["emergent_intelligence"] if c in failed_components]
        is_valid = not critical_failures and self.solver is not None
        
        self._health_metrics = {
            "operational_subsystems": len(self.subsystems) - len(failed_components),
            "total_subsystems": len(self.subsystems),
            "failed_subsystems": len(failed_components),
        }
        
        return {
            "valid": is_valid,
            "subsystem_status": {name: (inst is not None) for name, inst in self.subsystems.items()}
        }
        
    async def solve_ultimate_integrated_problem(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """究極的問題解決プロセス"""
        if self.integration_status != "operational":
            return {"error": f"システムが運用状態ではありません: {self.integration_status}"}
        if not self.solver:
            return {"error": "問題解決システムが初期化されていません。"}
        
        logger.info(f"🎯 統合究極問題解決プロセスを開始: {problem[:100]}...")
        solution = await self.solver.solve_ultimate_problem(problem, context)
        
        if "memory_consolidation" in self.subsystems:
            session_data = {"prompt": problem, "solution": solution.get('integrated_solution')}
            asyncio.create_task(self.subsystems["memory_consolidation"].consolidate_memories(session_data))
            
        return solution

    async def monitor_integration_health(self) -> Dict[str, Any]:
        """
        統合システムの健全性を監視します。（SystemHealthMonitorに委譲）
        """
        return await self.health_monitor.check_health()

    async def evolve_integrated_consciousness(self) -> Dict[str, Any]:
        return {"status": "simulated", "new_level": 0.1}

    async def generate_unified_wisdom(self, domain: Optional[str] = None) -> Dict[str, Any]:
        return {"status": "simulated", "wisdom": "placeholder wisdom"}