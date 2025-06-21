# /llm_api/core_engine/reasoning_strategies/low_complexity.py
# タイトル: Low Complexity Reasoning Strategy
# 役割: 低複雑性の問題に対して、過剰な思考（overthinking）を避け、効率的に直接的な回答を生成する戦略を実装する。

import logging
from typing import Any, Dict

from ...providers.base import LLMProvider
from ..enums import ComplexityRegime

logger = logging.getLogger(__name__)


async def execute_low_complexity_reasoning(
    provider: LLMProvider,
    prompt: str,
    system_prompt: str,
    base_model_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    低複雑性問題の推論（overthinking防止）。
    簡潔さと効率を重視し、直接的なアプローチで回答を生成します。

    Args:
        provider: 使用するLLMプロバイダー。
        prompt: ユーザーからのプロンプト。
        system_prompt: システムプロンプト。
        base_model_kwargs: モデルに渡す基本キーワード引数。

    Returns:
        推論結果を含む辞書。
    """
    logger.info("低複雑性推論モード: 簡潔・効率重視")

    efficient_prompt = f"""以下の問題に対して、簡潔で効率的な解答を提供してください。
過度な分析や長時間の検討は避け、直接的なアプローチを取ってください。

問題: {prompt}

重要: 最初に思いついた合理的な解答が往々にして正解です。"""

    # 修正: provider.callに渡す引数を整理し、重複を避ける
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)

    response = await provider.call(
        prompt=efficient_prompt,
        system_prompt=system_prompt,
        **call_kwargs
    )

    return {
        'solution': response.get('text', ''),
        'error': response.get('error'),
        'complexity_regime': ComplexityRegime.LOW.value,
        'reasoning_approach': 'efficient_direct',
        'overthinking_prevention': True
    }