import maya.cmds as cmds
import zbw_rig as rig
import maya.OpenMaya as om

#do everything noted inside PLUS:
#gimble controls
#------setup for space switching on IK joints (and FK joints?)(add message attrs that will link to the correct space objects, add in the offsets for the matching)
#------setup for stretchyness, ik, fk (only needs )
#later maybe add in bendy stuff?
#save option to save out presets?
#add a control skeleton to the mix? ik, fk --> ctrl --> bind?
#set up rotation orders based on values from main axis etc
#connect the two stretchy UI checkboxes?
#definitely have problems mirroring from rt to lf, figure this out later (maybe only create on left?)
#lock knee, elbow?

#PULL OUT ACTUAL BITS OF METHODS THAT DO THE THINGS I WANT TO OVERRIDE, SO I CAN JUST CALL THE METHOD AND THEN JUST OVERRIDE THE BITS THAT I WANT

#this is the generic limbUI class
class LimbUI(object):

	def __init__(self):

		super(LimbUI, self).__init__()

		self.widgets = {}

		##########  MODIFY FOR INHERERITANCE #########
		self.defaultLimbName = "limb"
		self.defaultJointList = ["top", "mid", "low", "end"]
		self.defaultLocValues = [[5,10,0], [10,10,0], [15,10, 0], [17, 10, 0]]

		self.buildUI()

	def buildUI(self):

		if (cmds.window("limbWin", exists=True)):
			cmds.deleteUI("limbWin")

		self.widgets["mainWindow"] = cmds.window("limbWin", title="generic Limb Window", w=320,h=600)
		self.widgets["scrollLayout"] = cmds.scrollLayout(vst=20)

		self.widgets["mainColumn"] = cmds.columnLayout(w=300,h=600)

		self.commonLimbUI()

		self.customLimbUI()

		self.buttonUI()

		cmds.showWindow(self.widgets["mainWindow"])

	def commonLimbUI(self):

		self.widgets["commonGeneralFrame"] = cmds.frameLayout(l="1. General Setup", cll=True, w=320, bgc=(.0, .0, .0))
		#text field group to get limb name
		self.widgets["limbNameTFG"] = cmds.textFieldGrp(l="Limb Name", cl2=("left", "left"), cw2 =(75,200),tx=self.defaultLimbName)
		#get lf, rt radio button grp for prefix
		self.widgets["prefixRBG"] = cmds.radioButtonGrp(l="Prefix:", nrb=4, l1="none", l2="lf", l3="rt", l4="other", cal=([1,"left"]), cw=([1, 50], [2,50], [3,50], [4,50]), sl=2, cc=self.prefixChange)

		#get other text field for prefix
		self.widgets["otherRCL"] = cmds.rowColumnLayout(nc=2, w=300)
		self.widgets["otherPrefixTFG"] = cmds.textFieldGrp(l="other", en=False, cl2=("left", "left"), cw2 =(40,80), tx="front")
		self.widgets["otherMirrorTFG"] = cmds.textFieldGrp(l="other(mirror)", en=False, cl2=("left", "left"), cw2 =(70,80), tx="back")

		cmds.setParent(self.widgets['commonGeneralFrame'])
		#get mirror check box
		self.widgets["mirrorCB"] = cmds.checkBox(l="Mirror?", v=True, cc=self.mirrorChange)
		#get what axis to mirror across
		self.widgets["axisRBG"] = cmds.radioButtonGrp(l="axis to mirror across", nrb=3,     l1="yz", l2="xz", l3="xy", cal=([1,"left"]), cw=([1, 75], [2,50], [3,50]), sl=1, en=True)

		#set row column here
		self.widgets["commonRCL"] = cmds.rowColumnLayout(nc=2, w=320)
		#get suffix for joints
		self.widgets["jntSuffixTFG"] = cmds.textFieldGrp(l="jnt suffix", tx="JNT", cl2=("left", "left"), cw2 =(50,75))
		#get suffix for ctrls
		self.widgets["ctrlSuffixTFG"] = cmds.textFieldGrp(l="ctrl suffix", tx="CTRL", cl2=("left", "left"), cw2 =(50,75))
		#get suffix for grps
		self.widgets["groupSuffixTFG"] = cmds.textFieldGrp(l="grp suffix", tx="GRP", cl2=("left", "left"), cw2 =(50,75))

		cmds.setParent(self.widgets["mainColumn"])
		#contents:
		self.widgets["commonContentsFrame"] = cmds.frameLayout(l="2. Contents/Joint Setup", cll=True, cl=True, w=320, bgc=(.0, .0, .0))
		#check box for ik, fk, bind, twist spread, stretchy,
