import numpy
import SimpleITK

def segment(array):

  maxJ = 0
  minJ = array.shape[0]
  maxK = 0
  minK = array.shape[1]   
    
  isinside = numpy.zeros(array.shape,'float')
  #isinside = numpy.ones(array.shape,'float')
  
  for j in range(0,array.shape[0]):
    for k in range(0,array.shape[1]):
      # grow out from upper left corner (which we assume to be outside)
      # actually we essentially assume the whole left/top edge to be outside
      # unless it is a part of the annotation
      if array[j,k] == 0:
        # NOT a part of the annotation
        if j-1 < 0 or k-1 < 0:
          # this is an edge pixel
          isinside[j,k] = 1
        elif isinside[j-1,k] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1
        elif isinside[j,k-1] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k-1] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1

  # find biggest & smallest X and Y that are in the annotations
      elif array[j,k] != 0:
        # part of the annotation
        if j > maxJ:
          maxJ = j
        elif j < minJ:
          minJ = j
        elif k > maxK:
          maxK = k
        elif k < minK:
          minK = k
  # end of finding the boundaries
  print(maxJ)
  print(minJ)
  print(maxK)
  print(minK)

  # loop through image again from bottom right corner of subregion
  for j in range(maxJ+1, minJ-1, -1):
    for k in range(maxK+1, minK-1, -1):
      if array[j,k] == 0:
        # NOT a part of the annotation
        if j+1 > maxJ+1 or k+1 > maxK+1:
          # this is an edge pixel
          isinside[j,k] = 1
        elif isinside[j+1,k] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1
        elif isinside[j,k+1] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1
        elif isinside[j+1,k+1] == 1:
          # a previous adjacent point belonged to the outside
          isinside[j,k] = 1
          
  # loop through image again from bottom left corner of subregion
  for k in range(maxK+1, minK-1, -1):
    for j in range(minJ-1, maxJ+1):
      if array[j,k] == 0:
        # NOT a part of the annotation
        if j-1 < minJ-1 or k+1 > maxK+1:
          # this is an edge pixel
          isinside[j,k] = 1
        elif isinside[j+1,k] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j+1,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j+1,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1

  # loop through image again from top right corner of subregion
  for k in range(minK-1, maxK+1):
    for j in range(maxJ+1, minJ-1, -1):
      if array[j,k] == 0:
        # NOT a part of the annotation
        if k-1 < minK-1 or j+1 > maxJ+1:
          # this is an edge pixel
          isinside[j,k] = 1
        elif isinside[j+1,k] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j+1,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j-1,k+1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1
        elif isinside[j+1,k-1] == 1:
          # an adjacent point belongs to the outside
          isinside[j,k] = 1

  return isinside

         

                        
"""
  isinside = numpy.zeros(array.shape,'float')
  for j in range(minJ-1,maxJ+1):
    for k in range(minK-1,maxK+1):
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
        if (countJPlus % 2 == 1 and countJMinus % 2 == 1 and countKPlus % 2 == 1 and countKMinus > 0) or (countJMinus % 2 == 1 and countKPlus % 2 == 1 and countKMinus % 2 == 1 and countJPlus > 0) or (countKPlus % 2 == 1 and countKMinus % 2 == 1 and countJPlus % 2 == 1 and countJMinus > 0) or (countKMinus % 2 == 1 and countJPlus % 2 == 1 and countJMinus % 2 == 1 and countKPlus > 0):
          # area is inside the circle / mask
          isinside[j,k] = 1
          #print("coord ",j,k)

      # else
          # do nothing since pixel is inside the annotation (>0) 
  return isinside
"""
