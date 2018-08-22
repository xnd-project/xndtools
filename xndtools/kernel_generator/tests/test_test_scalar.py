
import pytest
from xndtools.kernel_generator.utils import NormalizedTypeMap
long_t = NormalizedTypeMap()('long')

from xnd import xnd
import test_scalar as m

def unpack(x):
    if isinstance(x, xnd):
        return str(x.type), x.value
    if isinstance(x, tuple):
        return tuple(map(unpack, x))
    return x
    
def assert_equal(x, y):
    assert unpack(x) == unpack(y)
    
def test_scalar_input():
    dt = f'{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_input(a), None)
    assert_equal(a, xnd(10, type=long_t))

    dt = f'2 * {long_t}'
    a = xnd([10, 11], type=dt)
    assert_equal(m.test_scalar_input(a), None)
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_inplace():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_inplace(a), None)
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10, 11], dtype=long_t)
    assert_equal(m.test_scalar_inplace(a), None)
    assert_equal(a, xnd([10,11], dtype=long_t))
    
def test_scalar_inout():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_inout(a), None)
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_inout(a), None)
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_output():
    assert_equal(m.test_scalar_output(), xnd(0, type=long_t))

def test_scalar_hide():
    assert_equal(m.test_scalar_hide(), None)

def test_scalar_input_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_input_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_input_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

    
def test_scalar_inplace_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_inplace_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_inplace_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_inout_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_inout_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_inout_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_input():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_input(a), None)
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_input(a), None)
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_inplace():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_inplace(a), None)
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_inplace(a), None)
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_inout():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_inout(a), None)
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_inout(a), None)
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_output():
    assert_equal(m.test_scalar_ptr_output(), xnd(10, type=long_t))

def test_scalar_ptr_hide():
    assert_equal(m.test_scalar_ptr_hide(), None)

def test_scalar_ptr_input_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_input_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_input_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_inplace_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_inplace_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_inplace_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_inout_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_inout_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_inout_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_return_input():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_input(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_input(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_return_inplace():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_inplace(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=long_t)) # because C scalar cannot be changed inplace

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_inplace(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t)) # because C scalar cannot be changed inplace

def test_scalar_return_inout():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_inout(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=long_t)) # because C scalar cannot be changed inplace

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_inout(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t)) # because C scalar cannot be changed inplace

def test_scalar_return_output():
    assert_equal(m.test_scalar_return_output(), (xnd(0, type=long_t), xnd(20, type=long_t)))

def test_scalar_return_hide():
    assert_equal(m.test_scalar_return_hide(), xnd(20, type=long_t))

def test_scalar_return_input_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_input_output(a), (xnd(10, type=long_t),xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_input_output(a), (xnd([10,11], dtype=long_t),xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_return_inplace_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_inplace_output(a), (xnd(10, type=long_t),xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_inplace_output(a), (xnd([10,11], dtype=long_t),xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_return_inout_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_return_inout_output(a), (xnd(10, type=long_t), xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_return_inout_output(a), (xnd([10,11], dtype=long_t), xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_return_input():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_input(a), xnd(40, type=long_t))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_input(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_return_inplace():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_inplace(a), xnd(40, type=long_t))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_inplace(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_return_inout():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_inout(a), xnd(40, type=long_t))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_inout(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_return_output():
    assert_equal(m.test_scalar_ptr_return_output(), (xnd(10, type=long_t), xnd(30, type=long_t)))

def test_scalar_ptr_return_hide():
    assert_equal(m.test_scalar_ptr_return_hide(), xnd(30, type=long_t))

def test_scalar_ptr_return_input_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_input_output(a), (xnd(20, type=long_t),xnd(40, type=long_t)))
    assert_equal(a, xnd(10, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_input_output(a), (xnd([20,21], dtype=long_t),xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([10,11], dtype=long_t))

def test_scalar_ptr_return_inplace_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_inplace_output(a), (xnd(20, type=long_t),xnd(40, type=long_t)))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_inplace_output(a), (xnd([20,21], dtype=long_t),xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([20,21], dtype=long_t))

def test_scalar_ptr_return_inout_output():
    a = xnd(10, type=long_t)
    assert_equal(m.test_scalar_ptr_return_inout_output(a), (xnd(20, type=long_t), xnd(40, type=long_t)))
    assert_equal(a, xnd(20, type=long_t))

    a = xnd([10,11], dtype=long_t)
    assert_equal(m.test_scalar_ptr_return_inout_output(a), (xnd([20,21], dtype=long_t), xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([20,21], dtype=long_t))

# WITH VALUE
    
def test_scalar_value_input():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_input(a), None)
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_input(b), None)
    assert_equal(b, xnd(None, type=dt))

    dt = f'2 * ?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_input(a), None)
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_input(b), None)
    assert_equal(b, xnd([10,None], type=dt))
    
def test_scalar_value_inplace():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_inplace(a), None)
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_inplace(b), None)
    assert_equal(b, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_inplace(a), None)
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_inplace(b), None)
    assert_equal(b, xnd([10,5], type=dt))

def test_scalar_value_inout():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_inout(a), None)
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_inout(b), None)
    assert_equal(b, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_inout(a), None)
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_inout(b), None)
    assert_equal(b, xnd([10,5], type=dt))
    
