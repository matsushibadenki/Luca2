# /llm_api/quantum_engine.py
# タイトル: Quantum-Inspired Reasoning Engine (Final Fix)
# 役割: 量子インスパイアード推論を実装する。temperatureがNoneの場合にも対応するよう修正。

import asyncio
import logging
from typing import Any, Dict, List, Optional, cast

from .providers.base import LLMProvider

logger = logging.getLogger(__name__)

class QuantumReasoningEngine:
    """
    量子の重ね合わせや収縮の概念にヒントを得た推論エンジン。
    """
    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any]):
        self.provider = provider
        self.base_model_kwargs = base_model_kwargs

    async def solve(self, prompt: str, system_prompt: str) -> Dict[str, Any]:
        """
        量子インスパイアードアプローチで問題を解決する。
        1. 多様な仮説を生成する（重ね合わせ）。
        2. それらを統合・評価し、単一の堅牢な解に収縮させる。
        """
        logger.info("量子インスパイアード推論プロセスを開始しました。")

        # 1. 多様な仮説を並列で生成 (重ね合わせ)
        hypotheses = await self._generate_hypotheses(prompt, system_prompt)
        if not hypotheses:
            return {"solution": "", "error": "仮説の生成に失敗しました。"}
        
        # 2. 仮説を最終解に統合 (収縮)
        final_solution = await self._collapse_hypotheses(prompt, hypotheses, system_prompt)
        
        return {
            "solution": final_solution,
            "error": None,
            "reasoning_approach": "quantum_inspired_superposition",
            "hypotheses_generated": hypotheses,
        }

    async def _generate_hypotheses(self, prompt: str, system_prompt: str) -> List[Dict[str, str]]:
        """与えられたプロンプトに対して、複数の多様な思考経路を生成する。"""
        perspectives = [
            "楽観的な未来学者",
            "懐疑的で慎重なリスクアナリスト",
            "実現可能性に焦点を当てる現実的なエンジニア",
            "社会的影響を懸念する倫理学者",
            "過去の事例から類似点を見出す歴史家",
        ]

        async def get_hypothesis(perspective: str) -> Dict[str, str]:
            hypothesis_prompt = f"""
            あなたは「{perspective}」です。以下の問題を分析し、あなたのユニークな視点からの結論を提示してください。
            
            問題: {prompt}
            """
            call_kwargs = self.base_model_kwargs.copy()
            
            # --- ▼▼▼ ここから変更 ▼▼▼ ---
            # 多様性を促すため、温度を少し上げる
            # .get()の結果がNoneの場合も or 0.7 でデフォルト値が設定されるように修正
            current_temp = call_kwargs.get('temperature') or 0.7
            call_kwargs['temperature'] = (current_temp + 0.1) * 1.1
            # --- ▲▲▲ ここまで変更 ▲▲▲ ---
            
            call_kwargs['system_prompt'] = system_prompt

            response = await self.provider.call(hypothesis_prompt, **call_kwargs)
            
            return {"perspective": perspective, "analysis": response.get("text", "")}

        tasks = [get_hypothesis(p) for p in perspectives]
        results = await asyncio.gather(*tasks)
        
        valid_hypotheses = [res for res in results if res["analysis"]]
        logger.info(f"{len(valid_hypotheses)}個の多様な仮説を生成しました。")
        return valid_hypotheses

    async def _collapse_hypotheses(self, original_prompt: str, hypotheses: List[Dict[str, str]], system_prompt: str) -> str:
        """多様な仮説を単一の一貫した解に統合する。"""
        context = "\n\n---\n\n".join(
            f"**{h['perspective']}** の視点からの分析:\n{h['analysis']}" for h in hypotheses
        )
        
        collapse_prompt = f"""
        以下の「元の問題」に対して、複数の多様な視点と分析が生成されました。あなたの仕事は、マスター・シンセサイザー（統合の達人）として振る舞うことです。これらの視点を統合し、矛盾を解決し、単一で包括的、かつニュアンスに富んだ最終回答を構築してください。単に視点をリストアップするのではなく、それらを統合して優れた一つの解を生成してください。

        # 元の問題
        {original_prompt}

        --- 多様な仮説群 ---
        {context}
        --- 仮説群の終わり ---

        # 統合された最終回答
        """
        
        logger.info("仮説を最終解に収縮させています。")
        
        call_kwargs = self.base_model_kwargs.copy()
        
        # --- ▼▼▼ ここから変更 ▼▼▼ ---
        # 焦点が定まった一貫性のある最終回答のため、温度を下げる
        current_temp = call_kwargs.get('temperature') or 0.7
        call_kwargs['temperature'] = current_temp * 0.5
        # --- ▲▲▲ ここまで変更 ▲▲▲ ---

        call_kwargs['system_prompt'] = system_prompt
        
        response = await self.provider.call(collapse_prompt, **call_kwargs)
        
        return cast(str, response.get("text", "最終解の統合に失敗しました。"))
