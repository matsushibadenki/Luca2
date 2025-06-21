# /build_emotion_space.py
# タイトル: Emotion Space Builder Script
# 役割: 感情とSAE特徴のマッピングファイル(emotion_mapping.json)を生成するためのワンタイムスクリプト。

import json
import logging
import sys
from llm_api.emotion_core.sae_manager import SAEManager
from llm_api.emotion_core.emotion_space import EmotionSpace
from llm_api.providers import get_provider
from dotenv import load_dotenv

# 注: このスクリプトはLLMへのAPIコールを多数行い、計算に時間がかかります。

# --- 設定 ---
SAE_RELEASE = "gemma-scope-2b-pt-att"
SAE_ID = "layer_9/width_16k/average_l0_34"
CONCEPT_SETS_PATH = "data/emotion_concepts/english.json" # このファイルが別途必要
OUTPUT_MAPPING_PATH = "config/emotion_mapping.json"
PROVIDER_NAME = "ollama" # LLMへの単語入力に使用

# ロギング設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_dummy_concept_file():
    """ダミーのコンセプトセットファイルを作成する"""
    dummy_data = {
        "joy": ["joy", "happy", "cheerful", "glee", "delight"],
        "sadness": ["sadness", "unhappy", "sorrow", "grief", "misery"],
        "interest": ["interest", "curiosity", "fascination", "attention", "intrigue"]
    }
    import os
    os.makedirs(os.path.dirname(CONCEPT_SETS_PATH), exist_ok=True)
    with open(CONCEPT_SETS_PATH, 'w', encoding='utf-8') as f:
        json.dump(dummy_data, f, indent=2)
    logger.info(f"ダミーのコンセプトセットファイルを作成しました: {CONCEPT_SETS_PATH}")

async def main():
    logger.info("感情空間マッピングの構築を開始します...")
    
    # 事前にコンセプトファイルが存在するかチェック、なければダミーを作成
    import os
    if not os.path.exists(CONCEPT_SETS_PATH):
        create_dummy_concept_file()

    # DI (依存性注入) の設定
    try:
        load_dotenv()
        # 注: EmotionSpaceの構築にはLLMエンジンが必要だが、現在の設計では
        # LLMInferenceEngineが明確に分離されていないため、Providerを直接使う。
        # 本来はLLMInferenceEngineを渡すのが望ましい。
        llm_provider = get_provider(PROVIDER_NAME)
        
        # 簡易的なLLMエンジンとして振る舞うラッパーを作成
        class SimpleLLMEngineWrapper:
            def __init__(self, provider):
                self._provider = provider
            def get_hidden_states_for_text(self, text: str):
                # この機能は実際のLLMの内部実装に依存するため、ここではダミーのテンソルを返す
                logger.warning(f"'{text}'の隠れ状態取得はダミーです。実際の構築にはLLMの内部アクセスが必要です。")
                import torch
                # SAEの入力次元に合わせる (仮: 2048)
                return torch.randn(1, 1, 2048)

        llm_engine_dummy = SimpleLLMEngineWrapper(llm_provider)

        sae_manager = SAEManager(release=SAE_RELEASE, sae_id=SAE_ID)
        emotion_space = EmotionSpace(llm_engine_dummy, sae_manager)
        
        # 感情空間を構築
        emotion_space.build_space(CONCEPT_SETS_PATH)
        
        # 結果をファイルに保存
        emotion_space.save_mapping(OUTPUT_MAPPING_PATH)
        
        logger.info("感情空間マッピングの構築が完了しました！")

    except Exception as e:
        logger.error(f"構築中にエラーが発生しました: {e}", exc_info=True)

if __name__ == "__main__":
    import asyncio
    # Windows対応
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())