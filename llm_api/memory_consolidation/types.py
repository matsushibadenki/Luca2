# /llm_api/memory_consolidation/types.py
# タイトル: Memory Consolidation Data Types
# 役割: 記憶統合エンジンで利用されるデータ構造をTypedDictとして厳密に定義する。

from typing import TypedDict

class ConsolidationLogEntry(TypedDict):
    """
    記憶統合ログエントリのための厳密な型定義。
    mypyの型推論エラーを回避するために使用する。
    """
    timestamp: str
    session_id: str
    integrated_entities_count: int
    integrated_relations_count: int
    integrated_facts_concepts_count: int
    knowledge_graph_updated: bool
    total_extracted_items: int
    avg_confidence: float
    summary_of_integration: str