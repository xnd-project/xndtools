
from xnd import xnd
import example as m

print(dir(m))

def v(obj):
    return obj.type, obj.value

class xnd_data(object):
    def __add__(self, other):
        return (other.type, other.value)
    
_ = xnd_data()

def test_scalar_intent_in():
    assert _+ m.scalar_intent_in(xnd(1.0)) == _+ xnd(2.0)
    assert _+ m.scalar_intent_in(xnd(1, type='int32')) == _+ xnd(2, type='int32')
    assert _+ m.scalar_intent_in(xnd([1.0, 2.0])) == _+ xnd([2.0, 3.0])
    
def test_scalar_ptr_intent_in():
    assert _+ m.scalar_ptr_intent_in(xnd(1.0)) == _+ xnd(2.0)
    assert _+ m.scalar_ptr_intent_in(xnd(1, type='int32')) == _+ xnd(2, type='int32')
    assert _+ m.scalar_ptr_intent_in(xnd([1.0, 2.0])) == _+ xnd([2.0, 3.0])

def test_array_intent_in():
    assert _+ m.array_intent_in(xnd([1.0, 2.0])) == _+ xnd(3.0)
    assert _+ m.array_intent_in(xnd([1, 2], type='2 * int32')) == _+ xnd(3, type='int32')
    assert _+ m.array_intent_in(xnd([1, 2, 3], type='3 * int32')) == _+ xnd(4, type='int32')

def test_array_2d_c_intent_in():
    a = xnd([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], type='2 * 3 * float64')
    assert _+ (m.array_2d_c_intent_in(a)) == _+ xnd(4.0)

def test_array_2d_f_intent_in():
    a = xnd([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], type='!2 * 3 * float64')
    assert _+ (m.array_2d_f_intent_in(a)) == _+ xnd(4.0)
