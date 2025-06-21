# /llm_api/providers/llamacpp.py
# タイトル: Llama.cpp Provider with GPU Offload Support
# 役割: Llama.cppサーバーまたはローカルGGUFモデルと連携する。n_gpu_layers引数をサポート。

import logging
from typing import Any, Dict, Optional, cast
from llama_cpp import Llama

from ..config import settings
from .base import LLMProvider

logger = logging.getLogger(__name__)

class LlamaCppProvider(LLMProvider):
    """Llama.cppのPythonバインディングを使用するプロバイダー"""

    def __init__(
        self,
        api_key: str = "",
        model_path: Optional[str] = None,
        # --- ▼▼▼ ここから変更 ▼▼▼ ---
        n_gpu_layers: Optional[int] = None
        # --- ▲▲▲ ここまで変更 ▲▲▲ ---
    ):
        """
        Llama.cppプロバイダーを初期化します。

        Args:
            api_key: (未使用)
            model_path: 使用するローカルGGUFモデルへのパス。
            n_gpu_layers: GPUにオフロードするレイヤー数。-1は全レイヤーを意味する。
        """
        self.api_key = api_key
        self.model_path = model_path
        # --- ▼▼▼ ここから変更 ▼▼▼ ---
        self.n_gpu_layers = n_gpu_layers if n_gpu_layers is not None else -1 # デフォルトは全レイヤーオフロード
        # --- ▲▲▲ ここまで変更 ▲▲▲ ---
        self.client = None
        self.provider_name = "llamacpp"
        self._initialize_client()

    def _initialize_client(self):
        """モデルパスに基づいてLlama.cppクライアントを初期化する。"""
        if self.model_path:
            try:
                logger.info(f"Llama.cppモデルをロード中: {self.model_path}")
                # --- ▼▼▼ ここから変更 ▼▼▼ ---
                logger.info(f"GPUにオフロードするレイヤー数: {self.n_gpu_layers}")
                self.client = Llama(
                    model_path=self.model_path,
                    n_gpu_layers=self.n_gpu_layers,
                    n_ctx=settings.LLAMACPP_N_CTX,
                    verbose=settings.LLAMACPP_VERBOSE
                )
                # --- ▲▲▲ ここまで変更 ▲▲▲ ---
            except Exception as e:
                logger.error(f"Llama.cppモデルのロードに失敗しました: {e}", exc_info=True)
                raise ValueError(f"指定されたパスのLlama.cppモデルのロードに失敗しました: {self.model_path}")
        else:
            logger.warning("Llama.cppのモデルパスが設定されていません。")
            raise ValueError("LlamaCppProviderには `model_path` が必須です。")

    async def call(self, prompt: str, system_prompt: str = "", **kwargs: Any) -> Dict[str, Any]: # system_promptを追加
        """標準化された `call` メソッドの実装"""
        return await self.standard_call(prompt, system_prompt, **kwargs) # system_promptを渡す

    async def standard_call(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Llama.cppモデルにリクエストを送信する。"""
        if not self.client:
            return {"error": "Llama.cppクライアントが初期化されていません。"}

        final_temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        final_max_tokens = max_tokens if max_tokens is not None else settings.LLM_MAX_TOKENS

        try:
            logger.info(f"Llama.cppモデル '{self.model_path}' へのリクエストを送信中...")
            
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            response = self.client.create_chat_completion(
                messages=messages,
                temperature=final_temperature,
                max_tokens=final_max_tokens,
            )

            completion = response['choices'][0]['message']['content']
            usage = response.get('usage', {})

            return {
                "text": completion,
                "model": self.model_path,
                "usage": {
                    "prompt_tokens": usage.get("prompt_tokens"),
                    "completion_tokens": usage.get("completion_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
                "error": None
            }
        except Exception as e:
            logger.error(f"Llama.cpp API呼び出し中にエラー: {e}", exc_info=True)
            return {"error": f"Llama.cpp API呼び出し中にエラー: {str(e)}"}