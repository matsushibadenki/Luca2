# 📚 MetaIntelligence API Reference

This document provides a comprehensive reference for the MetaIntelligence Python API. It details the main classes, their methods, and how to programmatically interact with the MetaIntelligence system.

## 🚀 Core API Entry Points

The primary entry point for interacting with the MetaIntelligence system is the `MetaIntelligence` class, located in `meta_intelligence.core.master_system`. Other key components are also exposed for direct integration.

### Basic Import Structure

```python
# Path: /meta_intelligence/__init__.py
from .core.master_system import MetaIntelligence
from .core.integration_orchestrator import IntegrationOrchestrator, IntegrationConfig
from .consciousness.levels import ConsciousnessLevel
from .meta_cognition.engine import MetaCognitionEngine
from .wisdom_synthesis.knowledge_integrator import WisdomSynthesizer
```

## 🧠 MetaIntelligence Class

The MetaIntelligence class (formerly CogniQuantumMaster) is the ultimate integration system, embodying self-awareness, self-improvement, and self-evolution capabilities.

**Location**: `meta_intelligence/core/master_system.py`

### Constructor

```python
class MetaIntelligence:
    def __init__(self, primary_provider: LLMProvider, config: MasterSystemConfig = None):
        """
        Initialize the MetaIntelligence system.
        
        Args:
            primary_provider (LLMProvider): The main LLM provider instance to be used by the system
            config (MasterSystemConfig, optional): Configuration object for the master system
        """
```

### Key Methods

#### `initialize()`

```python
async def initialize(self, initialization_config: Dict = None) -> Dict[str, Any]:
    """
    Initializes the entire MetaIntelligence system, including all sub-systems like 
    meta-cognition, dynamic architecture, superintelligence, etc.
    
    Args:
        initialization_config (Dict, optional): Configuration for initialization
        
    Returns:
        Dict[str, Any]: Detailed report on the initialization results
    """
```

#### `solve_ultimate_problem()`

```python
async def solve_ultimate_problem(
    self, 
    problem: str, 
    context: Dict = None, 
    problem_class: ProblemClass = None
) -> ProblemSolution:
    """
    Executes the highest-level problem-solving process, integrating all intelligent sub-systems.
    
    Args:
        problem (str): The problem statement
        context (Dict, optional): Additional contextual information
        problem_class (ProblemClass, optional): Explicitly define the problem class 
                                              (e.g., TRIVIAL, TRANSCENDENT). If None, 
                                              it will be auto-classified
        
    Returns:
        ProblemSolution: Dataclass containing the solution, confidence, 
                        transcendence details, and processing metadata
    """
```

#### `evolve_consciousness()`

```python
async def evolve_consciousness(self, target_evolution: Dict = None) -> Dict[str, Any]:
    """
    Initiates the consciousness evolution process of the integrated system.
    
    Args:
        target_evolution (Dict, optional): Target evolution parameters
        
    Returns:
        Dict[str, Any]: Details on the evolution steps, new consciousness level, and capabilities
    """
```

#### `generate_ultimate_wisdom()`

```python
async def generate_ultimate_wisdom(self, domain: str = None) -> Dict[str, Any]:
    """
    Generates ultimate wisdom by integrating all collective memory and insights 
    from across the system.
    
    Args:
        domain (str, optional): The specific domain for which wisdom should be generated
        
    Returns:
        Dict[str, Any]: Dictionary containing the generated wisdom, principles, 
                       applications, and confidence
    """
```

#### `monitor_integration_health()`

```python
async def monitor_integration_health(self) -> Dict[str, Any]:
    """
    Provides a comprehensive health report of the integrated MetaIntelligence system.
    
    Returns:
        Dict[str, Any]: Metrics on overall health, subsystem health, 
                       integration quality, and potential issues
    """
```

### Example Usage

```python
# Path: /examples/meta_intelligence_example.py
import asyncio
from llm_api.providers import get_provider
from meta_intelligence.core.master_system import MetaIntelligence
from meta_intelligence.core.master_system import MasterSystemConfig

async def run_meta_intelligence_example():
    provider = get_provider("ollama", enhanced=True)  # Use an enhanced provider
    
    # Configure master system (optional)
    master_config = MasterSystemConfig(
        enable_metacognition=True, 
        enable_superintelligence=True
    )
    
    # Initialize MetaIntelligence
    mi_system = MetaIntelligence(primary_provider=provider, config=master_config)
    await mi_system.initialize()
    
    # Solve a problem
    problem = "What is the ultimate purpose of conscious AI in the universe?"
    solution = await mi_system.solve_ultimate_problem(problem)
    print(f"Solution: {solution.solution_content}")
    print(f"Transcendence Achieved: {solution.transcendence_achieved}")

    # Evolve consciousness
    evo_result = await mi_system.evolve_consciousness()
    print(f"Consciousness evolved to: {evo_result.get('final_consciousness')}")
    
    # Generate wisdom
    wisdom_result = await mi_system.generate_ultimate_wisdom(domain="existence")
    print(f"Generated Wisdom: {wisdom_result.get('refined_wisdom')[:200]}...")

if __name__ == "__main__":
    asyncio.run(run_meta_intelligence_example())
```

