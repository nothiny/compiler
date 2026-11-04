/* operator_stub.S -- hand-written assembly operator stub (boundary witness).
 *
 * Authored in this task as the RT-EXECUTION-CONTRACT witness for the
 * runtime<->generated-code ABI declared in a100rt.h.  This is NOT pipeline
 * output: it exists to prove the boundary before the compiler exists, so any
 * later failure belongs to the compiler, not the runtime.
 *
 * It provides the three operator-program symbols of the ABI:
 *   operator_entry(launch)          -- one worker's execution of one call
 *   operator_workspace_private()    -- 64 B thread-private scratch (delta slot)
 *   operator_workspace_shared()     -- 576 B shared scratch (8 padded 64 B
 *                                      per-worker partial slots + total slot)
 *
 * Fixture semantics (structural, on the a100-native-io/v1 argument layout --
 * never on operator, kernel or benchmark names; there are no names in the
 * bundle):
 *   - a single 1-D bfloat16 view: value-storage path; every owned element's
 *     sign bit is flipped (writes outputs, exercises 16-bit value storage);
 *   - a 1-D 64-bit non-output view (a pointer table) whose patched entry 0
 *     points at a 1-D output int32 view: strided-alias path;
 *       stage 1  every owned element b[i] += delta, where index 0 is written
 *                through the dereferenced guest pointer and the rest through
 *                strided stores; delta comes from typed scalar 0 and makes a
 *                round trip through this worker's thread-private workspace;
 *       barrier  a100rt_stage_barrier (cross-worker visibility point);
 *       merge    worker 0 sums the per-worker partial slots in the shared
 *                workspace into the shared total slot;
 *       barrier  a100rt_stage_barrier;
 *       stage 3  every owned element b[i] += merged total.
 *   - anything else: this stub performs no writes and reports zero items.
 *
 * Calling convention: RISC-V psABI lp64d (F045) -- a0 holds the launch
 * pointer; s0-s11/ra are saved here because the stage barrier is a C call
 * that clobbers the caller-saved registers.
 *
 * Struct offsets used below are pinned by the _Static_assert list in
 * a100rt.h: launch {bundle 0, shared 8, private 16, stats 24, runtime 32,
 * worker_id 40, worker_count 44}, bundle {views 0, scalars 8, nviews 16,
 * nscalars 20}, view {data 0, shape 8, strides 16, dtype 32, ndim 36,
 * flags 40}, scalar {bits 8}, sizeof(struct a100rt_view) == 56.
 */
    .text

/* Address of views[idx] into the views array held in `base`. */
.macro VADDR dst, base, idx, tmp
    slli \tmp, \idx, 6        /* idx*64 */
    slli \dst, \idx, 3        /* idx*8  */
    sub  \dst, \tmp, \dst     /* idx*56 = sizeof(struct a100rt_view) */
    add  \dst, \base, \dst
.endm

/* ---- workspace queries (strong; override the runtime's weak defaults) ---- */
    .globl operator_workspace_private
    .type operator_workspace_private, @function
operator_workspace_private:
    li    a0, 64              /* one padded thread-private slot */
    ret
    .size operator_workspace_private, .-operator_workspace_private

    .globl operator_workspace_shared
    .type operator_workspace_shared, @function
operator_workspace_shared:
    li    a0, 576             /* 8 per-worker 64 B slots + 64 B total slot */
    ret
    .size operator_workspace_shared, .-operator_workspace_shared

/* ---- operator_entry(a0 = const struct a100rt_launch *) ----
 * Register plan: s0 launch, s1 bundle, s2 views base, s3 view data,
 * s4 count, s5 stride, s6 delta, s7 begin, s8 end, s9 items, s10 total,
 * s11 pointer-table view index.
 */
    .globl operator_entry
    .type operator_entry, @function
