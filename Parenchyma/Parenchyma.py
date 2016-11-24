import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy
import pickle
import SimpleITK
import sitkUtils
#import Editor
import EditorLib
#from EditorLib.EditOptions import EditOptions
from EditorLib.EditUtil import EditUtil
import ParLib.Algorithms
#import ParLib.Paint
from slicer.ScriptedLoadableModule import *

#
# Parenchyma
#

class Parenchyma(ScriptedLoadableModule):
  """Uses ScriptedLoadableModule base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def __init__(self, parent):
    ScriptedLoadableModule.__init__(self, parent)
    self.parent.title = "Parenchyma" # TODO make this more human readable by adding spaces
    self.parent.categories = ["Examples"]
    self.parent.dependencies = []
    self.parent.contributors = ["IVS"] # replace with "Firstname Lastname (Organization)"
    self.parent.helpText = """
    This is an example of scripted loadable module bundled in an extension.
    """
    self.parent.acknowledgementText = """
    This file was originally developed by Jean-Christophe Fillion-Robin, Kitware Inc.
    and Steve Pieper, Isomics, Inc. and was partially funded by NIH grant 3P41RR013218-12S1.
""" # replace with organization, grant and thanks.


#
# ParenchymaWidget
#

class ParenchymaWidget(ScriptedLoadableModuleWidget):
  """Uses ScriptedLoadableModuleWidget base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  
  def __init__(self, parent = None):
    ScriptedLoadableModuleWidget.__init__(self, parent)
    self.masterNode = None
    self.labelNode = None
    
    self.paint = None
    self.paintMode = False
    self.correct = None
    self.correctMode = False
    self.logic = ParenchymaLogic()
    self.editUtil = EditUtil()
    #self.editUtil = EditorLib.EditUtil.EditUtil()
    #self.localParEditorWidget = None
       
  def setup(self):
    
    ScriptedLoadableModuleWidget.setup(self)
    # Instantiate and connect widgets ...

    #
    # Parameters Area
    #
    parametersCollapsibleButton = ctk.ctkCollapsibleButton()
    parametersCollapsibleButton.text = "Parameters"
    self.layout.addWidget(parametersCollapsibleButton)

    # Layout within the dummy collapsible button
    parametersLayout = qt.QFormLayout(parametersCollapsibleButton)

    #
    # input volume selector
    #
    self.inputSelector = slicer.qMRMLNodeComboBox()
    self.inputSelector.nodeTypes = ( ("vtkMRMLScalarVolumeNode"), "" )
    self.inputSelector.addAttribute( "vtkMRMLScalarVolumeNode", "LabelMap", 0 )
    self.inputSelector.selectNodeUponCreation = True
    self.inputSelector.addEnabled = False
    self.inputSelector.removeEnabled = False
    self.inputSelector.noneEnabled = True
    self.inputSelector.showHidden = False
    self.inputSelector.showChildNodeTypes = False
    self.inputSelector.setMRMLScene( slicer.mrmlScene )
    self.inputSelector.setToolTip( "Pick the input to the algorithm." )
    parametersLayout.addRow("Input Volume: ", self.inputSelector)
    
    #self.activeVolume = self.inputSelector.currentNode()
    #self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    #self.labelSelector = slicer.qSlicerLabelMapVolumeDisplayWidget()
    #parametersLayout.addRow("Label Map: ", self.labelSelector)
    
    #
    # Select Button
    #
    self.selectButton = qt.QPushButton("Select")
    self.selectButton.toolTip = "Select the volume."
    self.selectButton.enabled = True
    parametersLayout.addRow(self.selectButton)

    #
    # Gradient Button
    #
    self.gradientButton = qt.QPushButton("Gradient - sergio reimplementation")
    self.gradientButton.toolTip = "re-implementation of sergio's gradient."
    self.gradientButton.enabled = True
    parametersLayout.addRow(self.gradientButton)

    #
    # Paint Button
    #
    self.paintButton = qt.QPushButton("Paint")
    self.paintButton.toolTip = "Turn on paint."
    self.paintButton.enabled = True
    self.paintButton.checkable = True
    parametersLayout.addRow(self.paintButton)
    
    #
    # Apply mask Button
    #
    self.applyButton = qt.QPushButton("Apply mask")
    self.applyButton.toolTip = "Find area of mask."
    self.applyButton.enabled = True
    parametersLayout.addRow(self.applyButton)

    #
    # Range for threshold
    #
    self.threshold = ctk.ctkRangeWidget()
    lo, hi = self.getLoHiImageValues()
    self.threshold.minimum, self.threshold.maximum = lo, hi
    self.threshold.singleStep = (hi - lo) / 1000.
    parametersLayout.addRow(self.threshold)
    
    #
    # Grow Button
    #
    self.growButton = qt.QPushButton("Grow with Threshold")
    self.growButton.toolTip = "Grow into 3D with connected threshold."
    self.growButton.enabled = True
    parametersLayout.addRow(self.growButton)

    #
    # Liver 2D Button
    #
    self.liver2DButton = qt.QPushButton("Liver 2D")
    self.liver2DButton.toolTip = "Grow from mask in 2D, but up down into next slices."
    self.liver2DButton.enabled = True
    parametersLayout.addRow(self.liver2DButton)

    #
    # Cross remove Button
    #
    self.crossButton = qt.QPushButton("Cross remove")
    self.crossButton.toolTip = "re-implementation of sergio's cross remove."
    self.crossButton.enabled = True
    parametersLayout.addRow(self.crossButton)

    #
    # Connectivity reduction Button
    #
    self.connectivityButton = qt.QPushButton("Connectivity reduction")
    self.connectivityButton.toolTip = "re-implementation of sergio's connectivity reduction."
    self.connectivityButton.enabled = True
    parametersLayout.addRow(self.connectivityButton)
    
    #
    # Paint Button (correction)
    #
    self.correctButton = qt.QPushButton("Correct")
    self.correctButton.toolTip = "Turn on paint for annotating corrections."
    self.correctButton.enabled = True
    self.correctButton.checkable = True
    parametersLayout.addRow(self.correctButton)

    #
    # Track centroid under mask
    #
    self.trackMaskButton = qt.QPushButton("Track correction")
    self.trackMaskButton.toolTip = "Try to use correction mask, and track the centroid in has inside it"
    self.trackMaskButton.enabled = True
    parametersLayout.addRow(self.trackMaskButton)

    #
    # Erase mask (including all under)
    #
    self.eraseMaskButton = qt.QPushButton("Erase correction")
    self.eraseMaskButton.toolTip = "Delete the correction mask to hopefully orphan other areas"
    self.eraseMaskButton.enabled = True
    parametersLayout.addRow(self.eraseMaskButton)
    
    #
    # Remove unconnected
    #
    self.removeIsolatedButton = qt.QPushButton("Remove unconnected")
    self.removeIsolatedButton.toolTip = "try to see just the main blob and remove stuff not connected."
    self.removeIsolatedButton.enabled = True
    parametersLayout.addRow(self.removeIsolatedButton)

    
    # connections
    #buttons
    self.selectButton.connect('clicked(bool)', self.onSelectButton)
    self.gradientButton.connect('clicked(bool)', self.onGradientButton)   
    self.paintButton.connect('clicked(bool)', self.onPaintButton)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.growButton.connect('clicked(bool)', self.onGrowButton)
    self.liver2DButton.connect('clicked(bool)', self.onliver2DButton)
    self.crossButton.connect('clicked(bool)', self.onCrossButton)
    self.connectivityButton.connect('clicked(bool)', self.onConnectivityButton)
    # correction tools buttons
    self.correctButton.connect('clicked(bool)', self.onCorrectButton)
    self.trackMaskButton.connect('clicked(bool)', self.onTrackMaskButton)
    self.eraseMaskButton.connect('clicked(bool)', self.onEraseMaskButton)
    self.removeIsolatedButton.connect('clicked(bool)', self.onRemoveIsolatedButton)

    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    self.threshold.connect('valuesChanged(double,double)', self.onThresholdValuesChanged)

    # Creates and adds the custom Editor Widget to the module
    #self.localParEditorWidget = ParEditorWidget(parent=self.parent, showVolumesFrame=False)
    #self.localParEditorWidget.setup()
    #self.localParEditorWidget.enter()

    # Add vertical spacer
    self.layout.addStretch(1)

    # sets the layout to Red Slice Only
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)


  '''-----------------------------------------------------------------------------'''
    
  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode()
    self.masterNode = self.inputSelector.currentNode()

  def onSelectButton(self):
    self.masterNode = self.inputSelector.currentNode()
    lo, hi = self.getLoHiImageValues()
    self.threshold.minimum, self.threshold.maximum = lo, hi
    self.threshold.singleStep = (hi - lo) / 1000.
    #print(self.inputSelector.currentNode())

  def onLabelButton(self):
    self.labelNode = self.logic.createLabelMap(self.inputSelector.currentNode())

  def onProcessFilterButton(self):
    self.logic.processFilter(self.masterNode)

  def onPaintButton(self):
    if self.paintMode:
      self.paintMode = False
      print("deleting paint")
      self.painter.cleanup()
      self.painter = None
      #self.paint.removeObs()
    else:
      self.paintMode = True

      # just in case?
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActiveVolumeID( self.masterNode.GetID() )
      if self.labelNode == None:
        self.labelNode = self.logic.createLabelMap(self.inputSelector.currentNode())
      selectionNode.SetReferenceActiveLabelVolumeID( self.labelNode.GetID() )
      slicer.app.applicationLogic().PropagateVolumeSelection(0)

      self.editUtil.setLabel(1) # green
      
      print("create paint (editor paint effect tool)")
      lm = slicer.app.layoutManager()
      paintEffect = EditorLib.PaintEffectOptions()
      paintEffect.setMRMLDefaults()
      paintEffect.__del__()
      sliceWidget = lm.sliceWidget('Red')
      self.painter = EditorLib.PaintEffectTool(sliceWidget)

  def onApplyButton(self):
    self.logic.runMask(self.masterNode, self.labelNode)
    mean, std = self.logic.getMeanSD()
    max = mean + std
    min = mean - std
    hi = mean + 4*std
    lo = mean - 4*std
    self.threshold.minimum, self.threshold.maximum = lo, hi
    self.setThresholdValues(min, max)

  def onGrowButton(self):
    self.logic.runThreshold(self.masterNode, self.labelNode)

  def onGradientButton(self):
    self.logic.runGradient(self.masterNode)

  def onliver2DButton(self):    
    print("Liver button")
    #runFindLiver2D(self,masterNode,labelNode): 
    self.logic.runFindLiver2D(self.masterNode, self.labelNode)

  def onCrossButton(self):
    self.logic.runCrossRemove(self.masterNode, self.labelNode, 2) # need to pass in size of cross 

  def onConnectivityButton(self):
    self.logic.runConnectivity(self.masterNode, self.labelNode, 10) # need to pass in number of pixels around it that need to be 1

  def onCorrectButton(self):
    if self.correctMode:
      self.correctMode = False
      print("deleting correct")
      self.painter.cleanup()
      self.painter = None
      #self.paint.removeObs()
    else:
      self.correctMode = True

      # just in case?
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActiveVolumeID( self.masterNode.GetID() )
      if self.labelNode == None:
        self.labelNode = self.logic.createLabelMap(self.inputSelector.currentNode())
      selectionNode.SetReferenceActiveLabelVolumeID( self.labelNode.GetID() )
      slicer.app.applicationLogic().PropagateVolumeSelection(0)

      self.editUtil.setLabel(5) # red

      print("create correct (editor paint effect tool)")
      lm = slicer.app.layoutManager()
      paintEffect = EditorLib.PaintEffectOptions()
      paintEffect.setMRMLDefaults()
      paintEffect.__del__()
      sliceWidget = lm.sliceWidget('Red')
      self.painter = EditorLib.PaintEffectTool(sliceWidget)

  def onTrackMaskButton(self):
    self.logic.runTrackMask(self.masterNode, self.labelNode)

  def onEraseMaskButton(self):
    self.logic.runEraseMask(self.masterNode, self.labelNode)

  def onRemoveIsolatedButton(self):
    self.logic.runRemoveIsolated(self.masterNode, self.labelNode)
      
  def onEdgeButton(self):
    self.logic.runFindEdge(self.masterNode, self.labelNode)

  def getLoHiImageValues(self):
    backgroundImage = self.masterNode
    lo = 0
    hi = 100
    if backgroundImage:
      data = backgroundImage.GetImageData()
      lo, hi = data.GetScalarRange()
      print('Low: ', lo)
      print('High: ', hi)
    return lo, hi

  def onThresholdValuesChanged(self):
    print('value changed')
    min = self.threshold.minimumValue
    max = self.threshold.maximumValue
    print(min, max)

  def setThresholdValues(self, min, max):
    self.threshold.setMinimumValue( min )
    self.threshold.setMaximumValue( max )

