"""Worker range partition over source program instances (F018/F053/F019).

The unit of parallel work is a *native work range*: the set of source program
instances one persistent worker thread executes.  The default policy is
strided round-robin (partition policy (a) of COMPILER_ARCHITECTURE.md 5):
worker ``w`` of ``W`` executes programs ``w, w+W, w+2W, ...`` below the
runtime program count.  Striding preserves per-program semantics exactly --
each instance executes exactly once across all workers, and the ragged tail
program is owned like any other ("tails owned": no duplicated and no dropped
work at any worker count, including counts that do not divide the program
count).

The partition is computed *inside the generated program* from
``(worker_id, worker_count)``; this module is the pure model the plan carries
and the tests verify, and the lowering emits the same strided loop natively.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

__all__ = ["PartitionPolicy", "ExecutionPlan", "strided_range",
           "partition_table", "check_partition"]


def strided_range(worker_id: int, worker_count: int, program_count: int) -> List[int]:
    """The strided program range of one worker (pure model of the emitted loop)."""
    if worker_count not in (1, 2, 4, 8):
        raise ValueError(f"worker count {worker_count} not in 1/2/4/8 (F053)")
    if not (0 <= worker_id < worker_count):
        raise ValueError(f"worker id {worker_id} outside 0..{worker_count - 1}")
    if program_count < 0:
        raise ValueError("program count must be non-negative")
    return list(range(worker_id, program_count, worker_count))


def partition_table(worker_count: int, program_count: int) -> List[List[int]]:
    return [strided_range(w, worker_count, program_count)
            for w in range(worker_count)]


def check_partition(worker_count: int, program_count: int) -> Tuple[bool, str]:
    """Coverage/no-overlap/tail-ownership self-check for one configuration."""
    table = partition_table(worker_count, program_count)
    seen: Dict[int, int] = {}
    for w, row in enumerate(table):
        for p in row:
            if p in seen:
                return False, f"program {p} owned by workers {seen[p]} and {w}"
            seen[p] = w
    missing = set(range(program_count)) - set(seen)
    if missing:
        return False, f"programs {sorted(missing)} owned by no worker"
    # strided order: each worker's range is an arithmetic progression step W
    for w, row in enumerate(table):
        for a, b in zip(row, row[1:]):
            if b - a != worker_count:
                return False, f"worker {w} range is not strided: {row}"
    return True, "exactly-once coverage, disjoint ownership, strided order"


@dataclass
class PartitionPolicy:
    """The declared distribution policy (EXECUTION_MODEL.json mechanism row)."""

    policy: str = "strided"
    workers: Tuple[int, ...] = (1, 2, 4, 8)
    evidence: Tuple[str, ...] = ("F018", "F053", "F019", "F043")

    def range_of(self, worker_id: int, worker_count: int,
                 program_count: int) -> List[int]:
        if self.policy != "strided":
            raise ValueError(f"partition policy {self.policy!r} not implemented")
        return strided_range(worker_id, worker_count, program_count)


@dataclass
class ExecutionPlan:
    """Everything the lowering needs to shape the generated program.

    ``program_count`` is runtime (the native grid-evaluation routine computes
    it from bundle-visible quantities); the plan carries the *form*.
    """

    partition: PartitionPolicy = field(default_factory=PartitionPolicy)
    #: block extent (elements per source program) -- compile time
    block_extent: int = 0
    #: (vl, chunk_count) pieces of the block at the target's (SEW, LMUL)
    chunks: Tuple[Tuple[int, int], ...] = ()
    #: count of elements the operator stores per program (stats plan)
    counts_elements: bool = True
    #: workspace requirements in bytes (the slice needs none)
    workspace_private: int = 0
    workspace_shared: int = 0
    #: barrier stages between program-loop phases (none for elementwise)
    stages: Tuple[str, ...] = ()

    def total_chunks(self) -> int:
        return sum(n for _, n in self.chunks)

    def describe(self) -> dict:
        return {
            "partition": self.partition.policy,
            "workers": list(self.partition.workers),
            "block_extent": self.block_extent,
            "chunks": [[vl, n] for vl, n in self.chunks],
            "workspace_private": self.workspace_private,
            "workspace_shared": self.workspace_shared,
            "stages": list(self.stages),
        }
