# /llm_api/memory_consolidation/logic.py
# タイトル: Memory Consolidation Logic (Final Mypy Fix)
# 役割: 記憶統合エンジンから呼び出される具体的な処理ロジックを実装する。

import logging
import json
import re
from typing import Any, Dict, List, Optional
from datetime import datetime

from ..providers.base import LLMProvider
from .prompts import create_analysis_prompt
from .types import ConsolidationLogEntry

logger = logging.getLogger(__name__)

def format_item_as_knowledge(item: Dict[str, Any]) -> Optional[str]:
    """構造化されたアイテムをナレッジベース用のテキストに変換する。"""
    item_type = item.get("type")
    confidence = item.get("confidence", 0.5)
    
    if item_type in ["fact", "concept"]:
        content = item.get("content") or item.get("summary", "")
        if content and len(content.strip()) > 10:
            return f"[{item_type.upper()}] {content} (信頼度: {confidence:.2f})"
    
    elif item_type == "entity":
        name = item.get("name", "")
        description = item.get("description", "")
        if name and description:
            return f"[ENTITY] {name}: {description} (カテゴリ: {item.get('category', 'N/A')}, 信頼度: {confidence:.2f})"
            
    elif item_type == "relation":
        subject = item.get("subject", "")
        predicate = item.get("predicate", "")
        obj = item.get("object", "")
        if subject and predicate and obj:
            return f"[RELATION] {subject} {predicate} {obj} (強度: {item.get('strength', 'N/A')}, 信頼度: {confidence:.2f})"
            
    return None

async def analyze_session_data(provider: LLMProvider, session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """LLMを用いてセッションデータからエンティティ、関係性、主要な概念を抽出します。"""
    prompt = session_data.get("prompt", "")
    solution = session_data.get("solution", "")
    
    if not prompt and not solution:
        return []

    analysis_prompt = create_analysis_prompt(session_data)
    
    try:
        response = await provider.call(analysis_prompt, "")
        response_text = response.get("text", "[]")
        
        json_patterns = [r'\[.*?\]', r'```json\s*(\[.*?\])\s*```', r'```\s*(\[.*?\])\s*```']
        parsed_data = None
        for pattern in json_patterns:
            json_match = re.search(pattern, response_text, re.DOTALL)
            if json_match:
                json_string = json_match.group(1) if len(json_match.groups()) > 0 else json_match.group(0)
                try:
                    parsed_data = json.loads(json_string)
                    break
                except json.JSONDecodeError:
                    continue
        
        if parsed_data is None: return []
        return _validate_extracted_data(parsed_data)
        
    except Exception as e:
        logger.error(f"セッションデータ分析中にエラーが発生: {e}", exc_info=True)
        return []

def _validate_extracted_data(data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """抽出されたデータの検証とクリーニング"""
    if not isinstance(data, list): return []
    validated = []
    for item in data:
        if not isinstance(item, dict): continue
        item_type = item.get("type")
        if item_type not in ["entity", "relation", "fact", "concept"]: continue
        required_fields = {"entity": ["name"], "relation": ["subject", "predicate", "object"], "fact": ["content"], "concept": ["name", "summary"]}
        if any(field not in item for field in required_fields[item_type]): continue
        confidence = item.get("confidence", 0.5)
        if not isinstance(confidence, (int, float)) or not (0.0 <= confidence <= 1.0):
            item["confidence"] = 0.5
        validated.append(item)
    return validated

# --- ▼▼▼ ここから修正 ▼▼▼ ---
def record_consolidation_log(session_id: str, structured_info: List[Dict[str, Any]], update_result: bool) -> None:
    """記憶統合プロセスに関するログを記録します。"""
    
    # mypyの推論エラーを回避するため、値を先に変数として計算・定義します。
    ts: str = datetime.now().isoformat()
    entities_count: int = sum(1 for item in structured_info if item.get("type") == "entity")
    relations_count: int = sum(1 for item in structured_info if item.get("type") == "relation")
    facts_concepts_count: int = sum(1 for item in structured_info if item.get("type") in ["fact", "concept"])
    total_items: int = len(structured_info)
    avg_conf: float = (sum(item.get("confidence", 0.5) for item in structured_info) / total_items) if total_items > 0 else 0.0
    summary: str = f"Processed {total_items} items. KG updated: {update_result}"
    
    # 型が明確な変数のみを使用して辞書を構築します。
    log_entry: ConsolidationLogEntry = {
        "timestamp": ts,
        "session_id": session_id,
        "integrated_entities_count": entities_count,
        "integrated_relations_count": relations_count,
        "integrated_facts_concepts_count": facts_concepts_count,
        "knowledge_graph_updated": update_result,
        "total_extracted_items": total_items,
        "avg_confidence": avg_conf,
        "summary_of_integration": summary
    }
    
    logger.debug(f"統合ログ: {log_entry}")
# --- ▲▲▲ ここまで修正 ▲▲▲ ---