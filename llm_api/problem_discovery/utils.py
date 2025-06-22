# /llm_api/problem_discovery/utils.py
# タイトル: Problem Discovery Utility Functions
# 役割: 問題発見エンジンで利用される補助的な関数（データ前処理、後処理）を提供する。

import hashlib
import json
import logging
from collections import defaultdict
from typing import Any, Dict, List

import numpy as np
from ..providers.base import LLMProvider
from .types import (DataPattern, DiscoveredProblem, DiscoveryMethod,
                    ProblemSeverity, ProblemType)

logger = logging.getLogger(__name__)


# --- Data Pre-processing Functions ---

async def extract_data_patterns(provider: LLMProvider, data_sources: List[Dict[str, Any]]) -> List[DataPattern]:
    """
    データソースから統計的に有意なパターンを抽出します。

    Args:
        provider: 使用するLLMプロバイダー。
        data_sources: 分析対象のデータソースのリスト。

    Returns:
        抽出されたデータパターン（DataPattern）のリスト。
    """
    # (実装は簡略化されています)
    pattern_prompt = f"""
    以下のデータ群から、繰り返される興味深いパターンや相関関係を特定し、
    それぞれについて説明、頻度、統計的有意性を評価してください。

    データサンプル: {json.dumps(data_sources[:2], indent=2, ensure_ascii=False)}

    JSON形式でパターンのリストを返してください。
    [
      {{
        "description": "...",
        "frequency": 0.8,
        "statistical_significance": 0.95,
        "anomaly_indicators": ["..."],
        "related_features": ["..."]
      }}
    ]
    """
    response = await provider.call(pattern_prompt, "")
    try:
        patterns_data = json.loads(response.get("text", "[]"))
        return [DataPattern(
            pattern_id=f"p_{hashlib.md5(d.get('description','').encode()).hexdigest()[:8]}",
            description=d.get("description", ""),
            frequency=d.get("frequency", 0.0),
            statistical_significance=d.get("statistical_significance", 0.0),
            anomaly_indicators=d.get("anomaly_indicators", []),
            related_features=d.get("related_features", [])
        ) for d in patterns_data]
    except json.JSONDecodeError:
        logger.error("データパターンの抽出でJSON解析に失敗しました。")
        return []


async def detect_anomalies(provider: LLMProvider, data_sources: List[Dict[str, Any]], patterns: List[DataPattern]) -> List[Dict[str, Any]]:
    """データ内の異常値を検出します。"""
    # (実装は簡略化されています)
    logger.debug("データ異常検知を実行します（現在モック実装）。")
    return [{"anomaly_type": "unexpected_spike", "description": "Metric A spiked unexpectedly"}]


async def infer_causal_relationships(provider: LLMProvider, data_sources: List[Dict[str, Any]], patterns: List[DataPattern]) -> List[Dict[str, Any]]:
    """データ間の因果関係を推論します。"""
    # (実装は簡略化されています)
    logger.debug("因果関係の推論を実行します（現在モック実装）。")
    return [{"cause": "feature_x", "effect": "metric_y", "confidence": 0.85}]


# --- Result Post-processing Functions ---

def deduplicate_and_merge_problems(problems: List[DiscoveredProblem]) -> List[DiscoveredProblem]:
    """重複する問題を統合し、ユニークな問題のリストを作成します。"""
    unique_problems: Dict[str, DiscoveredProblem] = {}
    for problem in problems:
        if problem.problem_id not in unique_problems:
            unique_problems[problem.problem_id] = problem
        else:
            existing = unique_problems[problem.problem_id]
            existing.evidence.extend(problem.evidence)
            existing.confidence_score = max(existing.confidence_score, problem.confidence_score)
            existing.urgency_score = max(existing.urgency_score, problem.urgency_score)
    return list(unique_problems.values())


def prioritize_problems(problems: List[DiscoveredProblem]) -> List[DiscoveredProblem]:
    """問題の優先順位を決定します。"""
    severity_map = {ProblemSeverity.LOW: 1, ProblemSeverity.MODERATE: 2, ProblemSeverity.HIGH: 3, ProblemSeverity.CRITICAL: 4}
    def calculate_priority_score(p: DiscoveredProblem) -> float:
        score = (
            severity_map.get(p.severity, 0) * 0.5 +
            p.urgency_score * 0.3 +
            p.confidence_score * 0.2
        )
        return score
    return sorted(problems, key=calculate_priority_score, reverse=True)


def format_problem_summary(problem: DiscoveredProblem) -> Dict[str, Any]:
    """レポート用に問題の要約を生成します。"""
    return {
        "id": problem.problem_id,
        "title": problem.title,
        "severity": problem.severity.value,
        "confidence": f"{problem.confidence_score:.2f}",
        "urgency": f"{problem.urgency_score:.2f}",
        "method": problem.discovery_method.value
    }


def calculate_severity_distribution(problems: List[DiscoveredProblem]) -> Dict[str, int]:
    """問題リストの深刻度ごとの分布を計算します。"""
    distribution: Dict[str, int] = defaultdict(int)
    for p in problems:
        distribution[p.severity.value] += 1
    return dict(distribution)