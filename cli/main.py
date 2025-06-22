# /cli/main.py

import argparse
import asyncio
import logging
import os
import sys

from dotenv import load_dotenv
load_dotenv()

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from llm_api.config import settings
from cli.handler import MetaIntelligenceCLIHandler
from cli.command_runner import CLICommandRunner
from llm_api.utils.helper_functions import format_json_output, read_from_pipe_or_file
from llm_api.emotion_core.types import EmotionCategory
from .utils import print_colored

logger = logging.getLogger(__name__)

def create_parser() -> argparse.ArgumentParser:
    """ArgumentParserを生成する関数"""
    parser = argparse.ArgumentParser(
        description="MetaIntelligence V2 統合LLM CLI",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    # providerとpromptをオプション引数に変更
    parser.add_argument("-p", "--provider", help="使用するLLMプロバイダー")
    parser.add_argument("--prompt", help="LLMへのプロンプト")
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---
    
    mode_choices = [
        'simple', 'chat', 'reasoning', 'creative-fusion', 'self-correct',
        'efficient', 'balanced', 'decomposed', 'adaptive', 'paper_optimized', 'parallel',
        'quantum_inspired', 'edge', 'speculative_thought', 'self_discover'
    ]
    parser.add_argument("--mode", default=settings.V2_DEFAULT_MODE, choices=mode_choices, help="実行モード")
    parser.add_argument("--model", help="使用するモデル名")
    parser.add_argument("-f", "--file", help="ファイルからプロンプトを読み込み")
    parser.add_argument("--system-prompt", help="システムプロンプト")
    parser.add_argument("--temperature", type=float, help="生成の多様性")
    parser.add_argument("--max-tokens", type=int, help="最大トークン数")
    parser.add_argument("--json", action="store_true", help="JSON出力")

    perf_group = parser.add_argument_group('Performance Options')
    perf_group.add_argument("--n-gpu-layers", type=int, help="GPUにオフロードするレイヤー数")

    admin_group = parser.add_argument_group('Admin Commands')
    admin_group.add_argument("--list-providers", action="store_true", help="プロバイダー一覧表示")
    admin_group.add_argument("--system-status", action="store_true", help="システム状態表示")
    admin_group.add_argument("--health-check", action="store_true", help="健全性チェック実行")
    admin_group.add_argument("--troubleshooting", action="store_true", help="トラブルシューティングガイド")

    v2_group = parser.add_argument_group('V2 Options')
    v2_group.add_argument("--force-v2", action="store_true", help="V2機能強制使用")
    v2_group.add_argument("--no-fallback", action="store_true", help="フォールバック無効")
    v2_group.add_argument("--no-real-time-adjustment", dest="real_time_adjustment", action="store_false", help="リアルタイム複雑性調整を無効化")
    
    emotion_group = parser.add_argument_group('Emotion Steering Options (Experimental)')
    emotion_group.add_argument("--steer-emotion", type=str, choices=[e.name.lower() for e in EmotionCategory], help="LLMの出力感情を意図した方向へ誘導します。")
    emotion_group.add_argument("--steering-intensity", type=float, default=5.0, help="感情ステアリングの強度。")
    
    feedback_group = parser.add_argument_group('Learning Feedback Options')
    feedback_group.add_argument("--feedback", choices=['good', 'bad'], help="Provide feedback on the response quality.")
    
    rag_group = parser.add_argument_group('RAG Options')
    rag_group.add_argument("--rag", dest="use_rag", action="store_true", help="RAG機能を有効化")
    rag_group.add_argument("--knowledge-base", dest="knowledge_base_path", help="RAGが使用するナレッジベースのパス")
    rag_group.add_argument("--wikipedia", dest="use_wikipedia", action="store_true", help="RAGでWikipediaを使用")
    
    return parser

async def main():
    """CLIのメイン非同期関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    command_runner = CLICommandRunner()

    # プロンプトを必須としないコマンドを先に処理
    if args.list_providers:
        await command_runner.list_all_providers()
        return
    if args.system_status:
        await command_runner.show_system_status()
        return
    if args.health_check:
        if not args.provider:
            parser.error("--health-checkには--providerの指定が必要です。")
        await command_runner.run_health_check(args.provider)
        return
    if args.troubleshooting:
        command_runner.run_troubleshooting_guide()
        return

    # 通常実行時の必須引数をチェック
    if not args.provider:
        parser.error("プロバイダーが指定されていません (--provider <name>)。")
    
    prompt = await read_from_pipe_or_file(args.prompt, args.file)
    if not prompt:
        parser.error("プロンプトが指定されていません (--prompt <text> または --file <path>)。")

    try:
        cli_handler = MetaIntelligenceCLIHandler()
        kwargs_for_handler = {k: v for k, v in vars(args).items() if k not in ['provider', 'prompt']}

        response = await cli_handler.process_request(args.provider, prompt, **kwargs_for_handler)
        
        if args.json:
            print(format_json_output(response))
        else:
            if response.get("error"):
                print_colored(f"エラー: {response['error']}", "red")
                if response.get("suggestions"):
                    print("\n提案:")
                    for suggestion in response["suggestions"]:
                        print(f"- {suggestion}")
            else:
                print(response.get("text", ""), end='')

    except KeyboardInterrupt:
        print_colored("\n[INFO] プロセスが中断されました。", "yellow")
    except Exception as e:
        logger.critical(f"予期しない致命的エラー: {e}", exc_info=True)
        print_colored(f"\n[ERROR] 予期せぬエラーが発生しました: {e}", "red")
    
    finally:
        logger.debug("シャットダウン前の待機処理...")
        await asyncio.sleep(0.1)
        logger.debug("待機処理完了。")


if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    from llm_api import setup_logging
    setup_logging()
    asyncio.run(main())