'''-----------------------------------------------------------------------------'''

#
# ParenchymaLogic
#
class ParenchymaLogic(ScriptedLoadableModuleLogic):
  """This class should implement all the actual
  computation done by your module.  The interface
  should be such that other python code can import
  this class and make use of the functionality without
  requiring an instance of the Widget.
  Uses ScriptedLoadableModuleLogic base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """
  #def __init__(self, parent = None):
    #ScriptedLoadableModuleLogic.__init__(self, parent)
    #self.editPaint = EditorLib.PaintEffectOptions()

  # global variables for initial mask
  maskZ = 0
  centroidX = 0
  centroidY = 0
  mean = 0
  std = 0

  def getMeanSD(self):
    global mean, std
    return mean, std

  def hasImageData(self,volumeNode):
    """This is a dummy logic method that
    returns true if the passed in volume
    node has valid image data
    """
    if not volumeNode:
      print('no volume node')
      return False
    if volumeNode.GetImageData() == None:
      print('no image data')
      return False
    return True

  def createLabelMap(self,masterNode):
    self.delayDisplay('Creating label map')
    masterName = masterNode.GetName()
    mergeName = masterName + "-label"

    self.delayDisplay(mergeName)
    merge = slicer.modules.volumes.logic().CreateAndAddLabelVolume( slicer.mrmlScene, masterNode, mergeName )
    #self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(volumeNode, merge))
    labelColorTable = slicer.util.getNode('GenericAnatomyColors')
    merge.GetDisplayNode().SetAndObserveColorNodeID( labelColorTable.GetID() )

    # make the source node the active background, and the label node the active label
    selectionNode = slicer.app.applicationLogic().GetSelectionNode()
    selectionNode.SetReferenceActiveVolumeID( masterNode.GetID() )
    selectionNode.SetReferenceActiveLabelVolumeID( merge.GetID() )
    slicer.app.applicationLogic().PropagateVolumeSelection(0)

    return merge
    
  def runMask(self,masterNode,labelNode):
    """
    Run things in 2D, stuff with the mask
    """
    self.delayDisplay('Running the mask')
    # check there is a label map
    self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(masterNode, labelNode))
    # TODO: do not run algorithm if there is no label map
    
    # get the drawn mask
    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID())
    
    print(labelArray.shape)
    print(masterArray.shape)
    # TODO: compare dimensions to check they match
 
    intensitiesInsideOriginal = []
    #intensitiesInsideGradient = []
    # find the levels where there are annotations
    for i in range(0,labelArray.shape[0]):
      if numpy.max(labelArray[i,:,:]) == 1: # looking for green, which is label 1
        print('in z:', i)
        global maskZ
        maskZ = i
        # send the array of the one level
        annotatedSlice = masterArray[i,:,:]
        array = labelArray[i,:,:]            
        isinside = ParLib.Algorithms.segment(array, 1) # call function "segment"
        # print isinside
        # modify the label map to show what pixels are said to be inside the circle / mask
        for j in range(0,isinside.shape[0]):
          for k in range(0,isinside.shape[1]):
            if isinside[j,k] == 0:
              labelArray[i,j,k] = 1
              # get all the intensities from the actual + modified image
              intensitiesInsideOriginal.append(masterArray[i,j,k])
              #intensitiesInsideGradient.append(gradientArray[i,j,k])

    # uint8 (0-255) ok for binary image, but cannot trust all images will stay within those bounds (ct/mri images can be encoded +/- numbers)?
    invert = (isinside == 0).astype('uint8')   
    roi = SimpleITK.GetImageFromArray(invert, isVector=False)
    print('size of itk image (label):', roi.GetSize())
    shapefilter = SimpleITK.LabelShapeStatisticsImageFilter()
    shapefilter.SetBackgroundValue(0)
    shapefilter.Execute(roi)
    centroid = shapefilter.GetCentroid(1)
    print('centroid:', centroid)
    global centroidX
    global centroidY
    centroidX = int(centroid[0])
    centroidY = int(centroid[1])
    
    meanOriginal = numpy.mean(intensitiesInsideOriginal[:])
    print('mean:', meanOriginal)
    stdOriginal = numpy.std(intensitiesInsideOriginal[:])
    print('standard deviation:', stdOriginal)
    global mean, std
    mean = meanOriginal
    std = stdOriginal
    
    #masterNode.Modified()
    labelNode.Modified()
                   
    self.delayDisplay('Mask done')

    
  def runThreshold(self,masterNode,labelNode):

    masterImage = sitkUtils.PullFromSlicer(masterNode.GetID())

    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID())
      
    connectedThresholdIF = SimpleITK.ConnectedThresholdImageFilter()
    connectedThresholdIF.SetLower(mean-(1.5*std))
    connectedThresholdIF.SetUpper(mean+(1.5*std)) 

    print('Centroid:', int(centroidX), int(centroidY) )
    connectedThresholdIF.SetSeed([int(centroidX),int(centroidY),maskZ])
    print('starting: connected threshold filter')
    thresholdImage = connectedThresholdIF.Execute(masterImage)

    # take this out for now, as time costly and may be best to close holes in 2D
    '''
    print('starting: fill holes filter')
    fillHoleIF = SimpleITK.GrayscaleFillholeImageFilter()
    connectedImage = fillHoleIF.Execute(thresholdImage)
    '''
    
    sitkUtils.PushToSlicer(thresholdImage, 'connectedImage')
    #print('save self.connected image')

    '''
    print('copying the connected image to the label')
    connectedArray = SimpleITK.GetArrayFromImage(connectedImage)
    for i in range(0, labelArray.shape[0]):
      for j in range(0,labelArray.shape[1]):
        for k in range(0,labelArray.shape[2]):
          if connectedArray[i,j,k] == 1:
            labelArray[i,j,k] = 1
          else:
            labelArray[i,j,k] = 0
    '''

  def runFindLiver2D(self,masterNode,labelNode):

    labelArray = slicer.util.array(labelNode.GetID())
    connectedArray = slicer.util.array(masterNode.GetID())

    global maskZ
    global centroidX
    global centroidY

    print('find liver 2D:', maskZ, centroidX, centroidY)
    # grow in 2d to everything connected to that point that is segmented
    
    #regionGrow2D(self, z,x,y, newLabel, eraseLabel, labelArray):
    tempArray = ParLib.Algorithms.connected2D(maskZ, centroidY, centroidX, labelArray, connectedArray)
    tempImage = SimpleITK.GetImageFromArray(tempArray)
    sitkUtils.PushToSlicer(tempImage, 'liver')
    
    #tempImage = SimpleITK.GetImageFromArray(labelArray)
    #sitkUtils.PushToSlicer(tempImage, 'liverLabel')
    # put this in the label map liverNode
    
        
  # gradient filter
  def runGradient(self, masterNode):

    global mean
    global std

    tempImage = sitkUtils.PullFromSlicer(masterNode.GetID())
    '''
    castIF = SimpleITK.CastImageFilter()
    castIF.SetOutputPixelType(SimpleITK.sitkFloat32)
    masterImage = castIF.Execute(tempImage)
    
    smoothIF = SimpleITK.GradientAnisotropicDiffusionImageFilter()
    spacing = masterImage.GetSpacing()
    min_spacing = numpy.min(numpy.array(spacing))
    smoothIF.SetTimeStep(min_spacing/(math.pow(2, 4)))
    smoothIF.SetNumberOfIterations(10)
    smoothIF.SetConductanceParameter(10)
    smoothImage = smoothIF.Execute(masterImage)

    sitkUtils.PushToSlicer(smoothImage, 'smoothImage')
    print('Done smoothing')
    '''
    
    smoothArray = SimpleITK.GetArrayFromImage(tempImage)
    gradientArray = SimpleITK.GetArrayFromImage(tempImage) # duplicate to modify this one

    for j in range(1, smoothArray.shape[1]-2): # X
      for k in range(1, smoothArray.shape[2]-2): # Y
        gradientArray[:,j,k] = numpy.sum(numpy.sum(numpy.abs(smoothArray[:, j-2:j+2, k-2:k+2] - mean), axis=2), axis=1) / 9

    gradientImage = SimpleITK.GetImageFromArray(gradientArray)
    sitkUtils.PushToSlicer(gradientImage, 'gradientImage')
    print('Done sergio gradient')
    

  # re-implementation of sergio's
  def runCrossRemove(self, masterNode, labelNode, size_c):

    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID()) 

    # should be run on label array (copied over from connectedImage)
    for i in range(0, labelArray.shape[0]):
      print('crossRemove:', i)
      for j in range(size_c,labelArray.shape[1]-size_c):
        for k in range(size_c,labelArray.shape[2]-size_c):
          sum_j = 0
          sum_k = 0
          # go out 2 pixels in each 2D direction (j,k)
          sum_j = numpy.sum(labelArray[i,j-size_c:j+size_c+1,k])
          sum_k = numpy.sum(labelArray[i,j,k-size_c:k+size_c+1])
          
          if(labelArray[i,j,k] == 1):
            # check if not connected enough (and remove pixel if it is)
            if(sum_j <=1 or sum_k <=0):
              labelArray[i,j,k] = 0
          if(labelArray[i,j,k] == 0):
            # check if is very connected (and add pixel if it is)
            if(sum_j >= (2*size_c) or sum_k >= (2*size_c)):
              labelArray[i,j,k] = 1
              
  # re-implementation of sergio's
  def runConnectivity(self, masterNode, labelNode, connectivity):

    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID()) 

    # should be run on label array (copied over from connectedImage)
    for i in range(0, labelArray.shape[0]):
      print('connectivity:', i)
      for j in range(5,labelArray.shape[1]-5):
        for k in range(5,labelArray.shape[2]-5):
          if(labelArray[i,j,k] == 1):
            sum_square = 0
            sum_square = numpy.sum(labelArray[i,j-2:j+3,k-2:k+3]) - labelArray[i,j,k]
            # if its not connected enough, remove pixel
            if sum_square < connectivity:
              labelArray[i,j,k] = 17

              
                

  
  # 
  # STUFF FOR CORRECTION TOOL (below here)
  #
  def runTrackMask(self, masterNode, labelNode):

    self.delayDisplay('Tracking the correction mask')
    # check there is a label map
    self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(masterNode, labelNode))
    # TODO: do not run algorithm if there is no label map
    
    # get the drawn mask
    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID())
    
    print(labelArray.shape)
    print(masterArray.shape)
    # TODO: compare dimensions to check they match

    mZ = 0
    
    # find the levels where there are annotations
    for i in range(0,labelArray.shape[0]):
      if numpy.max(labelArray[i,:,:]) == 5: # looking for red, which is label 5
        print('in z (runCorrectMask):', i)
        mZ = i
        # send the array of the one level
        annotatedSlice = masterArray[i,:,:]
        array = labelArray[i,:,:]            
        isinside = ParLib.Algorithms.segment(array, 5) # call function "segment"
        segmentedInside = numpy.zeros(array.shape,'float')
        # print isinside
        # modify the label map to show what pixels are said to be inside the circle / mask
        for j in range(0,isinside.shape[0]):
          for k in range(0,isinside.shape[1]):
            if isinside[j,k] == 0 and labelArray[i,j,k] > 0:
              labelArray[i,j,k] = 5
              segmentedInside[j,k] = 1
            elif isinside[j,k] == 0:
              labelArray[i,j,k] = 5
               
    # uint8 (0-255) ok for binary image, but cannot trust all images will stay within those bounds (ct/mri images can be encoded +/- numbers)?
    temp = segmentedInside.astype('uint8')   
    roi = SimpleITK.GetImageFromArray(temp, isVector=False)
    print('size of itk image (label):', roi.GetSize())
    shapefilter = SimpleITK.LabelShapeStatisticsImageFilter()
    shapefilter.SetBackgroundValue(0)
    shapefilter.Execute(roi)
    centroid = shapefilter.GetCentroid(1)
    print('centroid:', centroid)
    centX = int(centroid[0])
    centY = int(centroid[1])
    
    labelArray = self.grow2DCentroid(labelArray, mZ, centX, centY)

    labelNode.Modified()
           
    self.delayDisplay('Correction mask done')

  def grow2DCentroid(self, labelArray, maskZ, centX, centY):

    newLabel = 4
    print('called grow 2d centroid:', maskZ, centX, centY)
    # flip them for label map?
    superiorCentX = centY
    superiorCentY = centX
    inferiorCentX = centY
    inferiorCentY = centX
    
    if labelArray[maskZ, centY, centX] > 0:
      eraseLabel = labelArray[maskZ,centY,centX]
      # z,x,y, newLabel, eraseLabel, labelArray
      # erase the mask
      iArray = ParLib.Algorithms.regionGrow2D(maskZ, centY, centX, 0, eraseLabel, labelArray)
    
    for i in range(maskZ+1,labelArray.shape[0]): # move superior
      isConnected = False
      if labelArray[i,superiorCentX,superiorCentY] > 0: # check if still in segmented area
        eraseLabel = labelArray[i,superiorCentX,superiorCentY]
        isConnected = True
        iArray = ParLib.Algorithms.regionGrow2D(i, superiorCentX, superiorCentY, newLabel, eraseLabel, labelArray)
      if isConnected == False:
        break # break out of enclosing for loop
      # update centroid
      temp = iArray.astype('uint8')   
      roi = SimpleITK.GetImageFromArray(temp, isVector=False)
      shapefilter = SimpleITK.LabelShapeStatisticsImageFilter()
      shapefilter.SetBackgroundValue(0)
      shapefilter.Execute(roi)
      centroid = shapefilter.GetCentroid(1)
      print('centroid:', int(centroid[0]), int(centroid[1]), 'prev:', superiorCentY, superiorCentX )
      distance = numpy.sqrt((superiorCentY - int(centroid[0]))**2 + (superiorCentX - int(centroid[1]))**2)
      print('moved (superior):', distance)
      if distance > 20:
        # go back one level before the break and switch eraselable and newlabel
        iArray = ParLib.Algorithms.regionGrow2D(i, superiorCentX, superiorCentY, eraseLabel, newLabel, labelArray)
        break
      else:
        # ok to erase previous level
        iArray = ParLib.Algorithms.regionGrow2D(i, superiorCentX, superiorCentY, 0, newLabel, labelArray)
      superiorCentY = int(centroid[0])
      superiorcentX = int(centroid[1])

    for i in range(maskZ-1,0,-1): # move inferior
      isConnected = False
      if labelArray[i,inferiorCentX,inferiorCentY] > 0: # check if still in segmented area
        eraseLabel = labelArray[i,inferiorCentX,inferiorCentY]
        isConnected = True
        iArray = ParLib.Algorithms.regionGrow2D(i, inferiorCentX, inferiorCentY, newLabel, eraseLabel, labelArray)
      if isConnected == False:
        break # break out of enclosing for loop
      # update centroid
      temp = iArray.astype('uint8')   
      roi = SimpleITK.GetImageFromArray(temp, isVector=False)
      shapefilter = SimpleITK.LabelShapeStatisticsImageFilter()
      shapefilter.SetBackgroundValue(0)
      shapefilter.Execute(roi)
      centroid = shapefilter.GetCentroid(1)
      print('centroid:', int(centroid[0]), int(centroid[1]), 'prev:', inferiorCentY, inferiorCentX )
      distance = numpy.sqrt((inferiorCentY - int(centroid[0]))**2 + (inferiorCentX - int(centroid[1]))**2)
      print('moved (inferior):', distance )
      if distance > 20:
        # go back one level before the break and switch eraselable and newlabel
        iArray = ParLib.Algorithms.regionGrow2D(i, inferiorCentX, inferiorCentY, eraseLabel, newLabel, labelArray)
        break
      else:
        # ok to erase previous level
        iArray = ParLib.Algorithms.regionGrow2D(i, inferiorCentX, inferiorCentY, 0, newLabel, labelArray)
      inferiorCentY = int(centroid[0])
      inferiorCentX = int(centroid[1])
        
    return labelArray

  def runEraseMask(self, masterNode, labelNode):

    self.delayDisplay('Erasing the correction mask')
    # check there is a label map
    self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(masterNode, labelNode))
    # TODO: do not run algorithm if there is no label map
    
    # get the drawn mask
    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID())
    
    print(labelArray.shape)
    print(masterArray.shape)
    # TODO: compare dimensions to check they match

    mZ = 0
    
    # find the levels where there are annotations
    for i in range(0,labelArray.shape[0]):
      if numpy.max(labelArray[i,:,:]) == 5: # looking for red, which is label 5
        print('in z (runCorrectMask):', i)
        mZ = i
        # send the array of the one level
        annotatedSlice = masterArray[i,:,:]
        array = labelArray[i,:,:]            
        isinside = ParLib.Algorithms.segment(array, 5) # call function "segment"
        segmentedInside = numpy.zeros(array.shape,'float')
        # print isinside
        # modify the label map to show what pixels are said to be inside the circle / mask
        for j in range(0,isinside.shape[0]):
          for k in range(0,isinside.shape[1]):
            if isinside[j,k] == 0:
              labelArray[i,j,k] = 0

    labelNode.Modified()
    self.delayDisplay('Erasing mask done')
            
    
  def modifyWrongArea(self, labelArray, maskZ, numSlices):

    print('in modifyWrongArea:', maskZ)
    # superior
    sup = maskZ + numSlices
    if(sup > labelArray.shape[0]):
      sup = labelArray.shape[0]
    for i in range(maskZ+1, sup): # go over the prescribed number of slices
      flag = 0
      for j in range(0,labelArray.shape[1]):
        for k in range(0,labelArray.shape[2]):
          if labelArray[maskZ,j,k] == 5: # and connectedArray[i,j,k] == 1:
            labelArray[i,j,k] = 0 # erase the segemented region
            if flag == 0:
              print('erase superior:', i)
              flag = 1
            
    # inferior
    inf = maskZ - numSlices+1
    if(inf < 0):
      inf = 0
    for i in range(inf, maskZ, -1): # go over the prescribed number of slices
      flag = 0
      for j in range(0,labelArray.shape[1]):
        for k in range(0,labelArray.shape[2]):
          if labelArray[maskZ,j,k] == 5: # and connectedArray[i,j,k] == 1:
            labelArray[i,j,k] = 0 # erase the segemented region
            if flag == 0:
              print('erase inferior:', i)
              flag = 1

    return labelArray
  
  # when click removeIsolateButton
  def runRemoveIsolated(self, masterNode, labelNode):

    labelArray = slicer.util.array(labelNode.GetID())
    masterArray = slicer.util.array(masterNode.GetID())

    # detect main region
    global centroidX 
    global centroidY
    global maskZ
    eraseLabel = labelArray[maskZ,centroidY,centroidX] # which way around should x and y be here?
    newLabel = eraseLabel+1
    if(newLabel == 5):
      newLabel = 6 # skip the red for corrections
    print('called region grow 3d:', maskZ)
    labelArray = ParLib.Algorithms.regionGrow3D(maskZ, centroidY, centroidX, newLabel, eraseLabel, labelArray)

    # delete everything in the label other than newLabel
    print('removing unconnected')
    for i in range(0, labelArray.shape[0]):
      for j in range(0,labelArray.shape[1]):
        for k in range(0,labelArray.shape[2]):
          if labelArray[i,j,k] != newLabel:
            labelArray[i,j,k] = 0

    labelNode.Modified()
    print('finished remove isolated area')
    
    




