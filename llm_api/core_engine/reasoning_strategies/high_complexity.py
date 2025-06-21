# /llm_api/core_engine/reasoning_strategies/high_complexity.py
# タイトル: High Complexity Reasoning Strategy
# 役割: 高複雑性の問題に対して、分解・並列解決・統合のアプローチを実行する戦略を実装する。

import asyncio
import json
import logging
import re
from typing import Any, Dict, List, Union, cast

from ...config import settings
from ...providers.base import LLMProvider
from ..enums import ComplexityRegime
from .medium_complexity import execute_medium_complexity_reasoning

logger = logging.getLogger(__name__)


async def execute_high_complexity_reasoning(
    provider: LLMProvider,
    prompt: str,
    system_prompt: str,
    base_model_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    高複雑性問題の推論（崩壊回避戦略）。
    問題をサブ問題に分解し、並列解決したのち、逐次的に統合して最終解を生成します。

    Args:
        provider: 使用するLLMプロバイダー。
        prompt: ユーザーからのプロンプト。
        system_prompt: システムプロンプト。
        base_model_kwargs: モデルに渡す基本キーワード引数。

    Returns:
        推論結果を含む辞書。
    """
    logger.info("高複雑性推論モード: 分解・並列解決・統合")

    sub_problems_result = await _decompose_complex_problem(provider, prompt, system_prompt, base_model_kwargs)
    if isinstance(sub_problems_result, dict) and sub_problems_result.get('error'):
        return {'solution': '', 'error': sub_problems_result['error']}
    sub_problems = cast(List[str], sub_problems_result)

    if not sub_problems:
        logger.warning("問題の分解に失敗。中複雑性モードにフォールバックします。")
        return await execute_medium_complexity_reasoning(provider, prompt, system_prompt, base_model_kwargs)

    staged_solutions = await _solve_decomposed_problems(provider, sub_problems, prompt, system_prompt, base_model_kwargs)
    if any(s.get('error') for s in staged_solutions):
        logger.warning("一部のサブ問題の解決中にエラーが発生しました。")

    final_solution_result = await _integrate_staged_solutions(provider, staged_solutions, prompt, system_prompt, base_model_kwargs)
    if isinstance(final_solution_result, dict) and final_solution_result.get('error'):
        return {'solution': '', 'error': final_solution_result['error']}
    final_solution = cast(str, final_solution_result)

    return {
        'solution': final_solution,
        'error': None,
        'complexity_regime': ComplexityRegime.HIGH.value,
        'reasoning_approach': 'decomposition_parallel_solve_integration',
        'decomposition': sub_problems,
        'sub_solutions': staged_solutions,
        'collapse_prevention': True
    }


async def _decompose_complex_problem(
    provider: LLMProvider, prompt: str, system_prompt: str, base_model_kwargs: Dict[str, Any]
) -> Union[List[str], Dict[str, Any]]:
    """複雑な問題を解決可能なサブ問題のJSONリストに分解します。"""
    decomposition_prompt = (
        f"Decompose the following complex problem: {prompt}. "
        "Output a JSON array of sub-problems."
    )
    
    # 修正: provider.callに渡す引数を整理し、重複を避ける
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)
    
    response = await provider.call(
        prompt=decomposition_prompt,
        system_prompt=system_prompt,
        **call_kwargs
    )
    if response.get('error'):
        return {'error': response['error']}

    try:
        response_text = response.get('text', '{}').strip()
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if not json_match:
            list_match = [line.strip('-* ').strip() for line in response_text.split('\n') if line.strip().startswith(('-', '*', '1.', '2.', '3.'))]
            if list_match:
                logger.warning(f"JSONが見つからず、リストとして解析: {list_match}")
                return list_match
            raise json.JSONDecodeError("No JSON or list found", response_text, 0)

        parsed_json = json.loads(json_match.group(0))
        sub_problems = parsed_json.get("sub_problems", [])
        if not isinstance(sub_problems, list):
            logger.error(f"'sub_problems'がリスト形式ではありません: {sub_problems}")
            return []
        logger.info(f"{len(sub_problems)}個のサブ問題に分解しました。")
        return sub_problems
    except (json.JSONDecodeError, Exception) as e:
        logger.error(f"問題の分解結果の解析中にエラー: {e}")
        return []


async def _solve_decomposed_problems(
    provider: LLMProvider, sub_problems: List[str], original_prompt: str, system_prompt: str, base_model_kwargs: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """分解されたサブ問題を並列で解決します。"""
    logger.info(f"{len(sub_problems)}個のサブ問題を並列解決します。")
    semaphore = asyncio.Semaphore(settings.OLLAMA_CONCURRENCY_LIMIT)

    async def solve_task(sub_problem: str, index: int) -> Dict[str, Any]:
        async with semaphore:
            staged_prompt = f"""Given the original problem: "{original_prompt}", solve the following sub-problem: "{sub_problem}"."""
            logger.debug(f"サブ問題 {index+1}/{len(sub_problems)} の解決を開始...")
            
            # 修正: provider.callに渡す引数を整理し、重複を避ける
            call_kwargs = base_model_kwargs.copy()
            call_kwargs.pop('system_prompt', None)

            response = await provider.call(
                prompt=staged_prompt,
                system_prompt=system_prompt,
                **call_kwargs
            )
            logger.debug(f"サブ問題 {index+1}/{len(sub_problems)} の解決が完了。")
            return {'sub_problem': sub_problem, 'solution': response.get('text', ''), 'error': response.get('error')}

    tasks = [solve_task(sp, i) for i, sp in enumerate(sub_problems)]
    return await asyncio.gather(*tasks)


async def _integrate_staged_solutions(
    provider: LLMProvider, staged_solutions: List[Dict[str, Any]], original_prompt: str, system_prompt: str, base_model_kwargs: Dict[str, Any]
) -> Union[str, Dict[str, Any]]:
    """段階的解決策を統合します。"""
    valid_solutions = [s['solution'] for s in staged_solutions if s.get('solution') and not s.get('error')]
    if not valid_solutions:
        return {"error": "統合する有効なサブ問題の解決策がありません。"}

    # 修正: provider.callに渡す引数を整理し、重複を避ける
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)

    integrated_solution = valid_solutions[0]
    for i, next_solution in enumerate(valid_solutions[1:]):
        integration_prompt = f"""Integrate the 'New Information' into the 'Previous Integrated Result'.

# Previous Integrated Result:
{integrated_solution}

# New Information:
{next_solution}

# New Integrated Result:"""
        response = await provider.call(
            prompt=integration_prompt,
            system_prompt=system_prompt,
            **call_kwargs
        )
        if response.get('error'):
            return cast(str, integrated_solution)
        integrated_solution = response.get('text', integrated_solution)

    final_polish_prompt = f"""Polish the following integrated text for the question: "{original_prompt}".

# Integrated Text:
{integrated_solution}

# Polished Final Report:"""
    final_response = await provider.call(
        prompt=final_polish_prompt,
        system_prompt=system_prompt,
        **call_kwargs
    )
    return cast(str, final_response.get('text', integrated_solution))