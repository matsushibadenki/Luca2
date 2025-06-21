# /llm_api/core_engine/pipelines/self_discover.py
# Title: Self-Discover Pipeline (Fixed)
# Role: Implements the SELF-DISCOVER paper's methodology with corrected provider calls.

import logging
import time
from typing import Any, Dict, List, Optional, Tuple, cast

from ...providers.base import LLMProvider
from ...reasoning.strategy_hub import ThinkingStrategyHub, Strategy
from ...reasoning.atomic_modules import get_atomic_module_prompt, ATOMIC_REASONING_MODULES
from ...rag import RAGManager

logger = logging.getLogger(__name__)

class SelfDiscoverPipeline:
    """
    SELF-DISCOVERフレームワークを実装するパイプライン。
    問題の性質に応じて動的に思考戦略を選択・実行する。
    """
    
    def __init__(self, provider: LLMProvider, base_model_kwargs: Dict[str, Any]):
        self.provider = provider
        self.base_model_kwargs = base_model_kwargs
        self.strategy_hub = ThinkingStrategyHub()
        logger.info("SelfDiscoverPipelineを初期化しました")

    async def execute(
        self,
        prompt: str,
        system_prompt: str = "",
        use_rag: bool = False,
        knowledge_base_path: Optional[str] = None,
        use_wikipedia: bool = False
    ) -> Dict[str, Any]:
        """自己発見パイプラインの実行"""
        logger.info(f"自己発見パイプライン開始: {prompt[:80]}...")
        
        current_prompt = prompt
        rag_source = None
        if use_rag or use_wikipedia:
            rag_manager = RAGManager(provider=self.provider, use_wikipedia=use_wikipedia, knowledge_base_path=knowledge_base_path)
            current_prompt = await rag_manager.retrieve_and_augment(prompt)
            rag_source = 'wikipedia' if use_wikipedia else 'knowledge_base'

        try:
            # 1. 問題クラスをLLMで分類
            problem_class = await self._classify_problem(current_prompt, system_prompt)

            # 2. 最適な戦略を取得 (なければ動的生成)
            strategy = self.strategy_hub.get_best_strategy(problem_class)
            if not strategy:
                logger.info(f"問題クラス '{problem_class}' の既存戦略が見つかりません。動的に生成します。")
                strategy = await self._discover_strategy(current_prompt, problem_class, system_prompt)
                self.strategy_hub.add_strategy(strategy)

            # 3. 戦略を実行
            final_result, thought_process = await self._execute_strategy(strategy, current_prompt, system_prompt)

            # 4. パフォーマンスを更新
            success = final_result is not None and "エラー" not in final_result
            self.strategy_hub.update_strategy_performance(strategy.id, success)
            
            v2_improvements = {
                'reasoning_approach': 'self_discover',
                'strategy_used': f"{strategy.name} ({strategy.id})",
                'strategy_steps': strategy.steps,
                'problem_class_detected': problem_class,
                'rag_enabled': use_rag or use_wikipedia,
                'rag_source': rag_source,
            }

            return self._format_response(final_result, thought_process, v2_improvements)

        except Exception as e:
            logger.error(f"自己発見パイプライン実行中にエラー: {e}", exc_info=True)
            return self._format_error_response(str(e))

    async def _classify_problem(self, prompt: str, system_prompt: str) -> str:
        """LLMを使って問題のクラスを分類する"""
        classify_prompt = f"""
        以下の問題を分析し、最も適切な問題クラスを一つだけ選んでください。
        選択肢: planning, analysis, synthesis, general

        問題: "{prompt}"

        回答は問題クラスの単語のみ（例: planning）でお願いします。
        """
        
        # 修正: provider.callの正しい引数形式に修正
        call_kwargs = self.base_model_kwargs.copy()
        call_kwargs.pop('system_prompt', None)  # 重複を避ける
        
        response = await self.provider.call(
            prompt=classify_prompt,
            system_prompt=system_prompt,
            **call_kwargs
        )

        classification = cast(str, response.get('text', 'general')).strip().lower()
        
        valid_classes = ["planning", "analysis", "synthesis", "general"]
        if classification in valid_classes:
            return classification
        return "general"

    async def _discover_strategy(self, prompt: str, problem_class: str, system_prompt: str) -> Strategy:
        """LLMにプロンプトを解決するための思考戦略を生成させる"""
        module_list = "\n".join([f"- {name}: {desc.strip()}" for name, desc in ATOMIC_REASONING_MODULES.items()])
        
        discover_prompt = f"""
        以下の問題を解決するための最適な思考戦略を立案してください。
        戦略は、提供された「アトミック推論モジュール」のリストから適切なものを順番に組み合わせることで構築します。

        # 問題
        "{prompt}"

        # 利用可能なアトミック推論モジュール
        {module_list}

        # 出力形式
        解決に最も適したモジュールの名前を、実行すべき順番でカンマ区切りでリストしてください。
        例: DECOMPOSE,PLAN_STEP_BY_STEP,VALIDATE_AND_REFINE
        """
        
        # 修正: provider.callの正しい引数形式に修正
        call_kwargs = self.base_model_kwargs.copy()
        call_kwargs.pop('system_prompt', None)  # 重複を避ける
        
        response = await self.provider.call(
            prompt=discover_prompt,
            system_prompt=system_prompt,
            **call_kwargs
        )
        
        steps_str = response.get('text', 'DECOMPOSE,SYNTHESIZE').strip()
        
        steps = [step.strip().upper() for step in steps_str.split(',')]
        
        valid_steps = [step for step in steps if step in ATOMIC_REASONING_MODULES]
        if not valid_steps:
            valid_steps = ["DECOMPOSE", "SYNTHESIZE"]

        new_strategy_id = f"strat_{int(time.time())}"
        new_strategy_name = f"Discovered Strategy for {problem_class}"
        
        return Strategy(id=new_strategy_id, name=new_strategy_name, problem_class=problem_class, steps=valid_steps)

    async def _execute_strategy(self, strategy: Strategy, prompt: str, system_prompt: str) -> Tuple[Optional[str], Dict[str, Any]]:
        """戦略の各ステップを順に実行する"""
        current_input: Optional[str] = prompt
        thought_process: Dict[str, Any] = {"strategy_steps": []}

        for step_name in strategy.steps:
            if current_input is None:
                break
            logger.info(f"戦略ステップ '{step_name}' を実行中...")
            step_prompt = get_atomic_module_prompt(step_name, current_input)
            
            # 修正: provider.callの正しい引数形式に修正
            call_kwargs = self.base_model_kwargs.copy()
            call_kwargs.pop('system_prompt', None)  # 重複を避ける
            
            response = await self.provider.call(
                prompt=step_prompt,
                system_prompt=system_prompt,
                **call_kwargs
            )
            
            if response.get('error'):
                error_msg = f"ステップ '{step_name}' でエラー: {response['error']}"
                logger.error(error_msg)
                thought_process['strategy_steps'].append({"step": step_name, "error": error_msg})
                return None, thought_process

            current_input = response.get('text', '')
            thought_process['strategy_steps'].append({
                "step": step_name,
                "output_preview": current_input[:200] + "..." if len(current_input) > 200 else current_input
            })
        
        return current_input, thought_process

    def _format_response(self, solution: Optional[str], thought_process: Dict[str, Any], v2_improvements: Dict[str, Any]) -> Dict[str, Any]:
        """統一されたレスポンス形式"""
        success = solution is not None
        return {
            'success': success,
            'final_solution': solution,
            'image_url': None,
            'thought_process': thought_process,
            'v2_improvements': v2_improvements,
            'version': 'v2',
            'error': None if success else "Strategy execution failed."
        }

    def _format_error_response(self, error_message: str) -> Dict[str, Any]:
        """エラーレスポンスの形式"""
        return {
            'success': False,
            'final_solution': None,
            'image_url': None,
            'thought_process': {'error': error_message},
            'v2_improvements': {'reasoning_approach': 'self_discover'},
            'version': 'v2',
            'error': error_message
        }