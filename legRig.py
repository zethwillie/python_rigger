import maya.cmds as cmds
import zbw_rig as rig
from baseLimb import LimbUI
from baseLimb import Limb

#----------add in offsets for feet joints for FK2IK matching


class LegUI(LimbUI):

	def __init__(self):

		super(LegUI,self).__init__()

		self.widgets = {}

		self.defaultLimbName = "leg"
		self.defaultJointList = ["thigh", "knee", "ankle", "ball", "legEnd"]
		self.defaultLocValues = [[3,6,0], [3,3,1], [3,1, 0], [3, 0, 2], [3, 0, 3]]

		self.buildUI()

	def buildUI(self):

		win = cmds.window("legWin", exists=True)
		if win:
			cmds.deleteUI("legWin")

		self.widgets["mainWindow"] = cmds.window("legWin", title="Leg Rig Creation Window", w=320,h=600)
		self.widgets["scrollLayout"] = cmds.scrollLayout(vst=20)

		self.widgets["mainColumn"] = cmds.columnLayout(w=300,h=600)

		self.commonLimbUI()

		self.customLimbUI()

		self.buttonUI()

		cmds.showWindow(self.widgets["mainWindow"])

	def customLimbUI(self):
		# cmds.setParent(self.widgets["mainColumn"])
		self.widgets["customFrame"] = cmds.frameLayout(l="3. Custom Limb Attributes", w=320, bgc=(0,0,0), p=self.widgets["mainColumn"])
		cmds.text("custom arms stuff here, like reverseFoot, etc")

	def callLocatorsGo(self, *args):
		#now pass these values to the Limb class - create an instance of Limb
		self.legs = Leg(self.limbName, self.prefix, self.mirror, self.mirrorAxis, self.jointSuffix, self.controlSuffix, self.groupSuffix, self.spreadTwist, self.spreadTwistLow, self.stretchy, self.numSpreadJnts, self.locVals, self.jointList, self.noFlip, self.mainAxis, self.secondaryAxis, self.straightLimb, self.mirrorName, self.posNeg)

		#do I need to add stuff here for hand? or can I just deal with it below in the hand class

		#now create locators
		self.legs.createLocators()

	def createLimb(self, *args):
		self.legs.createJoints()


class Leg(Limb):
	def __init__(self, limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg):
		super(Leg, self).__init__(limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg)
		print("got the super: %s, %s"%(limbName, prefix))
		print("and added some stuff to the init (hence this messgae)")

	def  setupIK(self, x):
		"""sets up the IK portion of the limb rig"""

		#set values for this chain, side
		thisChain = self.IKChains[x]
		side = self.prefixList[x]
		thisBind = self.bindChains[x]

		#create ik control from joint 0 to 2
		mainIK = "%s_%s_IK"%(side, self.limbName)
		IKHandle = cmds.ikHandle(n=mainIK, sj=thisChain[0], ee=thisChain[2], sol="ikRPsolver")[0]
		self.IKHandles.append(IKHandle)

		#create a control for the ik
		IKCtrl = self.setupIKCtrl(x, IKHandle)

		#call pole vector method? - pass IK name, normal or no flip
