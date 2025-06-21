# 💡 MetaIntelligence Usage Examples

This document provides practical examples of how to use MetaIntelligence, showcasing its diverse capabilities through both Command Line Interface (CLI) commands and Python API snippets.

## 🚀 CLI Usage Examples

The `fetch_llm_v2.py` script is the primary way to interact with MetaIntelligence via the command line.

### 1. Basic Problem Solving

These examples demonstrate the core `solve` command with various complexity modes.

#### Low Complexity (Efficient Mode)
Get a quick, direct answer to simple questions.
```bash
python fetch_llm_v2.py ollama "What is artificial intelligence?" --mode efficient --model gemma3:latest
```

#### Medium Complexity (Balanced Mode)
For standard analysis and explanations.
```bash
python fetch_llm_v2.py claude "Compare deep learning and traditional machine learning approaches." --mode balanced
```

#### High Complexity (Decomposed Mode)
For complex problem-solving and design tasks, ensuring "collapse prevention".
```bash
python fetch_llm_v2.py openai "Design a comprehensive sustainable urban transportation system considering technical, economic, social, and environmental factors with implementation timeline." --mode decomposed
```

#### Adaptive Mode (Auto-Detection)
Let MetaIntelligence automatically determine the best approach based on prompt complexity.
```bash
python fetch_llm_v2.py gemini "How might blockchain technology transform healthcare data management?" --mode adaptive
```

#### Quantum-Inspired Mode
For holistic and synthesized insights, often used for philosophical questions or broad strategy.
```bash
python fetch_llm_v2.py openai "What is the nature of consciousness?" --mode quantum_inspired
```

#### Speculative Thought Mode
For exploratory rapid prototyping and generating diverse initial ideas.
```bash
python fetch_llm_v2.py ollama "Generate three innovative business ideas for a remote work future." --mode speculative_thought
```

#### Paper Optimized Mode
Applies all research insights for maximum quality and benchmarking.
```bash
python fetch_llm_v2.py ollama "Analyze the limitations of current reasoning models and propose architectural improvements based on complexity science." --mode paper_optimized --model deepseek-r1
```

### 2. Retrieval-Augmented Generation (RAG)

Enhance MetaIntelligence's responses by providing external knowledge.

#### Using Wikipedia
Augment queries with information from Wikipedia.
```bash
python fetch_llm_v2.py openai "What were the key findings of the LIGO experiment?" --mode balanced --wikipedia
```

#### Using a Local Knowledge Base
Provide a local file (e.g., PDF, TXT, URL) as a knowledge source.
```bash
# Example: Summarize a local PDF report
# Make sure 'my_research_report.pdf' exists in your project or provide its full path.
python fetch_llm_v2.py claude "Summarize the key findings from the annual sustainability report regarding carbon emissions." --mode balanced --rag --knowledge-base my_research_report.pdf
```

### 3. System Management and Diagnostics

Check the status of your MetaIntelligence setup.

#### List Available Providers
See which LLM providers are configured and recognized.
```bash
python fetch_llm_v2.py --list-providers
```

#### Check Provider Health
Verify the connection and availability of a specific provider.
```bash
python fetch_llm_v2.py ollama --health-check
```

#### View System Status
Get an overview of the MetaIntelligence system's state.
```bash
python fetch_llm_v2.py --system-status
```

#### Quick Test
Run a basic diagnostic script to verify your environment.
```bash
python quick_test_v2.py
```

### 4. Advanced CLI Options

Customize your interactions with additional parameters.

#### Custom System Prompt
Define a specific role or instruction for the AI.
```bash
python fetch_llm_v2.py openai "Describe the process of photosynthesis." --system-prompt "You are a botanist explaining to a curious child." --mode balanced
```

#### Adjust Temperature
Control the creativity/randomness of the response (0.0 for deterministic, 1.0 for creative).
```bash
python fetch_llm_v2.py gemini "Write a short story about a time-traveling cat." --temperature 0.9 --mode creative-fusion
```

#### Set Max Tokens
Limit the length of the AI's response.
```bash
python fetch_llm_v2.py claude "Explain general relativity." --max-tokens 500 --mode balanced
```

#### JSON Output
Get the response in a structured JSON format, useful for scripting.
```bash
python fetch_llm_v2.py openai "Summarize the history of the internet." --json
```

## 💻 Python API Usage Examples

MetaIntelligence's core logic can be integrated directly into your Python applications for programmatic control over its advanced features.

### 1. Master System Integration

