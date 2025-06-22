# /llm_api/meta_cognition/engine.py
# タイトル: Meta-Cognition and Introspective Dialogue Engine
# 役割: メタ認知システムの全体を統合し、思考プロセスの分析、改善、適応のサイクルを調整する。
#       また、内部の思考エージェント間の「内省的対話」を促進・調停し、自己形成を行う。(統合・修正版)

import asyncio
import json
import logging
import re
import time
from collections import deque
# --- ▼▼▼ ここから修正 ▼▼▼ ---
from typing import Any, Deque, Dict, List, Optional, cast
# --- ▲▲▲ ここまで修正 ▲▲▲ ---

from ..providers.base import LLMProvider
from .optimizer import CognitiveArchitectOptimizer
from .reflection import SelfReflectionEngine
# --- ▼▼▼ ここから修正 ▼▼▼ ---
# types.pyとmental_agents.pyから必要なクラスをインポート
from .types import CognitiveState, ThoughtTrace, MetaCognitiveInsight, IntrospectiveDialogue, DialogueTurn
from .mental_agents import MentalAgent, get_default_agents
# --- ▲▲▲ ここまで修正 ▲▲▲ ---

logger = logging.getLogger(__name__)

class MetaCognitionEngine:
    """
    メタ認知と内省的対話を司る統合エンジン。
    """
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        # 従来のメタ認知コンポーネント
        self.reflection_engine = SelfReflectionEngine()
        self.architect_optimizer = CognitiveArchitectOptimizer()
        self.current_thought_trace: List[ThoughtTrace] = []
        self.meta_insights_history: Deque[Dict[str, Any]] = deque(maxlen=100)
        self.architecture_config: Dict[str, Any] = {}
        
        # 内省的対話コンポーネント
        self.dialogue_history: List[IntrospectiveDialogue] = []
        self.mental_agents: List[MentalAgent] = get_default_agents(provider)
        
        self.cognitive_state = CognitiveState.IDLE
        logger.info(f"🤔 Meta-Cognition Engine 初期化完了。{len(self.mental_agents)}体の思考エージェントをロードしました。")

    # --- 従来のメタ認知サイクル関連メソッド ---

    async def begin_metacognitive_session(self, problem_context: str) -> Dict[str, Any]:
        logger.info(f"メタ認知セッション開始: {problem_context[:50]}...")
        self.current_thought_trace = []
        self.cognitive_state = CognitiveState.ANALYZING
        problem_analysis = await self._analyze_problem_nature(problem_context)
        cognitive_strategy = await self._select_cognitive_strategy(problem_analysis)
        return {
            "session_id": f"meta_{int(time.time())}",
            "problem_analysis": problem_analysis,
            "cognitive_strategy": cognitive_strategy,
            "meta_config": self.architecture_config,
        }

    async def record_thought_step(
        self, cognitive_state: CognitiveState, context: str, reasoning: str,
        confidence: float, outputs: Optional[List[str]] = None
    ) -> None:
        thought_trace = ThoughtTrace(
            timestamp=time.time(), cognitive_state=cognitive_state,
            input_context=context, reasoning_step=reasoning,
            confidence_level=confidence, resource_usage={"tokens": len(reasoning)},
            intermediate_outputs=outputs or []
        )
        self.current_thought_trace.append(thought_trace)
        self.reflection_engine.thought_history.append(thought_trace)
        self.cognitive_state = cognitive_state

    async def perform_metacognitive_reflection(self) -> Dict[str, Any]:
        logger.info("メタ認知的反省を実行中...")
        self.cognitive_state = CognitiveState.REFLECTING
        if not self.current_thought_trace:
            return {"insights": [], "optimizations": {}}
        insights = await self.reflection_engine.analyze_thought_pattern(self.current_thought_trace)
        optimizations = await self.architect_optimizer.optimize_cognitive_architecture(insights)
        self.architecture_config.update(optimizations)
        for insight in insights:
            self.meta_insights_history.append(vars(insight))
        reflection_result = {
            "insights": [vars(i) for i in insights],
            "optimizations": optimizations
        }
        logger.info(f"メタ認知的反省完了: {len(insights)}個の洞察、{len(optimizations)}個の最適化案を生成。")
        self.cognitive_state = CognitiveState.ADAPTING
        return reflection_result

    # --- 内省的対話関連メソッド ---
    
    async def conduct_introspective_dialogue(self, topic: str) -> IntrospectiveDialogue:
        dialogue_id = f"dialogue_{int(time.time())}"
        logger.info(f"🎬 内省的対話を開始します (ID: {dialogue_id}, トピック: {topic})")
        dialogue = IntrospectiveDialogue(dialogue_id=dialogue_id, topic=topic, timestamp=time.time())
        tasks = [agent.process(topic) for agent in self.mental_agents]
        opinions = await asyncio.gather(*tasks)
        for agent, opinion in zip(self.mental_agents, opinions):
            dialogue.turns.append(DialogueTurn(agent_name=agent.name, opinion=opinion))
        synthesis = await self._synthesize_dialogue(dialogue)
        dialogue.synthesis = synthesis
        self.dialogue_history.append(dialogue)
        logger.info(f"🎬 内省的対話が完了しました。")
        return dialogue

    async def _synthesize_dialogue(self, dialogue: IntrospectiveDialogue) -> str:
        dialogue_log = "\n\n".join(f"### {turn.agent_name}の意見\n{turn.opinion}" for turn in dialogue.turns)
        synthesis_prompt = f"""
        あなたは、複数の内なる声（思考エージェント）の対話をまとめる、賢明な調停者です。
        以下の、あるトピックに関する内なる対話の記録を読み、全ての意見を考慮した上で、
        単なる要約ではない、より高次の、統合された結論を導き出してください。
        矛盾を乗り越え、多角的な視点から最も思慮深い行動方針や自己理解を形成してください。
        # 対話のトピック: {dialogue.topic}
        # 内なる対話の記録:\n{dialogue_log}
        # 統合された結論:
        """
        response = await self.provider.call(synthesis_prompt, "")
        return cast(str, response.get("text", "対話の統合に失敗しました。"))

    # --- プライベートヘルパーメソッド ---

    async def _analyze_problem_nature(self, problem: str) -> Dict[str, Any]:
        analysis_prompt = f"""
        以下の問題の性質を多角的に分析し、JSON形式で回答してください：
        - cognitive_complexity: 認知的複雑性 (1-10)
        - thinking_type: 必要な思考タイプ (例: logical, creative, strategic)
        - uncertainty_level: 不確実性の程度 (1-10)
        問題: "{problem}"
        """
        response = await self.provider.call(analysis_prompt, "")
        try:
            analysis_text = response.get('text', '{}')
            json_match = re.search(r'\{.*\}', analysis_text, re.DOTALL)
            if json_match:
                return cast(Dict[str, Any], json.loads(json_match.group(0)))
            return {}
        except json.JSONDecodeError:
            logger.warning("問題分析のJSON解析に失敗しました。")
            return {}

    async def _select_cognitive_strategy(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        complexity = analysis.get("cognitive_complexity", 5)
        uncertainty = analysis.get("uncertainty_level", 5)
        strategy = {"primary_approach": "balanced", "monitoring_frequency": "medium"}
        if complexity >= 8 or uncertainty >= 8:
            strategy["primary_approach"] = "decomposition"
            strategy["monitoring_frequency"] = "high"
        elif analysis.get("thinking_type") == "creative":
            strategy["primary_approach"] = "divergent_convergent"
        return strategy