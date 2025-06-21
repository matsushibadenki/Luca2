# llm_api/tool_integrations/web_search_tool.py
# タイトル: Web Search Tool (Corrected)
# 役割: SerpApiを使用してWeb検索を実行し、結果を返す。ImportErrorを修正済み。

import asyncio
import logging
from typing import List, Dict, Optional, Any

# 修正: 'GoogleSearch' の代わりに 'Client' をインポートする
from serpapi import Client as SerpApiClient

from ..config import settings

logger = logging.getLogger(__name__)

async def search(query: str, num_results: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    与えられたクエリでWeb検索を実行し、結果のリストを返します。
    この関数は同期的なライブラリを非同期で呼び出すため、asyncio.to_threadを使用します。

    Args:
        query (str): 検索するキーワード。
        num_results (int): 取得する検索結果の数。

    Returns:
        Optional[List[Dict[str, Any]]]: 検索結果のリスト。各結果は辞書型。
                                         APIキー未設定やエラーの場合はNoneを返す。
    """
    api_key = settings.SERPAPI_API_KEY
    if not api_key:
        logger.warning("SERPAPI_API_KEYが.envファイルに設定されていません。Web検索はスキップされます。")
        return None

    logger.info(f"SerpApiを使用してWeb検索を実行します: '{query}'")

    search_params = {
        "q": query,
        "engine": "google",
        "google_domain": "google.com",
        "gl": "jp",
        "hl": "ja",
        "num": num_results
    }

    try:
        # 修正: クライアントの初期化と呼び出し方法を変更
        client = SerpApiClient(api_key=api_key)
        
        loop = asyncio.get_event_loop()
        
        # 同期的なsearch()を別スレッドで実行
        results_data = await loop.run_in_executor(
            None,  # Default executor
            lambda: client.search(search_params)
        )

        if not results_data or "error" in results_data:
            error_message = results_data.get("error", "Unknown API error")
            logger.error(f"SerpApiからのエラー応答: {error_message}")
            return None

        # "organic_results" から必要な情報を抽出して整形
        organic_results = results_data.get("organic_results", [])
        formatted_results = [
            {
                "position": result.get("position"),
                "title": result.get("title"),
                "link": result.get("link"),
                "snippet": result.get("snippet"),
                "source": result.get("source"),
            }
            for result in organic_results
        ]
        
        logger.info(f"{len(formatted_results)} 件の検索結果を取得しました。")
        return formatted_results

    except Exception as e:
        logger.error(f"SerpApiによるWeb検索中に予期せぬエラーが発生しました: {e}", exc_info=True)
        return None