def test_scalar_value_output():
    assert_equal(m.test_scalar_value_output(), xnd(5, type=long_t))

def test_scalar_value_hide():
    assert_equal(m.test_scalar_value_hide(), None)

def test_scalar_value_input_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_input_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_input_output(b), xnd(5, type=long_t))
    assert_equal(b, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_input_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_input_output(b), xnd([10,5], dtype=long_t))
    assert_equal(b, xnd([10,None], type=dt))

def test_scalar_value_inplace_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_inplace_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_inplace_output(b), xnd(5, type=long_t))
    assert_equal(b, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_inplace_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_inplace_output(b), xnd([10,5], dtype=long_t))
    assert_equal(b, xnd([10,5], type=dt))

def test_scalar_value_inout_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_inout_output(a), xnd(10, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_value_inout_output(b), xnd(5, type=long_t))
    assert_equal(b, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_inout_output(a), xnd([10,11], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_value_inout_output(b), xnd([10,5], dtype=long_t))
    assert_equal(b, xnd([10,5], type=dt))
    

def test_scalar_ptr_value_input():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_input(a), None)
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_ptr_value_input(b), None)
    assert_equal(b, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_input(a), None)
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_ptr_value_input(b), None)
    assert_equal(b, xnd([10,None], type=dt))
    
def test_scalar_ptr_value_inplace():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_inplace(a), None)
    assert_equal(a, xnd(20, type=dt))
    assert_equal(m.test_scalar_ptr_value_inplace(b), None)
    assert_equal(b, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_inplace(a), None)
    assert_equal(a, xnd([20,21], type=dt))
    assert_equal(m.test_scalar_ptr_value_inplace(b), None)
    assert_equal(b, xnd([20,15], type=dt))

def test_scalar_ptr_value_inout():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_inout(a), None)
    assert_equal(a, xnd(20, type=dt))
    assert_equal(m.test_scalar_ptr_value_inout(b), None)
    assert_equal(b, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_inout(a), None)
    assert_equal(a, xnd([20,21], type=dt))
    assert_equal(m.test_scalar_ptr_value_inout(b), None)
    assert_equal(b, xnd([20,15], type=dt))
    
def test_scalar_ptr_value_output():
    assert_equal(m.test_scalar_ptr_value_output(), xnd(15, type=long_t))

def test_scalar_ptr_value_hide():
    assert_equal(m.test_scalar_ptr_value_hide(), None)

def test_scalar_ptr_value_input_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_input_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    assert_equal(m.test_scalar_ptr_value_input_output(b), xnd(15, type=long_t))
    assert_equal(b, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_input_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    assert_equal(m.test_scalar_ptr_value_input_output(b), xnd([20,15], dtype=long_t))
    assert_equal(b, xnd([10,None], type=dt))

def test_scalar_ptr_value_inplace_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_inplace_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(20, type=dt))
    assert_equal(m.test_scalar_ptr_value_inplace_output(b), xnd(15, type=long_t))
    assert_equal(b, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_inplace_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([20,21], type=dt))
    assert_equal(m.test_scalar_ptr_value_inplace_output(b), xnd([20,15], dtype=long_t))
    assert_equal(b, xnd([20,15], type=dt))
    
def test_scalar_ptr_value_inout_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    b = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_inout_output(a), xnd(20, type=long_t))
    assert_equal(a, xnd(20, type=dt))
    assert_equal(m.test_scalar_ptr_value_inout_output(b), xnd(15, type=long_t))
    assert_equal(b, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    b = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_inout_output(a), xnd([20,21], dtype=long_t))
    assert_equal(a, xnd([20,21], type=dt))
    assert_equal(m.test_scalar_ptr_value_inout_output(b), xnd([20,15], dtype=long_t))
    assert_equal(b, xnd([20,15], type=dt))

def test_scalar_value_return_input():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_input(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_input(a), xnd(25, type=long_t))
    assert_equal(a, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_input(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_input(a), xnd([30,25], dtype=long_t))
    assert_equal(a, xnd([10,None], type=dt))
    

def test_scalar_value_return_inplace():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_inplace(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=dt)) # because C scalar cannot be changed inplace
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_inplace(a), xnd(25, type=long_t))
    assert_equal(a, xnd(5, type=dt)) # because C scalar cannot be changed inplace

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_inplace(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt)) # because C scalar cannot be changed inplace
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_inplace(a), xnd([30,25], dtype=long_t))
    assert_equal(a, xnd([10,5], type=dt)) # because C scalar cannot be changed inplace

def test_scalar_value_return_inout():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_inout(a), xnd(30, type=long_t))
    assert_equal(a, xnd(10, type=dt)) # because C scalar cannot be changed inplace
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_inout(a), xnd(25, type=long_t))
    assert_equal(a, xnd(5, type=dt)) # because C scalar cannot be changed inplace
    
    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_inout(a), xnd([30,31], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt)) # because C scalar cannot be changed inplace
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_inout(a), xnd([30,25], dtype=long_t))
    assert_equal(a, xnd([10,5], type=dt)) # because C scalar cannot be changed inplace