#-----------------get argument from UI about what kind of handles
		thisPv = self.setupPV(IKHandle, "normal", x)

		#create stretchy bits
		cmds.addAttr(IKCtrl, ln="__EXTRA__", nn="__EXTRA__", at="short", k=True)
		cmds.setAttr("%s.__EXTRA__"%IKCtrl, l=True)
		cmds.addAttr(IKCtrl, ln="autoStretch", at="float", min=0, max=1, k=True)
		cmds.addAttr(IKCtrl, ln="scaleMin", at="float", min=0.5, max=3, k=True, dv=1)
		#add "upScale" and "lowScale" (.5-3)
		cmds.addAttr(IKCtrl, ln="upScale", at="float", min=0.3, max=3, k=True, dv=1.0)
		cmds.addAttr(IKCtrl, ln="lowScale", at="float", min=0.3, max=3, k=True, dv=1.0)

		#from measure, get final add node
		add = self.measureAdds[x]

		#orient the IK wrist to the control? do it here or elsewhere (for inheritance?)
		cmds.orientConstraint(IKCtrl, thisChain[2], mo=True)

		#create distance node from thigh to ctrl
		distance = rig.measureDistance("%s_%s_ikCtrlDistance"%(side, self.limbName), self.measureChains[x][0], IKCtrl)

		ratioMult, defaultMult, defaultBlend, conditional, upScaleMult, loScaleMult = rig.scaleStretchIK(("%s_%s"%(side, self.limbName)), thisChain[0], thisChain[1], thisChain[2], "%s.output"%add, "%s.distance"%distance, IKCtrl, self.jAxis1)

		#create the ik switch (call as "diamond")
		ikSwitchName = "%s_%s_FKIKSwitch"%(side, self.limbName)
		if x == 0:
			thisIKSwitch = rig.createControl(ikSwitchName, "diamond", self.jAxis1, "lightBlue")
		if x == 1:
			thisIKSwitch = rig.createControl(ikSwitchName, "diamond", self.jAxis1, "pink")
		rig.stripTransforms(thisIKSwitch)
		cmds.addAttr(thisIKSwitch, ln="FKIK", k=True, at="float", min=0, max=1, dv=0)
		#create reverse
		thisIKSwitchRev = cmds.shadingNode("reverse", asUtility=True, n="%s_%s_IKSwtchReverse"%(side, self.limbName))
		cmds.connectAttr("%s.FKIK"%thisIKSwitch, "%s.inputX"%thisIKSwitchRev)
		rig.groupOrient(thisBind[2], thisIKSwitch, self.groupSuffix)
		IKSwitchGrp = cmds.listRelatives(thisIKSwitch, p=True)

		#do stuff here to push the IKFK switch in the right direction
		if x== 0:
			offset = -3
		if x==1:
			offset = 3
		cmds.xform(IKSwitchGrp, os=True, r=True, t=(0, 0, offset))
		self.IKSwitches.append(thisIKSwitch)
		self.IKSwitchesRev.append(thisIKSwitchRev)

		#set up visibility switching from this for IK and PV controls
		#get pv parent group
		pvGroup = cmds.listRelatives(thisPv, p=True)[0]
		ikCtrlGroup = cmds.listRelatives(IKCtrl, p=True)[0]
		cmds.connectAttr("%s.FKIK"%thisIKSwitch, "%s.v"%pvGroup)
		cmds.connectAttr("%s.FKIK"%thisIKSwitch, "%s.v"%ikCtrlGroup)

		#pass onto the FK part of the rig
		self.setupFK(x)
	def setupIKCtrl(self, x, IKHandle):

		############# MODIFY FOR INHERITANCE  #############
		side = self.prefixList[x]
		thisChain = self.IKChains[x]

		#create a control for the ik
		name = "%s_%s_IK_CTRL"%(side, self.limbName)
		if x==0:
			IKCtrl = rig.createControl(name, "cube", self.jAxis1, "blue")
		if x==1:
			IKCtrl = rig.createControl(name, "cube", self.jAxis1, "red")
		self.IKCtrls.append(IKCtrl)
		#strip to rotate and translate
		rig.stripToRotateTranslate(IKCtrl)

		#G.O. control
		group = rig.groupOrient(thisChain[2], IKCtrl, self.groupSuffix)
		##########
		cmds.setAttr("%s.rotateX"%group, (0))
		cmds.setAttr("%s.rotateY"%group, (0))
		cmds.setAttr("%s.rotateZ"%group, (0))

		#orient constraint joint 2 (wrist ankle) to control
		##########
		# cmds.orientConstraint(IKCtrl, thisChain[2], mo=True)

		#parent ik handle to control
		cmds.parent(IKHandle, IKCtrl)

		return IKCtrl