# OrKa: Orchestrator Kit Agents
# Copyright © 2025 Marco Somma
#
# This file is part of OrKa – https://github.com/marcosomma/orka-reasoning
#
# Licensed under the Creative Commons Attribution-NonCommercial 4.0 International License (CC BY-NC 4.0).
# You may not use this file for commercial purposes without explicit permission.
#
# Full license: https://creativecommons.org/licenses/by-nc/4.0/legalcode
# For commercial use, contact: marcosomma.work@gmail.com
#
# Required attribution: OrKa by Marco Somma – https://github.com/marcosomma/orka-reasoning

"""
YAML Configuration Loader
==========================

The YAML Loader is responsible for loading, parsing, and validating configuration
files for OrKa workflows. It serves as the bridge between the declarative YAML
specifications and the runtime orchestration system.

Configuration Structure
-----------------------

OrKa configuration files consist of two main sections:

**Orchestrator Section**
    Global settings for the orchestration engine:

    * ``id`` - Unique identifier for the workflow
    * ``strategy`` - Execution strategy (e.g., sequential, parallel)
    * ``queue`` - Initial execution queue for agents
    * ``agents`` - List of agent IDs in execution order

**Agents Section**
    List of agent definitions, each containing:

    * ``id`` - Unique identifier for the agent
    * ``type`` - Agent type (e.g., llm, search, memory)
    * ``prompt`` - Template string for agent input
    * ``config`` - Type-specific configuration options
    * Additional agent-specific fields

Example Configuration
---------------------

.. code-block:: yaml

    orchestrator:
      id: knowledge_qa
      strategy: sequential
      queue: orka:knowledge_qa
      agents: [retriever, answerer]

    agents:
      - id: retriever
        type: memory
        config:
          operation: read
        namespace: knowledge_base
        prompt: "Retrieve information about {{ input }}"

      - id: answerer
        type: openai-answer
        prompt: "Answer the question based on this context: {{ previous_outputs.retriever }}"

Validation Features
-------------------

The YAMLLoader validates configuration to ensure:

* All required sections are present
* Data types are correct
* Agent references are valid
* Template syntax is properly formatted

This validation happens before the Orchestrator initializes the workflow,
preventing runtime errors from malformed configurations.

Usage Example
-------------

.. code-block:: python

    from orka.loader import YAMLLoader

    # Load and validate configuration
    loader = YAMLLoader("workflow.yml")
    loader.validate()

    # Access configuration sections
    orchestrator_config = loader.get_orchestrator()
    agents_config = loader.get_agents()
"""

from typing import Any, Dict, List

import yaml


class YAMLLoader:
    """
    A loader for YAML configuration files.
    Loads and validates the configuration for the OrKa orchestrator.
    """

    def __init__(self, path: str) -> None:
        """
        Initialize the YAML loader with the path to the configuration file.

        Args:
            path: Path to the YAML configuration file.
        """
        self.path = path
        self.config = self._load_yaml()

    def _load_yaml(self) -> Dict[str, Any]:
        """
        Load the YAML configuration from the file.

        Returns:
            The loaded YAML configuration.
        """
        with open(self.path) as f:
            return yaml.safe_load(f)  # type: ignore

    def get_orchestrator(self) -> Dict[str, Any]:
        """
        Get the orchestrator configuration section.

        Returns:
            The orchestrator configuration.
        """
        return self.config.get("orchestrator", {})  # type: ignore

    def get_agents(self) -> List[Dict[str, Any]]:
        """
        Get the agents configuration section.

        Returns:
            The list of agent configurations.
        """
        return self.config.get("agents", [])  # type: ignore

    def validate(self) -> bool:
        """
        Validate the configuration file.
        Checks for required sections and correct data types.

        Returns:
            True if the configuration is valid.

        Raises:
            ValueError: If the configuration is invalid.
        """
        if "orchestrator" not in self.config:
            raise ValueError("Missing 'orchestrator' section in config")
        if "agents" not in self.config:
            raise ValueError("Missing 'agents' section in config")
        if not isinstance(self.config["agents"], list):
            raise ValueError("'agents' should be a list")
        return True
