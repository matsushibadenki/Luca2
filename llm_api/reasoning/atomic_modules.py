# llm_api/reasoning/atomic_modules.py
# Title: Atomic Reasoning Modules
# Role: Defines the fundamental building blocks of thought, inspired by the SELF-DISCOVER paper. These are the "Lego bricks" for constructing complex reasoning strategies.

from typing import Dict

# 各モジュールは、LLMに特定の思考プロセスを促すためのプロンプトテンプレートとして機能します。
ATOMIC_REASONING_MODULES: Dict[str, str] = {
    "DECOMPOSE": """
        Break down the given complex problem into smaller, manageable, and logical sub-problems.
        List the sub-problems in the order they should be solved.
        Original Problem: {input}
    """,
    "CRITICAL_THINKING": """
        Critically evaluate the following statement or proposal.
        Identify potential biases, hidden assumptions, and logical fallacies.
        Consider counterarguments and alternative perspectives.
        Statement to Evaluate: {input}
    """,
    "PLAN_STEP_BY_STEP": """
        Create a detailed, step-by-step plan to achieve the following objective.
        The plan should be practical and actionable.
        Objective: {input}
    """,
    "SYNTHESIZE": """
        Synthesize the following pieces of information into a single, coherent, and comprehensive summary.
        Draw connections between different points and identify the overarching theme.
        Information to Synthesize: {input}
    """,
    "ANALOGICAL_REASONING": """
        Find an analogy from a different domain to better understand the following problem.
        Explain how the analogy helps to clarify the core issue and suggest potential solutions.
        Problem: {input}
    """,
    "VALIDATE_AND_REFINE": """
        Review the following solution draft. Validate its correctness, completeness, and clarity.
        Refine the draft to produce a polished and robust final version.
        Draft to Validate and Refine: {input}
    """
}

def get_atomic_module_prompt(module_name: str, input_text: str) -> str:
    """
    Returns the formatted prompt for a given atomic module.
    """
    if module_name not in ATOMIC_REASONING_MODULES:
        raise ValueError(f"Unknown atomic module: {module_name}")
    return ATOMIC_REASONING_MODULES[module_name].format(input=input_text)

