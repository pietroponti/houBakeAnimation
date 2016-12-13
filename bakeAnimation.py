"""
Import PYSIDE modules to work with
"""
from PySide import QtCore
from PySide import QtGui
import numpy

class BakeAnimation(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent, QtCore.Qt.WindowStaysOnTopHint)

# FETCH TIMELINE VARIABLES AUTOMATICALLY ON INIT.
# Here I create the lists that will be used for frames to 
# keyframe and frames to remove keyframes from.
# The axis list is declared, which includes all transforms as default.

        frameRange = hou.playbar.playbackRange
        self.firstFrame = int(frameRange()[0])
        self.lastFrame = int(frameRange()[1])
        self.framesToKey = [self.firstFrame,self.lastFrame]
        self.framesToClean = [self.firstFrame,self.lastFrame]
        self.axis=['tx','ty','tz','rx','ry','rz','sx','sy','sz']


# GET SELECTED NODES AND ASSIGN THEM TO VARIABLES.
# Here I should handle also an error message in case not enough nodes are selected.
# The if loop checks how many nodes are selected and passes them to variables accordingly.
# geoAnim are the nodes from which to inherit transforms.
# geoBake is the last selected node and the one where the transforms will be baked to.
        
        self.nodes = hou.selectedNodes()
        self.selected = len(self.nodes)
        
        if self.selected < 2:
            self.geoAnim=self.nodes[0]
            self.geoBake=self.nodes[0]
        
        elif self.selected == 2:
            self.geoAnim=self.nodes[0]
            self.geoBake=self.nodes[1]

        elif self.selected > 2:
                self.dGeoAnim={}
                for node in range(self.selected-1):
                        self.dGeoAnim['geoAnim{0}'.format(node)]=self.nodes[node]
                self.geoBake=self.nodes[-1]
                print self.dGeoAnim
                print self.geoBake


# BUILD INTERFACE NODES AND ASSIGN THEM TO VARIABLES



        # Create Layout for the interface inside a Grid.
        # Here I create all the different fields for the QT interface.

        layout = QtGui.QGridLayout()        

        self.setFixedSize(500,200)
        self.setWindowTitle('Bake Animation')
        
        lFirstF = QtGui.QLabel('First Frame')
        lFirstF.setAlignment(QtCore.Qt.AlignRight)
        self.firstF = QtGui.QLineEdit(str(self.firstFrame))
        
        lLastF = QtGui.QLabel('Last Frame')
        lLastF.setAlignment(QtCore.Qt.AlignRight)
        self.lastF = QtGui.QLineEdit(str(self.lastFrame))
        
        lPreRoll = QtGui.QLabel('Pre Roll')
        lPreRoll.setAlignment(QtCore.Qt.AlignRight)
        self.preRoll = QtGui.QLineEdit('0')
        
        lPostRoll = QtGui.QLabel('Post Roll')
        lPostRoll.setAlignment(QtCore.Qt.AlignRight)
        self.postRoll = QtGui.QLineEdit('0')
        
        lStep = QtGui.QLabel('Step')
        lStep.setAlignment(QtCore.Qt.AlignRight)
        self.step = QtGui.QLineEdit('1')
        
        
        self.lDropDown = QtGui.QLabel('Interpolation')
        self.lDropDown.setAlignment(QtCore.Qt.AlignRight)
        self.dropDown = QtGui.QComboBox()
        self.dropDown.addItems(['bezier','spline','linear','constant'])

        self.checkTra = QtGui.QCheckBox('Translate')
        self.checkTra.setChecked(True)

        self.checkRot = QtGui.QCheckBox('Rotate')
        self.checkRot.setChecked(True)

        self.checkSca = QtGui.QCheckBox('Scale')
        self.checkSca.setChecked(True)
        
        self.buttonBake = QtGui.QPushButton('-Bake Anim-')
        self.buttonBake.setToolTip('Please Select one or two nodes.\nFirst Select the node with transforms.')
        self.buttonBake.setFocusPolicy(QtCore.Qt.NoFocus)
        self.buttonBake.setStyleSheet("QPushButton { background-color:#FFFFFF; border-style:outset; border-width:2px; border-radius:5px; border-color:#222222; padding:4px}"
                                      "QPushButton:pressed { background-color:#999999 }")
        
        
        layout.addWidget(lFirstF,0,1)
        layout.addWidget(self.firstF,0,2)
        
        layout.addWidget(lLastF,1,1)
        layout.addWidget(self.lastF,1,2)
        
        layout.addWidget(lPreRoll,2,1)
        layout.addWidget(self.preRoll,2,2)
        
        layout.addWidget(lPostRoll,3,1)
        layout.addWidget(self.postRoll,3,2)
        
        layout.addWidget(lStep,4,1)
        layout.addWidget(self.step,4,2)
        
        layout.addWidget(self.lDropDown,5,1)
        layout.addWidget(self.dropDown,5,2)
        
        layout.addWidget(self.checkTra,0,3)
        layout.addWidget(self.checkRot,0,4)
        layout.addWidget(self.checkSca,0,5)
        
        layout.addWidget(self.buttonBake,5,6)
        
        layout.setSpacing(10)
        
        self.setLayout(layout)

        
        # Make all the connections of the different fields and buttons.
        # Everytime any change is made in a frame related field, the frameRanges function is re-run.
        
        self.firstF.textChanged.connect(self.frameRanges)
        self.lastF.textChanged.connect(self.frameRanges)
        self.preRoll.textChanged.connect(self.frameRanges)
        self.postRoll.textChanged.connect(self.frameRanges)
        self.step.textChanged.connect(self.frameRanges)

        if self.selected <=2:
            self.buttonBake.clicked.connect(self.bakeAnim)
        elif self.selected >2:
            self.buttonBake.clicked.connect(self.bakeAnimMulti)
        
        
        # Initialize the Functions needed on spawn.

        self.frameRanges()



