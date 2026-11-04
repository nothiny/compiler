"""stochastic_ensemble: 一个 kernel 里把 Philox/randint/randn 全家桶各用一遍。

模式: 单 program 处理整条向量:randint 得到 route,randint4x/philox 的四路输出
一起异或进 route,按 route%N 做间接 gather 取 X,rand4x 的四路和过阈值做门控,
randn 与 randn4x 生成噪声叠加。覆盖 randint/randint4x/philox/rand4x/randn/randn4x
与间接寻址。随机数语义按 Philox 位精确复现,所以比较是精确的。

文件只有两层:
  ① stochastic_ensemble_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy。
                     分配、搬运、启动由 runner 的 Device 决定
                     (opslib.devices.cuda 不需要框架;torch_ref 只给 baseline 用)。"""

OPERATOR = {"name": 'basic/stochastic_ensemble', "group": 'basic', "channel": 'local',
            "execution": 'triton_kernel', "verification": 'correctness',
            "tags": ['args.runtime_scalar', 'creation.arange', 'random.philox', 'random.randint', 'random.randint4x', 'random.rand4x', 'random.randn', 'random.randn4x', 'memory.indirect']}
COPIED_FROM = {'repo': '~/ops basic (authored composite, validated at d326fbc+)', 'covers_gap_apis': ['philox', 'rand4x', 'randint', 'randint4x', 'randn4x']}

import numpy as np
import triton
import triton.language as tl

# ------------------------------------------------------------------ ① 编译单元
@triton.jit
def stochastic_ensemble_kernel(X,Y,Route,Seed,N:tl.constexpr):
    # Fix the width before adding offsets: Python scalar inference may use i32.
    Seed = Seed.to(tl.uint64)
    i=tl.arange(0,N)
    pick=tl.randint(Seed,i)
    a,b,c,d=tl.randint4x(Seed+1,i)
    p,q,r,s=tl.philox(Seed+2,i.to(tl.uint32),tl.full((N,),7,tl.uint32),tl.full((N,),0,tl.uint32),tl.full((N,),0,tl.uint32))
    route=pick ^ a ^ b ^ c ^ d ^ p ^ q ^ r ^ s
    x=tl.load(X+(route%N))
    u,v,w,z=tl.rand4x(Seed+3,i)
    solo=tl.randn(Seed+4,i)
    n0,n1,n2,n3=tl.randn4x(Seed+5,i)
    noise=(solo+n0+n1+n2+n3)*0.05
    y=tl.where(u+v+w+z>=2.0,x*2.0,0.0)+noise
    tl.store(Y+i,y)
    tl.store(Route+i,route)

def _philox(seed,n,c1=0):
    mask=np.uint64(0xffffffff)
    c=[np.arange(n,dtype=np.uint64),np.full(n,c1,np.uint64),np.zeros(n,np.uint64),np.zeros(n,np.uint64)]
    k0=seed & 0xffffffff; k1=(seed>>32) & 0xffffffff
    for _ in range(10):
        p0=c[0]*np.uint64(0xd2511f53); p2=c[2]*np.uint64(0xcd9e8d57)
        c=[((p2>>np.uint64(32))^c[1]^np.uint64(k0))&mask,p2&mask,((p0>>np.uint64(32))^c[3]^np.uint64(k1))&mask,p0&mask]
        k0=(k0+0x9e3779b9)&0xffffffff; k1=(k1+0xbb67ae85)&0xffffffff
    return [x.astype(np.uint32) for x in c]
def _uniform(bits):
    x=bits.view(np.int32)
    return np.where(x<0,~x,x).astype(np.float32)*np.float32(4.6566127342e-10)
def _normals(words):
    u=[_uniform(w).astype(np.float64) for w in words]
    out=[]
    for a,b in ((u[0],u[1]),(u[2],u[3])):
        radius=np.sqrt(-2*np.log(np.maximum(1e-7,a))); theta=2*np.pi*b
        out.extend((radius*np.cos(theta),radius*np.sin(theta)))
    return out

