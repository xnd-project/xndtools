
from xnd import xnd
from xndlib.example import example_sum

ddata = xnd([1,2,3,4], type='4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)

print('r=',r)

ddata = xnd([[1,2,3,4],
             [5,6,7,8]], type='2 * 4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)
print('r=',r)
