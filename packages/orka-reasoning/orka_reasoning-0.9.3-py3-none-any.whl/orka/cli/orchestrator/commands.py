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
Orchestrator CLI Commands
========================

This module contains CLI commands related to orchestrator operations.
"""

import json
import logging
import sys
from pathlib import Path

from orka.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


async def run_orchestrator(args):
    """Run the orchestrator with the given configuration."""
    try:
        if not Path(args.config).exists():
            logger.error(f"Configuration file not found: {args.config}")
            return 1

        orchestrator = Orchestrator(args.config)
        result = await orchestrator.run(args.input)

        if args.json:
            logger.info(json.dumps(result, indent=2))
        else:
            logger.info("=== Orchestrator Result ===")
            logger.info(result)

        return 0
    except Exception as e:
        logger.error(f"Error running orchestrator: {e}")
        return 1
