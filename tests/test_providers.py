# /tests/test_providers.py

import pytest
from unittest.mock import patch, MagicMock
import os
import importlib

from llm_api.providers import get_provider, _provider_cache
from llm_api.providers.base import LLMProvider, EnhancedLLMProvider
from llm_api.providers.openai import OpenAIProvider
from llm_api.providers.enhanced_openai_v2 import EnhancedOpenAIProviderV2
from llm_api import config as api_config

@pytest.fixture(autouse=True)
def clear_provider_cache():
    """各テスト前にプロバイダーキャッシュをクリアする"""
    _provider_cache.clear()
    yield

@patch.dict(os.environ, {"OPENAI_API_KEY": "test_key"})
class TestProviderLoading:
    """get_provider 関数の挙動をテストする。"""

    def test_get_standard_provider(self):
        """enhanced=False で OpenAIProvider が返ること"""
        provider = get_provider("openai", enhanced=False)
        assert isinstance(provider, OpenAIProvider)
        assert not isinstance(provider, EnhancedLLMProvider)

    def test_get_enhanced_v2_provider(self):
        """enhanced=True で EnhancedOpenAIProviderV2 が返ること"""
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        provider = get_provider("openai", enhanced=True)
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        assert isinstance(provider, EnhancedOpenAIProviderV2)

    def test_get_provider_not_found(self):
        """未知のプロバイダー指定時に ValueError が発生する"""
        with pytest.raises(ValueError, match="不明なプロバイダー: non_existent_provider"):
            get_provider("non_existent_provider")

    def test_provider_caching(self):
        """同一プロバイダーはキャッシュされること"""
        provider1 = get_provider("openai", enhanced=False)
        provider2 = get_provider("openai", enhanced=False)
        assert provider1 is provider2

        provider3 = get_provider("openai", enhanced=True)
        provider4 = get_provider("openai", enhanced=True)
        assert provider3 is provider4
        assert provider1 is not provider3

def test_provider_availability_check():
    """OpenAIProvider の is_available 振る舞いをテスト"""
    from llm_api.providers import openai

    with patch.object(api_config.settings, 'OPENAI_API_KEY', None):
        importlib.reload(openai)
        provider = openai.OpenAIProvider()
        assert not provider.is_available()

    with patch.object(api_config.settings, 'OPENAI_API_KEY', "fake_key"):
        importlib.reload(openai)
        provider = openai.OpenAIProvider()
        assert provider.is_available()
