# OrKa: Orchestrator Kit Agents
# Copyright © 2025 Marco Somma
#
# This file is part of OrKa – https://github.com/marcosomma/orka-reasoning
#
# Licensed under the Apache License, Version 2.0 (Apache 2.0).
# You may not use this file for commercial purposes without explicit permission.
#
# Full license: https://www.apache.org/licenses/LICENSE-2.0
# For commercial use, contact: marcosomma.work@gmail.com
#
# Required attribution: OrKa by Marco Somma – https://github.com/marcosomma/orka-reasoning

"""
🧭 **GraphScout Agent** - Intelligent Path Discovery and Selection
================================================================

The GraphScoutAgent is an intelligent routing agent that automatically inspects
the workflow graph, evaluates possible paths, and selects the optimal next steps
based on the current question and context.

**Core Capabilities:**
- **Graph Introspection**: Automatically discovers available paths from current position
- **Smart Path Evaluation**: Uses LLM evaluation combined with heuristics for scoring
- **Dry-Run Simulation**: Safely previews path outcomes without side effects
- **Budget-Aware Decisions**: Considers cost and latency constraints
- **Safety Guardrails**: Enforces safety policies and risk assessment

**Key Features:**
- Modular architecture with pluggable components
- Global graph visibility with local planning horizon
- Intelligent scoring with multiple evaluation criteria
- Comprehensive trace logging for debugging
- Fallback strategies for edge cases

**Use Cases:**
- Dynamic routing in complex workflows
- Multi-path decision points
- Conditional branching based on content analysis
- Intelligent fallback selection
- Cost-optimized path selection
"""

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional, Tuple

from ..orchestrator.budget_controller import BudgetController
from ..orchestrator.decision_engine import DecisionEngine
from ..orchestrator.dry_run_engine import SmartPathEvaluator
from ..orchestrator.graph_api import GraphAPI
from ..orchestrator.graph_introspection import GraphIntrospector
from ..orchestrator.path_scoring import PathScorer
from ..orchestrator.safety_controller import SafetyController
from .base_node import BaseNode

logger = logging.getLogger(__name__)


@dataclass
class GraphScoutConfig:
    """Configuration for GraphScout agent behavior."""

    # Search parameters
    k_beam: int = 3
    max_depth: int = 2
    commit_margin: float = 0.15

    # Scoring weights
    score_weights: Optional[Dict[str, float]] = None

    # Budget constraints
    cost_budget_tokens: int = 800
    latency_budget_ms: int = 1200

    # Safety settings
    safety_profile: str = "default"
    safety_threshold: float = 0.2

    # Dry-run settings
    max_preview_tokens: int = 192
    tool_policy: str = "mock_all"

    # Memory settings
    use_priors: bool = True
    ttl_days: int = 21

    # Observability
    log_previews: str = "head64"
    log_components: bool = True

    def __post_init__(self) -> None:
        """Set default score weights if not provided."""
        if self.score_weights is None:
            self.score_weights = {
                "llm": 0.45,
                "heuristics": 0.20,
                "prior": 0.20,
                "cost": 0.10,
                "latency": 0.05,
            }


@dataclass
class PathCandidate:
    """Represents a candidate path for evaluation."""

    node_id: str
    path: List[str]
    score: float
    components: Dict[str, float]
    preview: str
    rationale: str
    expected_cost: float
    expected_latency: float
    safety_score: float
    confidence: float


@dataclass
class ScoutDecision:
    """Represents the final decision made by GraphScout."""

    decision_type: str  # "commit_next", "commit_path", "shortlist"
    target: Any  # node_id, path, or list of candidates
    confidence: float
    trace: Dict[str, Any]
    reasoning: str


