# /llm_api/dynamic_architecture/architect.py
# タイトル: System Architect (Fixed)
# 役割: 動的アーキテクチャシステムの主要オーケストレーター。コンポーネントアーキテクチャの管理、実行、進化を担当します。

import asyncio
import logging
from typing import Any, Dict, List, Optional, Deque, cast
from collections import deque

from ..providers.base import LLMProvider
# --- ▼▼▼ ここから修正 ▼▼▼ ---
from .types import ArchitectureBlueprint, ComponentType, AdaptiveComponent, ArchitectureStatus
# --- ▲▲▲ ここまで修正 ▲▲▲ ---
from .components import MetaAnalyzer, AdaptiveReasoner, SynthesisOptimizer, ReflectionValidator, CreativeEnhancer

logger = logging.getLogger(__name__)

class SystemArchitect:
    """システムアーキテクト - 動的アーキテクチャ管理"""
    
    def __init__(self, provider: LLMProvider):
        self.provider = provider
        self.components: Dict[str, AdaptiveComponent] = {}
        self.current_architecture: Optional[ArchitectureBlueprint] = None
        self.performance_history: Deque[Dict[str, Any]] = deque(maxlen=100)
        self.evolution_log: List[Dict[str, Any]] = []

    async def initialize_adaptive_architecture(self, initial_config: Dict[str, Any]) -> Dict[str, Any]:
        """適応的アーキテクチャの初期化"""
        logger.info("適応的アーキテクチャを初期化中...")
        
        try:
            self.components = {
                "meta_analyzer": MetaAnalyzer("meta_analyzer_001"),
                "adaptive_reasoner": AdaptiveReasoner("adaptive_reasoner_001", self.provider),
                "synthesis_optimizer": SynthesisOptimizer("synthesis_optimizer_001", self.provider),
                "reflection_validator": ReflectionValidator("reflection_validator_001", self.provider)
            }
            
            self.current_architecture = ArchitectureBlueprint(
                component_types=[ComponentType.ANALYZER, ComponentType.REASONER, 
                               ComponentType.SYNTHESIZER, ComponentType.VALIDATOR],
                connection_matrix={
                    "meta_analyzer": ["adaptive_reasoner"], 
                    "adaptive_reasoner": ["synthesis_optimizer"], 
                    "synthesis_optimizer": ["reflection_validator"], 
                    "reflection_validator": ["meta_analyzer"]
                },
                execution_flow=["meta_analyzer", "adaptive_reasoner", "synthesis_optimizer", "reflection_validator"],
                optimization_targets={"accuracy": 0.8, "efficiency": 0.7, "adaptability": 0.9},
                constraints={"max_execution_time": 60, "memory_limit": "1GB"}
            )
            
            return {
                "architecture_initialized": True, 
                "component_count": len(self.components),
                "initialization_timestamp": asyncio.get_event_loop().time()
            }
        except Exception as e:
            logger.error(f"アーキテクチャ初期化中にエラーが発生: {e}", exc_info=True)
            return {"architecture_initialized": False, "error": str(e)}

    async def execute_adaptive_pipeline(self, input_data: Any, context: Dict[str, Any]) -> Dict[str, Any]:
        """適応的パイプラインの実行（エラーハンドリング強化）"""
        logger.info("適応的パイプライン実行開始")
        
        if not self.current_architecture:
            logger.error("Architecture not initialized.")
            return {"error": "Architecture not initialized", "final_output": None}

        execution_trace: List[Dict[str, Any]] = []
        current_data = input_data
        pipeline_context = context.copy()
        errors: List[str] = []
        
        for component_id in self.current_architecture.execution_flow:
            component = self.components.get(component_id)
            if not component:
                error_msg = f"Component '{component_id}' not found"
                logger.warning(error_msg)
                errors.append(error_msg)
                continue

            try:
                start_time = asyncio.get_event_loop().time()
                # コンテキストの深いコピーを渡すことで、意図しない変更を防ぐ
                context_copy = self._deep_copy_context(pipeline_context)
                result = await component.execute(current_data, context_copy)
                execution_time = asyncio.get_event_loop().time() - start_time
                
                # 結果の検証
                if not isinstance(result, dict):
                    logger.warning(f"Component '{component_id}' returned invalid result type: {type(result)}")
                    result = {"output": str(result), "confidence": 0.5}
                
                execution_trace.append({
                    "component_id": component_id, 
                    "execution_time": execution_time, 
                    "confidence": result.get("confidence", 0.5),
                    "success": True
                })
                
                current_data = result
                # 安全なコンテキスト更新
                self._safe_update_context(pipeline_context, result)
                
            except Exception as e:
                error_msg = f"Component '{component_id}' execution failed: {e}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)
                execution_trace.append({
                    "component_id": component_id,
                    "execution_time": 0.0,
                    "confidence": 0.0,
                    "success": False,
                    "error": str(e)
                })
        
        try:
            performance_metrics = await self._evaluate_pipeline_performance(execution_trace, current_data)
            self.performance_history.append(performance_metrics)
        except Exception as e:
            logger.error(f"パフォーマンス評価中にエラー: {e}", exc_info=True)
            performance_metrics = {"error": "Performance evaluation failed"}
        
        return {
            "final_output": current_data, 
            "performance_metrics": performance_metrics,
            "execution_trace": execution_trace,
            "errors": errors,
            "success": len(errors) == 0
        }

    def _deep_copy_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """コンテキストの安全な深いコピー"""
        try:
            import copy
            return copy.deepcopy(context)
        except Exception:
            # 深いコピーに失敗した場合は浅いコピーにフォールバック
            return context.copy()

    def _safe_update_context(self, pipeline_context: Dict[str, Any], result: Dict[str, Any]) -> None:
        """コンテキストの安全な更新"""
        try:
            # 特定のキーのみ更新し、システム重要なキーは保護
            protected_keys = {"system_config", "architecture", "provider"}
            for key, value in result.items():
                if key not in protected_keys and isinstance(key, str):
                    pipeline_context[key] = value
        except Exception as e:
            logger.warning(f"コンテキスト更新中にエラー: {e}")

    async def _evaluate_pipeline_performance(self, trace: List[Dict[str, Any]], output: Any) -> Dict[str, Any]:
        """パイプラインパフォーマンスの評価（強化版）"""
        if not trace:
            return {"total_time": 0.0, "avg_confidence": 0.0, "output_quality": 0.0, "overall_score": 0.0}
        
        successful_executions = [step for step in trace if step.get("success", False)]
        total_time = sum(step.get("execution_time", 0.0) for step in trace)
        
        if successful_executions:
            avg_confidence = sum(step.get("confidence", 0.0) for step in successful_executions) / len(successful_executions)
            success_rate = len(successful_executions) / len(trace)
        else:
            avg_confidence = 0.0
            success_rate = 0.0
        
        # 出力品質の評価（シンプルな実装）
        output_quality = 0.8 if output and str(output).strip() else 0.0
        
        # 全体スコアの計算
        overall_score = (avg_confidence * 0.4 + success_rate * 0.4 + output_quality * 0.2)
        
        return {
            "total_time": total_time, 
            "avg_confidence": avg_confidence, 
            "output_quality": output_quality,
            "success_rate": success_rate,
            "overall_score": overall_score,
            "component_count": len(trace)
        }

    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    def get_architecture_status(self) -> ArchitectureStatus:
        """アーキテクチャの現在状態を取得"""
        current_perf: float = 0.0
        if self.performance_history:
            latest_metrics = self.performance_history[-1]
            # latest_metrics.get("overall_score", 0.0) の戻り値はAnyの可能性があるのでキャスト
            current_perf = float(latest_metrics.get("overall_score", 0.0))

        return {
            "initialized": self.current_architecture is not None,
            "component_count": len(self.components),
            "performance_history_length": len(self.performance_history),
            "evolution_count": len(self.evolution_log),
            "current_performance": current_perf 
        }
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    async def evolve_architecture(self, feedback: Dict[str, Any]) -> Dict[str, Any]:
        """アーキテクチャの進化（新機能）"""
        logger.info("アーキテクチャ進化プロセス開始...")
        
        if not self.current_architecture:
            return {"error": "No architecture to evolve"}
        
        current_performance = self.get_architecture_status().get("current_performance", 0.0)
        
        # パフォーマンスが閾値を下回る場合、アーキテクチャを調整
        if current_performance < 0.6:
            logger.info(f"パフォーマンス低下検出 ({current_performance:.2f}), アーキテクチャを調整します")
            
            # 新しいコンポーネントの追加を検討
            if "creative_enhancer" not in self.components:
                self.components["creative_enhancer"] = CreativeEnhancer("creative_enhancer_001", self.provider)
                # 実行フローに追加
                new_flow = self.current_architecture.execution_flow.copy()
                new_flow.insert(-1, "creative_enhancer")  # 最後の前に挿入
                
                self.current_architecture = ArchitectureBlueprint(
                    component_types=self.current_architecture.component_types + [ComponentType.OPTIMIZER],
                    connection_matrix=self.current_architecture.connection_matrix,
                    execution_flow=new_flow,
                    optimization_targets=self.current_architecture.optimization_targets,
                    constraints=self.current_architecture.constraints
                )
                
                evolution_entry = {
                    "timestamp": asyncio.get_event_loop().time(),
                    "action": "component_added",
                    "component": "creative_enhancer",
                    "reason": f"Performance below threshold: {current_performance}"
                }
                self.evolution_log.append(evolution_entry)
                
                return {"evolved": True, "action": "component_added", "new_component": "creative_enhancer"}
        
        return {"evolved": False, "current_performance": current_performance}