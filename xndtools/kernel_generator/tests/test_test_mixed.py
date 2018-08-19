import pytest
from xnd import xnd

try:
    import test_mixed as m
    skip_reason = None
except Exception as msg:
    m = None
    skip_reason = f'Failed to import test_mixed: {msg}'
    
def unpack(x):
    if isinstance(x, xnd):
        return str(x.type), x.value
    if isinstance(x, tuple):
        return tuple(map(unpack, x))
    return x
    
def assert_equal(x, y):
    assert unpack(x) == unpack(y)

@pytest.mark.skipif(m is None or not hasattr(m, 'test_mixed_matrices_inout_CF'),
                    reason=skip_reason or 'test_mixed_matrices_inout_CF not supported by ndtypes')
def test_mixed_matrices_CF_inout():
    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    r = m.test_mixed_matrices_inout_CF(a, b)
    assert_equal(r, xnd(26))

@pytest.mark.skipif(m is None, reason=skip_reason)
def test_mixed_matrices_CC_inout():
    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')
    r = m.test_mixed_matrices_inout_CC(a, b)
    assert_equal(r, xnd(27))
    return
    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    r = m.test_mixed_matrices_inout_CC(a, b)
    assert_equal(r, xnd(27))

    
@pytest.mark.skipif(m is None or not hasattr(m, 'test_mixed_matrices_inout_FF'),
                    reason=skip_reason or 'test_mixed_matrices_inout_FF not supported by ndtypes')
def test_mixed_matrices_FF_inout():
    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    r = m.test_mixed_matrices_inout_FF(a, b)
    assert_equal(r, xnd(36))
