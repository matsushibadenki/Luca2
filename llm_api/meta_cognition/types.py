# /llm_api/meta_cognition/types.py
# タイトル: Meta-Cognition Data Types
# 役割: メタ認知システムで使われるデータ構造（Enum、データクラス）を定義する。

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class CognitiveState(Enum):
    """
    システムの認知状態を表現するEnum。
    思考プロセスの各段階を定義します。
    """
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    SYNTHESIZING = "synthesizing"
    EVALUATING = "evaluating"
    REFLECTING = "reflecting"
    ADAPTING = "adapting"
    IDLE = "idle"


@dataclass
class ThoughtTrace:
    """
    思考の軌跡の一単位を記録するためのデータクラス。
    メタ認知分析の基礎データとなります。
    """
    timestamp: float
    cognitive_state: CognitiveState
    input_context: str
    reasoning_step: str
    confidence_level: float
    resource_usage: Dict[str, Any]
    intermediate_outputs: List[str] = field(default_factory=list)
    decision_points: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class MetaCognitiveInsight:
    """
    メタ認知による自己分析から得られた洞察を表現するデータクラス。
    システムの自己改善に利用されます。
    """
    insight_type: str  # 例: "efficiency_issue", "confirmation_bias"
    description: str
    confidence: float
    suggested_improvement: str
    impact_assessment: Dict[str, float]  # 例: {"efficiency": 0.3, "accuracy": 0.2}