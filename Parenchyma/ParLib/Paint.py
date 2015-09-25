import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy
#
# try to implement the bare minimum for painting
#

class Paint:
  def __init__(self, parent):
    print("Initializing paint")
    self.painting = False
    self.parent = parent
    #= self.sliceView.interactorStyle().GetInteractor()

    for e in ["LeftButtonPressEvent", "LeftButtonReleaseEvent", "MouseMoveEvent"]:
      print("Adding observer to interactor: " + e)
      self.parent.AddObserver(e, self.processEvent, 1.0)
    cursorPosition = qt.QCursor().pos()
    print(cursorPosition.x(), cursorPosition.y())

  def __del__(self):
    super(Paint,self).__del__()

  def processEvent(self, caller=None, event=None):
    print("processEvent")
    if event == "LeftButtonPressEvent":
      self.painting = True
    elif event == "LeftButtonReleaseEvent":
      self.painting = False
    elif event == "MouseMoveEvent":
      if self.painting:
        # get the image we are currently on (z level)
        #treeView = slicer.qMRMLAnnotationTreeView()
        cursorPosition = qt.QCursor().pos()
        #w = self.mainFrame.width
        #h = self.mainFrame.height
        # self.mainFrame.pos = qt.QPoint(cursorPosition.x() - w/2, cursorPosition.y() - h/2)
        print(cursorPosition.x(), cursorPosition.y())
        #treeView.mouseMoveEvent.
        #xy = self.interactor.GetEventPosition()
        #self.paintAddPoint(xy[0], xy[1])

  def paintLabelMap(self, labelNode):
    newArray = slicer.util.array(labelNode.GetID())
    cursorPosition = qt.QCursor().pos()
    w = self.mainFrame.width
    h = self.mainFrame.height
    # self.mainFrame.pos = qt.QPoint(cursorPosition.x() - w/2, cursorPosition.y() - h/2)
    print(cursorPosition.x(), cursorPosition.y())
    
    # paint the pixels stored in toBePainted
  
              # colour than voxel the first colour in the 'anatomy' set of colours - kind of a green
          #newArray[i,j,k] = 1
    #for i in range(0,newArray.shape[0]):
      #for j in range(0,newArray.shape[1]):
        #for k in range(0,newArray.shape[2]):


          
          
    
    
