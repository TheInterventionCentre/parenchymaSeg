import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import numpy
import pickle
#import Editor
import EditorLib
from EditorLib.EditUtil import EditUtil
import ParLib.Algorithms
import ParLib.Paint
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
    self.logic = ParenchymaLogic()
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
    # Stuff for drawing
    #
    self.labelButton = qt.QPushButton("Create label map")
    self.labelButton.toolTip = "Create label map."
    self.labelButton.enabled = True
    #self.labelButton.checkable = True
    parametersLayout.addRow(self.labelButton)

    #
    # Paint Button
    #
    self.paintButton = qt.QPushButton("Paint")
    self.paintButton.toolTip = "Turn on paint."
    self.paintButton.enabled = True
    self.paintButton.checkable = True
    parametersLayout.addRow(self.paintButton)
    
    #
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersLayout.addRow(self.applyButton)

    # connections
    self.selectButton.connect('clicked(bool)', self.onSelectButton)
    self.paintButton.connect('clicked(bool)', self.onPaintButton)
    self.labelButton.connect('clicked(bool)', self.onLabelButton)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Creates and adds the custom Editor Widget to the module
    #self.localParEditorWidget = ParEditorWidget(parent=self.parent, showVolumesFrame=False)
    #self.localParEditorWidget.setup()
    #self.localParEditorWidget.enter()

    # Add vertical spacer
    self.layout.addStretch(1)

    # sets the layout to Red Slice Only
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)


  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode()
    self.masterNode = self.inputSelector.currentNode()

  def onSelectButton(self):
    logic = ParenchymaLogic()
    self.masterNode = self.inputSelector.currentNode()
    #print(self.inputSelector.currentNode())

  def onLabelButton(self):
    self.labelNode = self.logic.createLabelMap(self.inputSelector.currentNode())
    #print(self.labelNode)

  def onPaintButton(self):
    #interactor = slicer.qMRMLSliceView().interactorStyle().GetInteractor()
    #sw = slicer.qMRMLSliceWidget()
    #swi = sw.interactorStyle()
    #interactor = swi.GetInteractor()
    if self.paintMode:
      self.paintMode = False
      print("deleting paint")
      self.painter.cleanup()
      self.painter = None
      #self.paint.removeObs()
    else:
      self.paintMode = True
      layoutManager = slicer.app.layoutManager()
      viewWidget = layoutManager.sliceWidget('Red')
      sliceWidget = viewWidget.sliceView()
      interactor = sliceWidget.interactorStyle().GetInteractor()
      #self.paint = ParLib.Paint.Paint(interactor)

      # just in case?
      selectionNode = slicer.app.applicationLogic().GetSelectionNode()
      selectionNode.SetReferenceActiveVolumeID( self.masterNode.GetID() )
      if self.labelNode == None:
        self.labelNode = self.logic.createLabelMap(self.inputSelector.currentNode())
      selectionNode.SetReferenceActiveLabelVolumeID( self.labelNode.GetID() )
      slicer.app.applicationLogic().PropagateVolumeSelection(0)

      print("create paint (editor paint effect tool)")
      lm = slicer.app.layoutManager()
      paintEffect = EditorLib.PaintEffectOptions()
      paintEffect.setMRMLDefaults()
      paintEffect.__del__()
      sliceWidget = lm.sliceWidget('Red')
      self.painter = EditorLib.PaintEffectTool(sliceWidget)

  def onApplyButton(self):
    self.logic.run(self.masterNode, self.labelNode)
    

  

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

  def run(self,masterNode,labelNode):
    """
    Run the actual algorithm
    """
    self.delayDisplay('Running the algorithm')
    # check there is a label map
    self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(masterNode, labelNode))
    # TODO: do not run algorithm if there is no label map
    
    #
    # get the drawn mask
    #
    newArray = slicer.util.array(labelNode.GetID())
    newArray2 = slicer.util.array(masterNode.GetID())
    #pickle.dump( newArray, open( "/Users/louise/Documents/source/ParSeg/Parenchyma/Testing/save_labelNode.p", "wb"))
    #pickle.dump( newArray2, open( "/Users/louise/Documents/source/ParSeg/Parenchyma/Testing/save_masterNode.p", "wb"))
    
    self.delayDisplay(newArray.shape)
    self.delayDisplay(newArray2.shape)
    # TODO: compare dimensions to check they match
    
    # find the levels where there are annotations
    for i in range(0,newArray.shape[0]):
      if numpy.max(newArray[i,:,:]) > 0:
        print('in z:', i)
        # send the array of the one level
        array = newArray[i,:,:]            
        isinside = ParLib.Algorithms.segment(array)
        #print isinside
        # modify the label map to show what pixels are said to be inside the circle / mask
        for j in range(0,isinside.shape[0]):
          for k in range(0,isinside.shape[1]):
            if isinside[j,k] == 0:
              newArray[i,j,k] = 21
              #self.editPaint.paintPixel(j,k)

    labelNode.Modified()
    self.delayDisplay('Algorithm done')

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


#class ParEditorWidget(Editor.EditorWidget):
  """
  def createEditBox(self):
    
    self.editLabelMapsFrame.collapsed = False
    self.editBoxFrame = qt.QFrame(self.effectsToolsFrame)
    self.editBoxFrame.objectName = 'EditBoxFrame'
    self.editBoxFrame.setLayout(qt.QVBoxLayout())
    self.effectsToolsFrame.layout().addWidget(self.editBoxFrame)
    self.toolsBox = ParEditBox(self.editBoxFrame, optionsFrame=self.effectOptionsFrame)
    """
    
#class ParEditBox(EditorLib.EditBox):
  """
  # create the edit box
  def create(self):

    
    self.findEffects()

    self.mainFrame = qt.QFrame(self.parent)
    self.mainFrame.objectName = 'MainFrame'
    vbox = qt.QVBoxLayout()
    self.mainFrame.setLayout(vbox)
    self.parent.layout().addWidget(self.mainFrame)

    #
    # the buttons
    #
    self.rowFrames = []
    self.actions = {}
    self.buttons = {}
    self.icons = {}
    self.callbacks = {}

    # create all of the buttons
    # createButtonRow() ensures that only effects in self.effects are exposed,
    self.createButtonRow( ("PreviousCheckPoint", "NextCheckPoint",
                               "DefaultTool", "PaintEffect", "EraseLabel","ChangeIslandEffect"),
                              rowLabel="Undo/Redo/Default: " )

    extensions = []
    for k in slicer.modules.editorExtensions:
        extensions.append(k)
    self.createButtonRow( extensions )

    #
    # the labels
    #
    self.toolsActiveToolFrame = qt.QFrame(self.parent)
    self.toolsActiveToolFrame.setLayout(qt.QHBoxLayout())
    self.parent.layout().addWidget(self.toolsActiveToolFrame)
    self.toolsActiveTool = qt.QLabel(self.toolsActiveToolFrame)
    self.toolsActiveTool.setText( 'Active Tool:' )
    self.toolsActiveTool.setStyleSheet("background-color: rgb(232,230,235)")
    self.toolsActiveToolFrame.layout().addWidget(self.toolsActiveTool)
    self.toolsActiveToolName = qt.QLabel(self.toolsActiveToolFrame)
    self.toolsActiveToolName.setText( '' )
    self.toolsActiveToolName.setStyleSheet("background-color: rgb(232,230,235)")
    self.toolsActiveToolFrame.layout().addWidget(self.toolsActiveToolName)

    self.updateUndoRedoButtons()
    self._onParameterNodeModified(self.editUtil.getParameterNode())
    """
