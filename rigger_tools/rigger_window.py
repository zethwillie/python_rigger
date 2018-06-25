import maya.cmds as cmds

class TempClass(object):
    """
    temp class so we don't have to import the real thing here. Switch out instances of this with real thing when this is inherited.
    """

    def __init__(self):
        pass


class RiggerWindow(object):
    def __init__(self):
        self.width = 300
        self.height = 600

        self.winInitName = "zbw_limbUI"
        self.winTitle="Base Limb UI"
        # common
        self.defaultLimbName = "arm"
        self.defaultOrigPrefix = "L"
        self.defaultMirPrefix = "R"
        self.pts = [(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)]
        self.baseName = ["shoulder", "elbow", "wrist", "wristEnd"]
        self.secRotOrderJnts = [2]
        self.make_UI()

    def make_UI(self):
        if cmds.window(self.winInitName, exists=True):
            cmds.deleteUI(self.winInitName)

        self.window = cmds.window(self.winInitName, w=self.width, h=self.height, title=self.winTitle, cc=self.resize_window)
        
        self.mainColumn = cmds.columnLayout(w=self.width, h=self.height)
        self.common_limb_UI()
        self.custom_limb_UI()
        self.execute_buttons_UI()

        cmds.window(self.winInitName, e=True, rtf=True, w=5, h=5)
        cmds.showWindow(self.window)


    def common_limb_UI(self):
        self.commonSetupFLO = cmds.frameLayout(l="1. General Setup", collapsable=False, w=self.width, bgc=(0, 0, 0), parent=self.mainColumn, cc=self.resize_window)
        self.limbNameTFG = cmds.textFieldGrp(l="Limb Name: ", columnAlign2=("left", "left"), columnWidth2=(75,200), tx=self.defaultLimbName)

        self.origPrefixNameRBG = cmds.radioButtonGrp(l="Orig Prefix:", numberOfRadioButtons=4, label1="none", label2="lf", label3="rt", label4="custom", columnAlign=([1,"left"]), columnWidth=([1, 65], [2,50], [3,50], [4,50]), select=2, changeCommand=self.prefix_change)

        self.otherRCL = cmds.rowColumnLayout(nc=2, w=self.width)
        self.otherPrefixTFG = cmds.textFieldGrp(l="Custom Prefix: ", enable=False, columnAlign2=("left", "left"), columnWidth2=(75,70), text=self.defaultOrigPrefix)
        self.otherMirrorTFG = cmds.textFieldGrp(l="Mirror Prefix: ", enable=False, columnAlign2=("left", "left"), columnWidth2 =(75,70), tx=self.defaultMirPrefix)
        
        cmds.setParent(self.commonSetupFLO)

        self.mirrorCB = cmds.checkBox(label="Mirror the limb?", value=True, changeCommand= self.change_mirror)
        self.mirrorAxisOM = cmds.optionMenu(l="mirrorAxis:")
        cmds.menuItem(l="xy")
        cmds.menuItem(l="xz")
        cmds.menuItem(l="yz")
        cmds.optionMenu(self.mirrorAxisOM, e=True, sl=3)


        self.commonRCL = cmds.rowColumnLayout(nc=2, w=self.width)
        self.jntSuffixTFG = cmds.textFieldGrp(l="jnt suffix", tx="JNT", cl2=("left", "left"), cw2 =(50,75), en=False)
        #get suffix for ctrls
        self.ctrlSuffixTFG = cmds.textFieldGrp(l="ctrl suffix", tx="CTRL", cl2=("left", "left"), cw2 =(50,75), en=False)
        #get suffix for grps
        self.groupSuffixTFG = cmds.textFieldGrp(l="grp suffix", tx="GRP", cl2=("left", "left"), cw2 =(50,75), en=False)

        cmds.setParent(self.mainColumn)
        self.commonJointsFLO = cmds.frameLayout(l="2. Rig/Joint Setup", cll=False, cl=True, w=self.width, bgc=(0, 0, 0), cc=self.resize_window)
