# llm_api/autonomous_action/orchestrator.py
# タイトル: Autonomous Action Orchestrator
# 役割: トリガーされた行動要求に基づき、適切なツールを選択・実行する。

import logging
from typing import Dict, Any, Optional, Callable

from ..providers.base import LLMProvider
from ..emotion_core.types import ActionRequest

logger = logging.getLogger(__name__)

class ActionOrchestrator:
    """
    自律的な行動要求を解釈し、適切なツールを実行するオーケストレーター。
    """

    def __init__(self, provider: LLMProvider, tools: Dict[str, Callable]):
        """
        ActionOrchestratorを初期化します。

        Args:
            provider (LLMProvider): 検索クエリ生成などに使用するLLMプロバイダー。
            tools (Dict[str, Callable]): "web_search"などのアクション名と、
                                         対応する実行可能な関数（ツール）のマッピング。
        """
        self.provider = provider
        self.tools = tools
        logger.info(f"ActionOrchestrator initialized with tools: {list(tools.keys())}")

    async def execute_action(self, request: ActionRequest) -> Optional[Dict[str, Any]]:
        """
        行動要求に応じて、対応するアクションを実行します。

        Args:
            request (ActionRequest): EmotionActionTriggerから発行された行動要求。

        Returns:
            Optional[Dict[str, Any]]: ツールの実行結果。
        """
        action_name = request.requested_action
        if action_name not in self.tools:
            logger.error(f"要求されたアクション '{action_name}' に対応するツールが見つかりません。")
            return None

        logger.info(f"アクション '{action_name}' の実行を開始します。")

        if action_name == "web_search":
            return await self._handle_web_search(request)
        
        # 将来的に他のアクション（例：データベース検索、コード実行など）を追加可能
        # elif action_name == "database_query":
        #     return await self._handle_database_query(request)

        logger.warning(f"アクション '{action_name}' のハンドラーが実装されていません。")
        return None

    async def _handle_web_search(self, request: ActionRequest) -> Optional[Dict[str, Any]]:
        """
        Web検索アクションを処理します。LLMを用いて最適なクエリを生成し、検索を実行します。

        Args:
            request (ActionRequest): Web検索の行動要求。

        Returns:
            Optional[Dict[str, Any]]: Web検索の結果。
        """
        # 1. コンテキストから検索クエリをLLMに生成させる
        context_summary = str(request.context.get("prompt_history", ""))
        if not context_summary:
            logger.warning("Web検索のためのコンテキストが空です。検索を中止します。")
            return None

        query_generation_prompt = f"""
以下の対話コンテキストは、AIが「興味」を持った内容です。
この興味を満たすためにWebで検索するべき、最も効果的で簡潔な検索キーワードを生成してください。
キーワードのみを返答してください。

# 対話コンテキスト
---
{context_summary[-1000:]} # 直近1000文字のコンテキストを使用
---

# 生成すべき検索キーワード:
"""
        
        try:
            response = await self.provider.call(query_generation_prompt)
            search_query = response.get("text", "").strip()

            if not search_query:
                logger.error("LLMによる検索クエリの生成に失敗しました。")
                return None
            
            logger.info(f"生成された検索クエリ: '{search_query}'")

            # 2. 検索ツールの実行
            web_search_tool = self.tools["web_search"]
            search_results = await web_search_tool(search_query)
            
            return {"action": "web_search", "query": search_query, "results": search_results}

        except Exception as e:
            logger.error(f"Web検索アクションの実行中にエラーが発生しました: {e}", exc_info=True)
            return None