# /llm_api/providers/ollama.py
# タイトル: OllamaProvider with Robust Payload Construction (Final)
# 役割: 'model'パラメータがリクエストから欠落するバグを修正。

import logging
import asyncio
from typing import Any, Dict
import json

import httpx
from .base import LLMProvider, ProviderCapability
from ..config import settings
from ..emotion_core.types import EmotionCategory

logger = logging.getLogger(__name__)

class OllamaProvider(LLMProvider):
    """
    Ollamaと対話するための標準プロバイダー
    """
    def __init__(self):
        self.api_base_url = settings.OLLAMA_API_BASE_URL
        self.default_model = settings.OLLAMA_DEFAULT_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT
        super().__init__()
        logger.info(f"Ollama provider initialized with API URL: {self.api_base_url} and default model: {self.default_model}")

    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        return {
            ProviderCapability.STANDARD_CALL: True,
            ProviderCapability.ENHANCED_CALL: False,
            ProviderCapability.STREAMING: True,
            ProviderCapability.SYSTEM_PROMPT: True,
            ProviderCapability.TOOLS: False,
            ProviderCapability.JSON_MODE: True,
        }

    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        return False

    async def call(self, prompt: str, system_prompt: str = "", **kwargs: Any) -> Dict[str, Any]:
        # ... (リトライロジックは変更なし)
        try:
            return await self.standard_call(prompt, system_prompt, **kwargs)
        except Exception as e:
            return {"text": "", "error": str(e)}

    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs: Any) -> Dict[str, Any]: # 戻り値はDict[str, Any]
        """
        Ollama APIを呼び出し、標準化された辞書形式で結果を返す。
        """
        simulated_preface = ""
        if kwargs.get('steering_vector') is not None and kwargs.get('steer_emotion'):
            steered_emotion_str = kwargs['steer_emotion']
            logger.info(f"OllamaProviderが感情 '{steered_emotion_str}' のステアリングを検知しました。効果をシミュレートします。")
            try:
                if EmotionCategory(steered_emotion_str) == EmotionCategory.JOY:
                    simulated_preface = "素晴らしい一日ですね！喜んでお答えします。\n\n"
            except ValueError:
                logger.warning(f"不明な感情 '{steered_emotion_str}'")

        api_url = f"{self.api_base_url}/api/chat"
        messages = [{"role": "system", "content": system_prompt}] if system_prompt else []
        messages.append({"role": "user", "content": prompt})

        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # modelパラメータを確実に取得する
        model_to_use = kwargs.get("model") or self.default_model
        if not model_to_use:
             raise ValueError("Ollamaのモデルが指定されていません。")
        
        payload: Dict[str, Any] = {
            "model": model_to_use,
            "messages": messages,
            "stream": False,
        }
        
        allowed_options = ['temperature', 'top_p', 'top_k', 'num_ctx', 'repeat_penalty']
        options = {key: kwargs[key] for key in allowed_options if key in kwargs}
        if options:
            payload['options'] = options
            
        if kwargs.get('json_mode'):
            payload['format'] = 'json'
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(api_url, json=payload)
            if 400 <= response.status_code < 500:
                try:
                    error_detail = response.json().get('error', response.text)
                    logger.error(f"Ollama APIから4xxエラー: {response.status_code} - {error_detail}")
                except json.JSONDecodeError:
                    logger.error(f"Ollama APIから4xxエラー: {response.status_code} - {response.text}")
            response.raise_for_status()
            response_data = response.json()

        full_response = simulated_preface + response_data.get('message', {}).get('content', '')
        prompt_tokens = response_data.get("prompt_eval_count", 0)
        completion_tokens = response_data.get("eval_count", 0)

        return {
            "text": full_response,
            "model": response_data.get("model"),
            "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens, "total_tokens": prompt_tokens + completion_tokens},
            "error": None
        }