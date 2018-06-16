
from xnd import xnd
import example as m

print(dir(m))

def v(obj):
    return obj.type, obj.value

class xnd_data(object): # temporary way of getting data for element-wise equality test
    def __add__(self, other):
        return (str(other.type), other.value)
    
_ = xnd_data()

def test_scalar_intent_in():
    assert _+ m.scalar_intent_in(xnd(1.0)) == _+ xnd(2.0)
    assert _+ m.scalar_intent_in(xnd(1, type='int32')) == _+ xnd(2, type='int32')
    assert _+ m.scalar_intent_in(xnd([1.0, 2.0])) == _+ xnd([2.0, 3.0])

    x = xnd([[1.0],[11.0,12.0]])
    assert _+m.scalar_intent_in(x) == _+xnd([[2.0],[12.0,13.0]])
    
def test_scalar_ptr_intent_in():
    assert _+ m.scalar_ptr_intent_in(xnd(1.0)) == _+ xnd(2.0)
    assert _+ m.scalar_ptr_intent_in(xnd(1, type='int32')) == _+ xnd(2, type='int32')
    assert _+ m.scalar_ptr_intent_in(xnd([1.0, 2.0])) == _+ xnd([2.0, 3.0])
    x = xnd([[1.0],[11.0,12.0]])
    assert _+m.scalar_intent_in(x) == _+xnd([[2.0],[12.0,13.0]])
    
def test_array_intent_in():
    assert _+ m.array_intent_in(xnd([1.0, 2.0])) == _+ xnd(3.0)
    assert _+ m.array_intent_in(xnd([1, 2], type='2 * int32')) == _+ xnd(3, type='int32')
    assert _+ m.array_intent_in(xnd([1, 2, 3], type='3 * int32')) == _+ xnd(4, type='int32')
    
    x = xnd([10.0, 2.0, 3.0, 4.0, 50.0])
    assert _+m.array_intent_in(x) == _ + xnd(60.0)
    
    assert _+ x[1::2] == _ + xnd([2.0, 4.0])
    assert _+m.array_intent_in(x[1::2]) == _ + xnd(6.0)

    x = xnd([1.0, 2.0, 3.0, 4.0, 5.0])[0::2]
    assert _+ x == _ + xnd([1.0, 3.0, 5.0])
    assert _+m.array_intent_in(x) == _ + xnd(6.0)

    x = xnd([1.0, 2.0, 3.0, 4.0, 5.0])[1:]
    assert _+ x == _ + xnd([2.0, 3.0, 4.0, 5.0])
    assert _+m.array_intent_in(x) == _ + xnd(7.0)

    x = xnd([[1.0, 2.0, 3.0, 4.0, 5.0], [10.0, 20.0, 30.0, 40.0, 50.0]])
    assert _+m.array_intent_in(x) == _ + xnd([6.0, 60.0])

    if 0:
        x = xnd([[1.0, 2.0, 3.0, 4.0, 5.0], [10.0, 20.0, 30.0, 40.0, 50.0, 60.0]]) # var * var * float64
        assert _+m.array_intent_in(x) == _ + xnd([6.0, 70.0])
    
def test_array_2d_intent_in():
    # array_2d_intent_in returns the sum of the first and the last element in first row
    a = xnd([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], type='2 * 3 * float64')
    assert _+ (m.array_2d_intent_in(a)) == _+ xnd(4.0)

    a = xnd([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]], type='!2 * 3 * float64')
    assert _+ (m.array_2d_intent_in(a)) == _+ xnd(4.0)
        
    a = xnd([[1.0, 2.0, 3.0, 4.0, 5.0],
             [110.0, 21.0, 31.0, 41.0, 510.0],
             [12.0, 22.0, 32.0, 42.0, 52.0],
             [13.0, 23.0, 33.0, 43.0, 53.0],
             [14.0, 24.0, 34.0, 44.0, 54.0],
    ], type='5 * 5 * float64')
    assert _+ (m.array_2d_intent_in(a)) == _+ xnd(6.0)
    assert _+ (m.array_2d_intent_in(a[1::2])) == _+ xnd(620.0)
    assert _+ (m.array_2d_intent_in(a[1::2,1::2])) == _+ xnd(62.0)

    a = xnd([[1.0, 2.0, 3.0, 4.0, 5.0],
             [110.0, 21.0, 31.0, 41.0, 510.0],
             [12.0, 22.0, 32.0, 42.0, 52.0],
             [13.0, 23.0, 33.0, 43.0, 53.0],
             [14.0, 24.0, 34.0, 44.0, 54.0],
    ], type='!5 * 5 * float64')
    assert _+ (m.array_2d_intent_in(a)) == _+ xnd(6.0)
    assert _+ (m.array_2d_intent_in(a[1::2])) == _+ xnd(620.0)
    assert _+ (m.array_2d_intent_in(a[1::2,1::2])) == _+ xnd(62.0)
    
