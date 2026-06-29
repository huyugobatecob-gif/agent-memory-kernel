"""Agent Memory Kernel.

Local-first auditable memory for AI agents.
"""

from .acceptance import assert_acceptance_suite, run_acceptance_suite, seed_acceptance_fixture
from .conformance import (
    assert_conformance_spec_shape,
    assert_conformance_suite,
    conformance_certification_report,
    conformance_registry_entry,
    conformance_spec,
    run_conformance_suite,
    seed_conformance_fixture,
)
from .contract import assert_contract_shape, memory_contract
from .orchestrator import MemoryOrchestrator
from .store import MemoryStore

__all__ = [
    "MemoryOrchestrator",
    "MemoryStore",
    "assert_acceptance_suite",
    "assert_conformance_spec_shape",
    "assert_conformance_suite",
    "assert_contract_shape",
    "conformance_certification_report",
    "conformance_registry_entry",
    "conformance_spec",
    "memory_contract",
    "run_acceptance_suite",
    "run_conformance_suite",
    "seed_acceptance_fixture",
    "seed_conformance_fixture",
]
__version__ = "0.1.0"
