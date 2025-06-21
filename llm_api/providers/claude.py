# llm_api/providers/claude.py
# タイトル: Anthropic Claude Provider (Mypy Fixed)
# 役割: Claude APIと対話する。重複メソッド定義を修正。

import logging
from typing import Any, Dict

from anthropic import AsyncAnthropic
from .base import LLMProvider, ProviderCapability
from ..config import settings

logger = logging.getLogger(__name__)

class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude APIと対話するための標準プロバイダー
    """
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.CLAUDE_API_KEY)
        self.default_model = settings.CLAUDE_DEFAULT_MODEL
        super().__init__()

    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        """このプロバイダーのケイパビリティを返す。"""
        return {
            ProviderCapability.STANDARD_CALL: True,
            ProviderCapability.ENHANCED_CALL: False,
            ProviderCapability.STREAMING: True,
            ProviderCapability.SYSTEM_PROMPT: True,
            ProviderCapability.TOOLS: True,
            ProviderCapability.JSON_MODE: False, # Claude 3はJSONモードをサポートしているが、ここではFalseのままにしておく
        }

    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        """標準プロバイダーは拡張機能を使用しない。"""
        return False

    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]: # 戻り値はDict[str, Any]
        """Claude APIを呼び出し、標準化された辞書形式で結果を返す。"""
        model_to_use = kwargs.get("model", self.default_model)
        try:
            # systemプロンプトが空でない場合のみ、引数として渡す
            extra_params = {}
            if system_prompt:
                extra_params['system'] = system_prompt

            response = await self.client.messages.create(
                model=model_to_use,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 4096), # Claudeの能力を活かすため上限を上げる
                **extra_params
            )

            # 応答が複数のcontentブロックに分かれている場合を考慮
            content = "".join([block.text for block in response.content if hasattr(block, 'text')])
            usage = response.usage

            return {
                "text": content.strip(),
                "model": response.model,
                "usage": {
                    "prompt_tokens": usage.input_tokens,
                    "completion_tokens": usage.output_tokens,
                    "total_tokens": usage.input_tokens + usage.output_tokens,
                },
                "error": None,
            }
        except Exception as e:
            logger.error(f"Claude API呼び出し中にエラー: {e}", exc_info=True)
            return {"text": "", "error": str(e)}