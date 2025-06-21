# /cli/handler.py
# Title: CLI Handler Facade (Final Dependency Injection Fix)
# 役割: CLIの初期化と、各専門クラスへの処理の委譲を行う。依存性注入を最終修正。

import logging
from typing import Any, Dict, Optional

from llm_api.providers import get_provider
from .request_processor import RequestProcessor
from llm_api.emotion_core.sae_manager import SAEManager
from llm_api.emotion_core.emotion_space import EmotionSpace
from llm_api.emotion_core.steering_manager import EmotionSteeringManager
from llm_api.emotion_core.monitoring_module import EmotionMonitor
from llm_api.autonomous_action.trigger import EmotionActionTrigger
from llm_api.autonomous_action.orchestrator import ActionOrchestrator
from llm_api.tool_integrations.web_search_tool import search as web_search_tool
from llm_api.value_evolution.evolution_engine import ValueEvolutionEngine
from llm_api.memory_consolidation.engine import ConsolidationEngine
from llm_api.rag.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

class MetaIntelligenceCLIHandler:
    """
    CLIのロジックを統合し、各専門クラスに処理を委譲するハンドラ。
    """
    def __init__(self):
        self.sae_manager: Optional[SAEManager] = None
        self.emotion_space: Optional[EmotionSpace] = None
        self.emotion_steering_manager: Optional[EmotionSteeringManager] = None
        self.emotion_monitor: Optional[EmotionMonitor] = None
        self.action_trigger: Optional[EmotionActionTrigger] = None
        self.action_orchestrator: Optional[ActionOrchestrator] = None
        self.value_evolution_engine: Optional[ValueEvolutionEngine] = None
        self.consolidation_engine: Optional[ConsolidationEngine] = None

        self._initialize_emotion_system()
        self._initialize_memory_system()

        self.request_processor = RequestProcessor(
            emotion_steering_manager=self.emotion_steering_manager,
            action_trigger=self.action_trigger,
            action_orchestrator=self.action_orchestrator,
            value_evolution_engine=self.value_evolution_engine,
            consolidation_engine=self.consolidation_engine
        )
        logger.debug("MetaIntelligenceCLIHandler (Facade) initialized.")

    def _initialize_emotion_system(self):
        """感情関連システムの初期化を試みる。失敗しても全体は停止しない。"""
        try:
            release = "gemma-scope-2b-pt-att"
            sae_id = "layer_9/width_16k/average_l0_34"
            emotion_map_path = "config/emotion_mapping.json"
            
            self.sae_manager = SAEManager(release=release, sae_id=sae_id)
            llm_engine_dummy = None
            self.emotion_space = EmotionSpace(llm_engine_dummy, self.sae_manager)
            if not self.emotion_space.load_mapping(emotion_map_path):
               logger.warning(f"感情マッピングファイル '{emotion_map_path}' が見つからないため、ダミーデータで初期化します。")
               self.emotion_space.emotion_to_features = {"interest": list(range(10)), "joy": list(range(10, 20))}
            
            self.emotion_steering_manager = EmotionSteeringManager(self.sae_manager, self.emotion_space)
            self.emotion_monitor = EmotionMonitor(self.sae_manager, self.emotion_space)
            self.action_trigger = EmotionActionTrigger()

            tools = {"web_search": web_search_tool}
            provider_for_orchestrator = get_provider("ollama", enhanced=False)
            self.action_orchestrator = ActionOrchestrator(provider_for_orchestrator, tools)
            self.value_evolution_engine = ValueEvolutionEngine(provider_for_orchestrator)
            logger.info("✅ 感情制御および自律行動システムが正常に初期化されました。")
        except Exception as e:
            logger.warning(f"⚠️ 感情システムの初期化中にエラーが発生しました。この機能は無効になります。理由: {e}")
            self.sae_manager = None
            self.emotion_space = None
            self.emotion_steering_manager = None
            self.emotion_monitor = None
            self.action_trigger = None
            self.action_orchestrator = None
            self.value_evolution_engine = None

    def _initialize_memory_system(self):
        """記憶関連システムの初期化"""
        try:
            provider_for_memory = get_provider("ollama", enhanced=False)
            # --- ▼▼▼ ここから修正 ▼▼▼ ---
            # KnowledgeBaseのインスタンスを生成し、正しい引数名 `knowledge_graph` で渡す
            kb_instance = KnowledgeBase()
            self.consolidation_engine = ConsolidationEngine(provider=provider_for_memory, knowledge_graph=kb_instance)
            # --- ▲▲▲ ここまで修正 ▲▲▲ ---
            logger.info("✅ 記憶統合システムが正常に初期化されました。")
        except Exception as e:
            logger.warning(f"⚠️ 記憶統合システムの初期化中にエラーが発生しました。この機能は無効になります。理由: {e}")
            self.consolidation_engine = None

    async def process_request(self, provider_name: str, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """リクエスト処理をRequestProcessorに委譲する。"""
        return await self.request_processor.process_request(provider_name, prompt, **kwargs)