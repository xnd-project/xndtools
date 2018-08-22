import pytest
from xndtools.kernel_generator.utils import NormalizedTypeMap
long_t = NormalizedTypeMap()('long')

from xnd import xnd
import test_array as m

def unpack(x):
    if isinstance(x, xnd):
        return str(x.type), x.value
    if isinstance(x, tuple):
        return tuple(map(unpack, x))
    return x
    
def assert_equal(x, y):
    assert unpack(x) == unpack(y)

def test_array_range_input():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    r = m.test_array_range_input(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(a, xnd([0,1,2], dtype=long_t)) # because `a` matches exactly

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    r = m.test_array_range_input(x)
    assert_equal(r, xnd(12, type=long_t))
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    assert_equal(a, xnd([1,2,3,4,5,6,7], dtype=long_t))

    # Strided kernel
    # TODO
    
def test_array_range_inplace():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    r = m.test_array_range_inplace(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(a, xnd([0,1,2], dtype=long_t))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    r = m.test_array_range_inplace(x)
    assert_equal(r, xnd(12, type=long_t))
    assert_equal(x, xnd([0,1,2], dtype=long_t))
    assert_equal(a, xnd([1,0,3,1,5,2,7], dtype=long_t))

    # Strided kernel
    # TODO

def test_array_range_inout():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    r = m.test_array_range_inout(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(a, xnd([0,1,2], dtype=long_t))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        r = m.test_array_range_inout(x)

    # Strided kernel
    # TODO
    
def test_array_range_input_output():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    o, r = m.test_array_range_input_output(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(o, xnd([0,1,2], dtype=long_t))
    assert_equal(a, xnd([1,2,3], dtype=long_t))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    o, r = m.test_array_range_input_output(x)
    assert_equal(r, xnd(12, type=long_t))
    assert_equal(o, xnd([0,1,2], dtype=long_t))
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    assert_equal(a, xnd([1,2,3,4,5,6,7], dtype=long_t))

    # Strided kernel
    # TODO

def test_array_range_inplace_output():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    o, r = m.test_array_range_inplace_output(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(o, xnd([0,1,2], dtype=long_t))
    assert_equal(a, xnd([0,1,2], dtype=long_t))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    o, r = m.test_array_range_inplace_output(x)
    assert_equal(r, xnd(12, type=long_t))
    assert_equal(o, xnd([0,1,2], dtype=long_t))
    assert_equal(x, xnd([0,1,2], dtype=long_t))
    assert_equal(a, xnd([1,0,3,1,5,2,7], dtype=long_t))

    # Strided kernel
    # TODO

def test_array_range_inout_output():
    # C kernel
    a = xnd([1,2,3], dtype=long_t)
    o, r = m.test_array_range_inout_output(a)
    assert_equal(r, xnd(6, type=long_t))
    assert_equal(o, xnd([0,1,2], dtype=long_t))
    assert_equal(a, xnd([0,1,2], dtype=long_t))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7], dtype=long_t)
    x = a[1::2]
    assert_equal(x, xnd([2,4,6], dtype=long_t))
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        o, r = m.test_array_range_inout_output(x)

    # Strided kernel
    # TODO
    
def test_array_range_output():
    # using C, F, or Xnd kernel if defined
    o, r = m.test_array_range_output(xnd(3, type=long_t))
    assert_equal(r, xnd(0, type=long_t)) # could be random
    assert_equal(o, xnd([0,1,2], dtype=long_t))


def test_array_range_hide():
    # using C, F, or Xnd kernel if defined
    r = m.test_array_range_hide(xnd(3, type=long_t))
    assert r.type == xnd(0, type=long_t).type
    # r value is random
