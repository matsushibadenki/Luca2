# /llm_api/autonomous_learning/__init__.py
# タイトル: Autonomous Learning Package Initializer (Refactored)
# 役割: 自律学習システムのパッケージ初期化。リファクタリングされた各モジュールから主要クラスをインポートし、公開インターフェースを定義する。

from typing import Any

# 各モジュールから主要なクラスをインポート
from .web_crawler import AutonomousWebCrawler
from .manager import ContinuousLearningManager
from .profiler import InterestProfiler
from .types import ContentType, InterestLevel, LearningGoal, WebContent
from .enhanced_web_crawler import EnhancedAutonomousWebCrawler, RenderingConfig, RenderingMethod

# web_searchとweb_fetchは、このパッケージを利用する側で具体的な関数を注入することを想定したプレースホルダーです。
# In a real setup, these would be integrated with external APIs or local web fetching libraries.
web_search: Any = None
web_fetch: Any = None


# パッケージの外から from llm_api.autonomous_learning import * でインポートされるものを定義
__all__ = [
    "AutonomousWebCrawler",
    "EnhancedAutonomousWebCrawler",
    "ContinuousLearningManager",
    "InterestProfiler",
    "WebContent",
    "LearningGoal",
    "InterestLevel",
    "ContentType",
    "RenderingConfig",
    "RenderingMethod",
    "web_search",
    "web_fetch",
]