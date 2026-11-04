"""randint__randint_kernel: Philox 随机整数 [0, high):一个 program 出 4 路结果。

模式: args.runtime_scalar, cast.to, creation.arange, memory.store.masked。

文件只有两层:
  ① randint_kernel   编译单元。编译器只读它的 AST,本文件里唯一不能改的部分。
  ② case 层          SHAPES / DTYPES / ref / make_case,只用 numpy;分配/搬运/启动由 runner 的 Device 决定。
     make_case 接受任意合法 shape。
"""

OPERATOR = {"name": "hidden/randint__randint_kernel", "group": "hidden", "channel": "local",
            "execution": "triton_kernel", "verification": "correctness",
            "tags": ["args.runtime_scalar", "cast.to", "creation.arange", "memory.store.masked"]}
COPIED_FROM = {"repo": "flaggems @ ~/ops", "path": "operators/randint__randint_kernel.py", "validated": True}

import triton
import triton.language as tl


# ------------------------------------------------------------------ ① 编译单元
@triton.jit(do_not_specialize=['philox_seed', 'philox_offset', 'N'])
def randint_kernel(out_ptr, N, high, philox_seed, philox_offset, BLOCK: tl.constexpr):
    philox_seed = philox_seed.to(tl.int64)
    philox_offset = philox_offset.to(tl.int64)
    c0 = (philox_offset & 4294967295).to(tl.uint32)
    c1 = (philox_offset >> 32 & 4294967295).to(tl.uint32)
    pid = tl.program_id(0)
    i = pid * BLOCK + tl.arange(0, BLOCK)
    c0 += i
    z = c0 * 0
    (r0, r1, r2, r3) = tl.philox(philox_seed, c0, c1, z, z)
    high_val = high.to(tl.uint64)
    r0_mod = (r0 % high_val).to(out_ptr.dtype.element_ty)
    r1_mod = (r1 % high_val).to(out_ptr.dtype.element_ty)
    r2_mod = (r2 % high_val).to(out_ptr.dtype.element_ty)
    r3_mod = (r3 % high_val).to(out_ptr.dtype.element_ty)
    start = pid.to(tl.uint64) * BLOCK * 4
    off0 = start + tl.arange(0, BLOCK)
    off1 = off0 + BLOCK
    off2 = off1 + BLOCK
    off3 = off2 + BLOCK
    tl.store(out_ptr + off0, r0_mod, mask=off0 < N)
    tl.store(out_ptr + off1, r1_mod, mask=off1 < N)
    tl.store(out_ptr + off2, r2_mod, mask=off2 < N)
    tl.store(out_ptr + off3, r3_mod, mask=off3 < N)


# ------------------------------------------------------------------ ② case 层
# shape 沿用 flaggems 集合的原配置(规模阶梯 + 该算子的 workload/配置形状);标「规模」的条目是追加的整数缩放变体(两个参考装置逐 case 验证):
#   规模  (1496,)  workload x2:dim0 748->1496
#   规模  (2244,)  workload x3:dim0 748->2244
SHAPES = ((17,), (120,))
DTYPES = ("int64",)

def ref(args,meta):
 import numpy as np
 def _philox(c0,seed,offset):
  mask=np.uint64(0xffffffff);c0=(np.asarray(c0,dtype=np.uint64)+np.uint64(offset&0xffffffff))&mask;c1=np.full(c0.shape,(offset>>32)&0xffffffff,np.uint64);c2=np.zeros_like(c0);c3=np.zeros_like(c0);k0=np.uint64(seed&0xffffffff);k1=np.uint64((seed>>32)&0xffffffff)
  for _ in range(10):
   p0=np.uint64(0xD2511F53)*c0;p1=np.uint64(0xCD9E8D57)*c2;hi0=p0>>np.uint64(32);lo0=p0&mask;hi1=p1>>np.uint64(32);lo1=p1&mask;c0,c1,c2,c3=(hi1^c1^k0)&mask,lo1,(hi0^c3^k1)&mask,lo0;k0=(k0+np.uint64(0x9E3779B9))&mask;k1=(k1+np.uint64(0xBB67AE85))&mask
  return tuple(v.astype(np.uint32) for v in (c0,c1,c2,c3))
 def _to_uniform(raw):
  signed=raw.view(np.int32).astype(np.int64);return (np.where(signed<0,-signed-1,signed).astype(np.float32)*np.float32(4.6566127342e-10)).astype(np.float32)
 def _random_words(n,seed,offset,block):
  out=np.empty(n,np.uint32);programs=(n+4*block-1)//(4*block)
  for pid in range(programs):
   r=_philox(pid*block+np.arange(block),seed,offset);base=pid*4*block
   for q in range(4):
    idx=base+q*block+np.arange(block);valid=idx<n;out[idx[valid]]=r[q][valid]
  return out
 def _uniform(n,seed,offset,block):return _to_uniform(_random_words(n,seed,offset,block))
 def _normal(n,seed,offset,block):
  out=np.empty(n,np.float32);programs=(n+4*block-1)//(4*block)
  for pid in range(programs):
   raw=_philox(pid*block+np.arange(block),seed,offset);u=[_to_uniform(v) for v in raw];r0=np.sqrt(-2*np.log(np.maximum(u[0],1e-7)));t0=2*np.pi*u[1];r1=np.sqrt(-2*np.log(np.maximum(u[2],1e-7)));t1=2*np.pi*u[3];vals=(r0*np.cos(t0),r0*np.sin(t0),r1*np.cos(t1),r1*np.sin(t1));base=pid*4*block
   for q in range(4):
    idx=base+q*block+np.arange(block);valid=idx<n;out[idx[valid]]=vals[q][valid]
  return out
 raw=_random_words(int(args["N"]),int(args["philox_seed"]),int(args["philox_offset"]),meta["BLOCK"]);return {"out_ptr":(raw%np.uint64(args["high"])).astype(np.int64)}

def _make_case(shape=SHAPES[0],dtype=DTYPES[0],seed=20260901):
 from case_utils import fast_rng
 del dtype
 import numpy as np
 N=int(shape[0]);rng=fast_rng(seed)
 B=64;args={"out_ptr":np.asarray(np.full(N,-1),"int64"),"N":N,"philox_seed":0x123456789ABCDEF,"philox_offset":37,"high":17};meta={"BLOCK":B};grid=((N+4*B-1)//(4*B),)
 outputs=('out_ptr',);return {"args": args, "meta": meta, "grid": grid, "outputs": outputs, "expected": ref(args, meta), "launch_meta": {"num_warps": 4, "num_stages": 1}, "comparison": {name: {"comparator": "allclose", "exact": False, "rtol": 0.0002, "atol": 2e-05, "equal_nan": True} for name in outputs}}

def make_case(shape=None, dtype=None, seed=None):
    """dtype 归一化和白名单检查,再交给 _make_case。"""
    from case_utils import public_make_case

    return public_make_case(_make_case, randint_kernel, DTYPES,
                            shape=shape, dtype=dtype, seed=seed, exact=False)