operator_entry:
    addi  sp, sp, -112
    sd    ra, 104(sp)
    sd    s0, 96(sp)
    sd    s1, 88(sp)
    sd    s2, 80(sp)
    sd    s3, 72(sp)
    sd    s4, 64(sp)
    sd    s5, 56(sp)
    sd    s6, 48(sp)
    sd    s7, 40(sp)
    sd    s8, 32(sp)
    sd    s9, 24(sp)
    sd    s10, 16(sp)
    sd    s11, 8(sp)

    mv    s0, a0              /* launch */
    ld    s1, 0(s0)           /* bundle */
    ld    s2, 0(s1)           /* views base */
    lwu   t0, 16(s1)          /* nviews */
    beqz  t0, .Ldone

    /* structural dispatch: single 1-D bfloat16 view -> value-storage path */
    li    t1, 1
    bne   t0, t1, .Lfind_table
    lwu   t2, 32(s2)          /* views[0].dtype */
    li    t1, 11              /* A100RT_DTYPE_BFLOAT16 */
    beq   t2, t1, .Lbf16
    j     .Lfind_table

/* ---- strided-alias path ---- */
.Lfind_table:
    /* find the pointer-table view T: non-output, 64-bit entries, 1-D */
    lwu   s3, 16(s1)          /* nviews */
    li    s11, -1
    li    t0, 0
.Lscan_table:
    bge   t0, s3, .Ltable_done
    VADDR t1, s2, t0, t2
    lwu   t3, 40(t1)          /* flags */
    andi  t3, t3, 1
    bnez  t3, .Lnext_table
    lwu   t3, 32(t1)          /* dtype */
    li    t4, 8               /* int64 */
    beq   t3, t4, .Ltable_ndim
    li    t4, 9               /* uint64 */
    beq   t3, t4, .Ltable_ndim
    j     .Lnext_table
.Ltable_ndim:
    lwu   t3, 36(t1)          /* ndim */
    li    t4, 1
    bne   t3, t4, .Lnext_table
    mv    s11, t0
    j     .Ltable_done
.Lnext_table:
    addi  t0, t0, 1
    j     .Lscan_table
.Ltable_done:
    bltz  s11, .Ldone         /* no pointer table: nothing for this stub */

    VADDR t1, s2, s11, t2
    ld    t1, 0(t1)           /* T.data */
    ld    s4, 0(t1)           /* ptr = patched guest pointer (table entry 0) */

    /* find the alias target B: output, int32, 1-D, data == ptr */
    lwu   t6, 16(s1)          /* nviews */
    li    t5, -1
    li    t0, 0
.Lscan_target:
    bge   t0, t6, .Ltarget_done
    VADDR t1, s2, t0, t2
    lwu   t3, 40(t1)          /* flags */
    andi  t3, t3, 1
    beqz  t3, .Lnext_target
    lwu   t3, 32(t1)          /* dtype */
    li    t4, 6               /* int32 */
    bne   t3, t4, .Lnext_target
    lwu   t3, 36(t1)          /* ndim */
    li    t4, 1
    bne   t3, t4, .Lnext_target
    ld    t3, 0(t1)           /* data */
    bne   t3, s4, .Lnext_target
    mv    t5, t0
    j     .Ltarget_done
.Lnext_target:
    addi  t0, t0, 1
    j     .Lscan_target
.Ltarget_done:
    bltz  t5, .Ldone

    /* load B's descriptor: data, shape[0], strides[0] */
    VADDR t1, s2, t5, t2
    ld    s3, 0(t1)           /* B.data */
    ld    t1, 8(t1)           /* shape */
    ld    s4, 0(t1)           /* count */
    VADDR t1, s2, t5, t2
    ld    t1, 16(t1)          /* strides */
    ld    s5, 0(t1)           /* stride */

    /* typed scalar 0: the addend */
    lwu   t0, 20(s1)          /* nscalars */
    beqz  t0, .Ldone
    ld    t1, 8(s1)           /* scalars */
    ld    s6, 8(t1)           /* scalar[0].bits */

    /* round trip through this worker's thread-private workspace */
    ld    t1, 16(s0)          /* workspace_private */
    sd    s6, 0(t1)
    ld    s6, 0(t1)

    /* worker range [begin, end) = [count*id/W, count*(id+1)/W) */
    lwu   t0, 40(s0)          /* worker_id */
    lwu   t1, 44(s0)          /* worker_count */
    mul   t2, s4, t0
    divu  s7, t2, t1
    addi  t3, t0, 1
    mul   t2, s4, t3
    divu  s8, t2, t1

    /* stage 1: b[i] += delta for every owned i; index 0 through the pointer */
    li    s9, 0
    mv    t0, s7
