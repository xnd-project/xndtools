from time import time
import numpy as np
from xnd import xnd
import mkl_vml as vml

def test_exp():
    a = xnd([1.0, 0.0])
    r = vml.exp(a)

def test_bench_exp():
    repeat = 100

    sizes = [2**i+1 for i in range(1,20)]
    sizes = np.arange(1,10000,100)
    xnd_timings = []
    numpy_timings = []
    
    for size in sizes:
        print(f'size={size}')
        a = np.random.uniform(0, 1, size=size)
        xa = xnd.from_buffer(a)

        exp = vml.exp
        t0 = time()
        for _r in range(repeat):
            xr = exp(xa)
        t1 = time()
        xnd_timings.append(1e3*(t1 - t0)/repeat)

        exp = np.exp
        t0 = time()
        for _r in range(repeat):
            xr = exp(a)
        t1 = time()
        numpy_timings.append(1e3*(t1 - t0)/repeat)

    try:
        from matplotlib import pyplot as plt
    except ImportError:
        return
    plt.plot(sizes, xnd_timings, 'x', label='mkl_vml.exp [XND]')
    plt.plot(sizes, numpy_timings, 'o', label='numpy.exp')
    plt.legend()
    plt.xlabel('Array size')
    plt.ylabel('Timing, ms per call')
    plt.savefig('mkl_vml_exp.png')
    plt.show()
        
