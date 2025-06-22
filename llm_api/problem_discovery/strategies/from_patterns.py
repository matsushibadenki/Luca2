# /llm_api/problem_discovery/strategies/from_patterns.py
# タイトル: Discovery Strategy from Data Patterns
# 役割: 抽出されたデータパターンに基づき、潜在的な問題を特定・生成する発見戦略。

import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional

from ...providers.base import LLMProvider
from ..types import (DataPattern, DiscoveredProblem, DiscoveryMethod,
                     ProblemSeverity, ProblemType)

logger = logging.getLogger(__name__)


async def discover_from_patterns(
    provider: LLMProvider,
    patterns: List[DataPattern],
    context: Dict[str, Any]
) -> List[DiscoveredProblem]:
    """
    抽出されたデータパターンから問題を発見します。
    統計的に有意なパターンをLLMに提示し、潜在的な問題を生成させます。

    Args:
        provider: 使用するLLMプロバイダー。
        patterns: 分析対象のデータパターンのリスト。
        context: 発見プロセスのコンテキスト情報。

    Returns:
        発見された問題（DiscoveredProblem）のリスト。
    """
    discovered: List[DiscoveredProblem] = []
    for pattern in patterns:
        # 信頼性が高い（統計的有意性が70%超の）パターンに注目
        if pattern.statistical_significance > 0.7:
            problem = await _create_problem_from_pattern(provider, pattern, context)
            if problem:
                discovered.append(problem)
    return discovered


async def _create_problem_from_pattern(
    provider: LLMProvider,
    pattern: DataPattern,
    context: Dict[str, Any]
) -> Optional[DiscoveredProblem]:
    """
    単一のデータパターンから、LLMを用いて具体的な問題を生成します。

    Args:
        provider: 使用するLLMプロバイダー。
        pattern: 問題生成の元となるデータパターン。
        context: 発見プロセスのコンテキスト情報。

    Returns:
        生成された問題オブジェクト、または生成に失敗した場合はNone。
    """
    problem_prompt = f"""
    以下のデータパターンは、システムやビジネスにおける潜在的な問題を示唆している可能性があります。
    このパターンから考えられる具体的な問題を特定し、その詳細をJSON形式で記述してください。

    # 分析対象のデータパターン
    - 説明: {pattern.description}
    - 発生頻度: {pattern.frequency:.2f}
    - 統計的有意性: {pattern.statistical_significance:.2f}
    - 関連する異常指標: {pattern.anomaly_indicators}
    - ドメインコンテキスト: {context.get('domain_description', '指定なし')}

    # 出力すべきJSONのフィールド
    - "title": 問題の簡潔なタイトル
    - "description": 問題がなぜ重要か、どのような影響があるかを含む詳細な説明
    - "problem_type": ["systemic", "operational", "ethical", "strategic", "emergent"] から選択
    - "severity": ["low", "moderate", "high", "critical"] から選択
    - "affected_domains": 影響を受ける可能性のあるドメインのリスト
    - "potential_impacts": 考えられる具体的な負の影響のリスト
    - "urgency": 緊急度 (0.0-1.0の数値)
    """
    response = await provider.call(problem_prompt, "")
    try:
        problem_data = json.loads(response.get("text", "{}"))
        if not problem_data or 'title' not in problem_data:
            logger.warning(f"パターンからの問題生成に失敗（不正なJSON）: {pattern.pattern_id}")
            return None

        return DiscoveredProblem(
            problem_id=f"prob_{hashlib.md5(problem_data['title'].encode()).hexdigest()[:10]}",
            title=problem_data.get("title"),
            description=problem_data.get("description"),
            problem_type=ProblemType(problem_data.get("problem_type", "systemic")),
            severity=ProblemSeverity(problem_data.get("severity", "moderate")),
            discovery_method=DiscoveryMethod.PATTERN_ANALYSIS,
            evidence=[{"pattern": pattern.to_dict()}],
            affected_domains=problem_data.get("affected_domains", []),
            potential_impacts=problem_data.get("potential_impacts", []),
            confidence_score=float(pattern.statistical_significance),
            urgency_score=float(problem_data.get("urgency", 0.5)),
            discovery_timestamp=time.time()
        )
    except (json.JSONDecodeError, ValueError, KeyError) as e:
        logger.error(f"パターンからの問題生成でエラー: {e}")
        return None