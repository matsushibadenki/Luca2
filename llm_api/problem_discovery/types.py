# /llm_api/problem_discovery/types.py
# タイトル: Problem Discovery Data Types
# 役割: 問題発見エンジンで利用されるデータ構造（Enum、データクラス）を定義する。

import time
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, List


class ProblemType(Enum):
    """問題のタイプ"""
    SYSTEMIC = "systemic"
    OPERATIONAL = "operational"
    ETHICAL = "ethical"
    STRATEGIC = "strategic"
    EMERGENT = "emergent"


class ProblemSeverity(Enum):
    """問題の深刻度"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class DiscoveryMethod(Enum):
    """問題の発見手法"""
    PATTERN_ANALYSIS = "pattern_analysis"
    ANOMALY_DETECTION = "anomaly_detection"
    CAUSAL_INFERENCE = "causal_inference"
    EMERGENT_SYNTHESIS = "emergent_synthesis"
    META_ANALYSIS = "meta_analysis"


@dataclass
class DiscoveredProblem:
    """発見された問題を表すデータクラス"""
    problem_id: str
    title: str
    description: str
    problem_type: ProblemType
    severity: ProblemSeverity
    discovery_method: DiscoveryMethod
    evidence: List[Dict[str, Any]]
    affected_domains: List[str]
    potential_impacts: List[str]
    confidence_score: float  # 0.0 - 1.0
    urgency_score: float  # 0.0 - 1.0
    discovery_timestamp: float = field(default_factory=time.time)
    status: str = "new"  # new, under_review, acknowledged, resolved

    def to_dict(self) -> Dict[str, Any]:
        """データクラスを辞書に変換します。"""
        return asdict(self)


@dataclass
class DataPattern:
    """データから抽出されたパターンを表すデータクラス"""
    pattern_id: str
    description: str
    frequency: float
    statistical_significance: float
    anomaly_indicators: List[str]
    related_features: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """データクラスを辞書に変換します。"""
        return asdict(self)