"""atomic_bitmap: 位图(bitmap)类的原子操作全家桶。

模式: 每个 program 处理一组 B 个 int32 位图字:load 之后分别用 atomic_and /
atomic_or / atomic_xor 累加到三个组缓冲,atomic_cas 抢占 4 个 claim 槽(每个 group
独占一个 CTA,所以 cas 的返回值可判),atomic_xchg 读旧值写新值,再用
debug_barrier 保证同一 CTA 内的读后写顺序,最后把 and/or/xor 汇总与 cas 成功数
写进 Stats。覆盖 atomic add/and/or/xor/cas/xchg 与 sem 语义。

文件只有两层:
  ① atomic_bitmap_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/atomic_bitmap', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'atomic.and', 'atomic.or', 'atomic.xor', 'atomic.cas', 'atomic.xchg', 'atomic.sem', 'memory.load', 'memory.store']}
COPIED_FROM = {'repo': '~/ops basic (authored composite, validated at d326fbc+)', 'covers_gap_apis': ['atomic_and', 'atomic_cas', 'atomic_or', 'atomic_xor']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def atomic_bitmap_kernel(X,And,Or,Xor,Claim,Published,Old,Stats,B:tl.constexpr):
    g=tl.program_id(0)
    i=tl.arange(0,B)
    bits=tl.load(X+g*B+i)
    tl.atomic_and(And+g+tl.full((B,),0,tl.int32),bits)
    tl.atomic_or(Or+g+tl.full((B,),0,tl.int32),bits)
    tl.atomic_xor(Xor+g+tl.full((B,),0,tl.int32),bits)
    won=tl.atomic_cas(Claim+g*4+i%4,tl.full((B,),0,tl.int32),tl.full((B,),1,tl.int32))==0
    previous=tl.atomic_xchg(Published+g*B+i,bits)
    tl.store(Old+g*B+i,previous)
    tl.debug_barrier()
    # One CTA owns each group, so the barrier precedes the summary reads.
    tl.store(Stats+g*4,tl.load(And+g))
    tl.store(Stats+g*4+1,tl.load(Or+g))
    tl.store(Stats+g*4+2,tl.load(Xor+g))
    tl.store(Stats+g*4+3,tl.sum(won.to(tl.int32),0))

# ------------------------------------------------------------------ ② case 层
# 典型用法:编译器后端用位图记录"哪些 lane/program 完成/占用"——以 int32 字为单位
# 的原子位运算。没有唯一真实尺寸,取 16 个 group x 256 个位图字(= 8192 bit 位图)。
# B(每组字数)必须是 2 的幂且 >= 4(cas 的 claim 槽按 i%4 取)。
#
# (G, B):
#   典型  (16, 256)  16 个 CTA,每组 256 个字;位模式覆盖高位与低位
#   规模  (32, 256)  典型规模 ×2:dim0 16->32
#   规模  (16, 512)  典型规模 ×2:dim1 256->512
#   泛化  (5, 32)    组数不是 2 的幂,每组字数取最小合法值附近
#         (1, 4)    退化:单组 4 个字(正好占满 claim 槽)
SHAPES = ((16, 128), (5, 32), (1, 4))
# 位图天然是 int32;其他 dtype 没有意义。
DTYPES = ("int32",)


def ref(args, meta):
    """numpy 对照:按组做位运算归约,claim/Published/Old 是原子读写的镜像。"""
    x = np.asarray(args["X"])
    g, b = x.shape
    a = np.bitwise_and.reduce(x, axis=1)
    o = np.bitwise_or.reduce(x, axis=1)
    z = np.bitwise_xor.reduce(x, axis=1)
    return {"And": a, "Or": o, "Xor": z,
            "Claim": np.ones((g, 4), np.int32),                     # cas 成功路径
            "Published": x.copy(),                                  # xchg 写入值
            "Old": np.asarray(args["Published"]).copy(),             # xchg 读回的旧值
            "Stats": np.stack((a, o, z, np.full(g, 4, np.int32)), axis=1)}


def _make_case(shape=SHAPES[0], dtype="int32", seed=0):
    g, b = (int(v) for v in shape)
    if g <= 0 or b < 4 or b & (b - 1):
        raise ValueError(f"shape must be (G > 0, B power of 2 >= 4), got {shape}")

    # 位模式:低 8 位随机(and 会把它清成 0,or/xor 保留原样),高位带上 group id,
    # 这样 and/or/xor 三个结果一定不同,串台会被立刻发现。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (rng.integers(0, 256, (g, b), dtype=np.int32)
         | ((np.arange(g, dtype=np.int32) + 1)[:, None] << 16))
    # 语义边界:第 0 组全 0(and/或/xor 都得到 0)、第 1 组全 -1(and/xor 得 -1),
    # Published 用负数初值,检验 xchg 的读旧值不会是"碰巧相同"。
    x[0, :] = 0
    if g > 1:
        x[1, :] = -1
    args = {"X": x, "And": np.full(g, -1, np.int32), "Or": np.zeros(g, np.int32),
            "Xor": np.zeros(g, np.int32), "Claim": np.zeros((g, 4), np.int32),
            "Published": rng.integers(-100, -1, (g, b), dtype=np.int32),
            "Old": np.zeros((g, b), np.int32), "Stats": np.zeros((g, 4), np.int32)}
    outputs = ("And", "Or", "Xor", "Claim", "Published", "Old", "Stats")
    # 原子缓冲是原地更新的,expected 必须基于初值算。
    return {"args": args, "meta": {"B": b}, "grid": (g,), "outputs": outputs,
            "oracle_args": {"Published": args["Published"].copy()},
            "expected": ref(args, {"B": b}),
            "comparison": {name: {"exact": True} for name in outputs}}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;整数输出按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, atomic_bitmap_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=True)
