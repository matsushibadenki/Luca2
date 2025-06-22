# /llm_api/core_engine/pipelines/adaptive.py
# Title: Adaptive Pipeline Handler (Refactored & PCM-Enabled)
# Role: 適応型推論のプロセス全体を調整するオーケストレーター。

import logging
import time
import asyncio
from typing import Any, Dict, Optional, Tuple

# --- ▼▼▼ ここから修正 ▼▼▼ ---
# 誤っていた相対インポートパスを修正 (.. -> ...)
from ...providers.base import LLMProvider
# --- ▲▲▲ ここまで修正 ▲▲▲ ---
from ...rag import RAGManager
from ..analyzer import AdaptiveComplexityAnalyzer
from ..reasoner import EnhancedReasoningEngine
from ..enums import ComplexityRegime
from ..learner import ComplexityLearner
from ..logic import self_adjustment, finalization

# MemoryConsolidationEngineの循環参照を避けるため、型ヒントとして文字列を使用
if False: # TYPE_CHECKING
    from ...memory_consolidation.engine import ConsolidationEngine

logger = logging.getLogger(__name__)

class AdaptivePipeline:
    """適応型パイプライン処理を担当するクラス（リファクタリング・PCM対応版）"""

    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any]):
        self.provider = provider
        self.base_model_kwargs = base_model_kwargs
        self.learner = ComplexityLearner()
        self.complexity_analyzer = AdaptiveComplexityAnalyzer(learner=self.learner)
        self.reasoning_engine = EnhancedReasoningEngine(provider, base_model_kwargs) 
        self.consolidation_engine: Optional['ConsolidationEngine'] = None 
        logger.info("AdaptivePipeline (Refactored & PCM-Enabled) を初期化しました")

    def set_consolidation_engine(self, engine: Any):
        """記憶統合エンジンを外部から設定する。"""
        self.consolidation_engine = engine
        logger.info("ConsolidationEngineがAdaptivePipelineに設定されました。")


    async def execute(
        self,
        prompt: str,
        system_prompt: str = "",
        force_regime: Optional[ComplexityRegime] = None,
        use_rag: bool = False,
        knowledge_base_path: Optional[str] = None,
        use_wikipedia: bool = False,
        real_time_adjustment: bool = True,
        mode: str = 'adaptive'
    ) -> Dict[str, Any]:
        """適応型パイプラインの実行（オーケストレーション）"""
        logger.info(f"適応型パイプライン開始 (モード: {mode}): {prompt[:80]}...")

        try:
            # 0. Edgeモードの特別処理
            if mode == 'edge':
                logger.info("エッジ最適化モードで実行。高度な機能を無効化します。")
                use_rag, use_wikipedia, real_time_adjustment = False, False, False
                force_regime = ComplexityRegime.LOW

            # 1. RAGのセットアップ
            current_prompt, rag_source = await self._setup_rag(prompt, use_rag, knowledge_base_path, use_wikipedia)

            # 2. 複雑性分析 (PCM対応済み)
            complexity_score, initial_regime = self.complexity_analyzer.analyze_complexity(current_prompt, mode=mode)
            current_regime = force_regime or initial_regime

            # 3. 推論ループの実行
            final_reasoning_result, final_regime = await self_adjustment.run_reasoning_loop(
                reasoning_engine=self.reasoning_engine,
                provider=self.provider,
                base_model_kwargs=self.base_model_kwargs,
                current_prompt=current_prompt,
                system_prompt=system_prompt,
                complexity_score=complexity_score,
                initial_regime=current_regime,
                original_prompt=prompt,
                enable_adjustment=(real_time_adjustment and not force_regime)
            )

            if not final_reasoning_result:
                return self._format_error_response("推論結果が得られませんでした。")

            # --- ▼▼▼ ここからPCM対応の修正 ▼▼▼ ---
            # 4. 記憶統合エンジンへの連携 (海馬から新皮質へ)
            self._trigger_memory_consolidation(
                prompt=prompt,
                final_reasoning_result=final_reasoning_result,
                novelty_score=complexity_score,
                final_regime=final_regime
            )
            # --- ▲▲▲ ここまでPCM対応の修正 ▲▲▲ ---

            # 5. 学習と最終化
            return await finalization.finalize_and_learn(
                learner=self.learner,
                provider=self.provider,
                base_model_kwargs=self.base_model_kwargs,
                reasoning_result=final_reasoning_result,
                original_prompt=prompt,
                system_prompt=system_prompt,
                final_regime=final_regime,
                initial_regime=initial_regime,
                complexity_score=complexity_score,
                rag_source=rag_source,
                mode=mode
            )

        except Exception as e:
            logger.error(f"適応型パイプライン実行中に予期せぬエラー: {e}", exc_info=True)
            return self._format_error_response(str(e))
    
    # --- ▼▼▼ 新規追加メソッド ▼▼▼ ---
    def _trigger_memory_consolidation(
        self,
        prompt: str,
        final_reasoning_result: Dict[str, Any],
        novelty_score: float,
        final_regime: ComplexityRegime
    ) -> None:
        """非同期で記憶統合プロセスをトリガーする"""
        if self.consolidation_engine:
            session_data = {
                "prompt": prompt,
                "solution": final_reasoning_result.get('solution'),
                "session_id": f"session_{int(time.time())}",
                "novelty_score": novelty_score, # 複雑性スコアを新規性スコアとして渡す
                "final_regime": final_regime.value,
                "thought_process": final_reasoning_result.get('thought_process', {}),
                "timestamp": time.time()
            }
            logger.info(f"セッション情報を記憶統合エンジンに送信します。新規性スコア: {novelty_score:.2f}")
            # 非同期タスクとして実行し、パイプラインの応答をブロックしない
            asyncio.create_task(self.consolidation_engine.consolidate_memories(session_data))
        else:
            logger.warning("ConsolidationEngineが設定されていないため、セッション記憶は保存されません。")
    # --- ▲▲▲ 新規追加メソッド ▲▲▲ ---

    async def _setup_rag(
        self, prompt: str, use_rag: bool, knowledge_base_path: Optional[str], use_wikipedia: bool
    ) -> Tuple[str, Optional[str]]:
        """RAGのセットアップを行い、拡張されたプロンプトと情報源を返す。"""
        if not (use_rag or use_wikipedia):
            return prompt, None

        rag_manager = RAGManager(provider=self.provider, use_wikipedia=use_wikipedia, knowledge_base_path=knowledge_base_path)
        augmented_prompt = await rag_manager.retrieve_and_augment(prompt)
        rag_source = 'wikipedia' if use_wikipedia else 'knowledge_base'
        return augmented_prompt, rag_source

    def _format_error_response(self, error_message: str) -> Dict[str, Any]:
        """エラーレスポンスの形式"""
        return {
            'success': False,
            'final_solution': None,
            'image_url': None,
            'thought_process': {'error': error_message},
            'v2_improvements': {'adaptive_execution': True, 'error_occurred': True},
            'version': 'v2',
            'error': error_message
        }