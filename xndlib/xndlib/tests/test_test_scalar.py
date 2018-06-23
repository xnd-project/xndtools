
import pytest
from xnd import xnd
import test_scalar as m

def assert_equal(x, y):
    if isinstance(x, xnd):
        x_data = str(x.type), x.value
    else:
        x_data = x
    if isinstance(y, xnd):
        y_data = str(y.type), y.value
    else:
        y_data = y
    assert x_data == y_data

def test_scalar_input():
    a = xnd(10)
    assert_equal(m.test_scalar_input(a), None)
    assert_equal(a, xnd(10))

def test_scalar_inplace():
    a = xnd(10)
    assert_equal(m.test_scalar_inplace(a), None)
    assert_equal(a, xnd(10))

def test_scalar_inout():
    a = xnd(10)
    assert_equal(m.test_scalar_inout(a), None)
    assert_equal(a, xnd(10))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_output():
    assert_equal(m.test_scalar_output(), xnd(0))

def test_scalar_hide():
    assert_equal(m.test_scalar_hide(), None)

def test_scalar_input_output():
    a = xnd(10)
    assert_equal(m.test_scalar_input_output(a), a)
    assert_equal(a, xnd(10))

def test_scalar_inplace_output():
    a = xnd(10)
    assert_equal(m.test_scalar_inplace_output(a), a)
    assert_equal(a, xnd(10))

def test_scalar_inout_output():
    a = xnd(10)
    assert_equal(m.test_scalar_inout_output(a), a)
    assert_equal(a, xnd(10))

def test_scalar_ptr_input():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_input(a), None)
    assert_equal(a, xnd(10))

def test_scalar_ptr_inplace():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_inplace(a), None)
    assert_equal(a, xnd(20))

def test_scalar_ptr_inout():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_inout(a), None)
    assert_equal(a, xnd(20))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_output():
    assert_equal(m.test_scalar_ptr_output(), xnd(0))

def test_scalar_ptr_hide():
    assert_equal(m.test_scalar_ptr_hide(), None)

def test_scalar_ptr_input_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_input_output(a), xnd(20))
    assert_equal(a, xnd(10))

def test_scalar_ptr_inplace_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_inplace_output(a), xnd(20))
    assert_equal(a, xnd(20))

def test_scalar_ptr_inout_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_inout_output(a), xnd(20))
    assert_equal(a, xnd(20))

def test_scalar_return_input():
    a = xnd(10)
    assert_equal(m.test_scalar_return_input(a), xnd(30))
    assert_equal(a, xnd(10))

def test_scalar_return_inplace():
    a = xnd(10)
    assert_equal(m.test_scalar_return_inplace(a), xnd(30))
    assert_equal(a, xnd(10)) # because C scalar cannot be changed inplace

def test_scalar_return_inout():
    a = xnd(10)
    assert_equal(m.test_scalar_return_inout(a), xnd(30))
    assert_equal(a, xnd(10)) # because C scalar cannot be changed inplace

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_return_output():
    assert_equal(m.test_scalar_return_output(), (xnd(0), xnd(0)))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_return_hide():
    assert_equal(m.test_scalar_return_hide(), xnd(0))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_return_input_output():
    a = xnd(10)
    assert_equal(m.test_scalar_return_input_output(a), (xnd(30),xnd(10)))
    assert_equal(a, xnd(10))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_return_inplace_output():
    a = xnd(10)
    assert_equal(m.test_scalar_return_inplace_output(a), (xnd(30),xnd(10)))
    assert_equal(a, xnd(10))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_return_inout_output():
    a = xnd(10)
    assert_equal(m.test_scalar_return_inout_output(a), (xnd(30), xnd(10)))
    assert_equal(a, xnd(10))




def test_scalar_ptr_return_input():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_input(a), xnd(40))
    assert_equal(a, xnd(10))

def test_scalar_ptr_return_inplace():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_inplace(a), xnd(40))
    assert_equal(a, xnd(20))

def test_scalar_ptr_return_inout():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_inout(a), xnd(40))
    assert_equal(a, xnd(20))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_return_output():
    assert_equal(m.test_scalar_ptr_return_output(), (xnd(0), xnd(0)))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_return_hide():
    assert_equal(m.test_scalar_ptr_return_hide(), xnd(0))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_return_input_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_input_output(a), (xnd(30),xnd(10)))
    assert_equal(a, xnd(10))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_return_inplace_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_inplace_output(a), (xnd(30),xnd(10)))
    assert_equal(a, xnd(10))

@pytest.mark.skip(reason="segfaults, gumath bug")
def test_scalar_ptr_return_inout_output():
    a = xnd(10)
    assert_equal(m.test_scalar_ptr_return_inout_output(a), (xnd(30), xnd(10)))
    assert_equal(a, xnd(10))
