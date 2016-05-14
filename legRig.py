import maya.cmds as cmds
import zbw_rig as rig
from baseLimb import LimbUI
from baseLimb import Limb
import maya.OpenMaya as om

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
		cmds.addAttr(IKCtrl, ln="__IKFOOT__", nn="__EXTRA__", at="short", k=True)
		cmds.setAttr("%s.__IKFOOT__"%IKCtrl, l=True)
		cmds.addAttr(IKCtrl, ln="ballRoll", at="float", k=True, dv=0)
		cmds.addAttr(IKCtrl, ln="toeRoll", at="float", k=True, dv=0)
		cmds.addAttr(IKCtrl, ln="heelRoll", at="float", k=True, dv=0)
		cmds.addAttr(IKCtrl, ln="toePivot", at="float", k=True, dv=0)
		cmds.addAttr(IKCtrl, ln="heelPivot", at="float", k=True, dv=0)
		cmds.addAttr(IKCtrl, ln="toeFlap", at="float", k=True, dv=0)

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

	def setupPV(self, IKHandle, type, x):
		"""type can be "normal" (a control) or "noFlip" with hidden control and twist attribute. add to self.PVList """
		#set values for this chain, side
		thisChain = self.IKChains[x]
		side = self.prefixList[x]

		pv = "%s_%s_PV"%(side, self.limbName)

		if type == "normal":
			if x==0:
				thisPV = rig.createControl(pv, "sphere", self.jAxis1, "darkBlue")
			if x==1:
				thisPV = rig.createControl(pv, "sphere", self.jAxis1, "darkRed")
			thisGrp = cmds.group(pv, n="%s_%s"%(pv,self.groupSuffix))

			#get pos of joints 0 and 2 to position pv group
			topPosRaw = cmds.xform(thisChain[0], ws=True, q=True, t=True)
			topPos = om.MVector(topPosRaw[0], topPosRaw[1], topPosRaw[2])
			lowPosRaw = cmds.xform(thisChain[2], ws=True, q=True, t=True)
			lowPos = om.MVector(lowPosRaw[0], lowPosRaw[1], lowPosRaw[2])

			midPos = (topPos + lowPos)/2

			cmds.xform(thisGrp, ws=True, t=(midPos.x, midPos.y, midPos.z))

			aim = cmds.aimConstraint(thisChain[1], thisGrp, aim=(0,0,-1))
			cmds.delete(aim)

			cmds.xform(thisGrp, os=True, r=True, t=(0, 0, -10))

			#strip control to translate
			rig.stripToTranslate(thisPV)

#-----------capture all constraints as list?
			#hook up pv
			cmds.poleVectorConstraint(thisPV, IKHandle)

			#add pv to list
			self.PVList.append(thisPV)

			#return pv
			return(thisPV)
		cmds.addAttr(thisPV, ln="follow", at="enum", en="world:foot")

		if type == "noFlip":
			pass
		pass


	def setupBind(self, x):
		thisChain = self.bindChains[x]
		thisIK = self.IKChains[x]
		thisFK = self.FKChains[x]
		thisSwitch = self.IKSwitches[x]
		side = self.prefixList[x]
		sideRotBlendList = []
		sideScaleBlendList = []

		upScaleBlend = rig.blendScale("%s_%s_upScaleBlend"%(side,self.limbName), thisIK[0], thisFK[0], thisChain[0], "%s.FKIK"%thisSwitch)
		lowScaleBlend = rig.blendScale("%s_%s_lowScaleBlend"%(side,self.limbName), thisIK[1], thisFK[1], thisChain[1], "%s.FKIK"%thisSwitch)

		if self.spreadTwist:
			cmds.disconnectAttr("%s.output"%upScaleBlend, "%s.scale"%thisChain[0])
			cmds.disconnectAttr("%s.output"%lowScaleBlend, "%s.scale"%thisChain[1])

		#store these blends
		sideScaleBlendList.append(upScaleBlend)
		sideScaleBlendList.append(lowScaleBlend)

		self.scaleBlendList.append(sideScaleBlendList)

		if self.jAxis1 == "x":
			colorAxis = "R"
		elif self.jAxis1 == "y":
			colorAxis = "G"
		elif self.jAxis1 == "z":
			colorAxis = "B"

		#for each joint (except last) setup blend color system
		#IK goes first in the blend, btw
		for i in range(len(thisChain)-1):
			ikJnt = thisIK[i]
			fkJnt = thisFK[i]
			bindJnt = thisChain[i]
			name = "%s_%s_%s_blendRot"%(side, self.limbName, self.jointList[i])

			thisRotBlend = rig.blendRotation(name, ikJnt, fkJnt, bindJnt, "%s.FKIK"%thisSwitch)

			sideRotBlendList.append(thisRotBlend)

		self.rotBlendList.append(sideRotBlendList)

		#deal with spread joints here
		numSpread = self.numSpreadJnts
