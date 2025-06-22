# /tests/test_autonomous_learning.py
# タイトル: Autonomous Learning System Tests
# 役割: 興味プロファイラー、Webクローラー、継続学習マネージャーの動作を検証する。

import pytest
from unittest.mock import MagicMock, AsyncMock, patch

from llm_api.autonomous_learning.profiler import InterestProfiler
from llm_api.autonomous_learning.crawler import AutonomousWebCrawler
from llm_api.autonomous_learning.renderer import PlaywrightRenderer
from llm_api.providers.base import LLMProvider


@pytest.fixture
def mock_provider():
    """モックのLLMProviderを作成する"""
    provider = MagicMock(spec=LLMProvider)
    provider.call = AsyncMock()
    return provider

@pytest.mark.asyncio
async def test_interest_profiler_evaluation(mock_provider):
    """InterestProfilerがコンテンツの興味度を評価できるかをテストする。"""
    profiler = InterestProfiler(mock_provider)

    # 変更点: 内部メソッドを直接モックして、最終スコアを予測可能にする
    with patch.object(profiler, '_basic_interest_assessment', new_callable=AsyncMock, return_value=0.85), \
         patch.object(profiler, '_assess_learning_value', new_callable=AsyncMock, return_value=0.7), \
         patch.object(profiler, '_assess_novelty', new_callable=AsyncMock, return_value=0.8), \
         patch.object(profiler, '_assess_relevance', new_callable=AsyncMock, return_value=0.9), \
         patch.object(profiler, '_extract_interesting_topics', new_callable=AsyncMock, return_value=["AI Ethics", "Cognitive Science"]):

        score, topics = await profiler.evaluate_content_interest(
            "A long text about AI ethics and cognitive science.",
            {'title': 'Test Title'}
        )
        
        # 期待されるスコア: (0.85*0.4) + (0.7*0.3) + (0.8*0.2) + (0.9*0.1) = 0.34 + 0.21 + 0.16 + 0.09 = 0.8
        assert score == pytest.approx(0.8)
        assert "AI Ethics" in topics

@pytest.mark.asyncio
async def test_autonomous_crawler_learning_cycle(mock_provider):
    """AutonomousWebCrawlerが基本的な学習サイクルを実行できるかをテストする。"""
    mock_renderer = MagicMock(spec=PlaywrightRenderer)
    # 修正: text_contentを200文字以上にする
    long_text = "This is a sufficiently long test content about artificial intelligence, ensuring that the processing is not skipped due to length constraints. We need to make sure this text exceeds the two-hundred character limit to properly test the crawler's discovery and learning cycle." * 3
    mock_renderer.render_page = AsyncMock(return_value=MagicMock(
        text_content=long_text,
        title="AI Test",
        error=None
    ))
    mock_search = AsyncMock(return_value={'results': [{'link': 'http://example.com/ai'}]})
    mock_fetch = AsyncMock()

    crawler = AutonomousWebCrawler(mock_provider, mock_search, mock_fetch, mock_renderer)
    crawler.min_interest_threshold = 0.5

    with patch.object(crawler.interest_profiler, 'evaluate_content_interest', new_callable=AsyncMock) as mock_evaluate:
        mock_evaluate.return_value = (0.7, ["AI"])
        mock_provider.call.side_effect = [
            {"text": "Summary of AI content"},
            {"text": "- Artificial Intelligence"}
        ]
        result = await crawler.start_autonomous_learning(initial_topics=["AI"], session_duration=10)

        assert result['pages_crawled'] >= 1
        assert len(result['session_summary']['content_discovered']) == 1
        assert "Artificial Intelligence" in result['session_summary']['knowledge_gained'][0]
        
        mock_search.assert_awaited()
        mock_renderer.render_page.assert_awaited_with('http://example.com/ai')