import pytest
from xndtools.kernel_generator.utils import NormalizedTypeMap
from xnd import xnd


m = pytest.importorskip("test_mixed")
long_t = NormalizedTypeMap()('long')


def assert_equal(x, y):
    assert x == y and x.dtype == y.dtype


def test_mixed_matrices_CF_inout():
    a = xnd([[10, 20],
             [30, 40]], type=f'2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'!2 * 2 * {long_t}')
    r = m.test_mixed_matrices_inout_CF(a, b)
    assert_equal(r, xnd(26, type=long_t))

    a = xnd([[10, 20],
             [30, 40]], type=f'!2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'2 * 2 * {long_t}')
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        r = m.test_mixed_matrices_inout_CF(a, b)

    a = xnd([[10, 20],
             [30, 40]], type=f'2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'2 * 2 * {long_t}')
    with pytest.raises(ValueError, match=r'.* must be F-contiguous .*'):
        r = m.test_mixed_matrices_inout_CF(a, b)


def test_mixed_matrices_FC_inout():
    a = xnd([[10, 20],
             [30, 40]], type=f'!2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'2 * 2 * {long_t}')
    r = m.test_mixed_matrices_inout_FC(a, b)
    assert_equal(r, xnd(37, type=long_t))


def test_mixed_matrices_CC_inout():
    a = xnd([[10, 20],
             [30, 40]], type=f'2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'2 * 2 * {long_t}')
    r = m.test_mixed_matrices_inout_CC(a, b)
    assert_equal(r, xnd(27, type=long_t))

    a = xnd([[10, 20],
             [30, 40]], type=f'!2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'!2 * 2 * {long_t}')
    with pytest.raises(ValueError, match=r'.* must be C-contiguous .*'):
        r = m.test_mixed_matrices_inout_CC(a, b)


def test_mixed_matrices_FF_inout():
    a = xnd([[10, 20],
             [30, 40]], type=f'!2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'!2 * 2 * {long_t}')
    r = m.test_mixed_matrices_inout_FF(a, b)
    assert_equal(r, xnd(36, type=long_t))

    a = xnd([[10, 20],
             [30, 40]], type=f'2 * 2 * {long_t}')
    b = xnd([[5, 6],
             [7, 8]], type=f'2 * 2 * {long_t}')

    with pytest.raises(ValueError, match=r'.* must be F-contiguous .*'):
        r = m.test_mixed_matrices_inout_FF(a, b)
