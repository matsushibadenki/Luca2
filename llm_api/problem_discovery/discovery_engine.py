# /llm_api/problem_discovery/discovery_engine.py
# タイトル: Problem Discovery Engine (Orchestrator)
# 役割: 問題発見のワークフロー全体を管理するオーケストレーター。データの前処理、各発見戦略の実行、結果の統合と分析を調整する。

import asyncio
import json  # ★ 修正: jsonモジュールをインポート
import logging
import time
from collections import deque
from typing import Any, Dict, List, Optional, cast

import numpy as np
from ..providers.base import LLMProvider
from .strategies import from_patterns
from . import utils
from .types import DiscoveredProblem # ★ 修正: 型定義をインポート

logger = logging.getLogger(__name__)


class ProblemDiscoveryEngine:
    """
    自律的問題発見エンジン。
    システム内外のデータから、まだ顕在化していない問題をプロアクティブに発見する。
    このクラスは、処理フローを管理するオーケストレーターとして機能する。
    """

    def __init__(self, provider: LLMProvider):
        """エンジンの初期化"""
        self.provider = provider
        self.discovered_problems: Dict[str, Any] = {}
        self.discovery_history: deque[Dict[str, Any]] = deque(maxlen=1000)
        logger.info("🧠 Problem Discovery Engine (Orchestrator) 初期化完了")

    async def discover_problems_from_data(
        self,
        data_sources: List[Dict[str, Any]],
        domain_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        与えられたデータソースから潜在的な問題を発見するメインメソッド。

        Args:
            data_sources: 分析対象のデータソースのリスト。
            domain_context: 問題発見のドメインに関するコンテキスト情報。

        Returns:
            発見された問題の要約と分析結果を含む辞書。
        """
        logger.info(f"データからの問題発見プロセス開始: {len(data_sources)}個のソース")
        domain_context = domain_context or {}
        all_discovered_problems: List[DiscoveredProblem] = []

        # 1. データの前処理
        logger.info("ステップ1: データの前処理を開始...")
        patterns = await utils.extract_data_patterns(self.provider, data_sources)
        anomalies = await utils.detect_anomalies(self.provider, data_sources, patterns)
        causal_networks = await utils.infer_causal_relationships(self.provider, data_sources, patterns)

        # 2. 各発見戦略の並列実行
        logger.info("ステップ2: 各発見戦略の並列実行を開始...")
        discovery_tasks = [
            from_patterns.discover_from_patterns(self.provider, patterns, domain_context),
            # 他戦略も同様に追加 (現在はスタブ)
            # from_anomalies.discover_from_anomalies(self.provider, anomalies, domain_context),
            # from_causality.discover_from_causality(self.provider, causal_networks, domain_context),
        ]
        results = await asyncio.gather(*discovery_tasks)
        for problems_list in results:
            all_discovered_problems.extend(problems_list)

        # 3. 結果の後処理
        logger.info("ステップ3: 発見された問題の後処理を開始...")
        unique_problems = utils.deduplicate_and_merge_problems(all_discovered_problems)
        prioritized_problems = utils.prioritize_problems(unique_problems)

        # 4. 問題の登録
        for problem in prioritized_problems:
            if problem.problem_id not in self.discovered_problems:
                self.discovered_problems[problem.problem_id] = problem.to_dict()
                self.discovery_history.append({
                    "timestamp": time.time(),
                    "problem_id": problem.problem_id,
                    "discovery_method": problem.discovery_method.value,
                    "confidence": problem.confidence_score
                })

        # 5. 最終分析とレポート生成
        logger.info("ステップ4: 最終分析とレポート生成を開始...")
        final_analysis = await self._analyze_discovery_results(prioritized_problems)

        discovery_report = {
            "problems_discovered": len(prioritized_problems),
            "problem_details": [utils.format_problem_summary(p) for p in prioritized_problems],
            "discovery_methods_used": list(set(p.discovery_method.value for p in prioritized_problems)),
            "severity_distribution": utils.calculate_severity_distribution(prioritized_problems),
            "high_priority_problems": [p.problem_id for p in prioritized_problems if p.urgency_score > 0.8],
            **final_analysis
        }

        logger.info(f"問題発見完了: {len(prioritized_problems)}個のユニークな問題を発見・更新")
        return discovery_report

    async def _analyze_discovery_results(self, problems: List[DiscoveredProblem]) -> Dict[str, Any]:
        """発見された問題群全体を分析し、高次の洞察を得る"""
        if not problems:
            return {}

        analysis_prompt = f"""
        以下に、システム内で自律的に発見された潜在的な問題のリストを示します。
        これらの問題全体を俯瞰し、以下の点について分析してください。
        1. 全体的なシステムの健全性に関する洞察
        2. 問題間に共通する根本原因やテーマ
        3. 特に注意を払うべき、複数の問題にまたがるドメインや領域

        発見された問題リスト:
        {json.dumps([utils.format_problem_summary(p) for p in problems[:10]], indent=2)}

        分析結果をJSON形式で返してください。
        """
        response = await self.provider.call(analysis_prompt, "")
        try:
            analysis = cast(Dict[str, Any], json.loads(response.get("text", "{}")))
            if problems:
                overall_confidence = np.mean([p.confidence_score for p in problems])
                analysis["overall_confidence"] = float(overall_confidence)
            return analysis
        except (json.JSONDecodeError, TypeError):
            return {}