def test_scalar_value_return_output():
    assert_equal(m.test_scalar_value_return_output(), (xnd(5, type=long_t), xnd(25, type=long_t)))

def test_scalar_value_return_hide():
    assert_equal(m.test_scalar_value_return_hide(), xnd(25, type=long_t))

def test_scalar_value_return_input_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_input_output(a), (xnd(10, type=long_t),xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_input_output(a), (xnd(5, type=long_t),xnd(25, type=long_t)))
    assert_equal(a, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_input_output(a), (xnd([10,11], dtype=long_t),xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_input_output(a), (xnd([10,5], dtype=long_t),xnd([30,25], dtype=long_t)))
    assert_equal(a, xnd([10,None], type=dt))

def test_scalar_value_return_inplace_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_inplace_output(a), (xnd(10, type=long_t),xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_inplace_output(a), (xnd(5, type=long_t),xnd(25, type=long_t)))
    assert_equal(a, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_inplace_output(a), (xnd([10,11], dtype=long_t),xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_inplace_output(a), (xnd([10,5], dtype=long_t),xnd([30,25], dtype=long_t)))
    assert_equal(a, xnd([10,5], type=dt))

def test_scalar_value_return_inout_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_value_return_inout_output(a), (xnd(10, type=long_t), xnd(30, type=long_t)))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_value_return_inout_output(a), (xnd(5, type=long_t),xnd(25, type=long_t)))
    assert_equal(a, xnd(5, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_value_return_inout_output(a), (xnd([10,11], dtype=long_t),xnd([30,31], dtype=long_t)))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_value_return_inout_output(a), (xnd([10,5], dtype=long_t),xnd([30,25], dtype=long_t)))
    assert_equal(a, xnd([10,5], type=dt))
    
def test_scalar_ptr_value_return_input():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input(a), xnd(40, type=long_t))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input(a), xnd(35, type=long_t))
    assert_equal(a, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input(a), xnd([40,35], dtype=long_t))
    assert_equal(a, xnd([10,None], type=dt))

def test_scalar_ptr_value_return_inplace():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace(a), xnd(40, type=long_t))
    assert_equal(a, xnd(20, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace(a), xnd(35, type=long_t))
    assert_equal(a, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([20,21], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace(a), xnd([40,35], dtype=long_t))
    assert_equal(a, xnd([20,15], type=dt))
    
def test_scalar_ptr_value_return_inout():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout(a), xnd(40, type=long_t))
    assert_equal(a, xnd(20, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout(a), xnd(35, type=long_t))
    assert_equal(a, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout(a), xnd([40,41], dtype=long_t))
    assert_equal(a, xnd([20,21], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout(a), xnd([40,35], dtype=long_t))
    assert_equal(a, xnd([20,15], type=dt))
    
def test_scalar_ptr_value_return_output():
    assert_equal(m.test_scalar_ptr_value_return_output(), (xnd(15, type=long_t), xnd(35, type=long_t)))

def test_scalar_ptr_value_return_hide():
    assert_equal(m.test_scalar_ptr_value_return_hide(), xnd(35, type=long_t))

def test_scalar_ptr_value_return_input_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input_output(a), (xnd(20, type=long_t),xnd(40, type=long_t)))
    assert_equal(a, xnd(10, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input_output(a), (xnd(15, type=long_t),xnd(35, type=long_t)))
    assert_equal(a, xnd(None, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input_output(a), (xnd([20,21], dtype=long_t),xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([10,11], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_input_output(a), (xnd([20,15], dtype=long_t),xnd([40,35], dtype=long_t)))
    assert_equal(a, xnd([10,None], type=dt))

def test_scalar_ptr_value_return_inplace_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace_output(a), (xnd(20, type=long_t),xnd(40, type=long_t)))
    assert_equal(a, xnd(20, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace_output(a), (xnd(15, type=long_t),xnd(35, type=long_t)))
    assert_equal(a, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace_output(a), (xnd([20,21], dtype=long_t),xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([20,21], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inplace_output(a), (xnd([20,15], dtype=long_t),xnd([40,35], dtype=long_t)))
    assert_equal(a, xnd([20,15], type=dt))

def test_scalar_ptr_value_return_inout_output():
    dt = f'?{long_t}'
    a = xnd(10, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout_output(a), (xnd(20, type=long_t), xnd(40, type=long_t)))
    assert_equal(a, xnd(20, type=dt))
    a = xnd(None, type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout_output(a), (xnd(15, type=long_t),xnd(35, type=long_t)))
    assert_equal(a, xnd(15, type=dt))

    dt = f'2*?{long_t}'
    a = xnd([10,11], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout_output(a), (xnd([20,21], dtype=long_t),xnd([40,41], dtype=long_t)))
    assert_equal(a, xnd([20,21], type=dt))
    a = xnd([10,None], type=dt)
    assert_equal(m.test_scalar_ptr_value_return_inout_output(a), (xnd([20,15], dtype=long_t),xnd([40,35], dtype=long_t)))
    assert_equal(a, xnd([20,15], type=dt))
