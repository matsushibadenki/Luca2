# /llm_api/providers/openai.py
import logging
from typing import Any, Dict, cast 

from openai import AsyncOpenAI, APIConnectionError, RateLimitError, APIStatusError
from .base import LLMProvider, ProviderCapability, Awaitable # Awaitableをインポート
from ..config import settings
from ..utils.retry import async_retry # 汎用デコレータをインポート

logger = logging.getLogger(__name__)

class OpenAIProvider(LLMProvider):
    """
    OpenAI APIと対話するための標準プロバイダー
    """
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.default_model = settings.OPENAI_DEFAULT_MODEL
        super().__init__()

    def is_available(self) -> bool:
        """APIキーが設定されているかで利用可能かを判断する。"""
        return settings.OPENAI_API_KEY is not None and settings.OPENAI_API_KEY != ""

    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        """このプロバイダーのケイパビリティを返す。"""
        return {
            ProviderCapability.STANDARD_CALL: True,
            ProviderCapability.ENHANCED_CALL: False,
            ProviderCapability.STREAMING: True,
            ProviderCapability.SYSTEM_PROMPT: True,
            ProviderCapability.TOOLS: True,
            ProviderCapability.JSON_MODE: True,
        }

    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        """標準プロバイダーは拡張機能を使用しない。"""
        return False

    @async_retry() # 汎用リトライデコレータを適用
    # standard_call のシグネチャを親クラスの期待する型に合わせる
    # async def は自動的に Coroutine を返すため、ここでは解決される型を直接指定
    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs: Any) -> Dict[str, Any]:
        """OpenAI APIを呼び出し、標準化された辞書形式で結果を返す。"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        model_to_use = kwargs.get("model", self.default_model)

        response = await self.client.chat.completions.create(
            model=model_to_use,
            messages=messages,
            temperature=kwargs.get("temperature", 0.7),
            max_tokens=kwargs.get("max_tokens", 1024),
        )

        content = response.choices[0].message.content
        usage = response.usage

        # ここで返されるのは Dict[str, Any] であり、async 関数が返す Coroutine はそれを解決する。
        # mypyが期待する戻り値の型 (Dict[str, Any]) に適合する。
        return {
            "text": content.strip() if content else "",
            "model": response.model,
            "usage": {
                "prompt_tokens": usage.prompt_tokens if usage else 0,
                "completion_tokens": usage.completion_tokens if usage else 0,
                "total_tokens": usage.total_tokens if usage else 0,
            },
            "error": None,
        }