# make these pull downs with positive and negative
        self.jntMainAxisRGB = cmds.radioButtonGrp(l="Main Joint Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 100], [2,50], [3,50]), sl=1, en=True)
        self.jntSecAxisRBG = cmds.radioButtonGrp(l="Second Joint Axis", nrb=3, l1="x", l2="y", l3="z", cal=([1,"left"]), cw=([1, 100], [2,50], [3,50]), sl=2, en=True)
        self.jntSecAxisDirRBG = cmds.radioButtonGrp(l="Secondary axis pos/neg", nrb=2, l1="+", l2="-", cal=([1,"left"]), cw=([1,150], [2,50], [3,50]), sl=1, en=False)        

        self.ikCBG = cmds.checkBoxGrp(ncb=1, l1="IK", v1=True)

        self.twistOnCBG = cmds.checkBoxGrp(ncb=1, l1="Twist Jnts", v1=True, cc1=self.spread_toggle) # could add twistup/lo, and stretchy options here
        self.numTwistJntsIFG = cmds.intFieldGrp(l="Number of (mid) twist jnts:", cal=[1,"left"], cw=([1,150], [2,50]), v1=2)
        self.noFlipCG = cmds.checkBox(l="Use a 'no flip' pole vector?", v=False, en=False)

    # sec rot order
        self.secRotOrderOM = cmds.optionMenu(l="Secondary Rot Order:", w=50)
        cmds.menuItem(l="xyz")
        cmds.menuItem(l="xzy")
        cmds.menuItem(l="yxz")
        cmds.menuItem(l="yzx")
        cmds.menuItem(l="zyx")
        cmds.menuItem(l="zxy")
        cmds.optionMenu(self.secRotOrderOM, e=True, sl=5)


    def custom_limb_UI(self):
        cmds.setParent(self.mainColumn)
        self.customFLO = cmds.frameLayout(l="3. Custom Limb Attributes", w=self.width, bgc=(0,0,0), cll=False, cl=True, cc=self.resize_window)
        #tmp
        cmds.text("This is where custom stuff for the limb type will be")


    def execute_buttons_UI(self):
        cmds.setParent(self.mainColumn)
        self.poseRigFLO = cmds.frameLayout(l="4. Create Rig", w=self.width, bgc=(.0, .0, .0), cll=False)
        self.poseRigBut = cmds.button(l="Create Pose Rig", bgc=(.8,.5,.5), w=self.width, h=30, c=self.create_rigger)

        cmds.setParent(self.mainColumn)
        self.createRigBut = cmds.frameLayout(l="5. Create Rig", w=self.width, bgc=(.0, .0, .0), cll=False)
        self.createRigBut = cmds.button(l="Create Rig", bgc = (.5,.8,.5),w=self.width, h=30, c=self.create_rig)


    def resize_window(self):
        cmds.window(self.window, e=True, rtf=True, w=100, h=100)


    def spread_toggle(self, *args):
        on = cmds.checkBoxGrp(self.twistOnCBG, q=True, v1=True)
        if on:
            cmds.intFieldGrp(self.numTwistJntsIFG, e=True, en=True)
        else:
            cmds.intFieldGrp(self.numTwistJntsIFG, e=True, en=False)


    def change_mirror(self, *args):
        on = cmds.checkBox(self.mirrorCB, q=True, v=True)
        if on:
            cmds.radioButtonGrp(self.mirrorAxisRBG, e=True, en=True)
        else:
            cmds.radioButtonGrp(self.mirrorAxisRBG, e=True, en=False)



    def prefix_change(self, *args):
        sel = cmds.radioButtonGrp(self.origPrefixNameRBG, q=True, sl=True)

        if sel == 4:
            cmds.textFieldGrp(self.otherPrefixTFG, e=True, en=True)
            cmds.textFieldGrp(self.otherMirrorTFG, e=True, en=True)
        else:
            cmds.textFieldGrp(self.otherPrefixTFG, e=True, en=False)
            cmds.textFieldGrp(self.otherMirrorTFG, e=True, en=False)


    def create_rigger(self, *args):
        ######### CHANGE ON INHERIT
        # create the instance of the rigger
    # DON"T ANY STUFF EXPLICITLY IN THIS BASECLASS (CIRCULAR LINK TO THE INHERITED CLASS). Use inheritance to call the specific rig class
        self.rigger = TempClass() # REPLACE THIS
        self.get_values_for_rigger()
        self.set_values_for_rigger()
        # get prefix

    def get_values_for_rigger(self):
        # do this here to help get rid of errors building if we can catch them here? At least for now, while building
        self.part = cmds.textFieldGrp(self.limbNameTFG, q=True, tx=True)

        self.jntSuffix = "JNT"
        # get prefix stuff here
        if cmds.radioButtonGrp(self.origPrefixNameRBG, q=True, sl=True)==1:
            self.origPrefix = ""
            self.mirPrefix = "Null"
        elif cmds.radioButtonGrp(self.origPrefixNameRBG, q=True, sl=True)==2:
            self.origPrefix = "lf"
            self.mirPrefix = "rt"
        elif cmds.radioButtonGrp(self.origPrefixNameRBG, q=True, sl=True)==3:
            self.origPrefix = "rt"
            self.mirPrefix = "lf"
        else:
            self.origPrefix = cmds.textFieldGrp(self.otherPrefixTFG, q=True, tx=True)
            self.mirPrefix = cmds.textFieldGrp(self.otherMirrorTFG, q=True, tx=True)

        self.mirror = cmds.checkBox(self.mirrorCB, q=True, value=True)
        self.mirrorAxis = cmds.optionMenu(self.mirrorAxisOM, q=True, v=True)


        primAx = cmds.radioButtonGrp(self.jntMainAxisRGB, q=True, sl=True)
        if primAx == 1:
            self.primaryAxis = "x"
        elif primAx == 2: 
            self.primaryAxis = "y"
        elif primAx == 3: 
            self.primaryAxis = "z"

        upAx = cmds.radioButtonGrp(self.jntSecAxisRBG, q=True, sl=True)
        if upAx == 1:
            self.upAxis = "x"
        elif upAx == 2: 
            self.upAxis = "y"
        elif upAx == 3: 
            self.upAxis = "z"

        axes = ["x", "y", "z"]
        axes.remove(self.primaryAxis)
        axes.remove(self.upAxis)
        self.orientOrder = "{0}{1}{2}".format(self.primaryAxis, self.upAxis, axes[0])
        self.upOrientAxis = "{0}up".format(self.upAxis)

        self.createIK = cmds.checkBoxGrp(self.ikCBG, q=True, v1=True)

        self.twist = cmds.checkBoxGrp(self.twistOnCBG, q=True, v1=True)
        self.numTwist = cmds.intFieldGrp(self.numTwistJntsIFG, q=True, v1=True)

        self.secRotOrder = cmds.optionMenu(self.secRotOrderOM, q=True, v=True)


    def set_values_for_rigger(self):
    ############ CHANGE ON INHERIT?
    # option for no ik?    
        # pass in the values to the rigger instance
        self.rigger.pts = self.pts # list of pt positions for initial jnts
        self.rigger.part = self.part         # ie. "arm"
        self.rigger.baseNames = self.baseNames # list of names of joints (i.e ["shoulder", "elbow", etc])
        self.rigger.jntSuffix = "JNT"      # what is the suffix for jnts
        self.rigger.groupSuffix = "GRP"
        self.rigger.ctrlSuffix = "CTRL"
        self.rigger.origPrefix = self.origPrefix      # ie. "lf"
        self.rigger.mirror = self.mirror          # do we mirror?
        if self.rigger.mirror:
            self.rigger.mirPrefix = self.mirPrefix   # ie. "rt"
        self.rigger.mirrorAxis = self.mirrorAxis      # what is axis for joint mirroring (ie. "yz")
        self.rigger.primaryAxis = self.primaryAxis      # down the joint axis
        self.rigger.upAxis = self.upAxis           # up axis for joints orient
        #self.rigger.tertiaryAxis = "z"     # third axis
        self.rigger.orientOrder = self.orientOrder    # orient order for joint orient (ie. "xyz" or "zyx")
        self.rigger.upOrientAxis = self.upOrientAxis   # joint orient up axis (ie. "yup" or "zup")
        self.rigger.createIK = self.createIK        # should we create an ik chain (leave True for now)
        self.rigger.twist = self.twist           # do we create twist joints?
        self.rigger.twistNum = self.numTwist           # how many (doesn't include top/bottom)?
        self.rigger.secRotOrder = self.secRotOrder  # the 'other' rotation order (ie. for wrists, etc)
        self.rigger.secRotOrderJnts = self.secRotOrderJnts   # which joints get the secRotOrder. This is a list of the indices

        self.create_guides()


    def create_guides(self):
        self.rigger.pose_initial_joints()


    def create_rig(self, *args):
        self.rigger.make_limb_rig()