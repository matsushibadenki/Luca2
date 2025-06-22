# /llm_api/dynamic_architecture/evaluators.py
# タイトル: Architectural Evaluators and Allocators
# 役割: パフォーマンス評価とリソース割り当てのための補助クラス群。

from collections import defaultdict, deque
from typing import Any, Deque, Dict, cast


class PerformanceEvaluator:
    """パフォーマンス評価エンジン"""

    def __init__(self) -> None:
        """パフォーマンス評価器を初期化します。"""
        self.metric_history: Dict[str, Deque[float]] = defaultdict(lambda: deque(maxlen=100))
        self.weights: Dict[str, float] = {
            "response_time": -0.3,
            "accuracy": 0.5,
            "resource_usage": -0.2
        }

    async def _calculate_weighted_score(self, metrics: Dict[str, float]) -> float:
        """重み付けされたパフォーマンススコアを計算します。"""
        score = sum(metrics.get(k, 0) * w for k, w in self.weights.items())
        return cast(float, score)


class ResourceAllocator:
    """リソース割り当てエンジン"""

    def __init__(self) -> None:
        """リソース割り当て器を初期化します。"""
        self.resource_limits = {"cpu": 8, "memory": 16384, "gpu": 1}
        self.current_allocations: Dict[str, Dict[str, Any]] = {}
        self.cost_factors: Dict[str, float] = {"cpu": 0.1, "memory": 0.05}

    async def _calculate_cost(self, allocation: Dict[str, Any]) -> float:
        """割り当てられたリソースのコストを計算します。"""
        cost = 0.0
        for component, resources in allocation.items():
            cost += resources.get("cpu", 0) * self.cost_factors["cpu"]
            cost += resources.get("memory", 0) * self.cost_factors["memory"]
        return cast(float, cost)