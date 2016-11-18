"""
Import PYSIDE modules to work with
"""
from PySide import QtCore
from PySide import QtGui
import numpy

class BakeAnimation(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
#FETCH TIMELINE VARIABLES AUTOMATICALLY ON INIT.
#Also here I create the lists that will be used for frames to 
#keyframe and frames to remove keyframes from.
#The axis tuple is declared, which includes all transforms.

        frameRange = hou.playbar.playbackRange
        self.firstFrame = int(frameRange()[0])
        self.lastFrame = int(frameRange()[1])
        self.framesToKey = [self.firstFrame,self.lastFrame]
        self.framesToClean = [self.firstFrame,self.lastFrame]
        self.axis=('tx','ty','tz','rx','ry','rz')     

#GET SELECTED NODES AND ASSIGN THEM TO VARIABLES.
#Here I should handle also an error message in case not enough nodes are selected.
#The if loop checks how many nodes are selected and passes them to variables accordingly.

        self.nodes = hou.selectedNodes()
        self.selected = len(self.nodes)
        
        if self.selected < 2:
            self.geoAnim=self.nodes[0]
            self.geoBake=self.nodes[0]
        
        elif self.selected == 2:
            self.geoAnim=self.nodes[0]
            self.geoBake=self.nodes[1]

        elif self.selected > 2:
                self.dn={}
                for node in range(self.selected-1):
                        self.dn['geoAnim{0}'.format(node)]=self.nodes[node]
                self.geoBake=self.nodes[-1]
                print self.dn
                print self.geoBake
            
# BUILD INTERFACE NODES AND ASSIGN THEM TO VARIABLES
    
        """
        Create Layout for the interface inside a Grid.
        Here I create all the different fields for the QT interface.
        """
        layout = QtGui.QGridLayout()        

        self.setGeometry(500, 300, 250, 110)
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
        
        self.buttonBake = QtGui.QPushButton('-Bake Animation-')
        self.buttonBake.setToolTip('Please Select one or two nodes.\nFirst Select the node with transforms.')
        self.buttonBake.setFocusPolicy(QtCore.Qt.NoFocus)
        
        
        layout.addWidget(lFirstF,1,1)        
        layout.addWidget(self.firstF,1,2)
        
        layout.addWidget(lLastF,2,1)        
        layout.addWidget(self.lastF,2,2)
        
        layout.addWidget(lPreRoll,3,1)        
        layout.addWidget(self.preRoll,3,2)
        
        layout.addWidget(lPostRoll,4,1)        
        layout.addWidget(self.postRoll,4,2)
        
        layout.addWidget(lStep,5,1)
        layout.addWidget(self.step,5,2)
        
        layout.addWidget(self.lDropDown,6,1)
        layout.addWidget(self.dropDown,6,2)
        
        layout.addWidget(self.buttonBake,7,1,1,2)
        
        self.setLayout(layout)

        """
        Make all the connections of the different fields and buttons.
        """
        self.firstF.textChanged.connect(self.frameRanges)
        self.lastF.textChanged.connect(self.frameRanges)
        self.preRoll.textChanged.connect(self.frameRanges)
        self.postRoll.textChanged.connect(self.frameRanges)
        self.step.textChanged.connect(self.frameRanges)

        if self.selected <=2:
            self.buttonBake.clicked.connect(self.bakeAnim)
        elif self.selected >2:
            self.buttonBake.clicked.connect(self.bakeAnimMulti)
        
        """
        Initialize the Functions needed on spawn.
        """
        self.frameRanges()

    """
    Frame Ranges function.
    This function queries frame ranges and populates the framesToKey and toClean lists
    """    
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

    """
    Bake animation functions.
    These are the baking functions at the core of the tool.
    There are two that account for either the baking of only one or more tranforms.
    THis is achieve by moving frame by frame and matching the world transform and setting the keyframe.
    """  
    def bakeAnim(self):
        for i in self.framesToClean:
            for ax in self.axis:
                self.geoBake.parm(ax).deleteAllKeyframes()
    
        for i in self.framesToKey:
            hou.setFrame(i)
            setKey = hou.Keyframe()
            setKey.setFrame(i)
        
            xform = self.geoAnim.worldtransform()
            self.geoBake.setWorldtransform(xform)
            
            for ax in self.axis:
                
                anim = self.geoBake.parm(ax).eval()
                setKey.setValue(anim)
                setKey.setExpression(self.dropDown.currentText()+'()')
                self.geoBake.parm(ax).setKeyframe(setKey)
                setKey.setInSlopeAuto(1)
                setKey.setSlopeAuto(1)

    def bakeAnimMulti(self):
        for i in self.framesToClean:
            for ax in self.axis:
                self.geoBake.parm(ax).deleteAllKeyframes()
    
        for i in self.framesToKey:
            hou.setFrame(i)
            setKey = hou.Keyframe()
            setKey.setFrame(i)

            dx={}
            
            for node in self.dn:
                dx['xform{0}'.format(node)]=self.dn[node].worldTransform()
                
            getMatrices = [ v for v in dx.values() ]

            print getMatrices

            XM = [M.explode(transform_order='srt', rotate_order='xyz', pivot=hou.Vector3()) for M in getMatrices]

            print XM
            
            tra = hou.Vector3(numpy.sum([d['translate'] for d in XM],axis=0)*(1/float((self.selected-1))))
            rot = hou.Vector3(numpy.sum([d['rotate'] for d in XM],axis=0)*(1/float((self.selected-1))))
            sca = hou.Vector3(numpy.sum([d['scale'] for d in XM],axis=0)*(1/float((self.selected-1))))

            NM = {'translate':tra,'rotate':rot,'scale':sca}

            xform=hou.hmath.buildTransform(NM)

            print xform


            # hou.node('/obj/torusTest').setWorldtransform(xform)


            # self.geoBake.setWorldtransform(xform)
            
            # for ax in self.axis:
            #     anim = self.geoBake.parm(ax).eval()
            #     setKey.setValue(anim)
            #     setKey.setExpression(self.dropDown.currentText()+'()')
            #     self.geoBake.parm(ax).setKeyframe(setKey)
            #     setKey.setInSlopeAuto(1)
            #     setKey.setSlopeAuto(1)


dialog = BakeAnimation()
dialog.show()
