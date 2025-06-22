# /llm_api/dynamic_architecture/types.py
# タイトル: Dynamic Architecture Data Types
# 役割: 動的アーキテクチャシステムの中核となるデータ構造、列挙型、抽象基底クラスを定義します。

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, TypedDict

# --- Enums ---

class ComponentType(Enum):
    """システム構成要素のタイプ"""
    ANALYZER = "analyzer"
    REASONER = "reasoner"
    SYNTHESIZER = "synthesizer"
    VALIDATOR = "validator"
    OPTIMIZER = "optimizer"
    REFLECTOR = "reflector"

class ComponentState(Enum):
    """構成要素の状態"""
    INACTIVE = "inactive"
    ACTIVE = "active"
    OPTIMIZING = "optimizing"
    LEARNING = "learning"
    EVOLVING = "evolving"

# --- Dataclasses ---

@dataclass
class ComponentPerformance:
    """構成要素のパフォーマンス記録"""
    success_rate: float = 0.0
    avg_execution_time: float = 0.0
    quality_score: float = 0.0
    resource_efficiency: float = 0.0
    learning_rate: float = 0.0
    adaptation_count: int = 0

@dataclass
class ArchitectureBlueprint:
    """アーキテクチャ設計図"""
    component_types: List[ComponentType]
    connection_matrix: Dict[str, List[str]]
    execution_flow: List[str]
    optimization_targets: Dict[str, float]
    constraints: Dict[str, Any]

# ★★★ ここに新しいTypedDictを追加 ★★★
class ArchitectureStatus(TypedDict):
    """アーキテクチャの現在の状態とパフォーマンスメトリクス"""
    initialized: bool
    component_count: int
    performance_history_length: int
    evolution_count: int
    current_performance: float

# --- Abstract Base Classes ---

class AdaptiveComponent(ABC):
    """適応可能な構成要素の基底クラス"""
    
    def __init__(self, component_id: str, component_type: ComponentType):
        self.component_id = component_id
        self.component_type = component_type
        self.state = ComponentState.INACTIVE
        self.performance = ComponentPerformance()
        self.config: Dict[str, Any] = {}
        self.connections: List[Any] = []
        
    @abstractmethod
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """構成要素の実行"""
        pass
    
    @abstractmethod
    async def self_optimize(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """自己最適化"""
        pass
    
    @abstractmethod
    async def learn_from_experience(self, experiences: List[Dict[str, Any]]) -> None:
        """経験からの学習"""
        pass
    
    async def adapt_to_context(self, context: Dict[str, Any]) -> None:
        """コンテキストへの適応"""
        self.state = ComponentState.LEARNING
        adaptation_strategy = await self._analyze_context_requirements(context)
        await self._implement_adaptation(adaptation_strategy)
        self.performance.adaptation_count += 1
        self.state = ComponentState.ACTIVE
    
    async def _analyze_context_requirements(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """コンテキスト要求の分析"""
        return {
            "required_capabilities": context.get("required_capabilities", []),
            "performance_targets": context.get("performance_targets", {}),
            "resource_constraints": context.get("resource_constraints", {})
        }
    
    async def _implement_adaptation(self, strategy: Dict[str, Any]) -> None:
        """適応戦略の実装"""
        for key, value in strategy.items():
            if key in self.config:
                self.config[key] = value