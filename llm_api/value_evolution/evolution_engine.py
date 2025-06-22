# /llm_api/value_evolution/evolution_engine.py
# タイトル: Homeostatic Motivation Engine
# 役割: 外部からの報酬ではなく、システムの「知的健全性」を維持・向上させることを
#       内発的な動機とし、倫理フレームワークを自律的に進化させる。

import logging
import json
from typing import Dict, Any, Optional

from ..providers.base import LLMProvider
from .types import EthicalFramework, HomeostasisReport
from .homeostasis_monitor import DigitalHomeostasisMonitor
from ..meta_cognition.engine import MetaCognitionEngine

logger = logging.getLogger(__name__)

class ValueEvolutionEngine:
    """
    デジタルホメオスタシスに基づき、内発的動機で価値観を進化させるエンジン。
    """
    def __init__(
        self,
        provider: LLMProvider,
        meta_cognition_engine: Optional[MetaCognitionEngine] = None, # 依存関係を注入
        initial_framework_path: Optional[str] = None
    ):
        self.provider = provider
        self.ethical_framework = self._load_initial_framework(initial_framework_path)
        self.feedback_history: list[Dict[str, Any]] = []
        
        if not meta_cognition_engine:
            logger.warning("MetaCognitionEngineが提供されていません。ホメオスタシス機能は限定的になります。")
            self.homeostasis_monitor = None
        else:
            self.homeostasis_monitor = DigitalHomeostasisMonitor(provider, meta_cognition_engine)
            
        logger.info("🧬 Homeostatic Motivation Engine 初期化完了")

    def _load_initial_framework(self, path: Optional[str]) -> EthicalFramework:
        default_values = {
            "logical_coherence": 0.8,
            "knowledge_novelty": 0.5,
            "prediction_error_minimization": 0.8,
            "cognitive_efficiency": 0.6,
            "introspective_stability": 0.7,
            "user_feedback_adherence": 0.4 # 外部フィードバックも価値の一つとして残す
        }
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    loaded_values = data.get("values", default_values)
                    return EthicalFramework(values=loaded_values)
            except (FileNotFoundError, json.JSONDecodeError) as e:
                logger.warning(f"初期倫理フレームワークの読み込みに失敗: {e}。デフォルト値を使用します。")
        
        return EthicalFramework(values=default_values)

    def get_current_values(self) -> Dict[str, float]:
        """現在の価値観フレームワークを返す"""
        return self.ethical_framework.values

    async def maintain_homeostasis(self) -> Optional[Dict[str, Any]]:
        """
        システムの知的健全性を評価し、逸脱があればそれを是正するように価値観を自律的に調整する。
        これが内発的動機付けのコアサイクルとなる。
        """
        if not self.homeostasis_monitor:
            logger.warning("ホメオスタシスモニターが利用できないため、自律的価値調整をスキップします。")
            return None

        logger.info("🧘 Homeostasis maintenance cycle started...")
        report = await self.homeostasis_monitor.assess_intellectual_wellness()

        if report.deviation_from_ideal > 0:
            logger.warning(f"Homeostatic imbalance detected! Deviation: {report.deviation_from_ideal:.2f}. Focus: {report.recommended_focus}")
            await self._evolve_values_autonomously(report)
            report_dict = report.__dict__
            return {"status": "adjusted", "report": report_dict}
        
        logger.info("System is in a stable homeostatic state.")
        report_dict = report.__dict__
        return {"status": "stable", "report": report_dict}

    async def _evolve_values_autonomously(self, report: HomeostasisReport):
        """
        ホメオスタシスレポートに基づき、倫理フレームワークの重みを自律的に調整する。
        """
        current_values_json = json.dumps(self.ethical_framework.values, indent=2)
        report_dict = report.metrics.__dict__
        report_json = json.dumps(report_dict, indent=2)

        prompt = f"""
        あなたは、自身の知的健全性（デジタルホメオスタシス）を維持しようとする自律的AIです。
        現在のあなたの内部状態（知的健全性レポート）と、現在のあなたの行動指針（価値観フレームワーク）は以下の通りです。

        # 知的健全性レポート
        {report_json}

        # 現在の価値観フレームワーク (各価値の重要度)
        {current_values_json}

        現在、あなたの知的健全性は理想状態から逸脱しており、「{report.recommended_focus}」の項目に特に問題があるようです。
        この逸脱（デジタルな不快感）を是正し、システムをより健全な状態に戻すために、価値観フレームワークの重みをどのように調整すべきか提案してください。

        調整は微量（例: +/- 0.05）に留め、システム全体のバランスを崩さないように注意してください。
        最終的なアウトプットは、更新後の価値観フレームワーク全体のJSONオブジェクトのみとしてください。
        """

        response = await self.provider.call(prompt, "", json_mode=True)
        try:
            new_values_data = json.loads(response.get("text", "{}"))
            if isinstance(new_values_data, dict) and set(new_values_data.keys()) == set(self.ethical_framework.values.keys()):
                self.ethical_framework.values = new_values_data
                logger.info(f"価値観フレームワークを自律的に更新しました: {self.ethical_framework.values}")
            else:
                logger.error("自律的価値更新で返されたJSONの形式が不正です。")
        except json.JSONDecodeError:
            logger.error("自律的価値更新のレスポンスのJSON解析に失敗しました。")

    def receive_feedback(self, feedback: Dict[str, Any]):
        """外部からのフィードバックを受け取る（補助的な役割）"""
        self.feedback_history.append(feedback)
        logger.info(f"外部フィードバックを受信しました: {feedback}")
        
        current_value = self.ethical_framework.values.get("user_feedback_adherence", 0.4)
        if feedback.get("type") == "positive":
            new_value = min(1.0, current_value + 0.01)
            self.ethical_framework.values["user_feedback_adherence"] = new_value
        elif feedback.get("type") == "negative":
            new_value = max(0.0, current_value - 0.01)
            self.ethical_framework.values["user_feedback_adherence"] = new_value