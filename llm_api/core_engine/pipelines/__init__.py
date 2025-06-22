# /llm_api/core_engine/pipelines/__init__.py
# タイトル: Pipeline Package Initializer
# 役割: 全てのパイプラインの統一インターフェース

from .adaptive import AdaptivePipeline
from .parallel import ParallelPipeline
from .quantum_inspired import QuantumInspiredPipeline
from .speculative import SpeculativePipeline
from .self_discover import SelfDiscoverPipeline # ★★★ 追加 ★★★

__all__ = [
    "AdaptivePipeline",
    "ParallelPipeline", 
    "QuantumInspiredPipeline",
    "SpeculativePipeline",
    "SelfDiscoverPipeline", # ★★★ 追加 ★★★
]