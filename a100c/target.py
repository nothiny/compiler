"""Target model as data, from the recorded facts (MECH-TARGET-DESCRIPTION-AS-DATA).

Every value here traces to a recorded Fact in
``docs/compiler-agent/PROJECT_STATE.json``; no target value is invented.  The
model is the data the backend consults (register files, VLEN, EEW range,
worker set, ABI); consumers never re-derive these from branches.

Facts consulted:
  F006  QEMU endpoint provides RVV 1.0 with VLEN=1024 (vlenb=128 observed).
  F026  EEW range 8..64 for vector element widths.
  F023/F039/F041  32 vector registers x VLENB bytes; exceeding the file has
        no architectural spill (compiler-owned spill/split).
  F053  at most 8 A100 compute workers (1/2/4/8 configurable).
  F045/F002  RISC-V psABI lp64d, rv64gcv cross toolchain.
  F005  the pinned QEMU execution endpoint.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple

__all__ = ["TargetModel", "DEFAULT_TARGET", "TARGET_MODEL_VERSION"]


#: Version of the model *shape and values*; changes invalidate every artifact
#: (the driver keys the cache on it).
TARGET_MODEL_VERSION = "a100-rvv1-vlen1024/1"

#: Facts backing each field (provenance, TGT-FACT-DISCIPLINE).
FIELD_EVIDENCE = {
    "isa": "F002/F042 (rv64gcv cross toolchain, probed)",
    "vlen_bits": "F006 (vlenb=128 observed under the pinned CPU model)",
    "elen_bits": "F006 (-cpu max,vlen=1024,elen=64)",
    "eew_range": "F026 (EEW 8..64)",
    "vector_registers": "F023/F039 (32 vector registers)",
    "gprs": "RISC-V psABI (F045)",
    "workers": "F053 (at most 8 compute workers, 1/2/4/8)",
    "abi": "F045 (lp64d)",
}


@dataclass(frozen=True)
class TargetModel:
    """The target as data: one row per resource, consulted not re-derived."""

    name: str = "spacemit-a100-qemu"
    isa: str = "rv64gcv"
    abi: str = "lp64d"
    vlen_bits: int = 1024
    elen_bits: int = 64
    eew_range: Tuple[int, ...] = (8, 16, 32, 64)
    vector_registers: int = 32
    gprs: int = 32
    workers: Tuple[int, ...] = (1, 2, 4, 8)
    #: reserved vector register: the working mask (vmerge / masked memory ops
    #: read only v0 -- RVV 1.0); never allocated.
    reserved_vector_regs: Tuple[int, ...] = (0,)
    #: reserved GPRs: zero, ra (calls), sp, gp, tp; a0 carries the launch
    #: pointer at entry and arguments at call boundaries.
    reserved_gprs: Tuple[str, ...] = ("zero", "ra", "sp", "gp", "tp", "a0")
    model_version: str = TARGET_MODEL_VERSION
    evidence: dict = field(default_factory=lambda: dict(FIELD_EVIDENCE))

    # -- derived quantities (pure functions of the data above) --------------
    @property
    def vlenb(self) -> int:
        """VLEN in bytes (the observed CSR value, F006)."""
        return self.vlen_bits // 8

    @property
    def vector_file_bytes(self) -> int:
        """The 32 x 128 B vector register file (F023/F039)."""
        return self.vector_registers * self.vlenb

    def vlmax(self, sew: int, lmul: int = 1) -> int:
        """Maximum vector length at (SEW, LMUL)."""
        return (self.vlen_bits * lmul) // sew

    def sew_supported(self, sew: int) -> bool:
        return sew in self.eew_range

    def chunk_plan(self, block: int, sew: int, lmul: int = 1) -> Tuple[Tuple[int, int], ...]:
        """Split a block extent into (chunk_vl, chunk_count) pieces.

        Exact vl per chunk (IR task contract): every chunk's vl is the exact
        number of block elements it owns; the last chunk takes the remainder.
        With power-of-two blocks and power-of-two vlmax every chunk is full.
        """
        if block <= 0:
            return ()
        vlmax = self.vlmax(sew, lmul)
        if block <= vlmax:
            return ((block, 1),)
        full, rest = divmod(block, vlmax)
        chunks = [(vlmax, 1)] * full
        if rest:
            chunks.append((rest, 1))
        return tuple((vl, 1) for vl, _ in chunks)

    def register_class_bytes(self, lmul: int) -> int:
        """Bytes of the vector file one (SEW, LMUL) group occupies."""
        return self.vlenb * lmul

    def describe(self) -> dict:
        return {
            "name": self.name, "isa": self.isa, "abi": self.abi,
            "vlen_bits": self.vlen_bits, "elen_bits": self.elen_bits,
            "eew_range": list(self.eew_range),
            "vector_registers": self.vector_registers,
            "vector_file_bytes": self.vector_file_bytes,
            "gprs": self.gprs, "workers": list(self.workers),
            "model_version": self.model_version,
        }


DEFAULT_TARGET = TargetModel()