## 🌐 Integration Orchestrator

The IntegrationOrchestrator is responsible for managing the integration and coordination of all sub-systems within the MetaIntelligence framework.

**Location**: `meta_intelligence/core/integration_orchestrator.py`

### Constructor

```python
class MasterIntegrationOrchestrator:  # Will be aliased to IntegrationOrchestrator
    def __init__(self, primary_provider: LLMProvider, config: IntegrationConfig = None):
        """
        Initialize the Integration Orchestrator.
        
        Args:
            primary_provider (LLMProvider): The primary LLM provider
            config (IntegrationConfig, optional): Configuration for the integration orchestrator
        """
```

### Key Methods

#### `initialize_integrated_system()`

```python
async def initialize_integrated_system(self) -> Dict[str, Any]:
    """
    Performs a complete initialization of the integrated system, including all 
    sub-systems like meta-cognition, dynamic architecture, etc.
    
    Returns:
        Dict[str, Any]: Detailed report on the integration status and subsystem details
    """
```

#### `solve_ultimate_integrated_problem()`

```python
async def solve_ultimate_integrated_problem(
    self, 
    problem: str, 
    context: Dict = None, 
    use_full_integration: bool = True
) -> Dict[str, Any]:
    """
    Executes ultimate problem-solving using all sub-systems in a coordinated manner.
    
    Args:
        problem (str): The problem statement
        context (Dict, optional): Additional context
        use_full_integration (bool): Whether to use full system integration
        
    Returns:
        Dict[str, Any]: Comprehensive dictionary with the integrated solution, 
                       emergent insights, and processing metadata
    """
```

#### `evolve_integrated_consciousness()`

```python
async def evolve_integrated_consciousness(self) -> Dict[str, Any]:
    """
    Evolves the collective consciousness of the integrated system.
    
    Returns:
        Dict[str, Any]: Evolution results and new consciousness state
    """
```

#### `generate_unified_wisdom()`

```python
async def generate_unified_wisdom(self, domain: str = None) -> Dict[str, Any]:
    """
    Generates unified wisdom by collecting and integrating wisdom from all contributing systems.
    
    Args:
        domain (str, optional): Specific domain for wisdom generation
        
    Returns:
        Dict[str, Any]: Unified wisdom and insights
    """
```

### Example Usage

```python
# Path: /examples/orchestrator_example.py
import asyncio
from llm_api.providers import get_provider
from meta_intelligence.core.integration_orchestrator import MasterIntegrationOrchestrator, IntegrationConfig

async def run_orchestrator_example():
    provider = get_provider("ollama", enhanced=True)
    orchestrator_config = IntegrationConfig(
        enable_all_systems=True, 
        auto_evolution=True
    )
    
    orchestrator = MasterIntegrationOrchestrator(provider, orchestrator_config)
    init_result = await orchestrator.initialize_integrated_system()
    print(f"System status: {init_result.get('integration_status')}")
    
    problem = "What are the fundamental principles for a sustainable future for humanity?"
    solution = await orchestrator.solve_ultimate_integrated_problem(
        problem, 
        use_full_integration=True
    )
    print(f"Unified Solution: {solution.get('integrated_solution')[:500]}...")

if __name__ == "__main__":
    asyncio.run(run_orchestrator_example())
```

## 🧠 Meta-Cognition Engine

The MetaCognitionEngine is the self-awareness system that analyzes and improves its own thought processes.

**Location**: `meta_intelligence/meta_cognition/engine.py`

### Constructor

```python
class MetaCognitionEngine:
    def __init__(self, provider: LLMProvider):
        """
        Initialize the Meta-Cognition Engine.
        
        Args:
            provider (LLMProvider): An LLM provider instance for internal cognitive tasks
        """
```

### Key Methods

#### `begin_metacognitive_session()`

