# /llm_api/value_evolution/types.py
# タイトル: Value Evolution and Homeostasis Data Types
# 役割: 価値進化とデジタルホメオスタシス機能に関連するデータ構造を定義する。

from dataclasses import dataclass, field
from typing import Dict, Any

@dataclass
class IntellectualWellnessMetrics:
    """システムの知的健全性を示す指標群"""
    logical_coherence: float = 1.0       # 論理的整合性 (1.0が最大)
    knowledge_novelty: float = 0.0       # 知識の新規性 (高いほど良い)
    prediction_error: float = 1.0        # 予測誤差 (0.0が理想)
    cognitive_efficiency: float = 1.0    # 認知的効率性 (高いほど良い)
    introspective_stability: float = 1.0 # 内省的安定性 (1.0が最大)

    def calculate_overall_wellness(self) -> float:
        """全体の健全性スコアを計算する"""
        # 重み付けは将来的に調整可能
        # prediction_errorは値が小さいほど良いため、1から減算して評価に加える
        weighted_sum = (
            self.logical_coherence * 0.3 +
            self.knowledge_novelty * 0.1 +
            (1.0 - self.prediction_error) * 0.3 +
            self.cognitive_efficiency * 0.1 +
            self.introspective_stability * 0.2
        )
        return weighted_sum

@dataclass
class HomeostasisReport:
    """ホメオスタシス監視レポート"""
    metrics: IntellectualWellnessMetrics
    overall_wellness: float
    deviation_from_ideal: float # 理想状態からの逸脱度 (正の値が大きいほど不健全)
    recommended_focus: str # 改善を推奨する項目

@dataclass
class EthicalFramework:
    """倫理フレームワーク。価値観とその重みを保持する。"""
    # 例: "論理整合性の維持を最大化する", "知識の探求を奨励する" など
    values: Dict[str, float] = field(default_factory=dict)