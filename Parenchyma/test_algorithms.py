import numpy
import Algorithms

array = numpy.zeros([10,12],'float')
for i in range(3,8):
  array[i,3] = 1
  array[i,8] = 1
  array[3,i] = 1
  array[8,i] = 1
print array
isinside = Algorithms.segment(array)

print isinside
