"""Standalone composition question used only to verify the question transport."""
import numpy as np
import triton
import triton.language as tl

SHAPES=((17,),(97,))
DTYPES=('float32','int32')
INDEPENDENT_ORACLE=True


@triton.jit
def twice_absolute(value):
    return tl.abs(value)*2


@triton.jit
def composed_kernel(x,y,n,B:tl.constexpr):
    i=tl.program_id(0)*B+tl.arange(0,B)
    values=tl.load(x+i,mask=i<n,other=0)
    result=twice_absolute(values)+1
    tl.store(y+i,result,mask=i<n)


def ref(args,meta):
    return {'y':np.abs(args['x'])*2+1}


def make_case(shape=None,dtype=None,seed=30):
    shape=tuple(shape or SHAPES[0]);dtype=dtype or DTYPES[0]
    if dtype not in DTYPES or len(shape)!=1 or shape[0]<1:
        raise ValueError('expected a positive vector shape and a declared dtype')
    x=np.random.default_rng(seed).integers(-16,17,size=shape).astype(dtype)
    args={'x':x,'y':np.zeros_like(x),'n':x.size}
    return dict(kernel=composed_kernel,args=args,meta={'B':32},grid=((x.size+31)//32,),
                outputs=('y',),expected=ref(args,{}),comparison={'y':{'exact':True}})