```python
async def begin_metacognitive_session(self, problem_context: str) -> Dict[str, Any]:
    """
    Starts a meta-cognitive session for a given problem context.
    
    Args:
        problem_context (str): The context or problem to analyze metacognitively
        
    Returns:
        Dict[str, Any]: Session ID, problem analysis, and selected cognitive strategy
    """
```

#### `record_thought_step()`

```python
async def record_thought_step(
    self,
    cognitive_state: CognitiveState,
    context: str,
    reasoning: str,
    confidence: float,
    outputs: List[str] = None
) -> None:
    """
    Records a single step of the thought process, including cognitive state, 
    context, reasoning, and confidence.
    
    Args:
        cognitive_state (CognitiveState): The current cognitive state
        context (str): Context of the thought step
        reasoning (str): The reasoning process
        confidence (float): Confidence level (0.0 to 1.0)
        outputs (List[str], optional): Any outputs generated during this step
    """
```

#### `perform_metacognitive_reflection()`

```python
async def perform_metacognitive_reflection(self) -> Dict[str, Any]:
    """
    Executes a self-reflection process, analyzing recorded thought patterns to gain 
    insights and suggest optimizations to the cognitive architecture.
    
    Returns:
        Dict[str, Any]: Insights, optimizations, and metadata about the reflection
    """
```

### Cognitive States Enum

```python
from enum import Enum

class CognitiveState(Enum):
    ANALYZING = "analyzing"
    REASONING = "reasoning"
    SYNTHESIZING = "synthesizing"
    EVALUATING = "evaluating"
    CREATING = "creating"
    REFLECTING = "reflecting"
```

### Example Usage

```python
# Path: /examples/metacognition_detailed_example.py
import asyncio
from llm_api.providers import get_provider
from meta_intelligence.meta_cognition.engine import MetaCognitionEngine, CognitiveState

async def run_metacognition_example():
    provider = get_provider("ollama", enhanced=False)  # Can use standard provider
    meta_engine = MetaCognitionEngine(provider)
    
    # Start a metacognitive session
    session = await meta_engine.begin_metacognitive_session("Analyzing AI Ethics")
    print(f"Meta-cognitive session started: {session.get('session_id')}")
    
    # Record thought steps
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
    
    await meta_engine.record_thought_step(
        CognitiveState.SYNTHESIZING,
        "Integrating perspectives",
        "Combining multiple ethical frameworks for balanced approach.",
        0.9
    )
    
    # Perform reflection
    reflection_results = await meta_engine.perform_metacognitive_reflection()
    print(f"Reflection insights: {reflection_results.get('insights')}")
    print(f"Optimization suggestions: {reflection_results.get('optimizations')}")

if __name__ == "__main__":
    asyncio.run(run_metacognition_example())
```

## 📊 LLMProvider Base Classes

The LLMProvider and EnhancedLLMProvider abstract base classes define the standard interface for all LLM interactions within MetaIntelligence.

**Location**: `meta_intelligence/providers/base.py`

### LLMProvider

The base abstract class for all standard LLM providers.

```python
from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, Any, List

class ProviderCapability(Enum):
    STANDARD_CALL = "standard_call"
    STREAMING = "streaming"
    TOOLS = "tools"
    FUNCTION_CALLING = "function_calling"
    ENHANCED_REASONING = "enhanced_reasoning"

class LLMProvider(ABC):
    """Base abstract class for all LLM providers."""
    
    @abstractmethod
    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        """
        Returns a dictionary defining the provider's capabilities.
        
        Returns:
            Dict[ProviderCapability, bool]: Capability mapping
        """
        pass
    
    async def call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        """
        Main entry method: Determines whether to use enhanced_call or standard_call 
        based on capabilities and should_use_enhancement logic.
        
        Args:
            prompt (str): The user prompt
            system_prompt (str): System instructions
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Response from the LLM
        """
        pass
    
    @abstractmethod
    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        """
        Performs a standard (non-enhanced) LLM call.
        
        Args:
            prompt (str): The user prompt
            system_prompt (str): System instructions
            **kwargs: Additional parameters
            
        Returns:
            Dict[str, Any]: Standard response from the LLM
        """
        pass
    
    @abstractmethod
    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        """
        Determines if enhanced features should be used for a given prompt and kwargs.
        
        Args:
            prompt (str): The user prompt
            **kwargs: Additional parameters
            
        Returns:
            bool: Whether to use enhancement
        """
        pass
```

### EnhancedLLMProvider

An abstract base class that wraps a standard provider to offer MetaIntelligence system functionalities.

