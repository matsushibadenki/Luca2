# /tests/test_reasoning.py
# タイトル: Reasoning Components Test Suite
# 役割: 思考戦略ハブ（ThinkingStrategyHub）および関連する推論コンポーネントの動作を検証する。

import pytest
import json
from pathlib import Path
from unittest.mock import patch

# テスト対象のクラス
from llm_api.reasoning.strategy_hub import ThinkingStrategyHub, Strategy

@pytest.fixture
def temp_strategy_file(tmp_path: Path) -> Path:
    """テスト用の戦略定義JSONファイルを作成するpytestフィクスチャ"""
    strategies_dir = tmp_path / "reasoning"
    strategies_dir.mkdir()
    file_path = strategies_dir / "strategy_hub.json"
    
    test_data = {
        "test_planning": {
            "id": "test_planning",
            "name": "Test Planning Strategy",
            "problem_class": "planning",
            "steps": ["DECOMPOSE", "PLAN_STEP_BY_STEP"],
            "performance_metrics": {"success_rate": 0.8, "execution_count": 10.0},
            "version": 1
        },
        "general_default": {
            "id": "general_default",
            "name": "Default Strategy",
            "problem_class": "general",
            "steps": ["DECOMPOSE", "SYNTHESIZE"],
            "performance_metrics": {"success_rate": 0.5, "execution_count": 20.0},
            "version": 1
        }
    }
    with file_path.open('w', encoding='utf-8') as f:
        json.dump(test_data, f, indent=4)
    return file_path

class TestThinkingStrategyHub:
    """ThinkingStrategyHubのテストスイート"""

    def test_initialization_with_no_file(self, tmp_path: Path):
        """JSONファイルが存在しない場合に、デフォルト戦略で初期化・保存されるかをテストする。"""
        storage_file = tmp_path / "new_strategy_hub.json"
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', storage_file):
            hub = ThinkingStrategyHub()
            # デフォルト戦略がロードされているか
            assert len(hub.strategies) > 0
            assert "general_default" in hub.strategies
            # ファイルが新規作成されたか
            assert storage_file.exists()
            with storage_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
                assert "general_default" in data

    def test_load_strategies_from_existing_file(self, temp_strategy_file: Path):
        """既存のJSONファイルから戦略を正しくロードできるかをテストする。"""
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', temp_strategy_file):
            hub = ThinkingStrategyHub()
            assert "test_planning" in hub.strategies
            assert hub.strategies["test_planning"].problem_class == "planning"
            assert hub.strategies["general_default"].performance_metrics["execution_count"] == 20.0

    def test_get_best_strategy_for_specific_class(self, temp_strategy_file: Path):
        """特定の問題クラスに最適な戦略を取得できるかをテストする。"""
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', temp_strategy_file):
            hub = ThinkingStrategyHub()
            strategy = hub.get_best_strategy("planning")
            assert strategy is not None
            assert strategy.id == "test_planning"

    def test_get_best_strategy_fallback_to_default(self, temp_strategy_file: Path):
        """特定の戦略がない場合にデフォルト戦略にフォールバックするかをテストする。"""
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', temp_strategy_file):
            hub = ThinkingStrategyHub()
            strategy = hub.get_best_strategy("non_existent_class")
            assert strategy is not None
            assert strategy.id == "general_default"

    def test_add_strategy(self, tmp_path: Path):
        """新しい戦略を追加し、それがファイルに永続化されるかをテストする。"""
        storage_file = tmp_path / "add_strategy_test.json"
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', storage_file):
            hub = ThinkingStrategyHub()  # デフォルトファイルが作成される
            new_strategy = Strategy(
                id="creative_writing",
                name="Creative Writing Strategy",
                problem_class="creative",
                steps=["ANALOGICAL_REASONING", "SYNTHESIZE"]
            )
            hub.add_strategy(new_strategy)

            # メモリ上で追加されたかを確認
            assert "creative_writing" in hub.strategies
            
            # ディスクに保存されたかを確認
            with storage_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
            assert "creative_writing" in data
            assert data["creative_writing"]["problem_class"] == "creative"

    def test_update_strategy_performance_on_success(self, temp_strategy_file: Path):
        """戦略のパフォーマンス指標が成功時に正しく更新されるかをテストする。"""
        with patch('llm_api.reasoning.strategy_hub.STORAGE_FILE', temp_strategy_file):
            hub = ThinkingStrategyHub()
            
            # 更新前の状態
            initial_runs = hub.strategies["test_planning"].performance_metrics["execution_count"]  # 10.0
            initial_rate = hub.strategies["test_planning"].performance_metrics["success_rate"]  # 0.8
            
            # 成功ケースで更新
            hub.update_strategy_performance("test_planning", success=True)
            
            # メモリ上の値を確認
            updated_metrics = hub.strategies["test_planning"].performance_metrics
            new_runs = initial_runs + 1
            expected_rate = (initial_rate * initial_runs + 1) / new_runs # (0.8 * 10 + 1) / 11 = 9 / 11
            
            assert updated_metrics["execution_count"] == new_runs
            assert updated_metrics["success_rate"] == pytest.approx(expected_rate)

            # ディスク上の値を確認
            with temp_strategy_file.open('r', encoding='utf-8') as f:
                data = json.load(f)
            saved_metrics = data["test_planning"]["performance_metrics"]
            assert saved_metrics["execution_count"] == new_runs
            assert saved_metrics["success_rate"] == pytest.approx(expected_rate)