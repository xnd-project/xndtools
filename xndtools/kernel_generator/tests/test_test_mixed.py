import pytest
from xnd import xnd

try:
    import test_mixed as m
    skip_reason = None
except Exception as msg:
    m = None
    skip_reason = f'Failed to import test_mixed: {msg}'
    print(skip_reason)

print(dir(m))
    
def unpack(x):
    if isinstance(x, xnd):
        return str(x.type), x.value
    if isinstance(x, tuple):
        return tuple(map(unpack, x))
    return x
    
def assert_equal(x, y):
    assert unpack(x) == unpack(y)

@pytest.mark.skipif(m is None,
                    reason=skip_reason)
def test_mixed_matrices_CF_inout():
    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    r = m.test_mixed_matrices_inout_CF(a, b)
    assert_equal(r, xnd(26))

    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        r = m.test_mixed_matrices_inout_CF(a, b)

    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')
    with pytest.raises(ValueError, match=r'.* must be F-contiguous .*'):
        r = m.test_mixed_matrices_inout_CF(a, b)

    
@pytest.mark.skipif(m is None,
                    reason=skip_reason)
def test_mixed_matrices_FC_inout():
    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')
    r = m.test_mixed_matrices_inout_FC(a, b)
    assert_equal(r, xnd(37))

    
@pytest.mark.skipif(m is None, reason=skip_reason)
def test_mixed_matrices_CC_inout():
    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')
    r = m.test_mixed_matrices_inout_CC(a, b)
    assert_equal(r, xnd(27))

    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        r = m.test_mixed_matrices_inout_CC(a, b)

    
@pytest.mark.skipif(m is None,
                    reason=skip_reason)
def test_mixed_matrices_FF_inout():
    a = xnd([[10,20],
             [30,40]], type='!2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='!2 * 2 * int64')
    r = m.test_mixed_matrices_inout_FF(a, b)
    assert_equal(r, xnd(36))

    a = xnd([[10,20],
             [30,40]], type='2 * 2 * int64')
    b = xnd([[5,6],
             [7,8]], type='2 * 2 * int64')

    with pytest.raises(ValueError, match=r'.* must be F-contiguous .*'):
        r = m.test_mixed_matrices_inout_FF(a, b)
