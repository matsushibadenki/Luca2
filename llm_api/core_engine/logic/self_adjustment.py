# /llm_api/core_engine/logic/self_adjustment.py
# Title: Self-Adjustment Logic with LLM-based Evaluation
# Role: 自己評価ロジックをLLMベースの評価に高度化し、より正確な再調整を行う。

import logging
import re
from typing import Any, Dict, Optional, Tuple

from ..reasoner import EnhancedReasoningEngine
from ..enums import ComplexityRegime
from ...providers.base import LLMProvider

logger = logging.getLogger(__name__)

MAX_ADJUSTMENT_ATTEMPTS = 2

async def run_reasoning_loop(
    reasoning_engine: EnhancedReasoningEngine,
    provider: LLMProvider,
    base_model_kwargs: Dict[str, Any],
    current_prompt: str,
    system_prompt: str,
    complexity_score: float,
    initial_regime: ComplexityRegime,
    original_prompt: str,
    enable_adjustment: bool
) -> Tuple[Optional[Dict[str, Any]], ComplexityRegime]:
    """
    自己調整ループを実行し、最終的な推論結果とレジームを返す。
    """
    current_regime = initial_regime
    final_reasoning_result = None

    for attempt in range(MAX_ADJUSTMENT_ATTEMPTS):
        logger.info(f"推論試行 {attempt + 1}/{MAX_ADJUSTMENT_ATTEMPTS} (レジーム: {current_regime.value})")
        
        reasoning_result = await reasoning_engine.execute_reasoning(
            current_prompt, system_prompt, complexity_score, current_regime
        )
        final_reasoning_result = reasoning_result.copy()

        if reasoning_result.get('error'):
            logger.error(f"推論エンジンでエラー: {reasoning_result['error']}")
            return None, current_regime

        if not enable_adjustment or (attempt + 1) >= MAX_ADJUSTMENT_ATTEMPTS:
            break

        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # LLMによる高度な自己評価を導入
        evaluation = await _llm_self_evaluate_solution(
            provider=provider,
            base_model_kwargs=base_model_kwargs,
            solution=final_reasoning_result.get('solution', ''),
            original_prompt=original_prompt,
            current_regime=current_regime
        )
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        final_reasoning_result['self_evaluation'] = evaluation

        if evaluation.get("is_sufficient"):
            logger.info("自己評価の結果、解は十分と判断しました。")
            break
        else:
            logger.info(f"自己評価の結果、解は不十分と判断({evaluation.get('reason')})。再調整します。")
            new_regime_str = evaluation.get("next_regime")
            if new_regime_str:
                try:
                    new_regime = ComplexityRegime(new_regime_str)
                    if new_regime != current_regime:
                        logger.info(f"複雑性を再調整: {current_regime.value} -> {new_regime.value}")
                        current_regime = new_regime
                        current_prompt = f"前回の回答は「{evaluation.get('reason')}」という理由で不十分でした。より深く、包括的な分析を行ってください。\n元の質問: {original_prompt}\n"
                    else:
                        logger.info("同じ複雑性レジームが推奨されたため、調整を終了します。")
                        break
                except ValueError:
                    logger.error(f"無効なレジーム '{new_regime_str}' が提案されたため、調整を終了します。")
                    break
            else:
                break
    
    return final_reasoning_result, current_regime


async def _llm_self_evaluate_solution(
    provider: LLMProvider,
    base_model_kwargs: Dict[str, Any],
    solution: str,
    original_prompt: str,
    current_regime: ComplexityRegime
) -> Dict[str, Any]:
    """
    LLMを用いて生成された解を自己評価し、次のアクションを決定する。
    """
    if not solution:
        return {"is_sufficient": False, "reason": "回答が空です。", "next_regime": current_regime.value}

    # Lowレジームで十分な回答が得られているかどうかの判断は特に重要
    if current_regime == ComplexityRegime.LOW:
        # 非常に単純な質問かどうかをまず判断
        is_trivial_prompt = f"""以下の質問は、一言または非常に短い文で回答できる単純な事実に関する質問ですか？ "yes" または "no" のみで答えてください。
質問: "{original_prompt}"
"""
        call_kwargs = base_model_kwargs.copy()
        call_kwargs.pop('system_prompt', None)
        is_trivial_res = await provider.call(is_trivial_prompt, "", **call_kwargs)
        if "yes" in is_trivial_res.get("text", "no").lower() and len(solution) < 200:
             return {"is_sufficient": True, "reason": "単純な質問に簡潔な回答が生成されたため。"}


    # 汎用的な自己評価プロンプト
    evaluation_prompt = f"""
あなたは、AIの思考プロセスを評価する超厳格な評価者です。
以下の「元の質問」に対して生成された「現在の回答」が、質問の意図を完全に満たしているか、深い洞察を提供できているかを評価してください。

# 元の質問:
{original_prompt}

# 現在の回答:
{solution}

# 評価基準:
- **深い理解**: 質問の核心を捉え、表面的でない回答か？
- **網羅性**: 質問に含まれる全ての要素に答えているか？
- **論理的一貫性**: 回答全体で論理矛盾がないか？

# 判断と次のステップ:
- **完璧な場合**: `sufficient` とだけ出力。
- **不十分な場合**: `insufficient: [理由], next_regime: [次のレジーム]` の形式で出力。
  - [理由]: なぜ不十分か具体的に記述（例: `具体例が不足`, `哲学的考察が浅い`）
  - [次のレジーム]: `low`, `medium`, `high` のいずれかを選択。現在のレジームより必ず一段階高いものを推奨すること。

現在の思考レジーム: {current_regime.value}
あなたの判断:
"""    
    call_kwargs = base_model_kwargs.copy()
    call_kwargs.pop('system_prompt', None)
    response = await provider.call(evaluation_prompt, "", **call_kwargs)
    evaluation_text = response.get("text", "sufficient").strip().lower()

    if evaluation_text.startswith("insufficient"):
        reason_match = re.search(r":\s*([^,]+)", evaluation_text)
        regime_match = re.search(r"next_regime:\s*(\w+)", evaluation_text)
        
        reason = reason_match.group(1).strip() if reason_match else "不明な理由"
        next_regime_str = regime_match.group(1).strip() if regime_match else current_regime.value
        
        try:
            next_regime = ComplexityRegime(next_regime_str)
            regime_order = {ComplexityRegime.LOW: 0, ComplexityRegime.MEDIUM: 1, ComplexityRegime.HIGH: 2}
            # 提案されたレジームが現在と同じかそれより下なら、ループを止める
            if regime_order.get(next_regime, -1) <= regime_order.get(current_regime, -1):
                return {"is_sufficient": True, "reason": "これ以上の改善は不要と判断されました。"}

            return {"is_sufficient": False, "reason": reason, "next_regime": next_regime.value}
        except ValueError:
             logger.warning(f"LLMが不正なレジーム '{next_regime_str}' を提案しました。")
             return {"is_sufficient": True, "reason": "不正なレジームが提案されたため評価を終了します。"}
    else:
        return {"is_sufficient": True, "reason": "回答は十分な品質と判断されました。"}