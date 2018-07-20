
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
    a = xnd([1,2,3])
    r = m.test_array_range_input(a)
    assert_equal(r, None)
    assert_equal(a, xnd([0,1,2])) # TODO, copy?

def test_array_range_inplace():
    a = xnd([1,2,3])
    r = m.test_array_range_inplace(a)
    assert_equal(r, None)
    assert_equal(a, xnd([0,1,2]))

def test_array_range_input_output():
    a = xnd([1,2,3])
    r = m.test_array_range_input_output(a)
    assert_equal(r, xnd([0,1,2]))
    assert_equal(a, xnd([0,1,2])) # TODO, copy?

def test_array_range_output():
    r = m.test_array_range_output(xnd(3))
    assert_equal(r, xnd([0,1,2]))
