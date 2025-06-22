# /llm_api/memory_consolidation/engine.py
# タイトル: Memory Consolidation Engine (Final Fix)
# 役割: mypyの不可解なエラーを回避するため、処理を極度に単純化して記述。PCMでは新規性スコアに基づき統合の優先度を決定する。

import logging
import asyncio
from typing import Any, Dict, List, Optional, Union

from ..providers.base import LLMProvider
from ..rag.knowledge_base import KnowledgeBase
from . import logic

logger = logging.getLogger(__name__)

class ConsolidationEngine:
    """
    記憶統合エンジン。
    短期的な学習経験を長期記憶（ナレッジグラフ）に統合するプロセスを管理する。
    """

    def __init__(self, provider: LLMProvider, knowledge_graph: Optional[KnowledgeBase] = None):
        self.provider = provider
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # 変数名のタイポを修正 (knowledge_base -> knowledge_graph)
        self.knowledge_graph = knowledge_graph or KnowledgeBase()
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        self.session_memory_buffer: List[Dict[str, Any]] = []
        # 型を明示的に Dict[str, int] と定義
        self.consolidation_stats: Dict[str, int] = {
            "total_sessions_processed": 0, "successful_consolidations": 0, "failed_consolidations": 0,
            "total_entities_extracted": 0, "total_relations_extracted": 0
        }
        logger.info("🧠 Memory Consolidation Engine 初期化完了。")

    async def consolidate_memories(self, session_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
        """単一または複数のセッション記憶を処理し、長期記憶に統合します。"""
        sessions = [session_data] if isinstance(session_data, dict) else []
        if isinstance(session_data, list):
            sessions = session_data

        if not sessions:
            return {"status": "skipped", "reason": "No session data"}

        logger.info(f"記憶統合プロセス開始: {len(sessions)}個のセッション")
        results: List[Dict[str, Any]] = []
        
        for i, session in enumerate(sessions):
            try:
                # PCMのコアロジック：新規性スコアが閾値未満の場合、処理をスキップ
                novelty_score = float(session.get("novelty_score", 0.0))
                if novelty_score < 40.0:
                    logger.info(f"セッション {session.get('session_id', i)} の新規性スコア({novelty_score:.2f})が閾値未満のため、統合をスキップします。")
                    continue
                logger.info(f"セッション {session.get('session_id', i)} の新規性スコア({novelty_score:.2f})が閾値を超えたため、統合を実行します。")
                
                current_processed = self.consolidation_stats["total_sessions_processed"]
                self.consolidation_stats["total_sessions_processed"] = current_processed + 1

                structured_info = await logic.analyze_session_data(self.provider, session)
                if not structured_info:
                    current_failed = self.consolidation_stats["failed_consolidations"]
                    self.consolidation_stats["failed_consolidations"] = current_failed + 1
                    continue
                
                update_result = await self._update_knowledge_graph(structured_info)
                
                entities_count = sum(1 for item in structured_info if item.get("type") == "entity")
                relations_count = sum(1 for item in structured_info if item.get("type") == "relation")

                current_entities = self.consolidation_stats["total_entities_extracted"]
                self.consolidation_stats["total_entities_extracted"] = current_entities + entities_count

                current_relations = self.consolidation_stats["total_relations_extracted"]
                self.consolidation_stats["total_relations_extracted"] = current_relations + relations_count
                
                session_id_val = session.get("session_id", "unknown")
                if isinstance(session_id_val, str):
                     pass

                results.append({"session_index": i, "success": True})
                
                current_successful = self.consolidation_stats["successful_consolidations"]
                self.consolidation_stats["successful_consolidations"] = current_successful + 1

            except Exception as e:
                logger.error(f"セッション {i} の統合中にエラー: {e}", exc_info=True)
                self.consolidation_stats["failed_consolidations"] += 1
                results.append({"session_index": i, "success": False, "error": str(e)})
        
        logger.info("✅ 記憶統合プロセス完了。")
        return {"status": "completed", "results": results, "stats": self.consolidation_stats}

    async def _update_knowledge_graph(self, structured_info: List[Dict[str, Any]]) -> bool:
        """抽出された情報をナレッジグラフに統合します。"""
        if not structured_info: return False
        
        knowledge_items = []
        updates_made = False
        for item in structured_info:
            if item.get("confidence", 0.5) < 0.3: continue
            content = logic.format_item_as_knowledge(item)
            if content:
                knowledge_items.append(content)
                updates_made = True
        
        if updates_made:
             logger.info(f"{len(knowledge_items)}個の新しい情報を統合（シミュレーション）")
        return updates_made
        
    def get_consolidation_statistics(self) -> Dict[str, Any]:
        return self.consolidation_stats

    def add_session_to_buffer(self, session_data: Dict[str, Any]) -> None:
        self.session_memory_buffer.append(session_data)

    async def batch_consolidate_from_buffer(self) -> Dict[str, Any]:
        if not self.session_memory_buffer:
            return {"status": "skipped"}
        sessions_to_process = self.session_memory_buffer.copy()
        self.session_memory_buffer.clear()
        return await self.consolidate_memories(sessions_to_process)