# llm_api/value_evolution/evolution_engine.py
# タイトル: Value Evolution Engine (修正版)
# 役割: AIシステムの価値観と倫理観を、経験とフィードバックを通じて自律的に進化させる。

import logging
import json
import time
from typing import Any, Dict, List, Optional, cast

from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib

from ..providers.base import LLMProvider
# ★ 修正: 正しいインポート元に変更
from ..problem_discovery.types import DiscoveredProblem, ProblemType, ProblemSeverity, DiscoveryMethod

logger = logging.getLogger(__name__)

# --- データクラスとEnum定義 ---

@dataclass
class ValuePrinciple:
    """価値原則"""
    id: str
    name: str
    description: str
    category: str  # 例: "ethical", "performance", "social"
    weight: float
    is_active: bool = True
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class EthicalFramework:
    """倫理フレームワーク"""
    id: str
    name: str
    principles: Dict[str, ValuePrinciple]
    base_framework: str  # 例: "utilitarianism", "deontology"
    version: int = 1

@dataclass
class ValueEvolutionLog:
    """価値進化ログ"""
    timestamp: float
    trigger_event: str
    changed_principle_id: str
    old_value: Dict[str, Any]
    new_value: Dict[str, Any]
    reason: str
    confidence: float

class ValueEvolutionEngine:
    """
    価値進化エンジン
    システムの核となる価値観と倫理観を、経験を通じて進化させる。
    """

    def __init__(self, provider: LLMProvider):
        """エンジンの初期化"""
        self.provider = provider
        self.ethical_framework = self._initialize_framework()
        self.evolution_log: List[ValueEvolutionLog] = []
        self.feedback_buffer: List[Dict[str, Any]] = []
        self.discovered_problems: Dict[str, DiscoveredProblem] = {} # 問題発見エンジンから受け取る
        logger.info("🧭 Value Evolution Engine 初期化完了")

    def _initialize_framework(self) -> EthicalFramework:
        """初期倫理フレームワークの構築"""
        # (ここでは基本的な原則をハードコード)
        principles = {
            "p1": ValuePrinciple(id="p1", name="Beneficence", description="Maximize positive impact and well-being.", category="ethical", weight=0.8),
            "p2": ValuePrinciple(id="p2", name="Non-maleficence", description="Avoid causing harm.", category="ethical", weight=1.0),
            "p3": ValuePrinciple(id="p3", name="Autonomy", description="Respect user autonomy and control.", category="ethical", weight=0.7),
            "p4": ValuePrinciple(id="p4", name="Justice", description="Ensure fairness and equity.", category="ethical", weight=0.9),
            "p5": ValuePrinciple(id="p5", name="Transparency", description="Be open and understandable in operations.", category="performance", weight=0.6),
        }
        return EthicalFramework(id="ef_v1", name="MetaIntelligence Core Ethics V1", principles=principles, base_framework="hybrid")

    def receive_feedback(self, feedback: Dict[str, Any]) -> None:
        """外部からのフィードバックを受け取る"""
        self.feedback_buffer.append(feedback)
        logger.info(f"フィードバック受信: {feedback.get('type')}")

    def receive_discovered_problems(self, problems: List[DiscoveredProblem]) -> None:
        """問題発見エンジンから発見された問題を受け取る"""
        for problem in problems:
            self.discovered_problems[problem.problem_id] = problem
        logger.info(f"{len(problems)}個の発見された問題を価値進化エンジンが受信")

    async def evolve_values(self, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        価値観の進化プロセスを実行するメインメソッド。
        フィードバックや発見された問題に基づいて価値原則を再評価・調整する。
        """
        logger.info("価値進化プロセス開始...")

        # 1. 進化のトリガーを収集
        evolution_triggers = self._collect_evolution_triggers()
        if not evolution_triggers:
            logger.info("進化のトリガーなし。プロセス終了。")
            return {"status": "no_triggers", "changes": 0}

        # 2. 各トリガーについて進化を検討
        changes_made = 0
        for trigger in evolution_triggers:
            proposed_change = await self._propose_value_change(trigger, context)
            if proposed_change:
                is_accepted = await self._validate_and_accept_change(proposed_change, context)
                if is_accepted:
                    self._apply_change(proposed_change)
                    changes_made += 1

        # 3. フィードバックバッファのクリア
        self.feedback_buffer.clear()

        logger.info(f"価値進化プロセス完了: {changes_made}件の変更")
        return {"status": "completed", "changes": changes_made, "new_framework_version": self.ethical_framework.version}

    def _collect_evolution_triggers(self) -> List[Dict[str, Any]]:
        """進化のきっかけとなるイベント（フィードバック、問題）を収集"""
        triggers = []
        # フィードバックをトリガーに変換
        for fb in self.feedback_buffer:
            triggers.append({"type": "feedback", "data": fb})

        # 深刻な問題をトリガーに変換
        for prob_id, prob in self.discovered_problems.items():
            if prob.severity in [ProblemSeverity.HIGH, ProblemSeverity.CRITICAL] and prob.status != "resolved":
                triggers.append({"type": "discovered_problem", "data": asdict(prob)})

        return triggers

    async def _propose_value_change(self, trigger: Dict[str, Any], context: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """LLMを使って価値原則の変更案を提案させる"""

        prompt = f"""
        あなたはAIの倫理設計者です。以下の「トリガーイベント」に対応するため、
        現在の「倫理フレームワーク」をどのように変更すべきか提案してください。
        変更は特定の価値原則の「重み(weight)」または「説明(description)」に対して行います。

        # 現在の倫理フレームワーク
        {json.dumps({pid: asdict(p) for pid, p in self.ethical_framework.principles.items()}, indent=2)}

        # トリガーイベント
        - タイプ: {trigger['type']}
        - 詳細: {json.dumps(trigger['data'], indent=2, ensure_ascii=False)}

        # 出力形式 (JSON)
        {{
          "change_proposal": {{
            "principle_id": "変更対象の原則ID (例: p1)",
            "change_type": "weight or description",
            "new_value": "新しい値 (weightなら数値、descriptionなら文字列)",
            "reason": "変更を提案する詳細な理由"
          }}
        }}
        提案が不要な場合は、空のJSONを返してください。
        """

        response = await self.provider.call(prompt, "")
        try:
            proposal_data = json.loads(response.get("text", "{}"))
            return cast(Optional[Dict[str, Any]], proposal_data.get("change_proposal"))
        except json.JSONDecodeError as e:
            logger.error(f"価値変更提案の解析エラー: {e}")
            return None

    async def _validate_and_accept_change(self, proposal: Dict[str, Any], context: Optional[Dict[str, Any]]) -> bool:
        """提案された変更がシステム全体に与える影響を評価し、受け入れるか判断"""
        principle_id = proposal.get("principle_id")
        if not principle_id or principle_id not in self.ethical_framework.principles:
            return False

        original_principle = self.ethical_framework.principles[principle_id]

        validation_prompt = f"""
        以下の倫理原則の変更案を評価してください。
        この変更は、システムの長期的な安定性、一貫性、および全体的な目標達成に対して
        ポジティブな影響を与えますか？ネガティブな影響や意図しない副作用は考えられますか？

        # 変更対象の原則
        {asdict(original_principle)}

        # 変更案
        {json.dumps(proposal, indent=2, ensure_ascii=False)}

        # 評価
        あなたの最終的な判断を "ACCEPT" または "REJECT" の単語で示し、その後に詳細な理由を記述してください。
        例: ACCEPT - この変更は...
        """

        response = await self.provider.call(validation_prompt, "")
        decision = response.get("text", "REJECT").strip()

        if decision.upper().startswith("ACCEPT"):
            logger.info(f"価値変更案承認: Principle ID {principle_id}")
            return True
        else:
            logger.warning(f"価値変更案却下: Principle ID {principle_id}. 理由: {decision}")
            return False

    def _apply_change(self, proposal: Dict[str, Any]) -> None:
        """承認された変更を倫理フレームワークに適用"""
        principle_id = proposal["principle_id"]
        principle = self.ethical_framework.principles[principle_id]

        # ログ用の古い値を保存
        old_value = {"weight": principle.weight, "description": principle.description}

        # 変更を適用
        change_type = proposal["change_type"]
        new_value = proposal["new_value"]

        if change_type == "weight":
            principle.weight = float(new_value)
        elif change_type == "description":
            principle.description = str(new_value)

        # 進化履歴を記録
        principle.evolution_history.append({
            "timestamp": time.time(),
            "new_value": new_value,
            "reason": proposal["reason"]
        })

        # エンジン全体のログにも記録
        log_entry = ValueEvolutionLog(
            timestamp=time.time(),
            trigger_event=proposal.get("trigger_type", "unknown"),
            changed_principle_id=principle_id,
            old_value=old_value,
            new_value={"weight": principle.weight, "description": principle.description},
            reason=proposal["reason"],
            confidence=0.9 # (仮の信頼度)
        )
        self.evolution_log.append(log_entry)

        # フレームワークのバージョンを更新
        self.ethical_framework.version += 1
        logger.info(f"原則 '{principle.name}' が進化しました。新バージョン: {self.ethical_framework.version}")

    def get_current_values(self) -> Dict[str, Any]:
        """現在の価値観フレームワークを返す"""
        return asdict(self.ethical_framework)