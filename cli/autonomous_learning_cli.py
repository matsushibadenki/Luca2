# cli/autonomous_learning_cli.py
# タイトル: 自律学習システム用CLIツール
# 役割: 自律学習システムのCLIインターフェースとメインエントリポイント

import asyncio
import argparse
import logging
import json
from typing import List, Dict, Any, Optional

from llm_api.providers import get_provider
from llm_api.autonomous_learning import AutonomousWebCrawler, ContinuousLearningManager
from llm_api.autonomous_learning.renderer import PlaywrightRenderer
from llm_api.utils.helper_functions import format_json_output

# Placeholder for actual web search and fetch tools.
# In a real setup, these would be integrated with external APIs or local web fetching libraries.
web_search: Any = None
web_fetch: Any = None

logger = logging.getLogger(__name__)

class AutonomousLearningCLI:
    """自律学習システムのCLIインターフェース"""
    
    def __init__(self):
        self.provider: Optional[Any] = None
        self.crawler: Optional[AutonomousWebCrawler] = None
        self.learning_manager: Optional[ContinuousLearningManager] = None
        self.renderer: Optional[PlaywrightRenderer] = None
    
    async def initialize(self, provider_name: str = "ollama") -> bool:
        """システムの初期化"""
        try:
            self.provider = get_provider(provider_name, enhanced=True)
            
            # Web検索・取得機能の設定
            # 実際の実装では web_search と web_fetch ツールを使用
            # from llm_api import web_search, web_fetch  # 実装時に追加
            
            # Rendererのインスタンスを生成
            self.renderer = PlaywrightRenderer()
            
            self.crawler = AutonomousWebCrawler(self.provider, web_search, web_fetch, self.renderer)
            self.learning_manager = ContinuousLearningManager(self.provider, web_search, web_fetch, self.renderer)
            
            logger.info(f"自律学習システム初期化完了 (プロバイダー: {provider_name})")
            return True
            
        except Exception as e:
            logger.error(f"初期化エラー: {e}")
            return False
    
    async def run_single_session(self, args: argparse.Namespace) -> Dict[str, Any]:
        """単発学習セッションの実行"""
        if not self.crawler:
            await self.initialize(args.provider)
        
        # 設定の調整
        if self.crawler: # Ensure crawler is not None
            self.crawler.min_interest_threshold = args.min_interest
            self.crawler.max_pages_per_session = args.max_pages
        
            logger.info(f"単発学習セッション開始:")
            logger.info(f"  期間: {args.duration}秒")
            logger.info(f"  トピック: {', '.join(args.topics)}")
            logger.info(f"  最小興味度: {args.min_interest}")
            
            result = await self.crawler.start_autonomous_learning(
                initial_topics=args.topics,
                session_duration=args.duration
            )
            
            return result
        return {"error": "Crawler not initialized."}
    
    async def setup_continuous_learning(self, args: argparse.Namespace) -> Dict[str, Any]:
        """継続学習の設定"""
        if not self.learning_manager:
            await self.initialize(args.provider)
        
        learning_intervals = {
            "daily_exploration": args.daily_duration,
            "weekly_deep_dive": args.weekly_duration,
            "monthly_review": args.monthly_duration
        }
        
        if self.learning_manager: # Ensure learning_manager is not None
            setup_result = await self.learning_manager.setup_continuous_learning(
                learning_intervals=learning_intervals,
                learning_goals=args.learning_goals
            )
            
            return setup_result
        return {"error": "Learning manager not initialized."}
    
    async def run_scheduled_session(self, args: argparse.Namespace) -> Dict[str, Any]:
        """スケジュールされたセッションの実行"""
        if not self.learning_manager:
            await self.initialize(args.provider)
        
        if self.learning_manager: # Ensure learning_manager is not None
            result = await self.learning_manager.execute_scheduled_learning(args.session_type)
            return result
        return {"error": "Learning manager not initialized."}

async def main() -> None:
    """メインCLI関数"""
    parser = argparse.ArgumentParser(
        description="MetaIntelligence 自律Web学習システム",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # 共通オプション
    parser.add_argument("--provider", default="ollama", help="LLMプロバイダー")
    parser.add_argument("--json", action="store_true", help="JSON出力")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細ログ")
    
    # サブコマンド
    subparsers = parser.add_subparsers(dest="command", help="使用可能なコマンド")
    
    # 単発学習コマンド
    single_parser = subparsers.add_parser("learn", help="単発学習セッション")
    single_parser.add_argument("--duration", type=int, default=1800, help="学習時間（秒）")
    single_parser.add_argument("--topics", nargs="+", default=["artificial intelligence"], 
                              help="探索トピック")
    single_parser.add_argument("--min-interest", type=float, default=0.6, 
                              help="最小興味度閾値")
    single_parser.add_argument("--max-pages", type=int, default=20, 
                              help="最大探索ページ数")
    
    # 継続学習設定コマンド
    continuous_parser = subparsers.add_parser("setup", help="継続学習設定")
    continuous_parser.add_argument("--daily-duration", type=int, default=1800, 
                                  help="日次学習時間（秒）")
    continuous_parser.add_argument("--weekly-duration", type=int, default=3600, 
                                  help="週次学習時間（秒）") 
    continuous_parser.add_argument("--monthly-duration", type=int, default=7200,
                                  help="月次学習時間（秒）")
    continuous_parser.add_argument("--learning-goals", nargs="+", 
                                  default=["AI研究動向", "技術革新", "応用事例"],
                                  help="学習目標")
    
    # スケジュール実行コマンド
    schedule_parser = subparsers.add_parser("run", help="スケジュール学習実行")
    schedule_parser.add_argument("session_type", 
                                choices=["daily_exploration", "weekly_deep_dive", "monthly_review"],
                                help="セッションタイプ")
    
    args = parser.parse_args()
    
    # ログレベル設定
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)
    
    # CLIインスタンス作成
    cli = AutonomousLearningCLI()
    
    try:
        if args.command == "learn":
            result = await cli.run_single_session(args)
            
            if args.json:
                print(format_json_output(result))
            else:
                print(f"🎓 学習セッション完了!")
                print(f"  探索ページ数: {result.get('pages_crawled')}")
                print(f"  発見コンテンツ: {len(result.get('session_summary', {}).get('content_discovered', []))}")
                print(f"  学習効率: {result.get('learning_efficiency'):.2f}")
                
                if result.get('session_summary', {}).get('knowledge_gained'):
                    print(f"\n📚 新たに学習した知識:")
                    for knowledge in result['session_summary']['knowledge_gained'][:5]:
                        print(f"  • {knowledge}")
        
        elif args.command == "setup":
            result = await cli.setup_continuous_learning(args)
            
            if args.json:
                print(format_json_output(result))
            else:
                print(f"⚙️  継続学習設定完了!")
                print(f"  学習スケジュール:")
                for session_type, duration in result.get('learning_schedule', {}).items():
                    print(f"    {session_type}: {duration}秒")
                print(f"  学習目標数: {len(result.get('learning_goals', []))}")
        
        elif args.command == "run":
            result = await cli.run_scheduled_session(args)
            
            if args.json:
                print(format_json_output(result))
            else:
                print(f"🚀 スケジュール学習完了!")
                print(f"  セッションタイプ: {result.get('session_type')}")
                print(f"  学習効率: {result.get('learning_result', {}).get('learning_efficiency'):.2f}")
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n学習セッションが中断されました。")
    except Exception as e:
        logger.error(f"実行エラー: {e}", exc_info=True)
        print(f"❌ エラーが発生しました: {e}")