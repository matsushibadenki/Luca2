# /llm_api/autonomous_learning/types.py
# タイトル: Autonomous Learning Data Types
# 役割: 自律学習システム全体で共有されるデータ構造（Enum、データクラス）を定義する。

from dataclasses import dataclass, field
from enum import Enum
from typing import List


class InterestLevel(Enum):
    """コンテンツに対する興味レベルを定義するEnum"""
    VERY_LOW = 0.1
    LOW = 0.3
    MODERATE = 0.5
    HIGH = 0.7
    VERY_HIGH = 0.9


class ContentType(Enum):
    """Webコンテンツのタイプを定義するEnum"""
    ARTICLE = "article"
    RESEARCH_PAPER = "research_paper"
    NEWS = "news"
    TUTORIAL = "tutorial"
    DOCUMENTATION = "documentation"
    FORUM_DISCUSSION = "forum_discussion"
    BLOG_POST = "blog_post"


@dataclass
class WebContent:
    """
    収集・分析されたWebコンテンツの情報を格納するデータクラス。
    """
    url: str
    title: str
    content: str
    content_type: ContentType
    discovery_timestamp: float
    interest_score: float
    learning_value: float
    summary: str
    key_concepts: List[str]
    related_topics: List[str]
    source_credibility: float


@dataclass
class LearningGoal:
    """
    自律学習システムの学習目標を表現するデータクラス。
    """
    goal_id: str
    description: str
    priority: float
    related_keywords: List[str]
    progress: float
    target_knowledge_areas: List[str]