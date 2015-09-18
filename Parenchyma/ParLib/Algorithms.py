import numpy

def segment(array):
  isinside = numpy.zeros(array.shape,'float')
  for j in range(0,array.shape[0]):
    for k in range(0,array.shape[1]):
      # for each pixel that is not a part of the annotation check...
      if array[j,k] == 0:
        # go +/- in j from the pixel
        countJPlus = 0
        countJMinus = 0
        insideJLine = False
        for j2 in range(j+1,array.shape[0]):
          if array[j2,k] > 0:
            # inside line
            if insideJLine == False:
              countJPlus += 1
            insideJLine = True
          else:
            # == 0, outside line
            insideJLine = False
        for j2 in range(0,j):
          if array[j2,k] > 0:
            # inside line
            if insideJLine == False:
              countJMinus += 1
            insideJLine = True
          else:
            # == 0, outside line
            insideJLine = False
        # go +/- in k from the pixel
        countKPlus = 0
        countKMinus = 0
        insideKLine = False
        for k2 in range(k+1,array.shape[1]):
          if array[j,k2] > 0:
            # inside line
            if insideKLine == False:
              countKPlus += 1
            insideKLine = True
          else:
            # == 0, outside line
            insideKLine = False
        for k2 in range(0,k):
          if array[j,k2] > 0:
            # inside line
            if insideKLine == False:
              countKMinus += 1
            insideKLine = True
          else:
            # == 0, outside line
            insideKLine = False
        # if there are an odd # of lines crossed on either side
        areaInsideMask = []
        if (countJPlus % 2 == 1 and countJMinus % 2 == 1 and countKPlus % 2 == 1) or (countJMinus % 2 == 1 and countKPlus % 2 == 1 and countKMinus % 2 == 1) or (countKPlus % 2 == 1 and countKMinus % 2 == 1 and countJPlus % 2 == 1) or (countKMinus % 2 == 1 and countJPlus % 2 == 1 and countJMinus % 2 == 1):
          # area is inside the circle / mask
          isinside[j,k] = 1
          print("coord ",j,k)

      # else
          # do nothing since pixel is inside the annotation (>0) 
  return isinside
