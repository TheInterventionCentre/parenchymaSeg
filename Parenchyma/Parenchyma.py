import os
import unittest
from __main__ import vtk, qt, ctk, slicer
import EditorLib
import Editor
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
    # Apply Button
    #
    self.applyButton = qt.QPushButton("Apply")
    self.applyButton.toolTip = "Run the algorithm."
    self.applyButton.enabled = True
    parametersLayout.addRow(self.applyButton)

    # connections
    self.selectButton.connect('clicked(bool)', self.onSelectButton)
    self.labelButton.connect('clicked(bool)', self.onLabelButton)
    self.applyButton.connect('clicked(bool)', self.onApplyButton)
    self.inputSelector.connect("currentNodeChanged(vtkMRMLNode*)", self.onSelect)

    # Creates and adds the custom Editor Widget to the module
    self.localParEditorWidget = ParEditorWidget(parent=self.parent, showVolumesFrame=False)
    self.localParEditorWidget.setup()
    self.localParEditorWidget.enter()


    # Add vertical spacer
    self.layout.addStretch(1)

    # sets the layout to Red Slice Only
    layoutManager = slicer.app.layoutManager()
    layoutManager.setLayout(slicer.vtkMRMLLayoutNode.SlicerLayoutOneUpRedSliceView)


  def cleanup(self):
    pass

  def onSelect(self):
    self.applyButton.enabled = self.inputSelector.currentNode()

  def onSelectButton(self):
    logic = ParenchymaLogic()
    self.masterNode = self.inputSelector.currentNode()
    print(self.inputSelector.currentNode())

  def onLabelButton(self):
    logic = ParenchymaLogic()
    self.labelNode = logic.createLabelMap(self.inputSelector.currentNode())
    print(self.labelNode)

  def onApplyButton(self):
    logic = ParenchymaLogic()
    logic.run(self.masterNode, self.labelNode)


  

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
    self.delayDisplay('Running the aglorithm')
    # check there is a label map
    self.delayDisplay(slicer.modules.volumes.logic().CheckForLabelVolumeValidity(masterNode, labelNode))

    #
    # get the drawn mask
    #
    #self.delayDisplay(dir(labelNode))
    self.delayDisplay(type(labelNode))
    newArray = slicer.util.array(labelNode.GetID())
    self.delayDisplay(newArray)

    
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
    downloads = (
        ('http://slicer.kitware.com/midas3/download?items=5767', 'FA.nrrd', slicer.util.loadVolume),
        )

    for url,name,loader in downloads:
      filePath = slicer.app.temporaryPath + '/' + name
      if not os.path.exists(filePath) or os.stat(filePath).st_size == 0:
        print('Requesting download %s from %s...\n' % (name, url))
        urllib.urlretrieve(url, filePath)
      if loader:
        print('Loading %s...\n' % (name,))
        loader(filePath)
    self.delayDisplay('Finished with download and loading\n')

    volumeNode = slicer.util.getNode(pattern="FA")
    logic = ParenchymaLogic()
    self.assertTrue( logic.hasImageData(volumeNode) )
    self.delayDisplay('Test passed!')


class ParEditorWidget(Editor.EditorWidget):
  """
  def createEditBox(self):
    
    self.editLabelMapsFrame.collapsed = False
    self.editBoxFrame = qt.QFrame(self.effectsToolsFrame)
    self.editBoxFrame.objectName = 'EditBoxFrame'
    self.editBoxFrame.setLayout(qt.QVBoxLayout())
    self.effectsToolsFrame.layout().addWidget(self.editBoxFrame)
    self.toolsBox = ParEditBox(self.editBoxFrame, optionsFrame=self.effectOptionsFrame)
    """
    
class ParEditBox(EditorLib.EditBox):
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