# DECLARE FUNCTIONS FOR THE TOOL


    # Frame Ranges function.
    # This function queries frame ranges and populates the framesToKey and framesToClean lists
   
    def frameRanges(self):
        self.firstFrame = int(self.firstF.text())
        self.lastFrame = int(self.lastF.text())
        self.framesToKey = [self.firstFrame,self.lastFrame]
        self.framesToClean = [self.firstFrame,self.lastFrame]
        
        for i in range (int(self.firstF.text())
                        -int(self.preRoll.text()),
                        int(self.lastF.text())
                        +int(self.postRoll.text()),
                        int(self.step.text())
                        ):
            self.framesToKey.append(i)
        for i in range (int(self.firstF.text())
                        -int(self.preRoll.text()),
                        int(self.lastF.text())
                        +int(self.postRoll.text())
                        ):
            self.framesToClean.append(i)
        
        list(set(self.framesToClean))
        list(set(self.framesToKey))
        
        print self.framesToClean
        print self.framesToKey

    
    # Bake animation functions.
    # These are the baking functions at the core of the tool.
    # There are two that account for either the baking of only one or more tranforms.
    # This is achieve by moving frame by frame and matching the world transform and setting the keyframe.
    
    def bakeAnim(self):
        for i in self.framesToClean:
            for ax in self.axis:
                self.geoBake.parm(ax).deleteAllKeyframes()
    
        for i in self.framesToKey:
            hou.setFrame(i)
            setKey = hou.Keyframe()
            setKey.setFrame(i)
        
            xform = self.geoAnim.worldTransform()
            self.geoBake.setWorldTransform(xform)
            
            for ax in self.axis:
                
                anim = self.geoBake.parm(ax).eval()
                setKey.setValue(anim)
                setKey.setExpression(self.dropDown.currentText()+'()')
                self.geoBake.parm(ax).setKeyframe(setKey)
                setKey.setInSlopeAuto(1)
                setKey.setSlopeAuto(1)

    def bakeAnimMulti(self):
        # For each frame in the list self.framesToClean,
        # go through each axis of the geo to bake and remove keyframes.
        for i in self.framesToClean:
            for ax in self.axis:
                self.geoBake.parm(ax).deleteAllKeyframes()

        # Reset the self.axis list to empty.
        # Check which transforms are checked on the interface.
        # For the ones active, append the x, y and z axis to the list
        self.axis = []

        if self.checkTra.isChecked() == True:
            self.axis.extend(['tx','ty','tz'])
        if self.checkRot.isChecked() == True:
            self.axis.extend(['rx','ry','rz'])
        if self.checkSca.isChecked() == True:
            self.axis.extend(['sx','sy','sz'])

        # For each frame in the framesToKey list a few operations are run.

        for i in self.framesToKey:
            hou.setFrame(i)
            setKey = hou.Keyframe()
            setKey.setFrame(i)

            dWorldTransforms={}
            
            for node in self.dGeoAnim:
                dWorldTransforms['xform{0}'.format(node)]=self.dGeoAnim[node].worldTransform()
                
            getMatrices = [ v for v in dWorldTransforms.values() ]

            XM = [M.explode(transform_order='srt', rotate_order='xyz', pivot=hou.Vector3()) for M in getMatrices]
            
            tra = hou.Vector3(numpy.sum([d['translate'] for d in XM],axis=0)*(1/float((self.selected-1))))
            rot = hou.Vector3(numpy.sum([d['rotate'] for d in XM],axis=0)*(1/float((self.selected-1))))
            sca = hou.Vector3(numpy.sum([d['scale'] for d in XM],axis=0)*(1/float((self.selected-1))))

            NM={}
            
            if self.checkTra.isChecked() == True:
                NM['translate']=tra
            if self.checkRot.isChecked() == True:
                NM['rotate']=rot  
            if self.checkSca.isChecked() == True:
                NM['scale']=sca
                
                
                
            xform=hou.hmath.buildTransform(NM)

            self.geoBake.setWorldTransform(xform)
            

            for ax in self.axis:
                anim = self.geoBake.parm(ax).eval()
                setKey.setValue(anim)
                setKey.setExpression(self.dropDown.currentText()+'()')
                self.geoBake.parm(ax).setKeyframe(setKey)
                setKey.setInSlopeAuto(1)
                setKey.setSlopeAuto(1)


dialog = BakeAnimation()
dialog.show()
