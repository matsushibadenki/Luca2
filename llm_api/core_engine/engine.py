# /llm_api/core_engine/engine.py
# タイトル: MetaIntelligence Core Engine (Refactored)
# 役割: 各推論パイプラインを管理し、問題のモードに応じて処理を振り分ける中核エンジン。

import logging
from typing import Any, Dict, Optional

from .enums import ComplexityRegime
from .pipelines import (
    AdaptivePipeline,
    ParallelPipeline,
    QuantumInspiredPipeline,
    SpeculativePipeline,
    SelfDiscoverPipeline,
)
from ..providers.base import LLMProvider
# --- ▼▼▼ ここから修正 ▼▼▼ ---
from ..memory_consolidation.engine import ConsolidationEngine
# --- ▲▲▲ ここまで修正 ▲▲▲ ---

logger = logging.getLogger(__name__)

class MetaIntelligenceEngine:
    """MetaIntelligence V2 メインエンジン"""

    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any], consolidation_engine: Optional[ConsolidationEngine] = None):
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        logger.info("MetaIntelligence Engine V2を初期化中")
        if not provider:
            raise ValueError("有効なLLMプロバイダーがMetaIntelligenceEngineに必要です。")

        self.provider = provider
        self.base_model_kwargs = base_model_kwargs

        # パイプライン初期化
        self.adaptive_pipeline = AdaptivePipeline(provider, base_model_kwargs)
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        if consolidation_engine:
            self.adaptive_pipeline.set_consolidation_engine(consolidation_engine)
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        self.parallel_pipeline = ParallelPipeline(
            provider, base_model_kwargs, shared_adaptive_pipeline=self.adaptive_pipeline
        )
        self.quantum_pipeline = QuantumInspiredPipeline(provider, base_model_kwargs)
        self.speculative_pipeline = SpeculativePipeline(provider, base_model_kwargs)
        self.self_discover_pipeline = SelfDiscoverPipeline(provider, base_model_kwargs)

        logger.info("MetaIntelligence Engine V2の初期化完了 - 全パイプライン利用可能")

    async def solve_problem(
        self,
        prompt: str,
        system_prompt: str = "",
        force_regime: Optional[ComplexityRegime] = None,
        use_rag: bool = False,
        knowledge_base_path: Optional[str] = None,
        use_wikipedia: bool = False,
        real_time_adjustment: bool = True,
        mode: str = "adaptive",
    ) -> Dict[str, Any]:
        """問題解決のメインエントリーポイント"""
        logger.info(
            f"問題解決プロセス開始（MetaIntelligence V2, モード: {mode}）: {prompt[:80]}..."
        )
        try:
            if mode in ["adaptive", "efficient", "balanced", "decomposed", "edge", "paper_optimized"]:
                logger.info("適応型パイプラインを選択")
                return await self.adaptive_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, force_regime=force_regime,
                    use_rag=use_rag, knowledge_base_path=knowledge_base_path, use_wikipedia=use_wikipedia,
                    real_time_adjustment=real_time_adjustment, mode=mode,
                )
            elif mode == "parallel":
                logger.info("並列パイプラインを選択")
                return await self.parallel_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, use_rag=use_rag,
                    knowledge_base_path=knowledge_base_path, use_wikipedia=use_wikipedia,
                )
            elif mode == "quantum_inspired":
                logger.info("量子インスパイアードパイプラインを選択")
                return await self.quantum_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, use_rag=use_rag,
                    knowledge_base_path=knowledge_base_path, use_wikipedia=use_wikipedia,
                )
            elif mode == "speculative_thought":
                logger.info("投機的思考パイプラインを選択")
                return await self.speculative_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, use_rag=use_rag,
                    knowledge_base_path=knowledge_base_path, use_wikipedia=use_wikipedia,
                )
            elif mode == "self_discover":
                logger.info("自己発見パイプラインを選択")
                return await self.self_discover_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, use_rag=use_rag,
                    knowledge_base_path=knowledge_base_path, use_wikipedia=use_wikipedia,
                )
            else:
                logger.warning(f"モード '{mode}' はV2専用ではないか未知のモードです。適応型パイプラインにフォールバックします。")
                return await self.adaptive_pipeline.execute(
                    prompt=prompt, system_prompt=system_prompt, mode="adaptive"
                )
        except Exception as e:
            logger.error(f"パイプライン実行中にエラー（モード: {mode}）: {e}", exc_info=True)
            return {"success": False, "error": str(e)}