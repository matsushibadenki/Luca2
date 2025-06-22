# /llm_api/providers/__init__.py
# タイトル: LLM Provider Factory (with GPU Offload Support)
# 役割: 指定されたプロバイダーのインスタンスを生成・管理するファクトリ。GPUオフロード引数を渡すように修正。

import logging
import asyncio 
from typing import Any, Dict, Optional, cast, List, Awaitable

from .base import LLMProvider, EnhancedLLMProvider, ProviderCapability 
from ..config import settings
import httpx

logger = logging.getLogger(__name__)

_provider_cache: Dict[str, LLMProvider] = {}

async def check_provider_health(provider_name: str, enhanced: bool) -> Dict[str, Any]:
    """
    指定されたプロバイダーの健全性をチェックします。
    プロバイダーをインスタンス化し、シンプルなテスト呼び出しを行います。
    """
    try:
        test_kwargs = {}
        if provider_name == 'ollama':
            try:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(f"{settings.OLLAMA_API_BASE_URL}/api/tags")
                    response.raise_for_status()
                    response_data = response.json() # .json()を呼び出す
                    models = [model['name'] for model in response_data.get('models', [])]
                    if models:
                        pass 
                    else:
                        return {'available': False, 'reason': "Ollama server is running but no models are loaded."}
            except Exception as e:
                return {'available': False, 'reason': f"Failed to get Ollama models: {e}"}
        elif provider_name == 'llamacpp':
            test_kwargs['model_path'] = settings.LLAMACPP_DEFAULT_MODEL_PATH
            if not test_kwargs['model_path']:
                return {'available': False, 'reason': "LLAMACPP_DEFAULT_MODEL_PATH is not configured."}

        init_kwargs_for_get_provider = {}
        if provider_name == 'llamacpp':
            if test_kwargs.get('model_path'):
                init_kwargs_for_get_provider['model_path'] = test_kwargs['model_path']

        provider = get_provider(provider_name, enhanced=enhanced, **init_kwargs_for_get_provider)

        test_prompt = "Hello, respond with just 'OK'"
        call_params = {"temperature": 0.01, "max_tokens": 10}
        
        if provider_name == 'ollama' and hasattr(provider, 'default_model'):
            call_params['model'] = provider.default_model

        # provider.callのシグネチャに合わせて引数を渡す
        response_from_call = await provider.call(test_prompt, system_prompt="", **call_params) # system_promptを明示的に渡す

        if response_from_call.get('error'):
            return {'available': False, 'reason': f"API call failed: {response_from_call['error']}"}

        if not response_from_call.get('text', '').strip():
            return {'available': False, 'reason': "API returned empty response."}

        return {'available': True, 'reason': "Successfully made a test call."}
    except ValueError as e:
        return {'available': False, 'reason': str(e)}
    except Exception as e:
        return {'available': False, 'reason': f"An unexpected error occurred during health check: {type(e).__name__} - {e}"}

