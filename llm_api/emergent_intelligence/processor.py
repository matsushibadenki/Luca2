# /llm_api/emergent_intelligence/processor.py
# タイトル: Emergent Intelligence Processor
# 役割: 統合情報理論(IIT)の思想に基づき、複数の専門家AIシステムの出力間の関係性や矛盾を分析し、
#       個々の出力の総和を超えた、全く新しい洞察（創発的知能）を生み出す。

import logging
import json
import time
import asyncio
from typing import Any, Dict, List, Optional, Tuple, cast
from dataclasses import dataclass, field, asdict
from enum import Enum

from ..providers.base import LLMProvider

logger = logging.getLogger(__name__)

# --- データクラス定義 ---

@dataclass
class AgentOutput:
    """個々のエージェントの出力を格納する"""
    agent_id: str
    perspective: str # エージェントの専門性や視点
    content: str
    confidence: float

@dataclass
class EmergentInsight:
    """創発された洞察"""
    insight_id: str
    content: str
    contributing_agents: List[str]
    synergy_score: float # 各出力がどれだけ相乗効果を生んだか
    phi_score: float # 統合情報量Φの概念を模したスコア
    emergence_level: float # 創発の度合い

# --- メインクラス ---

class EmergentIntelligenceProcessor:
    """
    複数のAIエージェントの出力を統合し、創発的な洞察を生み出すプロセッサ。
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        # システムは外部から登録されることを想定
        self.agents: Dict[str, Any] = {}
        self.insights_history: List[EmergentInsight] = []
        logger.info("🧠 Emergent Intelligence Processor 初期化完了")

    def register_agent(self, agent_id: str, agent_instance: Any, perspective: str):
        """専門家AIエージェントを登録する"""
        self.agents[agent_id] = {"instance": agent_instance, "perspective": perspective}
        logger.info(f"エージェント '{agent_id}' (視点: {perspective}) を登録しました。")

    async def synthesize_emergent_insight(
        self, problem: str, context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        問題に対して各エージェントからの出力を取得し、それらを統合して創発的洞察を生成する。
        """
        logger.info(f"🚀 創発的洞察の合成プロセス開始: {problem[:100]}...")
        context = context or {}

        # 1. 各エージェントから並列で出力を取得
        agent_outputs = await self._get_outputs_from_agents(problem, context)
        if not agent_outputs:
            logger.error("エージェントから有効な出力が得られませんでした。")
            return {"error": "No valid outputs from agents."}

        # 2. 出力間の関係性、矛盾、相乗効果を分析 (IITの統合プロセスに相当)
        relationship_analysis = await self._analyze_inter_output_relationships(agent_outputs)

        # 3. 分析結果から、高次の新しい洞察を生成 (創発)
        emergent_insight = await self._generate_emergent_insight(problem, agent_outputs, relationship_analysis)

        if not emergent_insight:
            logger.error("創発的洞察の生成に失敗しました。")
            return {"error": "Failed to generate emergent insight."}

        self.insights_history.append(emergent_insight)
        logger.info(f"✨ 創発的洞察の合成プロセス完了。Φスコア: {emergent_insight.phi_score:.2f}")

        return {
            "emergent_solution": emergent_insight.content,
            "emergence_level": emergent_insight.emergence_level,
            "phi_score": emergent_insight.phi_score,
            "synergy_score": emergent_insight.synergy_score,
            "contributing_agents": emergent_insight.contributing_agents,
            "relationship_analysis": relationship_analysis,
        }

    async def _get_outputs_from_agents(self, problem: str, context: Dict[str, Any]) -> List[AgentOutput]:
        """登録されたエージェント群に問題を投げ、並列で出力を収集する"""
        
        async def solve_with_agent(agent_id: str, agent_info: Dict) -> Optional[AgentOutput]:
            perspective = agent_info["perspective"]
            # 実際の solve メソッドはエージェントの仕様に依存
            # ここでは、エージェントが provider.call を持つ単純な構造と仮定する
            try:
                # エージェントごとに異なる視点をプロンプトに注入
                agent_prompt = f"あなたは「{perspective}」の専門家です。以下の問題について、あなたの専門的観点から詳細な分析と解決策を提示してください。\n\n問題: {problem}"
                response = await self.provider.call(agent_prompt, "")
                if response and not response.get("error"):
                    return AgentOutput(
                        agent_id=agent_id,
                        perspective=perspective,
                        content=response["text"],
                        confidence=0.9 # 仮
                    )
                return None
            except Exception as e:
                logger.error(f"エージェント '{agent_id}' の実行中にエラー: {e}")
                return None

        tasks = [solve_with_agent(aid, a_info) for aid, a_info in self.agents.items()]
        results = await asyncio.gather(*tasks)
        return [res for res in results if res]

    async def _analyze_inter_output_relationships(self, outputs: List[AgentOutput]) -> Dict[str, Any]:
        """
        複数のAI出力の関係性を分析する。
        IITにおける「統合」の概念を模倣し、共通点、矛盾点、相補性を抽出する。
        """
        if len(outputs) < 2:
            return {"error": "分析するには出力が少なすぎます。"}

        formatted_outputs = "\n\n".join(
            f"---視点: {out.perspective} (Agent ID: {out.agent_id})---\n{out.content}"
            for out in outputs
        )

        analysis_prompt = f"""
        以下の、異なる専門的視点から生成された複数の分析結果を調査してください。
        あなたのタスクは、これらの出力間の複雑な関係性をメタレベルで分析し、
        以下の情報を構造化されたJSON形式で抽出することです。

        1.  **commonalities**: 全ての視点で共通して指摘されている中心的な概念や結論。
        2.  **contradictions**: 視点間で明確に矛盾している点や対立する意見。
        3.  **complementary_insights**: ある視点が他の視点の欠けている部分を補完している具体的な箇所。
        4.  **synergies**: 複数の視点を組み合わせることで初めて明らかになる、新しい相乗効果や高次の洞察。

        # 分析対象の出力群
        {formatted_outputs}

        # 分析結果 (JSON形式で出力してください)
        """
        response = await self.provider.call(analysis_prompt, "", json_mode=True)
        try:
            analysis_result = json.loads(response.get("text", "{}"))
            return cast(Dict[str, Any], analysis_result)
        except json.JSONDecodeError:
            logger.error("出力間関係性の分析結果のJSON解析に失敗しました。")
            return {"error": "Failed to parse relationship analysis."}

    async def _generate_emergent_insight(
        self, problem: str, outputs: List[AgentOutput], analysis: Dict[str, Any]
    ) -> Optional[EmergentInsight]:
        """分析された関係性から、創発的な新しい洞察や解決策を生成する。"""

        synthesis_prompt = f"""
        あなたは、天才的な統合思想家です。
        ある複雑な問題「{problem}」に対して、複数の専門家の分析結果とその関係性分析が以下に提示されています。

        # 専門家の分析結果の要約
        {json.dumps([{'perspective': o.perspective, 'summary': o.content[:150] + '...'} for o in outputs], ensure_ascii=False, indent=2)}

        # 分析結果間の関係性
        {json.dumps(analysis, ensure_ascii=False, indent=2)}

        あなたの任務は、これらの情報を全て統合し、単なる要約や平均的な意見ではなく、
        個々の分析の総和を「超える」全く新しい、高次元の洞察（創発的洞察）を生み出すことです。
        矛盾を解決し、相乗効果を最大化し、誰も気づかなかった根本的な原理や革新的な解決策を提示してください。
        """
        response = await self.provider.call(synthesis_prompt, "")
        emergent_content = response.get("text")
        if not emergent_content:
            return None

        # スコアリング（簡易版）
        phi_score = (len(analysis.get("commonalities", [])) * 0.2 +
                     len(analysis.get("contradictions", [])) * 0.3 +
                     len(analysis.get("complementary_insights", [])) * 0.2 +
                     len(analysis.get("synergies", [])) * 0.5)
        
        emergence_level = len(analysis.get("synergies", [])) / (len(outputs) + 1e-6)
        synergy_score = phi_score / (len(outputs) + 1e-6)


        return EmergentInsight(
            insight_id=f"insight_{int(time.time())}",
            content=emergent_content,
            contributing_agents=[o.agent_id for o in outputs],
            synergy_score=min(1.0, synergy_score),
            phi_score=phi_score,
            emergence_level=min(1.0, emergence_level)
        )