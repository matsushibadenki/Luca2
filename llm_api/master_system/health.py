# /llm_api/master_system/health.py
# タイトル: System Health Monitor (Fixed)
# 役割: 統合マスターシステムの健全性を監視、評価、報告する。

import logging
import asyncio
# --- ▼▼▼ ここから修正 ▼▼▼ ---
from typing import Any, Dict, List, Optional, cast, TYPE_CHECKING

if TYPE_CHECKING:
    # 循環参照を避けるための型チェック時のみのインポート
    from .orchestrator import MasterIntegrationOrchestrator
# --- ▲▲▲ ここまで修正 ▲▲▲ ---

logger = logging.getLogger(__name__)

class SystemHealthMonitor:
    """システムの健全性監視を担当するクラス"""

    # --- ▼▼▼ ここから修正 ▼▼▼ ---
    def __init__(self, orchestrator: 'MasterIntegrationOrchestrator'):
        self.orchestrator = orchestrator
    # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    async def check_health(self) -> Dict[str, Any]:
        """統合システムの健全性監視を実行し、レポートを返す"""
        logger.info("🔍 統合システム健全性監視開始...")
        
        try:
            current_health = await self._assess_system_health()
            anomalies = self._detect_anomalies(current_health)
            recommendations = self._generate_health_recommendations(current_health, anomalies)
            
            return {
                "status": "completed",
                "integration_status": self.orchestrator.integration_status,
                "health_metrics": current_health,
                "anomalies": anomalies,
                "recommendations": recommendations,
                "overall_health_score": current_health.get("overall_score", 0.0)
            }
            
        except Exception as e:
            logger.error(f"健康性監視中にエラー: {e}", exc_info=True)
            return {"status": "failed", "error": str(e)}

    async def _assess_system_health(self) -> Dict[str, Any]:
        """システム健康状態の評価"""
        health_metrics = self.orchestrator._health_metrics.copy()
        
        health_metrics.update({
            "memory_usage": self._get_memory_usage(),
            "response_time": await self._measure_response_time(),
            "error_rate": self._calculate_error_rate(),
            "subsystem_connectivity": self._check_subsystem_connectivity()
        })
        
        scores: List[float] = []
        if health_metrics.get("total_subsystems", 0) > 0:
            op_subsystems = health_metrics.get("operational_subsystems", 0)
            total_subsystems = health_metrics.get("total_subsystems", 1)
            scores.append(op_subsystems / total_subsystems)
        
        scores.append(1.0 - health_metrics.get("error_rate", 0.0))

        if health_metrics.get("response_time", float('inf')) < 5.0:
            scores.append(0.9)
        else:
            scores.append(0.5)
        
        health_metrics["overall_score"] = sum(scores) / len(scores) if scores else 0.0
        # --- ▼▼▼ ここから修正 ▼▼▼ ---
        # mypyが戻り値の型を正しく推論できるようにキャストする
        return cast(Dict[str, Any], health_metrics)
        # --- ▲▲▲ ここまで修正 ▲▲▲ ---

    def _get_memory_usage(self) -> float:
        """メモリ使用量の取得（簡易実装）"""
        try:
            import psutil
            # --- ▼▼▼ ここから修正 ▼▼▼ ---
            # psutilの戻り値がAnyと解釈されるため、floatにキャストする
            return float(psutil.virtual_memory().percent)
            # --- ▲▲▲ ここまで修正 ▲▲▲ ---
        except ImportError:
            return 50.0

    async def _measure_response_time(self) -> float:
        """応答時間の測定"""
        start_time = asyncio.get_event_loop().time()
        await asyncio.sleep(0.001)
        return asyncio.get_event_loop().time() - start_time

    def _calculate_error_rate(self) -> float:
        """エラー率の計算"""
        total_errors = len(self.orchestrator._initialization_errors)
        return min(total_errors / 10.0, 1.0)

    def _check_subsystem_connectivity(self) -> float:
        """サブシステム間の接続性チェック"""
        connected_count = sum(1 for instance in self.orchestrator.subsystems.values() if instance is not None)
        total_count = len(self.orchestrator.subsystems)
        return connected_count / total_count if total_count > 0 else 0.0

    def _detect_anomalies(self, health_metrics: Dict[str, Any]) -> List[str]:
        """異常の検出"""
        anomalies = []
        if health_metrics.get("overall_score", 0) < 0.5: anomalies.append("Overall system health is below threshold")
        if health_metrics.get("error_rate", 0) > 0.3: anomalies.append("High error rate detected")
        if health_metrics.get("memory_usage", 0) > 80.0: anomalies.append("High memory usage")
        if health_metrics.get("failed_subsystems", 0) > 2: anomalies.append("Multiple subsystem failures")
        return anomalies

    def _generate_health_recommendations(self, health_metrics: Dict[str, Any], anomalies: List[str]) -> List[str]:
        """健康改善の推奨事項を生成"""
        recommendations = []
        if "High error rate detected" in anomalies: recommendations.append("システムの再初期化を検討してください")
        if "High memory usage" in anomalies: recommendations.append("メモリ使用量を最適化してください")
        if "Multiple subsystem failures" in anomalies: recommendations.append("失敗したサブシステムの依存関係を確認してください")
        if not recommendations: recommendations.append("システムは正常に動作しています")
        return recommendations