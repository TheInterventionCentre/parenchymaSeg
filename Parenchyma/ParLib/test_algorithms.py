import unittest
import numpy
import Algorithms
import pickle

class MyTest(unittest.TestCase):
  def test_twoblobs(self):
    array = numpy.zeros([12,12],'float')
    for i in range(3,10):
      # top edge
      array[2,i] = 1
    for i in range(2,7):
      # far left side
      array[i,2] = 1 
      # bottom left side
      array[7,i] = 1
    for i in range(4,8):
      # inner left side (left bump)
      array[i,6] = 1
    # spacer 
    array[4,7] = 1 
    for i in range(4,8):
      # inner right side (right bump)
      array[i,8] = 1
    for i in range(7,10):
      array[i,7] = 1
    for i in range(7,10):
      # bottom right side
      array[9,i] = 1
    for i in range(2,10):
      # far right side
      array[i,10] = 1
    isinside = Algorithms.segment(array)
    answer = [[ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  1,  1,  1,  1,  1,  1,  1,  0,  0],
        [ 0,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  1,  1,  1,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0],
        [ 0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0]]
    for i in range(0,len(answer)):
      for j in range(0, len(answer[i])):
        self.assertTrue(isinside[i][j] == answer[i][j])


#labelNode = pickle.load( open( "Testing/save_labelNode1.p", "rb"))
#masterNode = pickle.load( open( "Testing/save_masterNode1.p", "rb"))
#plt.imshow(labelNode[51,:,:])
#plt.show()
