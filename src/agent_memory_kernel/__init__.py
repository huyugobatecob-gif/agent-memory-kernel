"""Agent Memory Kernel.

Local-first auditable memory for AI agents.
"""

from .acceptance import assert_acceptance_suite, run_acceptance_suite, seed_acceptance_fixture
from .contract import assert_contract_shape, memory_contract
from .store import MemoryStore

__all__ = [
    "MemoryStore",
    "assert_acceptance_suite",
    "assert_contract_shape",
    "memory_contract",
    "run_acceptance_suite",
    "seed_acceptance_fixture",
]
__version__ = "0.1.0"
