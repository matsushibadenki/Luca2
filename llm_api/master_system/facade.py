# /llm_api/master_system/facade.py
import logging
from typing import Dict, Any, Optional, TYPE_CHECKING, cast

from ..providers.base import LLMProvider
from .types import MasterSystemConfig, IntegrationConfig

# ★ 修正: 循環参照を避けるためにTYPE_CHECKINGを使用
if TYPE_CHECKING:
    from .orchestrator import MasterIntegrationOrchestrator

logger = logging.getLogger(__name__)

class MetaIntelligence:
    """
    MetaIntelligence Master System
    This class acts as a facade, orchestrating the various sub-systems.
    """
    def __init__(self, primary_provider: LLMProvider, config: Optional[MasterSystemConfig] = None):
        # ★ 修正: Orchestratorのインポートを遅延させる
        from .orchestrator import MasterIntegrationOrchestrator

        self.primary_provider = primary_provider
        self.config = config or MasterSystemConfig()
        # IntegrationConfigにMasterSystemConfigを渡す
        integration_config = IntegrationConfig(master_system_config=self.config)
        self.orchestrator: MasterIntegrationOrchestrator = MasterIntegrationOrchestrator(primary_provider, integration_config)
        logger.info("🌟 MetaIntelligence Master System Facade インスタンス作成")

    async def initialize_master_system(self) -> Dict[str, Any]:
        """Initializes the entire master system via the orchestrator."""
        return cast(Dict[str, Any], await self.orchestrator.initialize_integrated_system()) # ★ castを追加

    async def solve_ultimate_problem(self, problem: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Solves an ultimate problem by delegating to the orchestrator."""
        return cast(Dict[str, Any], await self.orchestrator.solve_ultimate_integrated_problem(problem, context)) # ★ castを追加
    
    async def evolve_consciousness(self) -> Dict[str, Any]:
        """Evolves the system's consciousness by delegating to the orchestrator."""
        return cast(Dict[str, Any], await self.orchestrator.evolve_integrated_consciousness()) # ★ castを追加

    async def generate_ultimate_wisdom(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """Generates ultimate wisdom by delegating to the orchestrator."""
        return cast(Dict[str, Any], await self.orchestrator.generate_unified_wisdom(domain)) # ★ castを追加

    async def monitor_integration_health(self) -> Dict[str, Any]:
        """
        Provides a comprehensive health report of the integrated MetaIntelligence system
        by delegating to the orchestrator.
        """
        return cast(Dict[str, Any], await self.orchestrator.monitor_integration_health()) # ★ castを追加