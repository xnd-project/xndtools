
from xnd import xnd
from xndlib.example import example_sum, add_one

ddata = xnd([1,2,3,4], type='4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)

print('r=',r)

print ('-'*10)

ddata = xnd([[1,2,3,4], [5,6,7,8], [1,3,5,7]], type='3 * 4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)
print('r=',r)

ddata = xnd([[1,2,3,4], [5,6,7,8],
             [1,3,5,7], [10,11,12,13]], type='4 * 4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)
print('r=',r)

ddata = xnd([[[1,2,3,4], [5,6,7,8]],
             [[1,3,5,7], [10,11,12,13]]], type='2 * 2 * 4 * float64')
print('ddata=',ddata)
r = example_sum(ddata)
print('r=',r)

#ddata = xnd([1,2], type='var * int64')
#print(ddata)


#print (add_one(xnd(1)), add_one(xnd([2,3])))
#print (add_one(xnd([[1,2],[3]])))