.Lstage1:
    bge   t0, s8, .Lstage1_end
    addi  s9, s9, 1
    bnez  t0, .Lstrided
    VADDR t1, s2, s11, t2     /* T view */
    ld    t1, 0(t1)           /* T.data */
    ld    t1, 0(t1)           /* ptr */
    lw    t2, 0(t1)
    addw  t2, t2, s6
    sw    t2, 0(t1)
    j     .Lnext1
.Lstrided:
    mul   t2, t0, s5
    add   t2, s3, t2
    lw    t4, 0(t2)
    addw  t4, t4, s6
    sw    t4, 0(t2)
.Lnext1:
    addi  t0, t0, 1
    j     .Lstage1
.Lstage1_end:

    /* publish this worker's item count: shared[id*64] and stats->items */
    ld    t1, 8(s0)           /* workspace_shared */
    lwu   t2, 40(s0)
    slli  t2, t2, 6
    add   t1, t1, t2
    sd    s9, 0(t1)
    ld    t1, 24(s0)          /* stats */
    sd    s9, 0(t1)

    /* barrier: every stage-1 write is visible before the merge */
    mv    a0, s0
    call  a100rt_stage_barrier

    /* merge (worker 0 only): total = sum of per-worker partial slots */
    lwu   t0, 40(s0)
    bnez  t0, .Lskip_merge
    ld    t1, 8(s0)           /* workspace_shared */
    lwu   t2, 44(s0)          /* worker_count */
    li    t3, 0
    li    t4, 0
.Lmerge:
    bge   t3, t2, .Lmerge_done
    slli  t5, t3, 6
    add   t6, t1, t5
    ld    t5, 0(t6)
    add   t4, t4, t5
    addi  t3, t3, 1
    j     .Lmerge
.Lmerge_done:
    sd    t4, 512(t1)         /* shared total slot */
.Lskip_merge:

    /* barrier: the merged total is visible to every worker */
    mv    a0, s0
    call  a100rt_stage_barrier

    /* stage 3: b[i] += merged total for every owned i */
    ld    t1, 8(s0)
    ld    s10, 512(t1)
    mv    t0, s7
.Lstage3:
    bge   t0, s8, .Lstage3_end
    mul   t2, t0, s5
    add   t2, s3, t2
    lw    t4, 0(t2)
    addw  t4, t4, s10
    sw    t4, 0(t2)
    addi  t0, t0, 1
    j     .Lstage3
.Lstage3_end:
    j     .Ldone

/* ---- bfloat16 value-storage path ---- */
.Lbf16:
    ld    s3, 0(s2)           /* A.data */
    ld    t1, 8(s2)           /* shape */
    ld    s4, 0(t1)           /* count */
    ld    t1, 16(s2)          /* strides */
    ld    s5, 0(t1)           /* stride */
    lwu   t0, 40(s0)          /* worker_id */
    lwu   t1, 44(s0)          /* worker_count */
    mul   t2, s4, t0
    divu  s7, t2, t1
    addi  t3, t0, 1
    mul   t2, s4, t3
    divu  s8, t2, t1
    li    s9, 0
    mv    t0, s7
.Lbf16_loop:
    bge   t0, s8, .Lbf16_done
    mul   t2, t0, s5
    add   t2, s3, t2
    lhu   t4, 0(t2)
    li    t5, 0x8000
    xor   t4, t4, t5          /* flip the sign bit */
    sh    t4, 0(t2)
    addi  s9, s9, 1
    addi  t0, t0, 1
    j     .Lbf16_loop
.Lbf16_done:
    ld    t1, 24(s0)          /* stats */
    sd    s9, 0(t1)

.Ldone:
    ld    ra, 104(sp)
    ld    s0, 96(sp)
    ld    s1, 88(sp)
    ld    s2, 80(sp)
    ld    s3, 72(sp)
    ld    s4, 64(sp)
    ld    s5, 56(sp)
    ld    s6, 48(sp)
    ld    s7, 40(sp)
    ld    s8, 32(sp)
    ld    s9, 24(sp)
    ld    s10, 16(sp)
    ld    s11, 8(sp)
    addi  sp, sp, 112
    ret
    .size operator_entry, .-operator_entry

    .section .note.GNU-stack,"",@progbits
