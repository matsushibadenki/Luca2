# /llm_api/master_system/__init__.py
"""
MetaIntelligence Master System Package
全ての先進機能を統合した最高レベルのAIシステムパッケージ
"""

# facade.pyからメインのクラスをインポート
from .facade import MetaIntelligence 

# ★ 修正: orchestrator と types からのインポートを削除。
# __init__.pyでのトップレベルの循環参照を避けるため。
# これらは使用するファイルで直接インポートする必要があります。

# types.pyからデータクラスをインポート
from .types import MasterSystemState, ProblemClass, ProblemSolution

__all__ = [
    "MetaIntelligence",
    "MasterSystemState",
    "ProblemClass",
    "ProblemSolution",
    # "MasterIntegrationOrchestrator", # ★ 削除
    # "IntegrationConfig", # ★ 削除
]