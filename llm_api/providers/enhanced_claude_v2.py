# /llm_api/providers/enhanced_claude_v2.py
# Title: Refactored EnhancedClaudeProviderV2
# Role: ClaudeプロバイダーにMetaIntelligence V2の機能を提供する。共通ロジックは基底クラスに委譲し、パラメータ最適化に特化。

from typing import Any, Dict

from .base import EnhancedLLMProvider, ProviderCapability

class EnhancedClaudeProviderV2(EnhancedLLMProvider):
    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]: # 戻り値をDict[str, Any]にする
        return await self.standard_provider.standard_call(prompt, system_prompt, **kwargs) # awaitを追加

    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        return kwargs.get('force_v2', False) or kwargs.get('mode', 'simple') in [
            'efficient', 'balanced', 'decomposed', 'adaptive', 'paper_optimized', 'parallel',
            'quantum_inspired', 'edge', 'speculative_thought'
        ]

    def _get_optimized_params(self, mode: str, kwargs: Dict) -> Dict:
        """Claudeに最適化されたモデルパラメータを返す。"""
        params = kwargs.copy()
        if 'model' not in params:
            # モードに応じてデフォルトモデルを賢く選択
            if mode in ['decomposed', 'paper_optimized', 'quantum_inspired', 'speculative_thought']:
                params['model'] = 'claude-3-sonnet-20240229' # 高度なタスクにはSonnet
            else:
                params['model'] = 'claude-3-haiku-20240307' # それ以外はHaiku
        return params

    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        # 標準プロバイダーの能力を継承しつつ、拡張呼び出しを有効化
        capabilities = self.standard_provider.get_capabilities()
        capabilities[ProviderCapability.ENHANCED_CALL] = True
        return capabilities