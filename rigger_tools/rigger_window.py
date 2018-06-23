import maya.cmds as cmds

class TempClass(object):
    """
    temp class so we don't have to import the real thing here. Switch out instances of this with real thing when this is inherited.
    """

    def __init__(self):
        pass


class RiggerWindow(object):
    def __init__(self):
        pass


    def make_UI(self):
        pass


    def create_rigger(self):
        ######### CHANGE ON INHERIT
        # create the instance of the rigger
    # DON"T ANY STUFF EXPLICITLY IN THIS BASECLASS (CIRCULAR LINK TO THE INHERITED CLASS). Use inheritance to call the specific rig class
        self.rigger = TempClass() # REPLACE THIS
        self.set_values_for_rigger()
        pass

    def get_values_for_rigger(self):
        # do this here to help get rid of errors building if we can catch them here? At least for now, while building
        pass

    def set_values_for_rigger(self):
    ############ CHANGE ON INHERIT?
    # option for no ik?    
        # pass in the values to the rigger instance
        self.rigger.pts = [(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)] # list of pt positions for initial jnts
        self.rigger.part = "limb"          # ie. "arm"
        self.rigger.baseNames = ["limb1", "limb2", "limb3", "limb4"] # list of names of joints (i.e ["shoulder", "elbow", etc])
        self.rigger.jntSuffix = "JNT"      # what is the suffix for jnts
        self.rigger.origPrefix = "lf"      # ie. "lf"
        self.rigger.mirror = True          # do we mirror?
        if self.rigger.mirror:
            self.rigger.mirPrefix = "rt"   # ie. "rt"
        self.rigger.mirrorAxis = "yz"      # what is axis for joint mirroring (ie. "yz")
        self.rigger.primaryAxis = "x"      # down the joint axis
        self.rigger.upAxis = "y"           # up axis for joints orient
        self.rigger.tertiaryAxis = "z"     # third axis
        # below needs to be created from main axis, up axis etc (ie. "x")
        self.rigger.orientOrder = "xyz"    # orient order for joint orient (ie. "xyz" or "zyx")
        self.rigger.upOrientAxis = "yup"   # joint orient up axis (ie. "yup" or "zup")
        self.rigger.createIK = True        # should we create an ik chain (leave True for now)
        self.rigger.twist = True           # do we create twist joints?
        self.rigger.twistNum = 2           # how many (doesn't include top/bottom)?
        self.rigger.secRotOrder = "zyx"  # the 'other' rotation order (ie. for wrists, etc)
        self.rigger.secRotOrderJnts = [2]   # which joints get the secRotOrder. This is a list of the indices

    def create_guides(self):
        self.rigger.pose_initial_joints()


    def create_rig(self):
        self.rigger.make_limb_rig()