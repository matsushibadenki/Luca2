# /llm_api/providers/base.py
# タイトル: Abstract Base Classes for LLM Providers (Refactored)
# 役割: 循環参照を解消し、ProviderCapabilityをトップレベルで定義。

import logging
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional, cast, Awaitable # Awaitableはそのまま

logger = logging.getLogger(__name__)

# ProviderCapabilityをクラスの外で定義
class ProviderCapability(Enum):
    """プロバイダーの機能を定義するEnum"""
    STANDARD_CALL = "standard_call"
    ENHANCED_CALL = "enhanced_call"
    STREAMING = "streaming"
    SYSTEM_PROMPT = "system_prompt"
    TOOLS = "tools"
    JSON_MODE = "json_mode"

class LLMProvider(ABC):
    """
    全てのLLMプロバイダーの抽象基底クラス（ABC）
    """
    def __init__(self):
        self.provider_name = self.__class__.__name__.replace("Provider", "").lower()
        self.capabilities = self._get_default_capabilities()

    def _get_default_capabilities(self) -> Dict[ProviderCapability, bool]:
        if hasattr(self, 'get_capabilities'):
            try:
                return self.get_capabilities()
            except TypeError:
                 pass
        return {cap: False for cap in ProviderCapability}

    @abstractmethod
    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        """プロバイダーの機能を定義した辞書を返す。"""
        pass

    async def call(self, prompt: str, system_prompt: str = "", **kwargs: Any) -> Dict[str, Any]:
        """
        LLM APIを呼び出すメインメソッド。
        常に標準呼び出しを実行する。拡張機能の呼び出しはアプリケーション層の責務。
        """
        try:
            # standard_callはDict[str, Any]を返すことを期待
            result = await self.standard_call(prompt, system_prompt, **kwargs)
            return result 
        except Exception as e:
            logger.error(f"Provider '{self.provider_name}' call failed: {e}", exc_info=True)
            return {"error": str(e), "text": ""}

    @abstractmethod
    # standard_callの戻り値の型はDict[str, Any]のまま
    async def standard_call(self, prompt: str, system_prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """各プロバイダー固有のAPI呼び出しを実装する"""
        pass

    @abstractmethod
    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        """
        拡張機能（V2モード）を使用すべきかどうかのヒントを返す。
        実際の呼び出し分岐は行わない。
        """
        pass

class EnhancedLLMProvider(LLMProvider):
    """
    標準プロバイダーをラップし、V2モード用のパラメータ最適化機能などを提供する拡張プロバイダー。
    """
    def __init__(self, standard_provider: LLMProvider):
        if not isinstance(standard_provider, LLMProvider):
             raise TypeError("EnhancedLLMProviderには有効なstandard_providerインスタンスが必要です。")
        self.standard_provider = standard_provider

        super().__init__()
        self.provider_name = standard_provider.provider_name

    @abstractmethod
    def _get_optimized_params(self, mode: str, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """
        プロバイダーとモードに固有のモデルパラメータを最適化する。
        """
        pass