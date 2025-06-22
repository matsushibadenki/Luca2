# /llm_api/autonomous_learning/crawler.py
# タイトル: Autonomous Web Crawler
# 役割: 自律的なWeb巡回とコンテンツ分析のコアロジックを実装する（依存性注入を適用）。

import asyncio
import json
import logging
import time
import hashlib
from collections import deque
from typing import Any, Dict, List, Optional, cast

from ..providers.base import LLMProvider
from .profiler import InterestProfiler
from .types import WebContent, ContentType
# from .renderer import PlaywrightRenderer  <- この行を削除

logger = logging.getLogger(__name__)


class AutonomousWebCrawler:
    """
    自律的にWebを巡回し、興味深いコンテンツを発見・分析・学習するシステム。
    """

    def __init__(self, provider: LLMProvider, web_search_func: Any, web_fetch_func: Any, renderer: Any):
        """
        AutonomousWebCrawlerを初期化します。

        Args:
            provider: LLMプロバイダーのインスタンス。
            web_search_func: Web検索を実行する非同期関数。
            web_fetch_func: Webコンテンツを取得する非同期関数。
            renderer: Webページのレンダリングを担当するレンダラーのインスタンス。
        """
        self.provider = provider
        self.web_search = web_search_func
        self.web_fetch = web_fetch_func
        self.interest_profiler = InterestProfiler(provider)
        self.renderer = renderer # 依存性を注入

        # 学習状態の管理
        self.discovered_content: deque[WebContent] = deque(maxlen=1000)
        self.learned_knowledge: Dict[str, Any] = {}
        self.exploration_history: deque[Dict[str, Any]] = deque(maxlen=500)

        # 探索パラメータ
        self.min_interest_threshold = 0.6
        self.max_pages_per_session = 20
        self.exploration_strategies = [
            "follow_interesting_links",
            "search_related_topics",
            "explore_authoritative_sources",
        ]
        logger.info("AutonomousWebCrawlerが初期化されました。")

    async def start_autonomous_learning(
        self,
        initial_topics: Optional[List[str]] = None,
        session_duration: int = 3600
    ) -> Dict[str, Any]:
        """
        自律学習セッションを開始します。

        Args:
            initial_topics: 最初の探索トピックのリスト。
            session_duration: セッションの最大時間（秒）。

        Returns:
            セッションの結果と分析を含む辞書。
        """
        logger.info(f"自律学習セッション開始: {session_duration}秒間")
        session_start = time.time()
        session_id = f"session_{int(session_start)}"

        if not initial_topics:
            initial_topics = ["artificial intelligence", "cognitive science", "AI safety"]

        session_results: Dict[str, Any] = {
            "session_id": session_id,
            "content_discovered": [],
            "knowledge_gained": [],
            "new_interests": [],
        }
        pages_crawled = 0
        current_topics = initial_topics.copy()

        try:
            while (time.time() - session_start < session_duration and pages_crawled < self.max_pages_per_session):
                strategy = self.exploration_strategies[pages_crawled % len(self.exploration_strategies)]
                discovered_urls = await self._discover_content(current_topics, strategy)

                for url in discovered_urls[:3]:  # 1サイクルあたり最大3URL
                    if pages_crawled >= self.max_pages_per_session: break

                    content_analysis = await self._analyze_discovered_content(url)
                    if content_analysis and content_analysis.interest_score >= self.min_interest_threshold:
                        learning_result = await self._learn_from_content(content_analysis)
                        session_results["content_discovered"].append(vars(content_analysis))
                        session_results["knowledge_gained"].extend(learning_result.get("new_knowledge", []))
                        current_topics.extend(content_analysis.related_topics)
                        current_topics = list(set(current_topics))[:10]

                    pages_crawled += 1
                    await asyncio.sleep(1) # レート制限

        except Exception as e:
            logger.error(f"自律学習セッション中にエラー: {e}", exc_info=True)

        session_analysis = await self._analyze_session_results(session_results)
        logger.info(f"自律学習セッション完了: {pages_crawled}ページ探索。")

        return {
            "session_summary": session_results,
            "session_analysis": session_analysis,
            "pages_crawled": pages_crawled,
            "duration": time.time() - session_start,
            "learning_efficiency": len(session_results["knowledge_gained"]) / max(pages_crawled, 1)
        }

    async def _discover_content(self, topics: List[str], strategy: str) -> List[str]:
        """Web検索を通じて新しいコンテンツのURLを発見します。"""
        try:
            query = f"{topics[0]} {strategy.replace('_', ' ')}"
            search_results = await self.web_search(query)
            if search_results and 'results' in search_results:
                return [result['link'] for result in search_results['results'][:5] if 'link' in result]
        except Exception as e:
            logger.error(f"コンテンツ発見中にエラー: {e}")
        return []

    async def _analyze_discovered_content(self, url: str) -> Optional[WebContent]:
        """発見したURLのコンテンツを分析・評価します。"""
        try:
            # ページ取得に静的フェッチと動的レンダリングを使い分ける（例）
            # ここではシンプルにrendererを常に使う
            page_result = await self.renderer.render_page(url) if self.renderer else await self.web_fetch(url)

            if not page_result or getattr(page_result, 'error', None) or len(getattr(page_result, 'text_content', getattr(page_result, 'content', ''))) < 200:
                return None
            
            content = getattr(page_result, 'text_content', getattr(page_result, 'content', ''))
            title = getattr(page_result, 'title', 'No Title')


            interest_score, interesting_topics = await self.interest_profiler.evaluate_content_interest(content, {'title': title, 'url': url})
            content_type = await self._classify_content_type(content, title)
            summary = await self._generate_content_summary(content)
            key_concepts = await self._extract_key_concepts(content)

            return WebContent(
                url=url, title=title, content=content[:2000], content_type=content_type,
                discovery_timestamp=time.time(), interest_score=interest_score,
                learning_value=0.7, summary=summary, key_concepts=key_concepts,
                related_topics=interesting_topics, source_credibility=0.8
            )
        except Exception as e:
            logger.error(f"コンテンツ分析中にエラー ({url}): {e}")
            return None

    async def _classify_content_type(self, content: str, title: str) -> ContentType:
        """コンテンツのタイプを分類します。"""
        # (実装は簡略化)
        if "paper" in title.lower() or "arxiv" in title.lower(): return ContentType.RESEARCH_PAPER
        if "news" in title.lower(): return ContentType.NEWS
        return ContentType.ARTICLE

    async def _generate_content_summary(self, content: str) -> str:
        """LLMを用いてコンテンツの要約を生成します。"""
        summary_prompt = f"以下の内容を3文で要約してください:\n\n{content[:1500]}"
        response = await self.provider.call(summary_prompt, "")
        return cast(str, response.get("text", ""))

    async def _extract_key_concepts(self, content: str) -> List[str]:
        """LLMを用いてコンテンツからキーコンセプトを抽出します。"""
        concepts_prompt = f"以下の内容から重要な概念を5個、箇条書きで抽出してください:\n\n{content[:2000]}"
        response = await self.provider.call(concepts_prompt, "")
        concepts_text = response.get("text", "")
        return [line.strip('-* ').strip() for line in concepts_text.split('\n') if line.strip()]

    async def _learn_from_content(self, content: WebContent) -> Dict[str, Any]:
        """分析済みのコンテンツから知識を抽出し、内部ナレッジを更新します。"""
        # (この実装は簡略化されています。本来はナレッジグラフ等に知識を統合します。)
        self.discovered_content.append(content)
        return {"new_knowledge": content.key_concepts, "source": content.url}

    async def _analyze_session_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """学習セッション全体の結果を分析します。"""
        content_count = len(results["content_discovered"])
        if content_count == 0: return {}

        avg_interest = sum(c.get("interest_score", 0) for c in results["content_discovered"]) / content_count
        return {"average_interest_score": avg_interest}