#----------NOW I NEED TO ADD BACK IN THE TRANSLATION BLENDS/SPREADS FOR ALL AXES
		if self.spreadTwist:
			if numSpread == 0:
				pass
			else:
				#get distance from top to mid, divide by numSpread+1
				topJnt = thisChain[0]
				midJnt = thisChain[1]
				lowJnt = thisChain[2]
				topSpreadDist = cmds.getAttr("%s.t%s"%(midJnt, self.jAxis1))/(numSpread+1)
				lowSpreadDist = cmds.getAttr("%s.t%s"%(lowJnt, self.jAxis1))/(numSpread+1)

				#create a top mult node
				capLet = self.jAxis1.upper()
				topMult = cmds.shadingNode("multiplyDivide", n="%s_UpRot_mult"%topJnt, asUtility=True)
				#get number of joints to get a factor (i.e. 1/3)
				factor = 1.0/(numSpread + 1.0)
				cmds.setAttr("%s.input2"%topMult, factor, factor, factor)
				cmds.connectAttr("%s.output"%self.rotBlendList[x][0], "%s.input1"%topMult)

				#separate out the top joint
				cmds.parent(midJnt, w=True)
				#dupe the top joint numSpread number of times
				for i in range(numSpread):
#---------------get this name right side_chain_joint_"twist"num_JNT
					#here pull apart top jnt name (strip JNT)
					twistName = "%s_twist%i"%(topJnt,(i+1))
					cmds.duplicate(topJnt, n=twistName)
					#add twist to bind chain
					self.bindChains[x].insert(i+1,twistName)
					#move the joints this distance in axis (self.jAxis1 is letter of axis)
					if self.jAxis1 == "x":
						locDist = ((topSpreadDist*(i+1)), 0, 0)
					if self.jAxis1 == "y":
						locDist = (0, (topSpreadDist*(i+1)), 0)
					if self.jAxis1 == "z":
						locDist = (0, 0, (topSpreadDist*(i+1)))
					cmds.xform(twistName, r=True, os=True, t=locDist)
				#parent these back up chain
				for j in range(numSpread+1, 0, -1):
					child = self.bindChains[x][j]
					parent = self.bindChains[x][j-1]
					cmds.parent(child, parent)

				#hook up each new joint (and the mid joint)
				for k in range(numSpread, -1, -1):
					cmds.connectAttr("%s.output%s"%(upScaleBlend, colorAxis), "%s.s%s"%(self.bindChains[x][k], self.jAxis1))

				#do rotations
				for k in range (numSpread, -1, -1):
					thisJoint = self.bindChains[x][k]
					cmds.connectAttr("%s.output%s"%(topMult, capLet), "%s.rotate%s"%(thisJoint, capLet), force=True)

			#do the lower joints
			if self.spreadTwistLow:
				if numSpread == 0:
					pass
				else:
					lowRotMult = cmds.shadingNode("multiplyDivide", n="%s_lowRot_mult"%lowJnt, asUtility=True)
					cmds.setAttr("%s.input2"%lowRotMult, factor, factor, factor)
					cmds.connectAttr("%s.output"%self.rotBlendList[x][2], "%s.input1"%lowRotMult)

					cmds.parent(lowJnt, w=True)
					for i in range(numSpread):
#---------------get this name right side_chain_joint_"twist"num_JNT
						twistName = "%s_twist%i"%(lowJnt,(i+1))
						cmds.duplicate(midJnt, n=twistName)
						#add twist to bind chain
						self.bindChains[x].insert(i+numSpread+2,twistName)
						#move the joints this distance in axis (self.jAxis1 is letter of axis)
						if self.jAxis1 == "x":
							locDist = ((lowSpreadDist*(i+1)), 0, 0)
						if self.jAxis1 == "y":
							locDist = (0, (lowSpreadDist*(i+1)), 0)
						if self.jAxis1 == "z":
							locDist = (0, 0, (lowSpreadDist*(i+1)))
						cmds.xform(twistName, r=True, os=True, t=locDist)
					#parent these back up chain
					for j in range(((numSpread+1)*2), numSpread+1, -1):
						child = self.bindChains[x][j]
						parent = self.bindChains[x][j-1]
						cmds.parent(child, parent)

					#force inverse scale (for some reason they're not connected in lower twists)
					for a in range(numSpread+1, (numSpread*2)+1):
						parent = self.bindChains[x][a]
						child = self.bindChains[x][a+1]
						#2016 is telling me this is already done
						#cmds.connectAttr("%s.scale"%parent, "%s.inverseScale"%child, f=True)

					#scale joints (and mid joint)
					for k in range(numSpread*2+1, numSpread, -1):
						cmds.connectAttr("%s.output%s"%(lowScaleBlend, colorAxis), "%s.s%s"%(self.bindChains[x][k], self.jAxis1))

					#do rotations
					for k in range (((numSpread+1)*2), numSpread+1, -1):
						thisJoint = self.bindChains[x][k]
						cmds.connectAttr("%s.output%s"%(lowRotMult, capLet), "%s.rotate%s"%(thisJoint, capLet), force=True)

		else:
			numSpread = 0

		#create orient constraints on the bind wrist joint to FK wrist, IK wrist, connect to IK switch/reverse

#TO-DO----------------Make this something so that we can get offsets on both (IK ctrl, FK control, maybe use one orient constraint, and one parent with only rotation)
		# thisBindWristConstraint = cmds.orientConstraint(self.IKCtrls[x], thisFK[2], thisChain[(numSpread+1)*2])
		# cmds.connectAttr("%s.FKIK"%thisSwitch, "%s.%sW0"%(thisBindWristConstraint[0], self.IKCtrls[x]))
		# cmds.connectAttr("%s.outputX"%self.IKSwitchesRev[x], "%s.%sW1"%(thisBindWristConstraint[0], thisFK[2]))

		#call the finish method
		self.finishLimb(x)