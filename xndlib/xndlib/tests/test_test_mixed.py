import pytest
from xnd import xnd
#import test_mixed as m

def unpack(x):
    if isinstance(x, xnd):
        return str(x.type), x.value
    if isinstance(x, tuple):
        return tuple(map(unpack, x))
    return x
    
def assert_equal(x, y):
    assert unpack(x) == unpack(y)

@pytest.mark.skip(reason="ndtypes does not support mixed arguments??, importing test_mixed failes")
def test_mixed_matrices_input():
    a = xnd([[10,20], [30,40]], dtype='2 * 2 * int64')
    b = xnd([[5,6], [7,8]], dtype='!2 * 2 * int64')
    r = m.test_mixed_matrices_input(a, b)
    assert_equal(r, xnd(26))