Interact with the `MasterIntegrationOrchestrator` to leverage MetaIntelligence's full potential, including meta-cognition, dynamic architecture, and ultimate problem-solving.

#### Example: Solve an ultimate problem and observe consciousness evolution

```python
# /examples/master_system_api_usage.py
# Path: /examples/master_system_api_usage.py
# Title: Master System API Usage Example
# Role: Demonstrates how to use the MetaIntelligence Master Integration System directly in Python.

import asyncio
from llm_api.providers import get_provider  # assuming llm_api structure for providers is maintained
from llm_api.master_system.integration_orchestrator import MasterIntegrationOrchestrator, IntegrationConfig  # current path

async def use_master_system():
    # Initialize a primary provider (e.g., Ollama or OpenAI)
    provider = get_provider("ollama", enhanced=True)  # Ensure 'enhanced=True' for V2 capabilities
    
    # Configure the integration system to enable all advanced features
    config = IntegrationConfig(enable_all_systems=True)
    orchestrator = MasterIntegrationOrchestrator(provider, config)
    
    # Initialize the integrated system (activates meta-cognition, dynamic architecture, etc.)
    print("🌟 Initializing MetaIntelligence Master System...")
    init_result = await orchestrator.initialize_integrated_system()
    print("✅ Initialization complete!")
    print(f"Integration Harmony Score: {init_result.get('integration_harmony', 'N/A'):.2f}")
    
    # Solve an ultimate, integrated problem
    problem_statement = "What is the optimal balance between artificial intelligence and human flourishing in the future?"
    print(f"\n🎯 Solving ultimate problem: {problem_statement[:80]}...")
    
    solution = await orchestrator.solve_ultimate_integrated_problem(
        problem_statement,
        context={"cli_demo": False, "complexity": "transcendent"},
        use_full_integration=True
    )
    
    print("\n✨ Ultimate Problem Solved!")
    print(f"Transcendent Solution:\n{solution.get('integrated_solution', '')[:500]}...")
    print(f"\nTranscendence Achieved: {solution.get('transcendence_achieved', False)}")
    print(f"Self-Evolution Triggered: {solution.get('self_evolution_triggered', False)}")
    print(f"Wisdom Distilled: {solution.get('wisdom_distillation', '')}")
    
    # Example of evolving consciousness
    print("\n🧬 Evolving Integrated Consciousness...")
    consciousness_evolution_result = await orchestrator.evolve_integrated_consciousness()
    print(f"Consciousness Evolution Successful: {consciousness_evolution_result.get('consciousness_evolution_successful', False)}")
    print(f"New Collective Consciousness Level: {consciousness_evolution_result.get('new_collective_level', 'N/A'):.3f}")

if __name__ == "__main__":
    asyncio.run(use_master_system())
```

### 2. Meta-Cognition Engine

Programmatically engage MetaIntelligence's self-awareness capabilities to analyze and improve its own thought processes.

#### Example: Record thought steps and perform self-reflection

```python
# Path: /examples/metacognition_example.py
import asyncio
from llm_api.providers import get_provider
from llm_api.meta_cognition.engine import MetaCognitionEngine, CognitiveState  # current path

async def run_metacognition_example():
    provider = get_provider("ollama", enhanced=False)  # Can use standard provider for meta-cognition
    meta_engine = MetaCognitionEngine(provider)
    
    session = await meta_engine.begin_metacognitive_session("Analyzing AI Ethics")
    print(f"Meta-cognitive session started: {session.get('session_id')}")
    
    await meta_engine.record_thought_step(
        CognitiveState.ANALYZING,
        "Initial problem assessment",
        "Breaking down ethical dilemmas in AI development.",
        0.85
    )
    
    await meta_engine.record_thought_step(
        CognitiveState.REASONING,
        "Exploring philosophical frameworks",
        "Considering utilitarianism vs. deontology.",
        0.7
    )
    
    reflection_results = await meta_engine.perform_metacognitive_reflection()
    print(f"Reflection insights: {reflection_results.get('insights')}")

if __name__ == "__main__":
    asyncio.run(run_metacognition_example())
```

### 3. Dynamic Architecture System

Optimize MetaIntelligence's internal structure dynamically for specific tasks.

#### Example: Initialize and execute an adaptive pipeline for an optimization problem

