# /llm_api/core_engine/pipelines/speculative.py
# Title: Speculative Thought Pipeline Handler (Fixed)
# Role: Implements thinking-level speculative decoding with corrected provider calls.

import logging
from typing import Any, Dict, Optional, List, cast
import httpx
import asyncio

from .adaptive import AdaptivePipeline
from ...rag import RAGManager
from ...providers import get_provider
from ...providers.base import LLMProvider

logger = logging.getLogger(__name__)

class SpeculativePipeline:
    """思考レベルの投機的デコーディングを実装したパイプライン"""
    
    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any]):
        self.provider = provider # 検証・統合用の高機能プロバイダー
        self.base_model_kwargs = base_model_kwargs
        self.adaptive_pipeline = AdaptivePipeline(provider, base_model_kwargs)
        logger.info("SpeculativePipeline (Thinking-level Speculative Decoding) を初期化しました")
    
    async def execute(
        self,
        prompt: str,
        system_prompt: str = "",
        use_rag: bool = False,
        knowledge_base_path: Optional[str] = None,
        use_wikipedia: bool = False
    ) -> Dict[str, Any]:
        """投機的思考パイプラインの実行"""
        logger.info(f"思考レベルの投機的デコーディングパイプライン開始: {prompt[:80]}...")
        
        current_prompt = prompt
        rag_source = None
        if use_rag or use_wikipedia:
            rag_manager = RAGManager(provider=self.provider, use_wikipedia=use_wikipedia, knowledge_base_path=knowledge_base_path)
            current_prompt = await rag_manager.retrieve_and_augment(prompt)
            rag_source = 'wikipedia' if use_wikipedia else 'knowledge_base'

        # 1. ドラフト生成用の軽量モデルを自動選択
        draft_model_name = await self._find_lightweight_model()
        
        if not draft_model_name:
            logger.warning("適切な軽量ドラフトモデルが見つかりませんでした。適応型パイプラインにフォールバックします。")
            return await self.adaptive_pipeline.execute(current_prompt, system_prompt, mode='balanced')
        
        try:
            # 2. 軽量モデルで複数の思考ドラフトを並列生成
            drafts = await self._generate_speculative_drafts(current_prompt, draft_model_name)
            
            if not drafts:
                logger.error("ドラフト生成に失敗しました。")
                return self._format_error_response("ドラフト生成に失敗しました。")
            
            # 3. 高機能モデルで検証と統合
            final_solution = await self._verify_and_integrate(current_prompt, drafts, system_prompt)
            
            if not final_solution:
                logger.error("検証・統合に失敗しました。")
                return self._format_error_response("検証・統合に失敗しました。")
            
            thought_process = {
                'draft_generator_model': f"ollama/{draft_model_name}",
                'verifier_integrator_model': self.provider.provider_name,
                'drafts_generated': len(drafts),
                'speculative_method': 'thinking_level_speculative_decoding'
            }
            
            v2_improvements = {
                'reasoning_approach': 'speculative_thought_v2',
                'speculative_execution_enabled': True,
                'rag_enabled': use_rag or use_wikipedia,
                'rag_source': rag_source,
                'draft_model': draft_model_name,
            }

            return self._format_response(final_solution, thought_process, v2_improvements)
            
        except Exception as e:
            logger.error(f"投機的思考パイプライン実行中にエラー: {e}", exc_info=True)
            return self._format_error_response(str(e))
    
    async def _find_lightweight_model(self) -> Optional[str]:
        """Ollamaから利用可能な最も軽量なモデルを探索する"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get("http://localhost:11434/api/tags")
                response.raise_for_status()
                available_models = response.json().get('models', [])
            
            if not available_models:
                return None

            lightweight_candidates = []
            for model_info in available_models:
                model_name = model_info['name'].lower()
                size_gb = model_info.get('size', 0) / (1024**3)
                
                score = 0
                if any(k in model_name for k in ['phi', 'gemma:2b', 'tiny', '2b', '3b']):
                    score += 2
                if 'instruct' in model_name:
                    score += 1
                
                lightweight_candidates.append({'name': model_info['name'], 'size': size_gb, 'score': score})

            lightweight_candidates.sort(key=lambda x: (-x['score'], x['size']))
            
            selected_model = cast(str, lightweight_candidates[0]['name'])
            logger.info(f"Ollamaからドラフト生成用の軽量モデルを自動選択しました: {selected_model}")
            return selected_model
            
        except Exception as e:
            logger.warning(f"Ollamaから利用可能なモデルの取得に失敗しました: {e}")
            return None
    
    async def _generate_speculative_drafts(self, prompt: str, model_name: str) -> List[str]:
        """軽量モデルで複数の思考ドラフトを並列生成する"""
        try:
            draft_provider = get_provider('ollama', enhanced=False)
            
            perspectives = [
                "論理的で分析的な視点",
                "創造的で発散的な視点",
                "批判的で懐疑的な視点"
            ]
            
            tasks = []
            for perspective in perspectives:
                draft_prompt = f"""以下の質問に対して、「{perspective}」から考えられる思考のドラフトを一つ、簡潔に生成してください。