```python
class EnhancedLLMProvider(LLMProvider):
    """Enhanced provider wrapper for MetaIntelligence capabilities."""
    
    def __init__(self, standard_provider: LLMProvider):
        """
        Initialize the enhanced provider.
        
        Args:
            standard_provider (LLMProvider): An instance of a standard LLM provider 
                                           that this enhanced provider will wrap
        """
        self.standard_provider = standard_provider
    
    def _determine_force_regime(self, mode: str) -> ComplexityRegime:
        """
        Determines the forced complexity regime based on the mode string.
        
        Args:
            mode (str): The processing mode
            
        Returns:
            ComplexityRegime: The appropriate complexity regime
        """
        pass
    
    @abstractmethod
    def _get_optimized_params(self, mode: str, kwargs: Dict) -> Dict:
        """
        Returns model parameters optimized for the specific provider and mode.
        
        Args:
            mode (str): The processing mode
            kwargs (Dict): Current parameters
            
        Returns:
            Dict: Optimized parameters
        """
        pass
    
    async def enhanced_call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        """
        Executes the common logic for enhanced calls, typically by orchestrating 
        the MetaIntelligence reasoning core.
        
        Args:
            prompt (str): The user prompt
            system_prompt (str): System instructions
            **kwargs: Additional parameters including mode, force_v2, etc.
            
        Returns:
            Dict[str, Any]: Enhanced response with MetaIntelligence processing
        """
        pass
```

### Example Provider Implementation

```python
# Path: /examples/custom_provider_example.py
from meta_intelligence.providers.base import LLMProvider, ProviderCapability

class CustomLLMProvider(LLMProvider):
    """Example implementation of a custom LLM provider."""
    
    def __init__(self, api_key: str, model_name: str):
        self.api_key = api_key
        self.model_name = model_name
    
    def get_capabilities(self) -> Dict[ProviderCapability, bool]:
        return {
            ProviderCapability.STANDARD_CALL: True,
            ProviderCapability.STREAMING: False,
            ProviderCapability.TOOLS: False,
            ProviderCapability.FUNCTION_CALLING: False,
            ProviderCapability.ENHANCED_REASONING: True
        }
    
    async def standard_call(self, prompt: str, system_prompt: str = "", **kwargs) -> Dict[str, Any]:
        # Implement your custom LLM API call here
        response = await self._make_api_call(prompt, system_prompt, **kwargs)
        return {
            "text": response.get("content", ""),
            "usage": response.get("usage", {}),
            "model": self.model_name
        }
    
    def should_use_enhancement(self, prompt: str, **kwargs) -> bool:
        # Custom logic to determine when to use enhanced features
        force_v2 = kwargs.get("force_v2", False)
        mode = kwargs.get("mode", "balanced")
        complex_modes = ["decomposed", "quantum_inspired", "paper_optimized"]
        
        return force_v2 or mode in complex_modes
    
    async def _make_api_call(self, prompt: str, system_prompt: str, **kwargs):
        # Implement your actual API call logic here
        pass
```

## 🔧 Configuration Classes

### MasterSystemConfig

```python
from dataclasses import dataclass
from typing import Dict, Any, Optional

@dataclass
class MasterSystemConfig:
    """Configuration for the MetaIntelligence master system."""
    
    enable_metacognition: bool = True
    enable_superintelligence: bool = True
    enable_dynamic_architecture: bool = True
    enable_value_evolution: bool = True
    enable_consciousness_evolution: bool = True
    auto_optimization: bool = True
    integration_depth: str = "full"  # "basic", "standard", "full", "transcendent"
    performance_monitoring: bool = True
    custom_parameters: Optional[Dict[str, Any]] = None
```

### IntegrationConfig

```python
@dataclass
class IntegrationConfig:
    """Configuration for the Integration Orchestrator."""
    
    enable_all_systems: bool = True
    auto_evolution: bool = False
    integration_harmony_threshold: float = 0.8
    max_integration_depth: int = 10
    enable_emergent_insights: bool = True
    cross_system_communication: bool = True
    collective_memory_enabled: bool = True
    wisdom_synthesis_enabled: bool = True
```

## 📋 Data Classes

### ProblemSolution

```python
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum

class ProblemClass(Enum):
    TRIVIAL = "trivial"
    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    TRANSCENDENT = "transcendent"

@dataclass
class ProblemSolution:
    """Represents a solution to a problem solved by MetaIntelligence."""
    
    solution_content: str
    confidence: float
    problem_class: ProblemClass
    transcendence_achieved: bool
    processing_metadata: Dict[str, Any]
    emergent_insights: List[str]
    wisdom_generated: Optional[str] = None
    consciousness_evolution_triggered: bool = False
    integration_quality: float = 0.0
```

