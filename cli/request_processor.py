# /cli/request_processor.py
# Title: CLI Request Processor (Final Call Fix)
# 役割: 全ての依存関係を正しく受け取り、下位のエンジンに注入する。

import logging
import time
from typing import Any, Dict, List, Optional

from llm_api.providers import get_provider
from llm_api.providers.base import EnhancedLLMProvider
from llm_api.core_engine.engine import MetaIntelligenceEngine
from llm_api.core_engine.learner import ComplexityLearner
from llm_api.core_engine.enums import ComplexityRegime
from .utils import convert_kwargs_for_standard, generate_error_suggestions
from llm_api.emotion_core.types import EmotionCategory
from llm_api.emotion_core.steering_manager import EmotionSteeringManager
from llm_api.autonomous_action.trigger import EmotionActionTrigger
from llm_api.autonomous_action.orchestrator import ActionOrchestrator
from llm_api.value_evolution.evolution_engine import ValueEvolutionEngine
from llm_api.memory_consolidation.engine import ConsolidationEngine

logger = logging.getLogger(__name__)

class RequestProcessor:
    """リクエスト処理のコアロジックを担当するクラス"""

    def __init__(
        self,
        emotion_steering_manager: Optional[EmotionSteeringManager],
        action_trigger: Optional[EmotionActionTrigger],
        action_orchestrator: Optional[ActionOrchestrator],
        value_evolution_engine: Optional[ValueEvolutionEngine],
        consolidation_engine: Optional[ConsolidationEngine]
    ):
        self.v2_modes = {
            'efficient', 'balanced', 'decomposed', 'adaptive', 'paper_optimized', 'parallel',
            'quantum_inspired', 'edge', 'speculative_thought', 'self_discover'
        }
        self.emotion_steering_manager = emotion_steering_manager
        self.action_trigger = action_trigger
        self.action_orchestrator = action_orchestrator
        self.value_evolution_engine = value_evolution_engine
        self.consolidation_engine = consolidation_engine
        self.emotion_system_enabled = all([emotion_steering_manager, action_trigger, action_orchestrator])
        self.learner = ComplexityLearner()

    async def process_request(self, provider_name: str, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """
        リクエストを処理し、必要に応じてフォールバックを実行する。
        """
        start_time = time.time()
        mode = kwargs.get('mode', 'simple')
        use_v2 = mode in self.v2_modes or kwargs.get('force_v2', False)
        no_fallback = kwargs.get('no_fallback', False)
        errors_encountered: List[str] = []

        final_kwargs = await self._apply_emotion_steering(kwargs)

        if use_v2:
            try:
                logger.info(f"V2拡張モード (mode: {mode}) でプロバイダー '{provider_name}' の呼び出しを試みます。")

                enhanced_provider = get_provider(provider_name, enhanced=True)
                
                if not isinstance(enhanced_provider, EnhancedLLMProvider):
                    raise TypeError(f"'{provider_name}' はV2拡張プロバイダーではありません。")

                standard_provider = enhanced_provider.standard_provider
                base_model_kwargs = enhanced_provider._get_optimized_params(mode, final_kwargs)
                
                engine = MetaIntelligenceEngine(
                    standard_provider,
                    base_model_kwargs,
                    consolidation_engine=self.consolidation_engine
                )
                
                # --- ▼▼▼ ここから修正 ▼▼▼ ---
                # engine.solve_problemに全ての引数を正しく渡す
                system_kwargs = {
                    'use_rag': final_kwargs.get('use_rag', False),
                    'knowledge_base_path': final_kwargs.get('knowledge_base_path'),
                    'use_wikipedia': final_kwargs.get('use_wikipedia', False),
                    'real_time_adjustment': final_kwargs.get('real_time_adjustment', True),
                    'mode': mode
                }
                response = await engine.solve_problem(
                    prompt,
                    system_prompt=final_kwargs.get("system_prompt", ""),
                    **system_kwargs
                )
                # --- ▲▲▲ ここまで修正 ▲▲▲ ---

                if not response.get('error'):
                    feedback = kwargs.get('feedback')
                    if feedback:
                        v2_info = response.get('v2_improvements')
                        if v2_info:
                            final_regime_str = v2_info.get('regime')
                            if final_regime_str:
                                try:
                                    final_regime = ComplexityRegime(final_regime_str)
                                    self._handle_feedback(prompt, final_regime, feedback)
                                except ValueError:
                                    logger.warning(f"フィードバック処理中に無効なレジームを検出: {final_regime_str}")
                            else:
                                logger.warning("フィードバック処理に必要な 'regime' がレスポンスに含まれていません。")
                        else:
                            logger.warning("V2改善情報がレスポンスに含まれていません。フィードバックはComplexityLearnerにのみ適用されます。")
                            inferred_regime = ComplexityRegime.MEDIUM
                            if mode == 'efficient' or mode == 'edge':
                                inferred_regime = ComplexityRegime.LOW
                            elif mode == 'decomposed':
                                inferred_regime = ComplexityRegime.HIGH
                            self._handle_feedback(prompt, inferred_regime, feedback)

                    response = await self._trigger_autonomous_action(response, prompt)
                    return response
                else:
                    error_msg = f"V2拡張モードでエラー: {response.get('error')}"
                    logger.warning(error_msg)
                    errors_encountered.append(error_msg)

            except Exception as e:
                error_msg = f"V2拡張プロバイダーの呼び出し中に例外が発生しました: {e}"
                logger.error(error_msg, exc_info=True)
                errors_encountered.append(error_msg)

        if no_fallback:
            logger.warning("フォールバックが無効化されているため、処理を終了します。")
            return {'text': "", 'error': "V2拡張モードでの処理に失敗し、フォールバックは無効です。", 'all_errors': errors_encountered}

        logger.info(f"標準プロバイダー (mode: {mode}) にフォールバックします。")
        try:
            provider = get_provider(provider_name, enhanced=False)
            standard_kwargs = convert_kwargs_for_standard(final_kwargs)
            response = await provider.call(prompt, **standard_kwargs)
            if not response.get('error'):
                 return response
            else:
                error_msg = f"標準フォールバックモードでエラー: {response.get('error')}"
                logger.error(error_msg)
                errors_encountered.append(error_msg)
        except Exception as e:
            error_msg = f"標準プロバイダーの呼び出し中に例外が発生しました: {e}"
            logger.error(error_msg, exc_info=True)
            errors_encountered.append(error_msg)

        final_error_message = "全てのリクエスト戦略が失敗しました。"
        suggestions = generate_error_suggestions(provider_name, errors_encountered)
        logger.critical(f"{final_error_message} 提案: {suggestions}")

        return {'text': "", 'error': final_error_message, 'all_errors': errors_encountered, 'suggestions': suggestions}

    def _handle_feedback(self, prompt: str, final_regime: ComplexityRegime, feedback: str):
        """ユーザーからのフィードバックを処理し、学習結果を記録する"""
        logger.info(f"フィードバック '{feedback}' をプロンプト '{prompt[:50]}...' (最終レジーム: {final_regime.value}) に記録します。")
        
        if feedback == 'good':
            self.learner.record_outcome(prompt, final_regime)
            logger.info(f"学習: プロンプトに対してレジーム '{final_regime.value}' が適切であったと記録しました。")
        elif feedback == 'bad':
            if final_regime == ComplexityRegime.LOW:
                next_regime = ComplexityRegime.MEDIUM
            elif final_regime == ComplexityRegime.MEDIUM:
                next_regime = ComplexityRegime.HIGH
            else:
                logger.info(f"最高の複雑性レジーム({final_regime.value})でフィードバック'bad'を受け取りました。これ以上調整できません。")
                return

            logger.info(f"学習: 不適切な戦略 ({final_regime.value}) と判断し、次回は '{next_regime.value}' を試すように学習させます。")
            self.learner.record_outcome(prompt, next_regime)

        if self.value_evolution_engine:
            feedback_data = {
                "type": f"user_{feedback}_feedback",
                "content": prompt,
                "response_quality": feedback,
                "context_regime": final_regime.value,
                "timestamp": time.time()
            }
            self.value_evolution_engine.receive_feedback(feedback_data)
            logger.info(f"価値進化エンジンにフィードバックを送信しました: {feedback_data['type']}")

    async def _apply_emotion_steering(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """感情ステアリングが有効な場合にkwargsを更新する"""
        final_kwargs = kwargs.copy()
        if self.emotion_system_enabled and self.emotion_steering_manager and kwargs.get('steer_emotion'):
            emotion_str = kwargs['steer_emotion']
            try:
                emotion_cat = EmotionCategory(emotion_str.lower())
                intensity = kwargs.get('steering_intensity', 5.0)
                steering_vector = self.emotion_steering_manager.get_steering_vector(emotion_cat, intensity)
                if steering_vector is not None:
                    final_kwargs['steering_vector'] = steering_vector
                    logger.info(f"感情ステアリング '{emotion_str}' を適用します。")
            except (ValueError, AttributeError) as e:
                logger.warning(f"無効な感情名またはステアリングエラーです: {e}")
        return final_kwargs

    async def _trigger_autonomous_action(self, response: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """自律行動がトリガーされた場合にアクションを実行する"""
        if self.emotion_system_enabled and self.action_trigger and self.action_orchestrator:
            from llm_api.emotion_core.types import EmotionAnalysisResult
            analysis_result = EmotionAnalysisResult(interest_score=0.9) # これはダミー実装
            action_context = {"prompt_history": [prompt]}
            action_request = self.action_trigger.check_and_trigger(analysis_result, action_context)

            if action_request:
                logger.info(f"自律行動 '{action_request.requested_action}' がトリガーされました。")
                action_result = await self.action_orchestrator.execute_action(action_request)
                if action_result:
                    response['autonomous_action_result'] = action_result
                    logger.info(f"自律行動の結果: {action_result}")
        return response