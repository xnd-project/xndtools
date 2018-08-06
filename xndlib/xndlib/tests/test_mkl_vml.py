import pytest
from time import time
import numpy as np
from xnd import xnd
import mkl_vml as vml

def test_exp():
    a = xnd([1.0, 0.0])
    r = vml.exp(a)
    

def timeit(func, args, repeat=100): 
    t0 = time()
    for _r in range(repeat):
        res = func(*args)
    t1 = time()
    return 1e3*(t1 - t0)/repeat

@pytest.mark.skip(reason="Time consuming.")
def test_bench_exp():
    sizes = [2**i+1 for i in range(1,20)]
    sizes = np.linspace(1,3_000_000, 100, dtype=int)
    xnd_timings_exp = []
    xnd_timings_exp_inout = []
    xnd_timings_myexp = []
    xnd_timings_myexp_inout = []
    numpy_timings_exp = []
    numpy_timings_exp_inout = []
    xnd_timings_abs = []
    numpy_timings_abs = []
    xnd_timings_nothing = []
    xnd_timings_nothing_inout = []
    xnd_timings_copy = []
    xnd_timings_copy_inout = []
    xnd_timings_mycopy = []
    xnd_timings_mycopy_inout = []
    
    for size in sizes:
        print(f'size={size}')
        a = np.random.uniform(0, 1, size=size)
        r = np.empty(dtype=a.dtype, shape=size)
        xa = xnd.from_buffer(a)
        xr = xnd.from_buffer(r)

        if 0:
            xnd_timings_copy.append(timeit(vml.copy, (xa,)))
            xnd_timings_copy_inout.append(timeit(vml.copy_inout, (xa,xr)))
        if 0:
            xnd_timings_mycopy.append(timeit(vml.mycopy, (xa,)))
            xnd_timings_mycopy_inout.append(timeit(vml.mycopy_inout, (xa,xr)))
        if 0:
            xnd_timings_nothing.append(timeit(vml.nothing, (xa,)))
            xnd_timings_nothing_inout.append(timeit(vml.nothing_inout, (xa,xr)))
        if 0:
            xnd_timings_myexp.append(timeit(vml.myexp, (xa,)))
            xnd_timings_myexp_inout.append(timeit(vml.myexp_inout, (xa,xr)))
        if 1:
            xnd_timings_exp.append(timeit(vml.exp, (xa,)))
            xnd_timings_exp_inout.append(timeit(vml.exp_inout, (xa,xr)))
        if 1:
            numpy_timings_exp.append(timeit(np.exp, (a,)))
            numpy_timings_exp_inout.append(timeit(np.exp, (a,r)))

        #xnd_timings_abs.append(timeit(vml.abs, (xa,)))
        #numpy_timings_abs.append(timeit(np.abs, (a,)))

    try:
        from matplotlib import pyplot as plt
    except ImportError:
        return
    if 0:
        plt.plot(sizes, xnd_timings_copy, '+', label='mkl_vml.copy [XND]')
        plt.plot(sizes, xnd_timings_copy_inout, '+', label='mkl_vml.copy_inout [XND]')
    if 0:
        plt.plot(sizes, xnd_timings_mycopy, '+', label='mkl_vml.mycopy [XND]')
        plt.plot(sizes, xnd_timings_mycopy_inout, '+', label='mkl_vml.mycopy_inout [XND]')
    if 0:
        plt.plot(sizes, xnd_timings_nothing, '+', label='mkl_vml.nothing [XND]')
        plt.plot(sizes, xnd_timings_nothing_inout, '+', label='mkl_vml.nothing_inout [XND]')
    if 0:
        plt.plot(sizes, xnd_timings_myexp, '+', label='mkl_vml.myexp [XND]')
        plt.plot(sizes, xnd_timings_myexp_inout, 'x', label='mkl_vml.myexp_inout [XND]')
    if 1:
        plt.plot(sizes, xnd_timings_exp, '+', label='mkl_vml.exp(xa)->xr [XND]')
        plt.plot(sizes, xnd_timings_exp_inout, 'x', label='mkl_vml.exp_inout(xa, xr) [XND]')
    if 1:
        plt.plot(sizes, numpy_timings_exp, '.', label='numpy.exp(a)->r')
        plt.plot(sizes, numpy_timings_exp_inout, '.', label='numpy.exp(a, out=r)')
    #plt.plot(sizes, xnd_timings_abs, 'x', label='mkl_vml.abs [XND]')
    #plt.plot(sizes, numpy_timings_abs, '.', label='numpy.abs')
    plt.legend()
    plt.xlabel('Array size')
    plt.ylabel('Timing, ms per call')
    plt.savefig('mkl_vml_exp.png')
    plt.show()
        