#-------------fix the col width of the twist line
		self.widgets["jointOptionsCBG"] = cmds.checkBoxGrp(ncb=3, l1="spreadTwistTop", l2="stretchy", l3="spreadTwistLower", v1=True, v2=True, v3=True, cc1=self.spreadOn)
		self.widgets["numSpreadIFG"] = cmds.intFieldGrp(l="Number of twist spread joints", cal=[1,"left"], cw=([1,150], [2,50]), v1=2)
		self.widgets["jntMainAxisRBG"] = cmds.radioButtonGrp(l="main Joint Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 100], [2,50], [3,50]), sl=1, en=True)
		self.widgets["jntSecondAxisRBG"] = cmds.radioButtonGrp(l="second Joint Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 100], [2,50], [3,50]), sl=2, en=True)
		self.widgets["jntSecondAxisDirRBG"] = cmds.radioButtonGrp(l="secondary axis pos/neg", nrb=2, l1="+", l2="-", cal=([1,"left"]), cw=([1,150], [2,50], [3,50]), sl=1)


		self.widgets["straightLimbCB"] = cmds.checkBox(l="is limb geo bent? (as opposed to modeled straight)", v=True)
		self.widgets["noFlipCB"] = cmds.checkBox(l="use a 'no flip' pole vector?", v=False)
#----------colors for each side select the main, then the secondary colors

	def buttonUI(self):
		#create frame for locator button
		cmds.setParent(self.widgets["mainColumn"])
		self.widgets["LocButtonFrame"] = cmds.frameLayout(l="4. Create Locs", w=320, bgc=(.0, .0, .0))
		self.widgets["locatorButton"] = cmds.button(l="Create Locators", bgc=(.8,.5,0), w=300, h=30, c=self.setupArgs)
		#create frame for do it button
		cmds.setParent(self.widgets["mainColumn"])
		self.widgets["JointButtonFrame"] = cmds.frameLayout(l="5. Create Rig", w=320, bgc=(.0, .0, .0))
		self.widgets["limbButton"] = cmds.button(l="Create Limb", bgc = (0,.8,0),w=300, h=30, c=self.createLimb)

	def customLimbUI(self):
		#stuff like foot, hands, fingers, etc. Limb specific stuff
		cmds.setParent(self.widgets["mainColumn"])
		self.widgets["customFrame"] = cmds.frameLayout(l="3. Custom Limb Attributes", w=320, bgc=(0,0,0))
		#tmp
		cmds.text("this is where custom stuff for the limb type will be")

	def mirrorChange(self, *args):
		#get state of the mirror checkbox
		on = cmds.checkBox(self.widgets["mirrorCB"], q=True, v=True)
		#if it's on, turn on the other options
		if on:
			cmds.radioButtonGrp(self.widgets["axisRBG"], e=True, en=True)
		#if not, turn off the other options
		else:
			cmds.radioButtonGrp(self.widgets["axisRBG"], e=True, en=False)

	def prefixChange(self, *args):
		#get selected rb
		sel = cmds.radioButtonGrp(self.widgets["prefixRBG"], q=True, sl=True)
		#if other is selected, enable the tfg
		if sel == 4:
			cmds.textFieldGrp(self.widgets["otherPrefixTFG"], e=True, en=True)
			cmds.textFieldGrp(self.widgets["otherMirrorTFG"], e=True, en=True)
		else:
			cmds.textFieldGrp(self.widgets["otherPrefixTFG"], e=True, en=False)
			cmds.textFieldGrp(self.widgets["otherMirrorTFG"], e=True, en=False)

	def spreadOn(self, *args):
		#get value of spread joints cb
		on = cmds.checkBoxGrp(self.widgets["jointOptionsCBG"], q=True, v1=True)
		#if spread joints in on
		if on:
			cmds.intFieldGrp(self.widgets["numSpreadIFG"], e=True, en=True)
		else:
			cmds.intFieldGrp(self.widgets["numSpreadIFG"], e=True, en=False)

	def setupArgs(self,*args):
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

		self.callLocatorsGo()

	def callLocatorsGo(self, *args):
		#now pass these values to the Limb class - create an instance of Limb
		self.limb = Limb(self.limbName, self.prefix, self.mirror, self.mirrorAxis, self.jointSuffix, self.controlSuffix, self.groupSuffix, self.spreadTwist, self.spreadTwistLow, self.stretchy, self.numSpreadJnts, self.locVals, self.jointList, self.noFlip, self.mainAxis, self.secondaryAxis, self.straightLimb, self.mirrorName, self.posNeg)

		#now create locators
		self.limb.createLocators()

	def createLimb(self, *args):
		#just call the correct class.createLimb
		self.limb.createJoints()


class Limb(object):

	def __init__(self, limbName, prefix, mirror, mirrorAxis, jointSuffix, controlSuffix, groupSuffix, spreadTwist, spreadTwistLow, stretchy, numSpreadJoints, locVals, jointList, noFlip, mainAxis, secondaryAxis, straightLimb, mirrorName, posNeg):
		super(Limb, self).__init__()

#------------do all of the mirrored lists as lists of the various chains
		self.limbName = limbName
		self.prefix = prefix
		self.mirror = mirror
		self.mirrorAxis = mirrorAxis
		self.jointSuffix = jointSuffix
		self.controlSuffix = controlSuffix
		self.groupSuffix = groupSuffix
		self.spreadTwist = spreadTwist
		self.spreadTwistLow = spreadTwistLow
		self.stretchy = stretchy
		self.numSpreadJnts = numSpreadJoints[0]
		self.locList = []
		self.jointChains = ["IK", "FK", "bind", "measure"]
		self.IKJointOrig = []
		#self.IKJointMirror = []
		self.FKJointOrig = []
		#self.FKJointMirror = []
		self.bindJointOrig = []
		#self.bindJointMirror = []
		self.measureJointOrig = []
		#self.measureJointMirror = []
		self.IKChains = []
		self.FKChains = []
		self.bindChains = []
		self.measureChains = []
		self.prefixList = []
		self.IKHandles = []
		self.IKCtrls = []
		self.PVList = []
		self.FKCtrlChains = []
		self.IKSwitches = []
		self.limbGrps = []
		self.limbAttachGrps = []
		self.locPosValues = locVals
		self.jointList = jointList
		self.noFlip = noFlip
		self.mainAxis = mainAxis
		self.secondaryAxis = secondaryAxis
		self.straightLimb = straightLimb
		self.mirrorName = mirrorName
		self.posNeg = posNeg
		self.jAxis1 = "" #this is the letter repr of the main axis, x, y, z
		self.rotBlendList = []
		self.scaleBlendList = []
		self.transBlendList = []
		self.measureAdds = []
		self.IKSwitchesRev = []

	#create locator function first
	def createLocators(self):
		#create list of loc names (self.name)
		for i in range(len(self.jointList)):
			self.locList.append("%s_%s_Loc"%(self.jointList[i],self.limbName))

		#check that these don't exist already
		if (cmds.objExists(self.locList[0])):
			cmds.error("these limb locators exists already!")
		else:

			#fill dictionary - assign values from list
			self.locPos = {}
			for j in range(len(self.locList)):
				self.locPos[self.locList[j]] = self.locPosValues[j]

			#create the locs
			for key in self.locPos.keys():
				thisLoc = cmds.spaceLocator(n=key)
				cmds.move(self.locPos[key][0], self.locPos[key][1], self.locPos[key][2], thisLoc)

			#parent them together (from list of loc names)
			for k in range((len(self.locList)-1),0,-1):
				cmds.parent(self.locList[k], self.locList[k-1])

			#rotate second joint to just get a preferred angle
			cmds.setAttr("%s.ry"%self.locList[1], -5)

	def createJoints(self):
		#create joint list
		self.baseJoints = []

		for i in range(len(self.jointList)):
			self.baseJoints.append("%s_%s"%(self.jointList[i], self.jointSuffix))

		#populate IK list
		for baseJoint in self.baseJoints:
			ikName = "%s_IK_%s"%(self.prefix, baseJoint)
			self.IKJointOrig.append(ikName)

		#populate FK list
		for baseJoint in self.baseJoints:
			fkName = "%s_FK_%s"%(self.prefix, baseJoint)
			self.FKJointOrig.append(fkName)

		#populate bind list
		for baseJoint in self.baseJoints:
			bindName = "%s_bind_%s"%(self.prefix, baseJoint)
			self.bindJointOrig.append(bindName)

		#populate measure list
		for baseJoint in self.baseJoints:
			measureName = "%s_measure_%s"%(self.prefix, baseJoint)
			self.measureJointOrig.append(measureName)

		#create joints, parent, orient for each of (IK, FK, Bind, Measure)
		for chain in self.jointChains:
			for j in range(len(self.locList)):
				list = "self.%sJointOrig"%chain
				#get loc position
				locPos = cmds.xform(self.locList[j], q=True, ws=True, rp=True)
				cmds.select(cl=True)
				#create joints on loc
				cmds.joint(name=(eval("%s[j]"%list)), p=locPos)

		#parent up the joints to each other from each chain
		#ik
		for i in range(len(self.locList)-1, 0, -1):
			cmds.parent(self.IKJointOrig[i], self.IKJointOrig[i-1])
		#fk
		for i in range(len(self.locList)-1, 0, -1):
			cmds.parent(self.FKJointOrig[i], self.FKJointOrig[i-1])
		#bind
		for i in range(len(self.locList)-1, 0, -1):
			cmds.parent(self.bindJointOrig[i], self.bindJointOrig[i-1])
		#measure
		for i in range(len(self.locList)-1, 0, -1):
			cmds.parent(self.measureJointOrig[i], self.measureJointOrig[i-1])

		#orient the joint chains according to settings above
		#first letter in joint oj=flag. Second letter in xyz would be the secondary axis, this is +/-, which would then go into sao="letter"up/down flag.
		order = {1:"x", 2:"y", 3:"z"}
		self.jAxis1 = order[self.mainAxis]
		self.jAxis2 = order[self.secondaryAxis]
		ROPart = self.jAxis1 + self.jAxis2
		if (ROPart == "xy") or (ROPart == "yx"):
			self.jointOrientation = ROPart + "z"
		if (ROPart == "xz") or (ROPart=="zx"):
			self.jointOrientation = ROPart + "y"
		if (ROPart=="yz") or (ROPart=="zy"):
			self.jointOrientation = ROPart + "x"

		#get positive or negative
		if self.posNeg == 1:
			direct = "up"
		if self.posNeg == 2:
			direct = "down"

		#get the up/down secondary axis string
		minorAxis = self.jAxis2 + direct

		#orient the joints
		cmds.joint(self.IKJointOrig[0], e=True, oj = self.jointOrientation, ch=True, sao=minorAxis, zso=True )
		cmds.joint(self.FKJointOrig[0], e=True, oj = self.jointOrientation, ch=True, sao=minorAxis, zso=True )
		cmds.joint(self.measureJointOrig[0], e=True, oj = self.jointOrientation, ch=True, sao=minorAxis, zso=True )
		cmds.joint(self.bindJointOrig[0], e=True, oj = self.jointOrientation, ch=True, sao=minorAxis, zso=True )

		#mirroring - from here out prefix is repr by list (prefixList)
		if self.mirror:
			if self.prefix == "lf":
				self.prefixList = ["lf", "rt"]
			elif self.prefix == "rt":
				self.prefixList = ["rt", "lf"]
			else:
				self.prefixList = [self.prefix, self.mirrorName]
		else:
			self.prefixList = [self.prefix]

		if self.mirror:
			#get mirror plane, then mirror joint chain
			if self.mirrorAxis=="xy":
				self.IKJointMirror = cmds.mirrorJoint(self.IKJointOrig[0], mxy=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.FKJointMirror = cmds.mirrorJoint(self.FKJointOrig[0], mxy=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.measureJointMirror = cmds.mirrorJoint(self.measureJointOrig[0], mxy=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.bindJointMirror = cmds.mirrorJoint(self.bindJointOrig[0], mxy=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
			elif self.mirrorAxis == "yz":
				self.IKJointMirror = cmds.mirrorJoint(self.IKJointOrig[0], myz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.FKJointMirror = cmds.mirrorJoint(self.FKJointOrig[0], myz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.measureJointMirror = cmds.mirrorJoint(self.measureJointOrig[0], myz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.bindJointMirror = cmds.mirrorJoint(self.bindJointOrig[0], myz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
			elif self.mirrorAxis == "xz":
				self.IKJointMirror = cmds.mirrorJoint(self.IKJointOrig[0], mxz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.FKJointMirror = cmds.mirrorJoint(self.FKJointOrig[0], mxz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.measureJointMirror = cmds.mirrorJoint(self.measureJointOrig[0], mxz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))
				self.bindJointMirror = cmds.mirrorJoint(self.bindJointOrig[0], mxz=True, mb=True, sr=(self.prefixList[0], self.prefixList[1]))

		#now set up list for each type of chain, gets "orig" version and if mirror from uI,  then gets "mirror" version of chain appended to the end
		self.IKChains.append(self.IKJointOrig)
		if self.mirror:
			self.IKChains.append(self.IKJointMirror)

		self.FKChains.append(self.FKJointOrig)
		if self.mirror:
			self.FKChains.append(self.FKJointMirror)

		self.measureChains.append(self.measureJointOrig)
		if self.mirror:
			self.measureChains.append(self.measureJointMirror)

		self.bindChains.append(self.bindJointOrig)
		if self.mirror:
			self.bindChains.append(self.bindJointMirror)

		#start the measure method - go through this once for each chain
		for x in range(len(self.prefixList)):
			self.setupMeasure(self.prefixList, x)

	def setupMeasure(self, prefixList, x):
		"""sets up the measure joint portion of the the limb rig"""
		#set values for this chain, side
		thisChain = self.measureChains[x]
		side = self.prefixList[x]

		self.measureUp = "%s_%s_upDistance"%(side, self.limbName)
		self.measureLow = "%s_%s_lowDistance"%(side, self.limbName)
		self.totalDistAdd = "%s_%s_lengthADL"%(side, self.limbName)
		#measure top two joints
		rig.measureDistance(self.measureUp, thisChain[0], thisChain[1])
#----------add these to a list of lists of arm measures
		#measure low two joints
		rig.measureDistance(self.measureLow, thisChain[1], thisChain[2])

		#add the results
		thisTotal = rig.createAdd(self.totalDistAdd, "%s.distance"%self.measureUp, "%s.distance"%self.measureLow)

		self.measureAdds.append(thisTotal)

		#call to start the IK setup part of the rig
		self.setupIK(x)

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
		#create mult node, put add into input 2, set to divide!
#---------orient the IK wrist to the control? do it here or elsewhere (for inheritance?)
		cmds.orientConstraint(IKCtrl, thisChain[2])

		#create distance node from thigh to ctrl
		distance = rig.measureDistance("%s_%s_ikCtrlDistance"%(side, self.limbName), self.measureChains[x][0], IKCtrl)

		ratioMult, defaultMult, defaultBlend, conditional, upScaleMult, loScaleMult = rig.scaleStretchIK(("%s_%s"%(side, self.limbName)), thisChain[0], thisChain[1], thisChain[2], "%s.output"%add, "%s.distance"%distance, IKCtrl, self.jAxis1)

		#create the ik switch (call as "diamond")
		ikSwitchName = "%s_%s_FKIKSwitch"%(side, self.limbName)
		thisIKSwitch = rig.createControl(ikSwitchName, "diamond", self.jAxis1)
		rig.stripTransforms(thisIKSwitch)
		cmds.addAttr(thisIKSwitch, ln="FKIK", k=True, at="float", min=0, max=1, dv=0)
		#create reverse
		thisIKSwitchRev = cmds.shadingNode("reverse", asUtility=True, n="%s_%s_IKSwtchReverse"%(side, self.limbName))
		cmds.connectAttr("%s.FKIK"%thisIKSwitch, "%s.inputX"%thisIKSwitchRev)
		rig.groupOrient(thisBind[2], thisIKSwitch, self.groupSuffix)
		IKSwitchGrp = cmds.listRelatives(thisIKSwitch, p=True)
		if x== 0:
			offset = -3
		if x==1:
			offset = 3

#---------------so stuff here to push the IKFK switch in the right direction (if statements)
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
		IKCtrl = rig.createControl(name, "cube", self.jAxis1)
		self.IKCtrls.append(IKCtrl)
		#strip to rotate and translate
		rig.stripToRotateTranslate(IKCtrl)

		#G.O. control
		rig.groupOrient(thisChain[2], IKCtrl, self.groupSuffix)

		#orient constraint joint 2 (wrist ankle) to control
		cmds.orientConstraint(IKCtrl, thisChain[2])

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
			thisPV = rig.createControl(pv, "sphere", self.jAxis1)
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

#------------ capture all constraints as list?
			#hook up pv
			cmds.poleVectorConstraint(thisPV, IKHandle)

			#add pv to list
			self.PVList.append(thisPV)

			#return pv
			return(thisPV)

		if type == "noFlip":
			pass
		pass

	def setupFK(self, x):
		"""sets up the fk portion of this limb"""
		thisChain = self.FKChains[x]
		side = self.prefixList[x]

		ctrlList = []
		grpList = []

		for i in range(len(thisChain)-1):
			#create control for joint (octagon)
			ctrlName = (thisChain[i].rstrip(self.jointSuffix) + self.controlSuffix)

			#create control
			ctrl = rig.createControl(ctrlName, "sphere", self.jAxis1)
			grpName = "%s_%s"%(ctrl,self.groupSuffix)

			rig.groupOrient(thisChain[i], ctrl, self.groupSuffix)

			#connect the joints to the controls
#--------------catch this constraint with variable????
			cmds.orientConstraint(ctrl, thisChain[i])

			#deal with attrs
			rig.stripToRotate(ctrl)
			cmds.addAttr(ctrl, at="short", ln="__EXTRA__", nn="__EXTRA__", k=True)
			cmds.setAttr("%s.__EXTRA__"%ctrl, l=True)
			cmds.addAttr(ctrl, at="float", ln="stretch", dv=1, min=0.3, max=3, k=True)
			cmds.connectAttr("%s.stretch"%ctrl, "%s.s%s"%(thisChain[i], self.jAxis1))

			ctrlList.append(ctrl)
			grpList.append(grpName)

		#parent up the controls to each other
		for j in range((len(grpList)-1), 0, -1):
			cmds.parent(grpList[j], ctrlList[j-1])

		#create lists of controls
		self.FKCtrlChains.append(ctrlList)

		#do the visibilty of the fk chain from the IK switch
		ikS = self.IKSwitches[x]
		rName = ("%s_%s_ikReverse"%(self.prefixList[x], self.limbName))
		grpTop = cmds.listRelatives(self.FKCtrlChains[x][0], p=True)[0]
		cmds.shadingNode("reverse", asUtility=True, n=( rName))
		cmds.connectAttr("%s.FKIK"%ikS, "%s.inputX"%rName)
		cmds.connectAttr("%s.outputX"%rName, "%s.visibility"%grpTop)

		#pass to bind setup
		self.setupBind(x)

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
			name = "%s_%s_blendRot"%(side,self.jointList[i])

			thisRotBlend = rig.blendRotation(name, ikJnt, fkJnt, bindJnt, "%s.FKIK"%thisSwitch)

			sideRotBlendList.append(thisRotBlend)

		self.rotBlendList.append(sideRotBlendList)

		#deal with spread joints here
		numSpread = self.numSpreadJnts

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
					cmds.connectAttr("%s.s%s"%(thisIK[0], self.jAxis1), "%s.s%s"%(self.bindChains[x][k], self.jAxis1))

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
						cmds.connectAttr("%s.scale"%parent, "%s.inverseScale"%child, f=True)

					#scale joints (and mid joint)
					for k in range(numSpread*2+1, numSpread, -1):
						cmds.connectAttr("%s.s%s"%(thisIK[1], self.jAxis1), "%s.s%s"%(self.bindChains[x][k], self.jAxis1))

					#do rotations
					for k in range (((numSpread+1)*2), numSpread+1, -1):
						thisJoint = self.bindChains[x][k]
						cmds.connectAttr("%s.output%s"%(lowRotMult, capLet), "%s.rotate%s"%(thisJoint, capLet), force=True)

		else:
			numSpread = 0

		#create orient constraints on the bind wrist joint to FK wrist, IK wrist, connect to IK switch/reverse?????
		thisBindWristConstraint = cmds.orientConstraint(self.IKCtrls[x], thisFK[2], thisChain[(numSpread+1)*2])
		cmds.connectAttr("%s.FKIK"%thisSwitch, "%s.%sW0"%(thisBindWristConstraint[0], self.IKCtrls[x]))
		cmds.connectAttr("%s.outputX"%self.IKSwitchesRev[x], "%s.%sW1"%(thisBindWristConstraint[0], thisFK[2]))

#--------------Blend scale along jAxis to each of the bind joints to the correct IK, FK joints




		#call the finish method
		self.finishLimb(x)

	def finishLimb(self, x):

		side = self.prefixList[x]
		limbGrpName = "%s_%s_%s"%(side, self.limbName, self.groupSuffix)
		limbAttachGrpName = "%s_%s_attach_%s"%(side, self.limbName, self.groupSuffix)

		thisIK = self.IKChains[x]
		thisFK = self.FKChains[x]
		thisMeasure = self.measureChains[x]
		thisBind = self.bindChains[x]
		thisFKCtrlsC  = self.FKCtrlChains[x]
		thisFKGrp = cmds.listRelatives(thisFKCtrlsC[0], p=True)

#--------------create gimbal controls (put vis on the IKFK switch)
#--------------setup space switching

		#get location of top node of one, say IK chain
		limbPos = cmds.xform(thisIK[0], ws=True, q=True, t=True)

		#group all of the joints and FK controls
		limbGrp = cmds.group(empty=True, name=limbGrpName)
		cmds.xform(limbGrp, ws=True, t=limbPos)
		limbAttachGrp = cmds.group(empty=True, name=limbAttachGrpName)
		cmds.xform(limbAttachGrp, ws=True, t=limbPos)
		cmds.parent(limbGrp, limbAttachGrp)
		cmds.parent(thisIK[0], thisFK[0], thisMeasure[0], thisBind[0], thisFKGrp, limbGrp)
		self.limbGrps.append(limbGrp)
		self.limbAttachGrps.append(limbAttachGrp)

		#package up other stuff
		ikGrpName = "IK_%s_%s"%(self.controlSuffix, self.groupSuffix)
		if cmds.objExists(ikGrpName):
			pass
		else:
			cmds.group(empty=True, n=ikGrpName)

		PV = cmds.listRelatives(self.PVList[x], p=True)
		IK = cmds.listRelatives(self.IKCtrls[x], p=True)
		switch = cmds.listRelatives(self.IKSwitches[x], p=True)

		cmds.parent(PV, IK, switch, ikGrpName )

		# if x== 0:
		#     cmds.delete(self.locList[0])

#---------------addd some stuff for setting up IK snapping and matching, message attrs

##########  here is where to add methods for feet, hands, bendy, etc ##############


