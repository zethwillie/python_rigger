import maya.cmds as cmds
import zbw_rig as rig
reload(rig)
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

	def setupArgs(self,*args):
		super(ArmUI, self).setupArgs()
		#add things here from UI for hand stuff

	def callLocatorsGo(self, *args):
		#now pass these values to the Limb class - create an instance of Limb
		self.arms = Arm(self.limbName, self.prefix, self.mirror, self.mirrorAxis, self.jointSuffix, self.controlSuffix, self.groupSuffix, self.spreadTwist, self.spreadTwistLow, self.stretchy, self.numSpreadJnts, self.locVals, self.jointList, self.noFlip, self.mainAxis, self.secondaryAxis, self.straightLimb, self.mirrorName, self.posNeg)

		#do I need to add stuff here for hand? or can I just deal with it below in the hand class

		#now create locators
		self.arms.createLocators()

	def createLimb(self, *args):
		self.arms.createJoints()

class Arm(Limb):
	def __init__(self, limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg):
		super(Arm, self).__init__(limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg)
		print("got the super: %s, %s"%(limbName, prefix))
		print("and added some stuff to the init (hence this messgae)")

	# def setupIK(self, x, IKHandle):
		#pass





#create hand (big job!) separate class? Get variables here for myself (don't do them above?)

#locs in basic hand shape (query how many fingers)

#create joint structure for basic hand shape (create such that "cup" attr works correctly)

#create finger joints

#for finger rig, use multiple groups (one for adjustments, one for stretch(?), one for sdks, one for attr controls and one master for placement (all above the controls))

#finger stretch? or just use the FK controls to move things (parent constrain to the controls, not orient) 
#if I do that then I can also use a "stretch" attr that moves the controls(!) not the joints

#leave a place for IK finger controls. . . 

#finally, hook the hand into the bind rig wrist control