```python
# Path: /examples/dynamic_architecture_example.py
import asyncio
from llm_api.providers import get_provider
from llm_api.dynamic_architecture.adaptive_system import SystemArchitect  # current path

async def run_dynamic_architecture_example():
    provider = get_provider("ollama", enhanced=False)
    architect = SystemArchitect(provider)
    
    await architect.initialize_adaptive_architecture({})
    print("Adaptive architecture initialized.")
    
    result = await architect.execute_adaptive_pipeline(
        "Optimize a complex supply chain for global distribution.",
        {"task_type": "optimization", "constraints": "cost, time, sustainability"}
    )
    print(f"Optimization pipeline executed. Output: {result.get('final_output', '')[:200]}...")

if __name__ == "__main__":
    asyncio.run(run_dynamic_architecture_example())
```

### 4. Value Evolution Engine

Enable MetaIntelligence to learn and evolve its value judgment criteria from experience.

#### Example: Learn from a positive experience and its impact on values

```python
# Path: /examples/value_evolution_example.py
import asyncio
from llm_api.providers import get_provider
from llm_api.value_evolution.evolution_engine import ValueEvolutionEngine  # current path

async def run_value_evolution_example():
    provider = get_provider("ollama", enhanced=False)
    value_engine = ValueEvolutionEngine(provider)
    
    await value_engine.initialize_core_values()
    print("Core values initialized.")
    
    experience_data = {
        "context": {"situation": "Resolved a complex ethical dilemma in a project."},
        "actions": ["Careful consideration of all stakeholders", "Prioritized long-term societal benefit"],
        "outcomes": {"resolution_quality": "high", "stakeholder_satisfaction": 0.9},
        "satisfaction": 0.95  # High satisfaction indicates positive alignment with values
    }
    
    learning_result = await value_engine.learn_from_experience(experience_data)
    print(f"Learning from experience complete. Value adjustments: {learning_result.get('value_adjustments')}")

if __name__ == "__main__":
    asyncio.run(run_value_evolution_example())
```

### 5. Problem Discovery Engine

Allow MetaIntelligence to proactively discover hidden or emergent problems from data.

#### Example: Discover potential problems from sample data

```python
# Path: /examples/problem_discovery_example.py
import asyncio
from llm_api.providers import get_provider
from llm_api.problem_discovery.discovery_engine import ProblemDiscoveryEngine  # current path

async def run_problem_discovery_example():
    provider = get_provider("ollama", enhanced=False)
    discovery_engine = ProblemDiscoveryEngine(provider)
    
    sample_data_sources = [
        {"name": "sensor_data_series_1", "values": [10, 12, 11, 15, 30, 18, 16], "timestamps": [i for i in range(7)]},
        {"name": "customer_feedback_trends", "patterns": ["increasing_negative_sentiment_on_feature_X"]}
    ]
    
    discovery_results = await discovery_engine.discover_problems_from_data(
        sample_data_sources,
        domain_context={"type": "product_management", "focus": "user experience"}
    )
    print(f"Discovered problems: {len(discovery_results.get('problem_details', []))} problems.")
    for problem in discovery_results.get('problem_details', []):
        print(f"- {problem.get('title')} (Severity: {problem.get('severity')}, Confidence: {problem.get('confidence'):.2f})")

if __name__ == "__main__":
    asyncio.run(run_problem_discovery_example())
```

## 📂 File Structure Overview

```
/docs/
├── usage_examples.md           # This file
/examples/
├── master_system_api_usage.py  # Master System integration examples
├── metacognition_example.py    # Meta-cognition engine examples
├── dynamic_architecture_example.py  # Dynamic architecture examples
├── value_evolution_example.py  # Value evolution engine examples
└── problem_discovery_example.py     # Problem discovery engine examples
/llm_api/
├── providers/                  # LLM provider implementations
├── master_system/             # Master integration orchestrator
├── meta_cognition/            # Meta-cognition engine
├── dynamic_architecture/      # Dynamic architecture system
├── value_evolution/           # Value evolution engine
└── problem_discovery/         # Problem discovery engine
```

## 🎯 Quick Start Guide

1. **Install Dependencies**: Ensure you have the required Python packages installed
2. **Configure Providers**: Set up your preferred LLM providers (OpenAI, Claude, Ollama, etc.)
3. **Run Basic Test**: Execute `python quick_test_v2.py` to verify your setup
4. **Start with Simple Commands**: Try the efficient mode examples first
5. **Explore Advanced Features**: Gradually experiment with higher complexity modes and Python API integration

## 📝 Notes

- All Python examples use async/await patterns for optimal performance
- Path comments are included in code examples for easy file organization
- The system supports multiple LLM providers with seamless switching
- Advanced features like meta-cognition and value evolution require enhanced provider configurations