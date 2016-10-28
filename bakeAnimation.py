from PySide import QtCore
from PySide import QtGui

class BakeAnimation(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        
# FETCH TIMELINE VARIABLES AUTOMATICALLY ON INIT        
        frameRange = hou.playbar.playbackRange
        self.firstFrame = int(frameRange()[0])
        self.lastFrame = int(frameRange()[1])
        self.framesToKey = [self.firstFrame,self.lastFrame]
        self.framesToClean = [self.firstFrame,self.lastFrame]
        self.axis=('tx','ty','tz','rx','ry','rz')     
        
# GET SELECTED NODES AND ASSIGN THEM TO VARIABLES
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
                        self.dn['self.geoAnim{0}'.format(node)]=self.nodes[node]
                self.geoBake=self.nodes[-1]
                print self.dn
                print self.geoBake
            
# BUILD INTERFACE NODES AND ASSIGN THEM TO VARIABLES
    # CREATE NESTED LAYOUTS OF GRID INSIDE A VBOX
    
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
        self.preRoll = QtGui.QLineEdit('3')
        
        lPostRoll = QtGui.QLabel('Post Roll')
        lPostRoll.setAlignment(QtCore.Qt.AlignRight)
        self.postRoll = QtGui.QLineEdit('3')
        
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

        
        self.firstF.textChanged.connect(self.frameRanges)
        self.lastF.textChanged.connect(self.frameRanges)
        self.preRoll.textChanged.connect(self.frameRanges)
        self.postRoll.textChanged.connect(self.frameRanges)
        self.step.textChanged.connect(self.frameRanges)

        if self.selected <=2:
            self.buttonBake.clicked.connect(self.bakeAnim)
        elif self.selected >2:
            self.buttonBake.clicked.connect(self.test)
        
        self.frameRanges()
        
    def frameRanges(self):
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

    def test(self):
        dx={}
        print self.dn
        for node in range(self.selected-1):
            dx['xform{0}'.format(node)]=self.dn[node].worldTransform()
        print dx


    # def bakeAnimMulti(self):
    #     for i in self.framesToClean:
    #         for ax in self.axis:
    #             self.geoBake.parm(ax).deleteAllKeyframes()
    
    #     for i in self.framesToKey:
    #         hou.setFrame(i)
    #         setKey = hou.Keyframe()
    #         setKey.setFrame(i)

    #         dx={}
    #         for node in range(self.selected-1):
    #             dx['xform{0}'.format(node)]=self.dn{0}.worldTransform()

    #         # xform = self.geoAnim.worldTransform()
    #         self.geoBake.setWorldTransform(xform)
            
    #         for ax in self.axis:
                
    #             anim = self.geoBake.parm(ax).eval()
    #             setKey.setValue(anim)
    #             setKey.setExpression(self.dropDown.currentText()+'()')
    #             self.geoBake.parm(ax).setKeyframe(setKey)
    #             setKey.setInSlopeAuto(1)
    #             setKey.setSlopeAuto(1)

dialog = BakeAnimation()
dialog.show()
