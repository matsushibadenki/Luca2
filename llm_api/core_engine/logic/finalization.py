# /llm_api/core_engine/logic/finalization.py
# タイトル: Finalization Logic for Adaptive Pipeline
# 役割: 推論結果の最終的な評価・改善と、学習結果の記録を担当する。

import logging
from typing import Any, Dict, Optional, cast

from ..enums import ComplexityRegime
from ..learner import ComplexityLearner
from ...providers.base import LLMProvider

logger = logging.getLogger(__name__)

async def finalize_and_learn(
    learner: ComplexityLearner,
    provider: LLMProvider,
    base_model_kwargs: Dict[str, Any],
    reasoning_result: Dict[str, Any],
    original_prompt: str,
    system_prompt: str,
    final_regime: ComplexityRegime,
    initial_regime: ComplexityRegime,
    complexity_score: float,
    rag_source: Optional[str],
    mode: str
) -> Dict[str, Any]:
    """
    学習を記録し、最終的な解を生成・整形して返す。
    """
    if final_regime != initial_regime:
        learner.record_outcome(original_prompt, final_regime)

    final_solution = await _evaluate_and_refine(
        provider, base_model_kwargs,
        reasoning_result.get('solution', ''),
        original_prompt, system_prompt, final_regime
    )

    thought_process = {
        'complexity_score': complexity_score,
        'initial_regime': initial_regime.value,
        'final_regime': final_regime.value,
        'decomposition': reasoning_result.get('decomposition'),
        'sub_solutions': reasoning_result.get('sub_solutions'),
        'self_evaluation': reasoning_result.get('self_evaluation'),
    }

    v2_improvements = {
        'regime': final_regime.value,
        'reasoning_approach': reasoning_result.get('reasoning_approach'),
        'overthinking_prevention': reasoning_result.get('overthinking_prevention', False),
        'collapse_prevention': reasoning_result.get('collapse_prevention', False),
        'rag_enabled': rag_source is not None,
        'rag_source': rag_source,
        'real_time_adjustment_active': final_regime != initial_regime,
        'learned_suggestion_used': learner.get_suggestion(original_prompt) is not None,
        'is_edge_optimized': mode == 'edge',
    }

    return _format_response(final_solution, thought_process, v2_improvements)


async def _evaluate_and_refine(
    provider: LLMProvider,
    base_model_kwargs: Dict[str, Any],
    solution: str,
    original_prompt: str,
    system_prompt: str,
    regime: ComplexityRegime
) -> str:
    """
    生成された解を評価し、必要であれば改善する。
    """
    if regime == ComplexityRegime.LOW or not solution:
        return solution
    
    logger.info("解の限定的改善プロセスを開始...")
    refinement_prompt = f"""以下の「元の質問」に対する「回答案」です。内容をレビューし、明確さ、正確性、完全性の観点で改善してください。改善した最終版の回答のみを出力してください。

# 元の質問: {original_prompt}
# 回答案: {solution}
# 改善された最終回答:
"""
    # 修正: provider.callに渡す引数を整理し、重複を避ける
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)

    response = await provider.call(
        prompt=refinement_prompt,
        system_prompt=system_prompt,
        **call_kwargs
    )
    return cast(str, response.get('text', solution))


def _format_response(
    solution: Optional[str],
    thought_process: Optional[Dict[str, Any]],
    v2_improvements: Optional[Dict[str, Any]],
    success: bool = True,
    error: Optional[str] = None
) -> Dict[str, Any]:
    """統一されたレスポンス形式で出力する。"""
    return {
        'success': success,
        'final_solution': solution,
        'image_url': None,
        'thought_process': thought_process,
        'v2_improvements': v2_improvements,
        'version': 'v2',
        'error': error
    }