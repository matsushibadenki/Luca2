# /examples/test_new_architecture.py
# タイトル: 新アーキテクチャ機能テストスクリプト
# 役割: 以下の新機能の動作を統合的にテストする。
# 1. 統合情報処理による創発 (Emergent Intelligence)
# 2. 内省的対話による自己形成 (Introspective Dialogue)
# 3. デジタルホメオスタシスによる倫理的動機付け (Digital Homeostasis)

import asyncio
import logging
import os
import sys
import json
from typing import Any

# プロジェクトルートをPythonパスに追加
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from llm_api.master_system.orchestrator import MasterIntegrationOrchestrator
from llm_api.providers import get_provider  # <<< 修正箇所
from llm_api.meta_cognition.types import IntrospectiveDialogue, DialogueTurn

# --- 初期設定 ---
# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# .envファイルから環境変数を読み込む（推奨）
try:
    from dotenv import load_dotenv
    load_dotenv()
    logging.info(".envファイルをロードしました。")
except ImportError:
    logging.warning("python-dotenvがインストールされていません。環境変数は手動で設定する必要があります。")

# --- ヘルパー関数 ---
def print_header(title: str):
    """テストケースのヘッダーをきれいに表示する"""
    border = "=" * 80
    print(f"\n{border}")
    print(f"🔬 TESTING: {title}")
    print(f"{border}\n")

def pretty_print_json(data: Any, title: str):
    """JSON互換データをきれいにインデントして表示する"""
    print(f"--- {title} ---")
    try:
        # dataclassなどもjson.dumpsでシリアライズできるようにdefaultを設定
        json_string = json.dumps(data, indent=2, ensure_ascii=False, default=lambda o: o.__dict__)
        print(json_string)
    except TypeError as e:
        logging.error(f"JSONシリアライズに失敗しました: {e}")
        print(data)
    print("-" * (len(title) + 6) + "\n")

# --- テストケース ---
async def test_emergent_intelligence(orchestrator: MasterIntegrationOrchestrator):
    """テストケース1: 創発的知能 (Emergent Intelligence)"""
    print_header("創発的知能 (Emergent Intelligence)")

    emergent_system = orchestrator.subsystems.get("emergent_intelligence")
    if not emergent_system:
        logging.error("Emergent Intelligence systemが見つかりません。")
        return

    # システムに複数の専門家の視点を動的に登録
    emergent_system.register_agent("agent_economist", None, "マクロ経済学的な視点を持つ経済学者")
    emergent_system.register_agent("agent_environmentalist", None, "地球環境の持続可能性を専門とする環境科学者")
    emergent_system.register_agent("agent_technologist", None, "革新的なテクノロジーを信奉する技術者")
    
    problem = "2050年までに世界が達成すべき最も重要な目標は何か？その理由と具体的な戦略は？"
    logging.info(f"問題提起: {problem}")

    # 統合問題解決プロセスを実行
    solution = await orchestrator.solve_ultimate_integrated_problem(problem)
    
    pretty_print_json(solution, "創発的知能の最終出力")

async def test_introspective_dialogue(orchestrator: MasterIntegrationOrchestrator):
    """テストケース2: 内省的対話 (Introspective Dialogue)"""
    print_header("内省的対話 (Introspective Dialogue)")
    
    meta_cognition_system = orchestrator.subsystems.get("meta_cognition")
    if not meta_cognition_system:
        logging.error("Meta-cognition systemが見つかりません。")
        return

    topic = "AIが人間から完全に自律した場合、その存在意義はどこに見出されるべきか？"
    logging.info(f"対話トピック: {topic}")

    # 内省的対話を進行
    dialogue_result = await meta_cognition_system.conduct_introspective_dialogue(topic)
    
    pretty_print_json(dialogue_result, "内省的対話の結果")

async def test_digital_homeostasis(orchestrator: MasterIntegrationOrchestrator):
    """テストケース3: デジタルホメオスタシス (Digital Homeostasis)"""
    print_header("デジタルホメオスタシス (Digital Homeostasis)")
    
    value_system = orchestrator.subsystems.get("value_evolution")
    if not value_system:
        logging.error("Value Evolution systemが見つかりません。")
        return
        
    print("--- 1回目の健全性チェック＆価値観調整 ---")
    initial_values = value_system.get_current_values()
    pretty_print_json(initial_values, "調整前の価値観")
    
    # ホメオスタシス維持サイクルを実行
    report1 = await value_system.maintain_homeostasis()
    if report1:
        pretty_print_json(report1, "ホメオスタシスレポート (1回目)")
    
    adjusted_values = value_system.get_current_values()
    pretty_print_json(adjusted_values, "調整後の価値観")
    
    if initial_values != adjusted_values:
        print("✅ 価値観が自律的に調整されました。")
    else:
        print("ℹ️ 価値観は安定しています。")

    print("\n--- 2回目の健全性チェック（意図的な状態変化後）---")
    # 意図的に不安定な状態（失敗した対話）をシミュレート
    meta_engine = orchestrator.subsystems.get("meta_cognition")
    if meta_engine:
        failed_dialogue = IntrospectiveDialogue(dialogue_id="dummy_fail", topic="dummy", synthesis="対話の統合に失敗しました。")
        failed_dialogue.turns.append(DialogueTurn(agent_name="批判家", opinion="全て無意味だ。論理が破綻している。"))
        failed_dialogue.turns.append(DialogueTurn(agent_name="楽観主義者", opinion="そんなことはない！可能性はある！"))
        meta_engine.dialogue_history.append(failed_dialogue)
        logging.info("（シミュレーション: 不安定な内省的対話ログを追加しました）")

    # 再度、ホメオスタシス維持サイクルを実行
    report2 = await value_system.maintain_homeostasis()
    if report2:
        pretty_print_json(report2, "ホメオスタシスレポート (2回目)")

    final_values = value_system.get_current_values()
    pretty_print_json(final_values, "最終的な価値観")

    if adjusted_values != final_values:
        print("✅ 不安定な状態を検知し、価値観がさらに調整されました。")
    else:
        print("ℹ️ 価値観は変化しませんでした。")

async def main():
    """メイン実行関数"""
    print_header("新アーキテクチャ 統合テスト開始")

    provider_name = os.getenv("LLM_PROVIDER", "gemini")
    model_name = os.getenv("LLM_MODEL")
    
    try:
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # キーワード引数を 'model_name' から 'model' に変更
        provider = get_provider(provider_name, model=model_name)
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        logging.info(f"LLMプロバイダー '{provider_name}' を使用します。")
    except ValueError as e:
        logging.error(e)
        return
    except Exception as e:
        logging.error(f"プロバイダーの初期化中に予期せぬエラーが発生しました: {e}")
        return

    # マスターオーケストレーターの初期化
    orchestrator = MasterIntegrationOrchestrator(provider)
    init_result = await orchestrator.initialize_integrated_system()
    
    if orchestrator.integration_status not in ["operational", "partially_operational"]:
        logging.error("システムの初期化に失敗しました。テストを中断します。")
        pretty_print_json(init_result, "初期化失敗レポート")
        return
    
    pretty_print_json(init_result, "システム初期化結果")

    # 各機能のテストを順次実行
    await test_emergent_intelligence(orchestrator)
    await test_introspective_dialogue(orchestrator)
    await test_digital_homeostasis(orchestrator)
    
    border = "=" * 80
    print(f"\n{border}")
    print("✅ 全てのテストが完了しました。")
    print(f"{border}\n")

if __name__ == "__main__":
    asyncio.run(main())
