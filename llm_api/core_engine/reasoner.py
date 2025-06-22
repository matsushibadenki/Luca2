# /llm_api/core_engine/reasoner.py
# タイトル: Enhanced Reasoning Engine
# 役割: 複雑性レジームに基づいて、低・中・高の各推論戦略を呼び分けるディスパッチャ。

import logging
from typing import Any, Dict, Optional

from .enums import ComplexityRegime
from ..providers.base import LLMProvider
from .reasoning_strategies import low_complexity, medium_complexity, high_complexity

logger = logging.getLogger(__name__)

class EnhancedReasoningEngine:
    """
    複雑性レジームに基づいて、低・中・高の各推論戦略を呼び分ける
    ディスパッチ専用の推論エンジン。
    """
    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any]):
        self.provider = provider
        self.base_model_kwargs = base_model_kwargs

    async def execute_reasoning(
        self,
        prompt: str,
        system_prompt: str,
        complexity_score: float,
        regime: ComplexityRegime
        ) -> Dict[str, Any]:
        """
        指定された複雑性レジームに対応する推論戦略を実行する。
        """
        logger.info(f"EnhancedReasoningEngineがレジーム '{regime.value}' で推論を実行します。")
        
        if regime == ComplexityRegime.LOW:
            return await low_complexity.execute_low_complexity_reasoning(
                self.provider, prompt, system_prompt, self.base_model_kwargs
            )
        elif regime == ComplexityRegime.MEDIUM:
            return await medium_complexity.execute_medium_complexity_reasoning(
                self.provider, prompt, system_prompt, self.base_model_kwargs
            )
        elif regime == ComplexityRegime.HIGH:
            return await high_complexity.execute_high_complexity_reasoning(
                self.provider, prompt, system_prompt, self.base_model_kwargs
            )
        else:
            logger.error(f"未知の複雑性レジームが指定されました: {regime}")
            return {"solution": "", "error": f"Unknown complexity regime: {regime}"}