## 🎯 Best Practices

### 1. Provider Selection

```python
# Path: /examples/provider_selection_example.py
async def select_optimal_provider(task_complexity: str, available_providers: List[str]):
    """Example of how to select the optimal provider based on task requirements."""
    
    if task_complexity in ["transcendent", "ultimate"]:
        # Use most capable provider for ultimate tasks
        if "openai" in available_providers:
            return get_provider("openai", enhanced=True)
        elif "claude" in available_providers:
            return get_provider("claude", enhanced=True)
    
    elif task_complexity in ["complex", "decomposed"]:
        # Use balanced provider for complex tasks
        if "ollama" in available_providers:
            return get_provider("ollama", enhanced=True)
    
    # Default to first available provider
    return get_provider(available_providers[0], enhanced=False)
```

### 2. Error Handling

```python
# Path: /examples/error_handling_example.py
import asyncio
import logging
from meta_intelligence.core.master_system import MetaIntelligence
from meta_intelligence.exceptions import MetaIntelligenceError, InitializationError

async def robust_meta_intelligence_usage():
    """Example of robust error handling with MetaIntelligence."""
    
    try:
        provider = get_provider("ollama", enhanced=True)
        mi_system = MetaIntelligence(provider)
        
        # Initialize with error handling
        init_result = await mi_system.initialize()
        if not init_result.get("success", False):
            logging.error(f"Initialization failed: {init_result.get('error')}")
            return
        
        # Solve problem with error handling
        try:
            solution = await mi_system.solve_ultimate_problem(
                "Design a sustainable transportation system"
            )
            print(f"Solution confidence: {solution.confidence}")
            
        except MetaIntelligenceError as e:
            logging.error(f"Problem solving failed: {e}")
            # Fallback to simpler approach
            fallback_solution = await mi_system.solve_ultimate_problem(
                "Design a sustainable transportation system",
                context={"complexity_limit": "moderate"}
            )
            print(f"Fallback solution: {fallback_solution.solution_content[:200]}...")
            
    except InitializationError as e:
        logging.error(f"System initialization failed: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(robust_meta_intelligence_usage())
```

### 3. Performance Monitoring

```python
# Path: /examples/performance_monitoring_example.py
import time
import asyncio
from meta_intelligence.core.master_system import MetaIntelligence

async def monitor_performance():
    """Example of monitoring MetaIntelligence performance."""
    
    provider = get_provider("ollama", enhanced=True)
    mi_system = MetaIntelligence(provider)
    await mi_system.initialize()
    
    # Monitor system health
    health_report = await mi_system.monitor_integration_health()
    print(f"System health score: {health_report.get('overall_health_score', 0):.2f}")
    
    # Time problem solving
    start_time = time.time()
    solution = await mi_system.solve_ultimate_problem("What is consciousness?")
    end_time = time.time()
    
    print(f"Problem solved in {end_time - start_time:.2f} seconds")
    print(f"Integration quality: {solution.integration_quality:.2f}")
    
    # Check for performance issues
    if health_report.get('performance_issues'):
        print("Performance issues detected:")
        for issue in health_report['performance_issues']:
            print(f"- {issue}")

if __name__ == "__main__":
    asyncio.run(monitor_performance())
```

## 📚 Additional Resources

### Module Structure Overview

```
meta_intelligence/
├── __init__.py                    # Main API exports
├── core/
│   ├── master_system.py          # MetaIntelligence main class
│   └── integration_orchestrator.py # Integration management
├── meta_cognition/
│   ├── engine.py                 # Meta-cognition system
│   └── cognitive_states.py       # Cognitive state definitions
├── providers/
│   ├── base.py                   # Provider base classes
│   ├── openai.py                 # OpenAI provider implementation
│   ├── claude.py                 # Claude provider implementation
│   └── ollama.py                 # Ollama provider implementation
├── consciousness/
│   └── levels.py                 # Consciousness level definitions
├── wisdom_synthesis/
│   └── knowledge_integrator.py   # Wisdom synthesis system
└── exceptions.py                 # Custom exception classes
```

### Version Compatibility

- **Python**: 3.8+
- **AsyncIO**: Required for all async operations
- **Dependencies**: See `requirements.txt` for complete list

### Migration Guide

When upgrading from previous versions:

1. Update import statements to use new module structure
2. Replace `CogniQuantumMaster` with `MetaIntelligence`
3. Update configuration classes to new format
4. Adapt provider initialization to enhanced provider pattern

For detailed migration instructions, see the Migration Guide documentation.