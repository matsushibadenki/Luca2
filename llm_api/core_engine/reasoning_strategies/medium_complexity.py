# /llm_api/core_engine/reasoning_strategies/medium_complexity.py
# タイトル: Medium Complexity Reasoning Strategy
# 役割: 中程度の複雑性を持つ問題に対して、構造化された段階的な推論を実行する戦略を実装する。

import logging
from typing import Any, Dict

from ...providers.base import LLMProvider
from ..enums import ComplexityRegime

logger = logging.getLogger(__name__)


async def execute_medium_complexity_reasoning(
    provider: LLMProvider,
    prompt: str,
    system_prompt: str,
    base_model_kwargs: Dict[str, Any]
) -> Dict[str, Any]:
    """
    中程度複雑性問題の推論（バランス型思考）。
    段階的かつ体系的な解決プロセスを通じて、バランスの取れた回答を生成します。

    Args:
        provider: 使用するLLMプロバイダー。
        prompt: ユーザーからのプロンプト。
        system_prompt: システムプロンプト。
        base_model_kwargs: モデルに渡す基本キーワード引数。

    Returns:
        推論結果を含む辞書。
    """
    logger.info("中複雑性推論モード: バランス型思考")

    structured_prompt = f"""以下の中程度の複雑性を持つ問題を、段階的かつ体系的に解決してください。

問題: {prompt}

推論プロセス:
1. 問題の核心的な要素を特定し、主要な論点を整理します。
2. 解決に必要な情報や背景知識を考慮に入れます。
3. 段階的な解決戦略を構築し、各ステップの目的を明確にします。
4. 各段階を実行し、論理的な一貫性を保ちながら中間的な結論を導き出します。
5. 全ての中間結果を統合し、包括的で説得力のある最終的な回答を生成します。

各段階での思考を明示し、論理的な繋がりが分かるように記述してください。"""

    # 修正: provider.callに渡す引数を整理し、重複を避ける
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)

    response = await provider.call(
        prompt=structured_prompt,
        system_prompt=system_prompt,
        **call_kwargs
    )

    return {
        'solution': response.get('text', ''),
        'error': response.get('error'),
        'complexity_regime': ComplexityRegime.MEDIUM.value,
        'reasoning_approach': 'structured_progressive',
        'stage_verification': True
    }