def get_provider(
    provider_name: str, 
    enhanced: bool = False,
    **kwargs: Any
) -> LLMProvider:
    """
    指定されたプロバイダーのインスタンスを取得します。
    インスタンスはキャッシュされ、同じ設定での再呼び出し時には再利用されます。
    """
    from .openai import OpenAIProvider
    from .claude import ClaudeProvider
    from .gemini import GeminiProvider
    from .huggingface import HuggingFaceProvider
    from .ollama import OllamaProvider
    from .llamacpp import LlamaCppProvider
    
    from .enhanced_openai_v2 import EnhancedOpenAIProviderV2
    from .enhanced_claude_v2 import EnhancedClaudeProviderV2
    from .enhanced_gemini_v2 import EnhancedGeminiProviderV2
    from .enhanced_huggingface_v2 import EnhancedHuggingFaceProviderV2
    from .enhanced_ollama_v2 import EnhancedOllamaProviderV2
    from .enhanced_llamacpp_v2 import EnhancedLlamaCppProviderV2

    provider_map = {
        "openai": OpenAIProvider,
        "claude": ClaudeProvider,
        "gemini": GeminiProvider,
        "huggingface": HuggingFaceProvider,
        "ollama": OllamaProvider,
        "llamacpp": LlamaCppProvider,
    }

    enhanced_provider_map = {
        "openai": EnhancedOpenAIProviderV2,
        "claude": EnhancedClaudeProviderV2,
        "gemini": EnhancedGeminiProviderV2,
        "huggingface": EnhancedHuggingFaceProviderV2,
        "ollama": EnhancedOllamaProviderV2,
        "llamacpp": EnhancedLlamaCppProviderV2,
    }

    base_provider_name = provider_name.lower()
    if base_provider_name not in provider_map:
        raise ValueError(f"不明なプロバイダー: {provider_name}")

    target_map = enhanced_provider_map if enhanced else provider_map
    cache_key_suffix = "_enhanced" if enhanced else "_standard"
    
    # kwargsの内容に基づいてキャッシュキーを生成
    # sortedで引数の順序に関わらず同じキーになるようにする
    args_key = "_".join(f"{k}:{v}" for k, v in sorted(kwargs.items()))
    cache_key = f"{base_provider_name}{cache_key_suffix}_{args_key}"


    if cache_key in _provider_cache:
        logger.info(f"プロバイダー '{cache_key}' のキャッシュされたインスタンスを返します。")
        return _provider_cache[cache_key]

    logger.info(f"プロバイダー '{cache_key}' の新しいインスタンスを生成します。")
    provider_class = target_map[base_provider_name]

    try:
        if enhanced:
            standard_provider_kwargs = {k: v for k, v in kwargs.items() if k in ['model', 'model_path', 'n_gpu_layers', 'api_key']}
            standard_provider = get_provider(base_provider_name, enhanced=False, **standard_provider_kwargs)
            enhanced_kwargs = {k:v for k,v in kwargs.items() if k not in standard_provider_kwargs}
            instance = provider_class(standard_provider=standard_provider, **enhanced_kwargs)
        else:
            if base_provider_name == 'llamacpp':
                init_kwargs = {
                    'model_path': kwargs.get('model_path') or settings.LLAMACPP_DEFAULT_MODEL_PATH,
                    'n_gpu_layers': kwargs.get('n_gpu_layers')
                }
                init_kwargs = {k: v for k, v in init_kwargs.items() if v is not None}
                instance = provider_class(**init_kwargs)
            else:
                # --- ▼▼▼ ここから修正 ▼▼▼ ---
                # 他のプロバイダー (openai, claude, gemini, etc.) にもkwargsを渡す
                instance = provider_class(**kwargs)
                # --- ▲▲▲ ここまで修正 ▲▲▲ ---
                
    except TypeError as e:
        logger.error(f"{provider_class.__name__} の初期化に失敗しました。引数を確認してください: {e}", exc_info=True)
        raise
    except ValueError as e:
        logger.error(f"{provider_class.__name__} の初期化に失敗しました。設定を確認してください: {e}", exc_info=True)
        raise

    _provider_cache[cache_key] = instance
    return cast(LLMProvider, instance)

def list_providers() -> List[str]:
    """設定されているプロバイダー名をリストアップする。"""
    return list({
        "openai", "claude", "gemini", "huggingface", "ollama", "llamacpp"
    })

def list_enhanced_providers() -> Dict[str, List[str]]:
    """利用可能なV2拡張プロバイダーのリストを返します。"""
    return {
        "v2": list({
            "openai", "claude", "gemini", "huggingface", "ollama", "llamacpp"
        })
    }

def _log_available_providers():
    """利用可能なプロバイダーをログに出力します。"""
    standard_providers = list_providers()
    v2_providers = list_enhanced_providers().get('v2', [])
    logger.info(f"利用可能な標準プロバイダー: {standard_providers}")
    logger.info(f"利用可能なV2拡張プロバイダー: {v2_providers}")

logger.info("プロバイダーモジュール初期化開始")
_log_available_providers()
logger.info("プロバイダーモジュール初期化完了")