'''-----------------------------------------------------------------------------'''  

class ParenchymaTest(ScriptedLoadableModuleTest):
  """
  This is the test case for your scripted module.
  Uses ScriptedLoadableModuleTest base class, available at:
  https://github.com/Slicer/Slicer/blob/master/Base/Python/slicer/ScriptedLoadableModule.py
  """

  def setUp(self):
    """ Do whatever is needed to reset the state - typically a scene clear will be enough.
    """
    slicer.mrmlScene.Clear(0)

  def runTest(self):
    """Run as few or as many tests as needed here.
    """
    self.setUp()
    self.test_Parenchyma1()

  def test_Parenchyma1(self):
    """ Ideally you should have several levels of tests.  At the lowest level
    tests sould exercise the functionality of the logic with different inputs
    (both valid and invalid).  At higher levels your tests should emulate the
    way the user would interact with your code and confirm that it still works
    the way you intended.
    One of the most important features of the tests is that it should alert other
    developers when their changes will have an impact on the behavior of your
    module.  For example, if a developer removes a feature that you depend on,
    your test should break so they know that the feature is needed.
    """

    self.delayDisplay("Starting the test")
    #
    # first, get some data 
    #
    import urllib
    #downloads = ( ('http://slicer.kitware.com/midas3/download?items=216203', '0.nrrd', slicer.util.loadVolume),)

    downloads = ( ('http://10.163.46.32/midas/download?items=163', '0.nrrd', slicer.util.loadVolume),)

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="0")
    logic = ParenchymaLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')