質問: {prompt}"""
                
                draft_model_kwargs = {'model': model_name, 'temperature': 0.8}
                tasks.append(draft_provider.standard_call(draft_prompt, "", **draft_model_kwargs))

            draft_responses = await asyncio.gather(*tasks)
            
            valid_drafts = [res.get('text', '').strip() for res in draft_responses if res and not res.get('error')]
            logger.info(f"{len(valid_drafts)}個の思考ドラフトを生成しました。")
            return valid_drafts
            
        except Exception as e:
            logger.error(f"ドラフト生成中にエラー: {e}")
            return []
    
    async def _verify_and_integrate(self, original_prompt: str, drafts: List[str], system_prompt: str) -> Optional[str]:
        """高機能モデルでドラフトを検証・統合する"""
        try:
            drafts_context = "\n\n---\n\n".join(f"思考ドラフト {i+1}:\n{draft}" for i, draft in enumerate(drafts))
            
            verification_prompt = f"""以下の「元の質問」に対して、軽量モデルが生成した複数の「思考ドラフト」が提供されました。
あなたは専門家として、これらのドラフトを評価・検証し、最も正確で包括的な最終回答を1つに統合してください。
各ドラフトの良い点を取り入れ、誤りを修正し、論理的に一貫した最終回答を生成してください。

# 元の質問
{original_prompt}

# 思考ドラフト
---
{drafts_context}
---

# 検証・統合済みの最終回答
"""
            
            # 修正: provider.callの正しい引数形式に修正
            call_kwargs = self.base_model_kwargs.copy()
            call_kwargs.pop('model', None)  # --model引数を削除してプロバイダーのデフォルトを使用
            call_kwargs.pop('system_prompt', None)  # 重複を避ける
            
            response = await self.provider.call(
                prompt=verification_prompt,
                system_prompt=system_prompt,
                **call_kwargs
            )
            
            if response.get('error'):
                logger.error(f"検証・統合でエラー: {response['error']}")
                return None
            
            return cast(Optional[str], response.get('text', ''))
        except Exception as e:
            logger.error(f"検証・統合中にエラー: {e}")
            return None
    
    def _format_response(self, solution: str, thought_process: Dict[str, Any], v2_improvements: Dict[str, Any]) -> Dict[str, Any]:
        """統一されたレスポンス形式"""
        return {
            'success': True,
            'final_solution': solution,
            'image_url': None,
            'thought_process': thought_process,
            'v2_improvements': v2_improvements,
            'version': 'v2',
            'error': None
        }

    def _format_error_response(self, error_message: str) -> Dict[str, Any]:
        """エラーレスポンスの形式"""
        return {
            'success': False,
            'final_solution': None,
            'image_url': None,
            'thought_process': {'error': error_message},
            'v2_improvements': {'speculative_execution_enabled': True},
            'version': 'v2',
            'error': error_message
        }