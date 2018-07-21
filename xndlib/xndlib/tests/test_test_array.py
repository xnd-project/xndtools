
import pytest
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
    a = xnd([1,2,3])
    r = m.test_array_range_input(a)
    assert_equal(r, xnd(6))
    assert_equal(a, xnd([0,1,2])) # because `a` matches exactly

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7])
    x = a[1::2]
    r = m.test_array_range_input(x)
    assert_equal(r, xnd(12))
    assert_equal(x, xnd([2,4,6]))
    assert_equal(a, xnd([1,2,3,4,5,6,7]))

    # Strided kernel
    # TODO
    
def test_array_range_inplace():
    # C kernel
    a = xnd([1,2,3])
    r = m.test_array_range_inplace(a)
    assert_equal(r, xnd(6))
    assert_equal(a, xnd([0,1,2]))

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7])
    x = a[1::2]
    assert_equal(x, xnd([2,4,6]))
    r = m.test_array_range_inplace(x)
    assert_equal(r, xnd(12))
    assert_equal(x, xnd([0,1,2]))
    assert_equal(a, xnd([1,0,3,1,5,2,7]))

    # Strided kernel
    # TODO
    
def test_array_range_input_output():
    # C kernel
    a = xnd([1,2,3])
    o, r = m.test_array_range_input_output(a)
    assert_equal(r, xnd(6))
    assert_equal(o, xnd([0,1,2]))
    assert_equal(a, xnd([0,1,2])) # because `a` matches exactly

    # F kernel
    # TODO
    
    # Xnd kernel
    a = xnd([1,2,3,4,5,6,7])
    x = a[1::2]
    assert_equal(x, xnd([2,4,6]))
    o, r = m.test_array_range_input_output(x)
    assert_equal(r, xnd(12))
    assert_equal(o, xnd([0,1,2]))
    assert_equal(x, xnd([2,4,6]))
    assert_equal(a, xnd([1,2,3,4,5,6,7]))

    # Strided kernel
    # TODO
    
def test_array_range_output():
    # using C, F, or Xnd kernel if defined
    o, r = m.test_array_range_output(xnd(3))
    assert_equal(r, xnd(0)) # could be random
    assert_equal(o, xnd([0,1,2]))
