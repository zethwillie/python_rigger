import maya.cmds as cmds
import zbw_rig as rig
from baseLimb import LimbUI
from baseLimb import Limb

class ArmUI(LimbUI):

	def __init__(self):

		#super(ArmUI,self).__init__()

		self.widgets = {}

		self.defaultLimbName = "arm"
		self.defaultJointList = ["shoulder", "elbow", "wrist", "armEnd"]
		self.defaultLocValues = [[5,10,0], [10,10,0], [15,10, 0], [17, 10, 0]]

		self.buildUI()

	def buildUI(self):

		win = cmds.window("armWin", exists=True)
		if win:
			cmds.deleteUI("armWin")

		self.widgets["mainWindow"] = cmds.window("armWin", title="Arm Rig Creation Window", w=320,h=600)
		self.widgets["scrollLayout"] = cmds.scrollLayout(vst=20)

		self.widgets["mainColumn"] = cmds.columnLayout(w=300,h=600)

		self.commonLimbUI()

		self.customLimbUI()

		self.buttonUI()

		cmds.showWindow(self.widgets["mainWindow"])

	def customLimbUI(self):
		# cmds.setParent(self.widgets["mainColumn"])
		self.widgets["customFrame"] = cmds.frameLayout(l="3. Custom Limb Attributes", w=320, bgc=(0,0,0), p=self.widgets["mainColumn"])
		cmds.text("custom arms stuff here, like hand, etc")

	def callLocators(self,*args):
		#set up the variables to pass to the LimbClass?
		self.limbName = cmds.textFieldGrp(self.widgets["limbNameTFG"], q=True, tx=True) #string
		self.prefixRaw = cmds.radioButtonGrp(self.widgets["prefixRBG"], q=True, sl=True ) #string
		if self.prefixRaw == 1:
			self.prefix = ""
		elif self.prefixRaw == 2:
			self.prefix = "lf"
		elif self.prefixRaw == 3:
			self.prefix = "rt"
		elif self.prefixRaw == 4:
			self.prefix = cmds.textFieldGrp(self.widgets["otherPrefixTFG"], q=True, tx=True)
		self.mirror = cmds.checkBox(self.widgets["mirrorCB"],q=True, v=True)#bool
		self.mirrorAxisRaw = cmds.radioButtonGrp(self.widgets["axisRBG"], q=True, sl=True)#string
		if self.mirrorAxisRaw == 1:
			self.mirrorAxis = "yz"
		elif self.mirrorAxisRaw ==2:
			self.mirrorAxis = "xz"
		elif self.mirrorAxisRaw ==3:
			self.mirrorAxis = "xy"
		self.jointSuffix = cmds.textFieldGrp(self.widgets["jntSuffixTFG"], q=True, tx=True) #string
		self.controlSuffix = cmds.textFieldGrp(self.widgets["ctrlSuffixTFG"], q=True, tx=True) #string
		self.groupSuffix = cmds.textFieldGrp(self.widgets["groupSuffixTFG"], q=True, tx=True) #string
		self.spreadTwist = cmds.checkBoxGrp(self.widgets["jointOptionsCBG"], q=True, v1=True)#bool
		self.spreadTwistLow = cmds.checkBoxGrp(self.widgets["jointOptionsCBG"], q=True, v3=True)#bool
		self.stretchy = cmds.checkBoxGrp(self.widgets["jointOptionsCBG"], q=True, v2=True) #bool
		self.numSpreadJnts = cmds.intFieldGrp(self.widgets["numSpreadIFG"], q=True, v=True) #int
		self.locVals = self.defaultLocValues
		self.jointList = self.defaultJointList
		self.noFlip = cmds.checkBox(self.widgets["noFlipCB"], q=True, v=True )
		self.mainAxis = cmds.radioButtonGrp(self.widgets["jntMainAxisRBG"], q=True, sl=True)
		self.secondaryAxis = cmds.radioButtonGrp(self.widgets["jntSecondAxisRBG"], q=True, sl=True)
		self.straightLimb = cmds.checkBox(self.widgets["straightLimbCB"], q=True, v=True)
		self.mirrorName = cmds.textFieldGrp(self.widgets["otherMirrorTFG"], q=True, tx=True)
		self.posNeg = cmds.radioButtonGrp(self.widgets["jntSecondAxisDirRBG"], q=True, sl=True)

######### pull the below bit out into separate function in baseLimb to just override that????

		#now pass these values to the Limb class - create an instance of Limb
		self.arms = Arm(self.limbName, self.prefix, self.mirror, self.mirrorAxis, self.jointSuffix, self.controlSuffix, self.groupSuffix, self.spreadTwist, self.spreadTwistLow, self.stretchy, self.numSpreadJnts, self.locVals, self.jointList, self.noFlip, self.mainAxis, self.secondaryAxis, self.straightLimb, self.mirrorName, self.posNeg)

		#now create locators
		self.arms.createLocators()

	def createLimb(self, *args):
		self.arms.createJoints()

class Arm(Limb):
	def __init__(self, limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg):
		super(Arm, self).__init__(limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg)
		print("got the super: %s, %s"%(limbName, prefix))
		print("and added some stuff to the init (hence this messgae)")

	# def setupIK(self, x):
		#pull out the bits from teh main main IK code into methods that create the control and do shit to it. This way I can just overwrite that bit

	#create hand (big job!)



