# /cli/command_runner.py
# タイトル: CLI Management Command Runner
# 役割: 健全性チェックや情報表示など、LLMへのリクエストを伴わない管理コマンドを実行する。

import logging
import time
from typing import Any, Dict

import httpx
from llm_api.providers import (check_provider_health, list_providers, list_enhanced_providers) 

logger = logging.getLogger(__name__)

class CLICommandRunner:
    """管理コマンドの実行を担当するクラス"""

    def __init__(self):
        logger.debug("CLICommandRunner initialized.")

    def list_providers(self):
        """利用可能なプロバイダーを一覧表示する。"""
        print("\n=== 利用可能なプロバイダー ===")
        standard_providers = list_providers()
        enhanced_info = list_enhanced_providers()
        print(f"標準プロバイダー: {', '.join(standard_providers)}")
        print(f"拡張プロバイダー (V2): {', '.join(enhanced_info.get('v2', []))}")
        print("==============================")

    def show_system_status(self):
        """現在のシステム状態（プロバイダー、モード）を表示します。"""
        self.list_providers()
        v2_modes = {
            'efficient', 'balanced', 'decomposed', 'adaptive', 'paper_optimized', 'parallel',
            'quantum_inspired', 'edge', 'speculative_thought', 'self_discover'
        }
        print(f"V2専用モード: {', '.join(sorted(v2_modes))}")
        print("===================================")


    def show_troubleshooting_guide(self):
        """トラブルシューティングガイドを表示します。"""
        guide = """
=== MetaIntelligence V2 トラブルシューティングガイド ===

【Ollamaモデルが見つからない / 接続できない】
1. `ollama serve` を実行してサーバーを起動してください。
2. `ollama pull gemma3:latest` などでモデルをダウンロードしてください。
3. `ollama list` で利用可能なモデルを確認してください。
4. `python fetch_llm_v2.py ollama --health-check` で状態を確認してください。

【APIキーのエラー】
1. プロジェクトルートに `.env` ファイルが存在し、APIキーが正しく設定されているか確認してください。
   例: `OPENAI_API_KEY="sk-..."`
2. `python fetch_llm_v2.py openai --health-check` などでキーの有効性を確認してください。

【V2機能が動作しない】
1. `--force-v2` フラグをつけて実行を試みてください。
2. `python fetch_llm_v2.py --system-status` でV2対応プロバイダーを確認してください。

【デバッグ情報の取得】
より詳細なログを表示するには、環境変数 `LOG_LEVEL` を `DEBUG` に設定して実行してください。
例: `LOG_LEVEL=DEBUG python fetch_llm_v2.py ollama "test" --json`
"""
        print(guide)

    async def run_health_check(self, provider_name: str) -> Dict[str, Any]:
        """プロバイダーの健全性をチェックする。"""
        health_report: Dict[str, Any] = {
            'provider_name': provider_name,
            'timestamp': time.time(),
            'checks': {}
        }
        logger.info(f"プロバイダー '{provider_name}' の健全性チェックを開始します。")

        try:
            health_report['checks']['standard_provider'] = await check_provider_health(provider_name, enhanced=False)
        except Exception as e:
            health_report['checks']['standard_provider'] = {'available': False, 'error': str(e)}

        try:
            health_report['checks']['enhanced_v2_provider'] = await check_provider_health(provider_name, enhanced=True)
        except Exception as e:
            health_report['checks']['enhanced_v2_provider'] = {'available': False, 'error': str(e)}

        if provider_name == 'ollama':
            health_report['checks']['ollama_models'] = await self._check_ollama_models()

        return health_report

    async def _check_ollama_models(self) -> Dict[str, Any]:
        """Ollamaサーバーの接続性とモデルの可用性をチェックします。"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                response.raise_for_status()
                data = response.json()
                models = [model['name'] for model in data.get('models', [])]

                if not models:
                    return {
                        'server_available': True,
                        'models_loaded': False,
                        'error': 'Ollamaサーバーは起動していますが、モデルが読み込まれていません。`ollama pull <model_name>`でモデルをダウンロードしてください。'
                    }
                return {
                    'server_available': True,
                    'models_loaded': True,
                    'models_available': models,
                    'model_count': len(models)
                }
        except (httpx.RequestError, ConnectionRefusedError) as e:
            return {'server_available': False, 'error': f'Ollamaサーバーに接続できません: {e}'}
        except Exception as e:
            return {'server_available': False, 'error': f'予期せぬエラーが発生しました: {str(e)}'}