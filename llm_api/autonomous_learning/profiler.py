# /llm_api/autonomous_learning/profiler.py
# タイトル: Interest Profiler
# 役割: 自律学習システムのために、Webコンテンツの興味度、学習価値、新規性などを評価する。

import asyncio  # ★ 修正: asyncioをインポート
import logging
import hashlib
from collections import defaultdict
from typing import Any, Dict, List, Tuple

from ..providers.base import LLMProvider

logger = logging.getLogger(__name__)


class InterestProfiler:
    """
    コンテンツの興味度を多角的に評価し、プロファイリングするシステム。
    """

    def __init__(self, provider: LLMProvider):
        """
        InterestProfilerを初期化します。

        Args:
            provider: LLMプロバイダーのインスタンス。
        """
        self.provider = provider
        self.interest_patterns: Dict[str, Any] = {}
        self.learned_preferences: Dict[str, float] = defaultdict(float)
        self.topic_importance: Dict[str, float] = defaultdict(float)
        logger.info("InterestProfilerが初期化されました。")

    async def evaluate_content_interest(self, content: str, metadata: Dict[str, Any]) -> Tuple[float, List[str]]:
        """
        コンテンツの総合的な興味度を評価します。

        Args:
            content: 評価対象のテキストコンテンツ。
            metadata: コンテンツのメタデータ（タイトル、URLなど）。

        Returns:
            (総合興味度スコア, 関連トピックのリスト) のタプル。
        """
        # 各評価指標を並行して計算
        assessments = await asyncio.gather(
            self._basic_interest_assessment(content, metadata),
            self._assess_learning_value(content),
            self._assess_novelty(content),
            self._assess_relevance(content),
            self._extract_interesting_topics(content)
        )

        basic_interest, learning_value, novelty_score, relevance_score, interesting_topics = assessments

        # 重み付けされた総合興味度を計算
        overall_interest = (
            basic_interest * 0.4 +
            learning_value * 0.3 +
            novelty_score * 0.2 +
            relevance_score * 0.1
        )

        logger.debug(f"コンテンツ '{metadata.get('title', 'N/A')}' の興味度評価: {overall_interest:.2f}")

        return min(1.0, overall_interest), interesting_topics

    async def _basic_interest_assessment(self, content: str, metadata: Dict[str, Any]) -> float:
        """LLMを用いて基本的な興味度を評価します。"""
        interest_prompt = f"""
        以下のコンテンツについて、AI・機械学習・認知科学・哲学・未来技術の観点から
        興味度を0.0から1.0の間の数値で評価してください。

        タイトル: {metadata.get('title', '')}
        コンテンツの冒頭: {content[:1000]}...

        評価基準:
        - 1.0: 非常に革新的で、分野に大きな影響を与える可能性のある重要な内容。
        - 0.8: 非常に興味深く、新しい洞察を与える内容。
        - 0.6: 関連分野の者にとって興味深い内容。
        - 0.4: やや興味深いが、既知の情報のまとめに近い。
        - 0.2: あまり興味を引かない一般的な内容。
        - 0.0: 全く興味なし、または無関係。

        評価スコアの数値のみを返答してください。例: 0.75
        """
        try:
            response = await self.provider.call(interest_prompt, "")
            score_text = response.get("text", "0.0").strip()
            return max(0.0, min(1.0, float(score_text)))
        except (ValueError, TypeError) as e:
            logger.warning(f"興味度スコアの解析に失敗: {e}. デフォルト値0.0を返します。")
            return 0.0

    async def _assess_learning_value(self, content: str) -> float:
        """コンテンツに含まれる学習価値をキーワードベースで評価します。"""
        learning_indicators = [
            "研究", "実験", "発見", "新しい", "革新", "方法", "技術",
            "アルゴリズム", "理論", "仮説", "証明", "分析", "データ", "結果",
            "考察", "提案", "モデル", "フレームワーク"
        ]
        content_lower = content.lower()
        indicator_count = sum(1 for indicator in learning_indicators if indicator in content_lower)
        return min(1.0, indicator_count / 10.0)  # 10個以上のキーワードで満点

    async def _assess_novelty(self, content: str) -> float:
        """コンテンツの新規性をハッシュ値を用いて簡易的に評価します。"""
        # この実装は簡略化されています。
        # 本来は、過去に学習したコンテンツのベクトル表現と比較するなど、より高度な手法が考えられます。
        content_hash = hashlib.md5(content.encode()).hexdigest()
        # ここでは、常に一定の新規性があると仮定します。
        novelty_score = 0.8
        return novelty_score

    async def _assess_relevance(self, content: str) -> float:
        """現在の学習目標との関連性を評価します。"""
        # この実装は簡略化されています。
        # 本来は、設定された学習目標との意味的な関連性を計算します。
        return 0.7

    async def _extract_interesting_topics(self, content: str) -> List[str]:
        """LLMを用いてコンテンツから興味深いトピックを抽出します。"""
        topic_prompt = f"""
        以下のコンテンツから、AIや認知科学に関連する主要なトピック、概念、キーワードを5個以内で抽出してください。

        コンテンツ:
        {content[:2000]}...

        抽出したトピックを箇条書き（- プレフィックス）で列挙してください。
        """
        try:
            response = await self.provider.call(topic_prompt, "")
            topics_text = response.get("text", "")

            topics = []
            for line in topics_text.split('\n'):
                line = line.strip()
                if line.startswith(('-', '•', '*')):
                    topic = line.lstrip('-•* ').strip()
                    if topic:
                        topics.append(topic)
            return topics[:5]
        except Exception as e:
            logger.error(f"トピック抽出中にエラー: {e}")
            return []