class GraphScoutAgent(BaseNode):
    """
    🧭 **Intelligent Path Discovery Agent**

    The GraphScoutAgent automatically inspects the workflow graph and selects
    the optimal next path based on the current question and context.

    **Architecture:**
    - **Modular Design**: Pluggable components for each responsibility
    - **Graph Introspection**: Discovers available paths from current position
    - **Multi-Criteria Scoring**: LLM evaluation + heuristics + priors + budget
    - **Safety-First**: Comprehensive safety checks and guardrails
    - **Trace-Enabled**: Full observability for debugging and optimization

    **Configuration Example:**

    .. code-block:: yaml

        - id: graph_scout_0
          type: graph-scout
          params:
            k_beam: 3
            max_depth: 2
            commit_margin: 0.15
            score_weights:
              llm: 0.45
              heuristics: 0.20
              prior: 0.20
              cost: 0.10
              latency: 0.05
            safety_profile: default
            cost_budget_tokens: 800
            latency_budget_ms: 1200
          prompt: |
            You are GraphScout. Analyze the question and available paths.
            Select the best next step based on relevance, safety, and efficiency.
            Return your decision as JSON only.

    **Decision Types:**
    - **commit_next**: Single next node with high confidence
    - **commit_path**: Multi-step path when evidence is strong
    - **shortlist**: Multiple options when margin is thin
    """

    def __init__(self, node_id: str, **kwargs: Any) -> None:
        """Initialize GraphScout with modular components."""
        super().__init__(node_id=node_id, **kwargs)

        # Parse configuration
        params = kwargs.get("params", {})
        self.config = GraphScoutConfig(
            k_beam=params.get("k_beam", 3),
            max_depth=params.get("max_depth", 2),
            commit_margin=params.get("commit_margin", 0.15),
            score_weights=params.get("score_weights"),
            cost_budget_tokens=params.get("cost_budget_tokens", 800),
            latency_budget_ms=params.get("latency_budget_ms", 1200),
            safety_profile=params.get("safety_profile", "default"),
            safety_threshold=params.get("safety_threshold", 0.2),
            max_preview_tokens=params.get("max_preview_tokens", 192),
            tool_policy=params.get("tool_policy", "mock_all"),
            use_priors=params.get("use_priors", True),
            ttl_days=params.get("ttl_days", 21),
            log_previews=params.get("log_previews", "head64"),
            log_components=params.get("log_components", True),
        )

        # Initialize modular components
        self.graph_api: Optional[GraphAPI] = None
        self.introspector: Optional[GraphIntrospector] = None
        self.scorer: Optional[PathScorer] = None
        self.smart_evaluator: Optional[SmartPathEvaluator] = None
        self.safety_controller: Optional[SafetyController] = None
        self.budget_controller: Optional[BudgetController] = None
        self.decision_engine: Optional[DecisionEngine] = None

        logger.info(f"GraphScout '{node_id}' initialized with config: {self.config}")

    async def initialize(self) -> None:
        """Initialize all modular components."""
        try:
            # Initialize components in dependency order
            self.graph_api = GraphAPI()
            self.introspector = GraphIntrospector(self.config)
            self.scorer = PathScorer(self.config)
            self.smart_evaluator = SmartPathEvaluator(self.config)
            self.safety_controller = SafetyController(self.config)
            self.budget_controller = BudgetController(self.config)
            self.decision_engine = DecisionEngine(self.config)

            logger.info(f"GraphScout '{self.node_id}' components initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize GraphScout components: {e}")
            raise

    async def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution method for GraphScout agent.

        Args:
            context: Execution context containing input, previous_outputs, orchestrator

        Returns:
            Decision result with selected path and trace information
        """
        try:
            # Ensure components are initialized
            if not self.graph_api:
                await self.initialize()

            # Extract key information from context
            question = self._extract_question(context)
            orchestrator = context.get("orchestrator")
            run_id = context.get("run_id", "unknown")

            if not orchestrator:
                raise ValueError("GraphScout requires orchestrator context")

            logger.info(f"GraphScout processing question: {question[:100]}...")

            # Step 1: Graph Introspection - Discover available paths
            assert self.graph_api is not None
            graph_state = await self.graph_api.get_graph_state(orchestrator, run_id)
            assert self.introspector is not None
            candidates = await self.introspector.discover_paths(
                graph_state, question, context, executing_node=self.node_id
            )

            if not candidates:
                return self._handle_no_candidates(context)

            logger.info(f"Discovered {len(candidates)} candidate paths")

            # Step 2: Budget Check - Early filtering
            assert self.budget_controller is not None
            candidates = await self.budget_controller.filter_candidates(candidates, context)

            if not candidates:
                return self._handle_budget_exceeded(context)

            # Step 3: Smart LLM Evaluation - Two-stage analysis
            assert self.smart_evaluator is not None
            # Add current agent ID to context to prevent self-routing
            evaluation_context = context.copy()
            evaluation_context["current_agent_id"] = self.node_id
            candidates_with_llm_evaluation = await self.smart_evaluator.simulate_candidates(
                candidates, question, evaluation_context, orchestrator
            )

            # Step 4: Safety Assessment - Filter unsafe paths
            assert self.safety_controller is not None
            safe_candidates = await self.safety_controller.assess_candidates(
                candidates_with_llm_evaluation, context
            )

            if not safe_candidates:
                return self._handle_safety_violation(context)

            # Step 5: Path Scoring - Evaluate all criteria
            assert self.scorer is not None
            scored_candidates = await self.scorer.score_candidates(
                safe_candidates, question, context
            )

            # Step 6: Decision Making - Select final path
            assert self.decision_engine is not None
            # Ensure context includes current agent ID for path filtering
            decision_context = context.copy()
            decision_context["current_agent_id"] = self.node_id
            decision_result = await self.decision_engine.make_decision(
                scored_candidates, decision_context
            )

            # Step 7: Generate comprehensive trace
            trace = self._build_trace_dict(
                question, candidates, scored_candidates, decision_result, context
            )

            logger.info(
                f"GraphScout decision: {decision_result.get('decision_type')} -> {decision_result.get('target')} "
                f"(confidence: {decision_result.get('confidence', 0.0):.3f})"
            )

            # Return structured result for execution engine and logging
            result = {
                "decision": decision_result.get("decision_type"),
                "target": decision_result.get("target"),
                "confidence": decision_result.get("confidence", 0.0),
                "reasoning": decision_result.get("reasoning", ""),
                "trace": trace,
                "status": "success",
                # Add fields for proper logging/tracing
                "input": question,
                "previous_outputs": context.get("previous_outputs", {}),
                "result": {
                    "decision": decision_result.get("decision_type"),
                    "target": decision_result.get("target"),
                    "confidence": decision_result.get("confidence", 0.0),
                    "reasoning": decision_result.get("reasoning", ""),
                    "candidates_evaluated": len(candidates),
                    "top_score": (
                        scored_candidates[0].get("score", 0.0) if scored_candidates else 0.0
                    ),
                },
            }

            return result

        except Exception as e:
            logger.error(f"GraphScout execution failed: {e}")
            return {
                "decision": "fallback",
                "target": None,
                "confidence": 0.0,
                "reasoning": f"GraphScout failed: {e}",
                "error": str(e),
                "status": "error",
            }

    def _extract_question(self, context: Dict[str, Any]) -> str:
        """Extract the question/query from context."""
        # Try multiple sources for the question
        question = context.get("formatted_prompt") or context.get("input", "")
        if isinstance(question, dict):
            question = question.get("input", str(question))
        if not isinstance(question, str):
            question = str(question)

        return question.strip()

    def _handle_no_candidates(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where no candidate paths are found."""
        logger.warning("No candidate paths discovered")
        return {
            "decision": "fallback",
            "target": None,
            "confidence": 0.0,
            "reasoning": "No viable paths found from current position",
            "status": "no_candidates",
        }

    def _handle_budget_exceeded(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where all candidates exceed budget."""
        logger.warning("All candidates exceed budget constraints")
        return {
            "decision": "shortlist",
            "target": [],
            "confidence": 0.0,
            "reasoning": "All paths exceed budget constraints",
            "status": "budget_exceeded",
        }

    def _handle_safety_violation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle case where all candidates fail safety checks."""
        logger.warning("All candidates failed safety assessment")
        return {
            "decision": "human_gate",
            "target": None,
            "confidence": 0.0,
            "reasoning": "All paths failed safety assessment - human review required",
            "status": "safety_violation",
        }

    def _build_trace_dict(
        self,
        question: str,
        candidates: List[Dict[str, Any]],
        scored_candidates: List[Dict[str, Any]],
        decision_result: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Build comprehensive trace for debugging and analysis."""
        return {
            "graph_scout_version": "1.0.0",
            "timestamp": datetime.now(UTC).isoformat(),
            "question": question,
            "config": {
                "k_beam": self.config.k_beam,
                "max_depth": self.config.max_depth,
                "commit_margin": self.config.commit_margin,
                "score_weights": self.config.score_weights,
            },
            "discovery": {
                "total_candidates": len(candidates),
                "candidate_nodes": [c.get("node_id", "unknown") for c in candidates],
            },
            "scoring": {
                "scored_candidates": len(scored_candidates),
                "top_scores": [
                    {
                        "node_id": c.get("node_id", "unknown"),
                        "score": c.get("score", 0.0),
                        "components": c.get("components", {}),
                    }
                    for c in scored_candidates[:3]
                ],
            },
            "decision": {
                "type": decision_result.get("decision_type"),
                "target": decision_result.get("target"),
                "confidence": decision_result.get("confidence", 0.0),
                "reasoning": decision_result.get("reasoning", ""),
            },
            "execution_metadata": {
                "node_id": self.node_id,
                "run_id": context.get("run_id", "unknown"),
                "step_index": context.get("step_index", 0),
            },
        }
