# llm_api/reasoning/strategy_hub.py
# Title: Thinking Strategy Hub
# Role: Manages the storage, retrieval, and evolution of reasoning strategies, acting as the system's "library of thought".

import json
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)
STORAGE_FILE = Path(__file__).parent / "strategy_hub.json"

@dataclass
class Strategy:
    """Represents a single reasoning strategy."""
    id: str
    name: str
    problem_class: str
    steps: List[str]  # List of atomic module names
    performance_metrics: Dict[str, float] = field(default_factory=lambda: {"success_rate": 0.0, "execution_count": 0.0})
    version: int = 1

class ThinkingStrategyHub:
    """
    A hub that discovers, stores, and evolves reasoning strategies.
    This acts as the long-term memory for "how to think".
    """
    def __init__(self) -> None:
        self.strategies: Dict[str, Strategy] = self._load_strategies()
        logger.info(f"Thinking Strategy Hub initialized with {len(self.strategies)} strategies.")

    def _load_strategies(self) -> Dict[str, Strategy]:
        """Loads strategies from the JSON storage file."""
        if not STORAGE_FILE.exists():
            default_strategies: Dict[str, Strategy] = {
                "general_planning": Strategy(id="general_planning", name="General Planning Strategy", problem_class="planning", steps=["DECOMPOSE", "PLAN_STEP_BY_STEP", "VALIDATE_AND_REFINE"]),
                "general_analysis": Strategy(id="general_analysis", name="General Analysis Strategy", problem_class="analysis", steps=["CRITICAL_THINKING", "SYNTHESIZE", "VALIDATE_AND_REFINE"]),
                "general_default": Strategy(id="general_default", name="Default Strategy", problem_class="general", steps=["DECOMPOSE", "SYNTHESIZE"]),
            }
            self.strategies = default_strategies
            self._save_strategies()
            return default_strategies
        try:
            with open(STORAGE_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {sid: Strategy(**s_data) for sid, s_data in data.items()}
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Failed to load strategies from {STORAGE_FILE}: {e}")
            return {}

    def _save_strategies(self) -> None:
        """Saves the current strategies to the JSON storage file."""
        try:
            with open(STORAGE_FILE, 'w', encoding='utf-8') as f:
                serializable_data = {sid: asdict(strategy) for sid, strategy in self.strategies.items()}
                json.dump(serializable_data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Failed to save strategies to {STORAGE_FILE}: {e}")

    def add_strategy(self, strategy: Strategy) -> None:
        """Adds a new strategy to the hub and saves it."""
        if strategy.id in self.strategies:
            logger.warning(f"Strategy with ID {strategy.id} already exists. Overwriting.")
        self.strategies[strategy.id] = strategy
        self._save_strategies()
        logger.info(f"Added new strategy '{strategy.name}' to the hub.")

    def get_best_strategy(self, problem_class: str) -> Optional[Strategy]:
        """Finds the best strategy for a given problem class based on performance."""
        candidate_strategies = [s for s in self.strategies.values() if s.problem_class == problem_class]
        if not candidate_strategies:
            return self.strategies.get("general_default")
        
        best = sorted(candidate_strategies, key=lambda s: (s.performance_metrics.get('success_rate', 0.0), s.performance_metrics.get('execution_count', 0.0)), reverse=True)[0]
        logger.info(f"Selected strategy '{best.name}' for problem class '{problem_class}'.")
        return best

    def update_strategy_performance(self, strategy_id: str, success: bool) -> None:
        """Updates the performance metrics of a strategy after execution."""
        if strategy_id not in self.strategies:
            logger.error(f"Attempted to update performance for non-existent strategy ID: {strategy_id}")
            return

        strategy = self.strategies[strategy_id]
        metrics = strategy.performance_metrics
        
        total_runs = metrics.get('execution_count', 0.0)
        current_success_rate = metrics.get('success_rate', 0.0)
        
        new_success_rate = (current_success_rate * total_runs + (1 if success else 0)) / (total_runs + 1)
        
        metrics['success_rate'] = new_success_rate
        metrics['execution_count'] = total_runs + 1
        
        self._save_strategies()
        logger.info(f"Updated performance for strategy '{strategy.name}': success_rate={new_success_rate:.2f}, runs={metrics['execution_count']}")