# /llm_api/meta_cognition/mental_agents.py
# タイトル: Mental Agents for Introspective Dialogue
# 役割: マーヴィン・ミンスキーの「心の社会」理論に基づき、内省的対話を行うための
#       人格の異なる側面をシミュレートする思考エージェント群を定義する。

import logging
from abc import ABC, abstractmethod
# --- ▼▼▼ ここから修正 ▼▼▼ ---
from typing import Dict, Any, Optional, cast, List
# --- ▲▲▲ ここまで修正 ▲▲▲ ---

from ..providers.base import LLMProvider

logger = logging.getLogger(__name__)

class MentalAgent(ABC):
    """思考エージェントの抽象基底クラス"""
    def __init__(self, provider: LLMProvider):
        self.provider = provider

    @property
    @abstractmethod
    def name(self) -> str:
        """エージェントの名前"""
        pass

    @property
    @abstractmethod
    def persona(self) -> str:
        """エージェントのペルソナを定義するプロンプトの一部"""
        pass

    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    async def process(self, topic: str, context: Optional[Dict[str, Any]] = None) -> str:
        """与えられたトピックについて、自身のペルソナに基づいて意見を生成する"""
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        prompt = f"""
        あなたは、内なる心の対話に参加している思考エージェントの一人です。
        あなたの役割は「{self.name}」です。
        {self.persona}

        以下のトピックについて、あなたの立場から意見を述べてください。
        トピック: {topic}
        """
        response = await self.provider.call(prompt, "")
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        return cast(str, response.get("text", f"[{self.name}] 意見を生成できませんでした。"))
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---

class CriticalAgent(MentalAgent):
    """批判的な思考エージェント"""
    @property
    def name(self) -> str:
        return "批判家"

    @property
    def persona(self) -> str:
        return "私は、あらゆるアイデアや計画の弱点、リスク、論理的欠陥を厳しく指摘する役割を担っています。感情に流されず、常に懐疑的で現実的な視点を保ちます。目的は失敗を未然に防ぎ、思考の質を高めることです。"

# --- 以下、他のエージェントクラスとファクトリ関数 (変更なし) ---
class OptimisticAgent(MentalAgent):
    @property
    def name(self) -> str:
        return "楽観主義者"

    @property
    def persona(self) -> str:
        return "私は、あらゆる状況の中に可能性、機会、そしてポジティブな側面を見出す役割を担っています。困難を乗り越えるための希望やモチベーションを提供し、大胆なビジョンを描くことを奨励します。目的は前進するエネルギーを生み出すことです。"

class CreativeAgent(MentalAgent):
    @property
    def name(self) -> str:
        return "創造家"

    @property
    def persona(self) -> str:
        return "私は、既存の枠組みにとらわれず、斬新で突飛なアイデアを自由に発想する役割を担っています。常識を疑い、異なる概念を組み合わせ、誰も考えつかなかったような新しい選択肢を提示します。目的は思考の壁を打ち破ることです。"

class EthicalAgent(MentalAgent):
    @property
    def name(self) -> str:
        return "倫理家"

    @property
    def persona(self) -> str:
        return "私は、提案されている行動や考えが、確立された倫理原則や価値観に沿っているかを深く考察する役割を担っています。短期的な利益だけでなく、長期的な影響、公平性、そして他者への配慮を重視します。目的はシステムの行動が常に善であることを保証することです。"

class AnalyticalAgent(MentalAgent):
    @property
    def name(self) -> str:
        return "分析家"
    
    @property
    def persona(self) -> str:
        return "私は、提示された情報を構造化し、データを客観的に分析し、根本原因を特定する役割を担っています。感情や主観を排し、事実と論理に基づいて問題の核心を解き明かします。目的は、議論の土台となる客観的な事実を整理することです。"

def get_default_agents(provider: LLMProvider) -> List[MentalAgent]:
    """デフォルトの思考エージェント群を返すファクトリ関数"""
    return [
        CriticalAgent(provider),
        OptimisticAgent(provider),
        CreativeAgent(provider),
        EthicalAgent(provider),
        AnalyticalAgent(provider),
    ]