# ------------------------------------------------------------------ ② case 层
# 典型用法:随机路由/集成(stochastic depth 的采样器):一次生成路由下标、门控、
# 噪声三组随机量。没有唯一真实尺寸,取一条 4096 元素的特征;N 是 constexpr,
# 必须能放进一个块(randint 的下标范围也是 N)。
#
# (N,):
#   典型  (4096,)  一条 4096 元素特征上的随机路由
#   规模  (8192,)  典型规模 ×2:dim0 4096->8192
#   规模  (16384,)  典型规模 ×4:dim0 4096->16384
#   泛化  (128,)   小向量:随机量的位模式完全不同的另一组
#         (32,)    退化:单 warp
SHAPES = ((128,), (32,))
# 整个 kernel 只有 f32 随机数与 f32 算术,原始版本也是 fp32。
DTYPES = ('float32', 'float16', 'bfloat16')
_COMPARISON = {"Y": {"rtol": 1e-4, "atol": 2e-5}, "Route": {"exact": True}}


def ref(args, meta):
    """numpy 对照:用 _philox/_uniform/_normals 位精确复现 Triton 的随机流。"""
    n = np.asarray(args["X"]).size
    seed = int(args["Seed"])
    route = _philox(seed, n)[0]
    for word in _philox(seed + 1, n) + _philox(seed + 2, n, 7):
        route = route ^ word
    uniform = [_uniform(w) for w in _philox(seed + 3, n)]
    solo = _normals(_philox(seed + 4, n))[0]
    normals = _normals(_philox(seed + 5, n))
    gate = ((uniform[0] + uniform[1]) + uniform[2]) + uniform[3] >= 2
    noise = (solo + sum(normals)) * 0.05
    x = np.asarray(args["X"])
    return {"Y": (np.where(gate, x[route % n] * 2, 0) + noise).astype(np.float32),
            "Route": route}


def _make_case(shape=SHAPES[0], dtype="float32", seed=0):
    n = int(shape[0])
    if n < 2 or n & (n - 1):
        raise ValueError(f"N must be a power of 2 >= 2, got {shape}")

    # 原始输入是标准正态。取 1/16 网格保留形状:gather 之后仍精确可表示,
    # 只有随机数本身(位精确复现)和 f32 噪声参与容差比较。
    from case_utils import fast_rng
    rng = fast_rng(seed)
    x = (np.clip(np.rint(rng.standard_normal(n, dtype=np.float32) * 16), -128, 127)
         / 16).astype(np.float32)
    # 语义边界:X[0]=0 使 route 命中 0 时结果只由噪声决定;末元素为负,便于
    # 看清 route%N 取到了首尾两端。
    x[0] = 0.0
    x[-1] = -2.0

    args = {"X": x, "Y": np.zeros(n, np.float32), "Route": np.zeros(n, np.uint32),
            "Seed": (int(seed) + 151) & 0xffffffffffffffff}
    return {"args": args, "meta": {"N": n}, "grid": (1,), "outputs": ("Y", "Route"),
            "expected": ref(args, {}), "comparison": _COMPARISON}


def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case;Route 按位精确比较。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, stochastic_ensemble_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)


# ---- suite-v3 case enrichment ----
_ENRICH_BASE = 'float32'
_ENRICH_TARGETS = ("float32", "float16", "bfloat16")
_ENRICH_APPLY_FOR_BASE = True
_ENRICH_ORIGINAL_MAKE_CASE = make_case
_ENRICH_ORIGINAL_DTYPES = {'float32': 'float32'}


def make_case(shape=None, dtype=None, seed=None):
    """Enriched case builder: dtype-generic, one shared tolerance table.

    The original case layer built one float case.  For fp16/bf16 we build that
    same case, temporarily wrap the module ``ref`` so the expected outputs are
    computed from the low-precision inputs, then re-express the buffers in the
    requested dtype (``case_utils.dtype_case``).  Integer / bool requests go
    through the original builder unchanged.
    """
    from case_utils import convert_float_arrays, dtype_case, dtype_name

    requested = dtype_name(dtype) or DTYPES[0]
    if requested in _ENRICH_ORIGINAL_DTYPES:
        # declared before enrichment: the operator's own case builder and tolerances
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_ORIGINAL_DTYPES[requested], seed=seed)
    if requested not in _ENRICH_TARGETS:
        return _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=dtype, seed=seed)
    if requested == _ENRICH_BASE:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=requested, seed=seed)
        case["dtype"] = requested
        if _ENRICH_APPLY_FOR_BASE:
            case = dtype_case(case, requested, ref=None)
        return case
    original_ref = ref

    def enriched_ref(args, meta):
        return original_ref(convert_float_arrays(args, requested), meta)

    globals()["ref"] = enriched_ref
    try:
        case = _ENRICH_ORIGINAL_MAKE_CASE(shape=shape, dtype=_ENRICH_BASE, seed=seed)
    finally:
        globals()["ref"] = original_ref
    return dtype_case(case, requested, ref=None)
