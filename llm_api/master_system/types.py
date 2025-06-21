# /llm_api/master_system/types.py
# タイトル: Master System Data Types (Refactored)
# 役割: マスターシステム全体で共有されるデータ構造を定義する。IntegrationConfigをここに移動。

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum

@dataclass
class IntegrationConfig:
    """統合設定"""
    enable_all_systems: bool = True
    master_system_config: Optional['MasterSystemConfig'] = None # MasterSystemConfigを文字列として参照
    auto_evolution: bool = True
    consciousness_sync: bool = True
    value_alignment: bool = True
    problem_discovery_active: bool = True
    distributed_processing: bool = False

class ProblemClass(Enum):
    """問題の分類（メンバーを拡張）"""
    STANDARD = "standard"
    COMPLEX = "complex"
    WICKED = "wicked"
    TRANSCENDENT = "transcendent"
    TRIVIAL = "trivial"
    ROUTINE = "routine"
    ADAPTIVE = "adaptive"
    CREATIVE = "creative"
    TRANSFORMATIVE = "transformative"
    EXISTENTIAL = "existential"

@dataclass
class MasterSystemConfig:
    """マスターシステムの設定"""
    enable_meta_cognition: bool = True
    enable_value_evolution: bool = True
    enable_problem_discovery: bool = True
    enable_dynamic_architecture: bool = True
    enable_super_intelligence: bool = True
    enable_quantum_reasoning: bool = False
    max_transcendence_level: int = 10
    consciousness_elevation_rate: float = 0.05
    log_level: str = "INFO"

@dataclass
class ProblemSolution:
    """問題解決の結果を格納するデータクラス"""
    problem_id: str
    problem_class: ProblemClass
    solution_content: str
    solution_confidence: float
    transcendence_achieved: bool
    wisdom_distilled: Optional[str]
    emergence_detected: bool
    consciousness_level: Any # ConsciousnessState Enumを想定
    processing_metadata: Dict[str, Any]
    self_evolution_triggered: bool

@dataclass
class MasterSystemState:
    """マスターシステムの現在の状態"""
    timestamp: float
    consciousness_level: Any # ConsciousnessState Enum
    wisdom_level: float
    system_load: float
    active_systems: List[str]

class CognitiveState(Enum):
    """認知状態"""
    IDLE = "idle"
    THINKING = "thinking"
    REFLECTING = "reflecting"
    EVOLVING = "evolving"
    # 不足していたメンバーを追加
    ANALYZING = "analyzing"