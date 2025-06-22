# /llm_api/memory_consolidation/prompts.py
# タイトル: Memory Consolidation Prompts
# 役割: 記憶統合エンジンで使用されるプロンプトテンプレートを定義する。

from typing import Dict, Any

def create_analysis_prompt(session_data: Dict[str, Any]) -> str:
    """セッションデータ分析用のプロンプトを生成する。"""
    prompt = session_data.get("prompt", "")
    solution = session_data.get("solution", "")
    
    additional_context = ""
    if "v2_improvements" in session_data:
        additional_context += f"\n改善点: {session_data['v2_improvements']}"
    if "thought_process" in session_data:
        additional_context += f"\n思考過程: {session_data['thought_process']}"
    if "metadata" in session_data:
        additional_context += f"\nメタデータ: {session_data['metadata']}"

    return f"""
    以下のAIの対話（問題と解決策）から、主要なエンティティ（人物、組織、概念、技術名など）と、それらの間の関係性を特定してください。
    また、この対話から得られる新しい事実や知識、重要な洞察を抽出してください。
    
    重要: 応答は必ずJSON配列形式で返してください。各要素が抽出された情報を示します。

    # 対話データ
    問題: {prompt}
    解決策: {solution}
    {additional_context}

    # 抽出すべき情報の例:
    [
        {{
            "type": "entity",
            "name": "人工知能",
            "description": "人間の知能を模倣する技術",
            "category": "Technology",
            "confidence": 0.9
        }},
        {{
            "type": "relation",
            "subject": "人工知能",
            "predicate": "影響を与える",
            "object": "社会",
            "strength": 0.8,
            "confidence": 0.85
        }},
        {{
            "type": "fact",
            "content": "AIの倫理的課題には公平性、透明性、説明責任がある。",
            "confidence": 0.9,
            "domain": "AI Ethics"
        }},
        {{
            "type": "concept",
            "name": "予測的符号化",
            "summary": "脳が次の感覚入力を予測し、誤差のみを処理する理論。",
            "confidence": 0.8,
            "domain": "Neuroscience"
        }}
    ]
    
    注意事項:
    - 必ずJSON配列として応答してください
    - 各項目にconfidenceスコア(0.0-1.0)を含めてください
    - 明確で具体的な情報のみを抽出してください
    - 推測や不確実な情報は含めないでください
    """