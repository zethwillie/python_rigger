import maya.cmds as cmds
import python_rigger.rigger_tools.rigger_tools as zrt
reload(zrt)
import python_rigger.rigger_tools.BaseLimb as BL
reload(BL)
import zTools.rig.zbw_rig as rig
reload(rig)
import maya.OpenMaya as om
import python_rigger.rigger_tools.rigger_window as zrw
reload(zrw)


class LegRigUI(zrw.RiggerWindow):
    def __init__(self):
        self.width = 300
        self.height = 600

        self.winInitName = "zbw_legRiggerUI"
        self.winTitle="Leg Rigger UI"
        # common
        self.defaultLimbName = "leg"
        self.defaultOrigPrefix = "L"
        self.defaultMirPrefix = "R"
        self.pts = [(5,12, 0),(5, 7, 1), (5, 2, 0), (5, 1, 3), (5, 1, 4)]
        self.baseNames = ["thigh", "knee", "ankle", "ball", "ballEnd"]
        self.secRotOrderJnts = []
        self.make_UI()

    def create_rigger(self, *args):
        self.rigger = LegRig()
        self.get_values_for_rigger()
        self.set_values_for_rigger()


class LegRig(BL.BaseLimb):
    def __init__(self):
        BL.BaseLimb.__init__(self)
    # can add this in tht ui? need to?    
        self.revFootPts = [(5, 1, 3), (5, 0, 4), (5, 0, -2)]
    # can add sides to this
        self.revFootNames = ["ball", "toe", "heel"]
        self.revFootLocs = []

    def pose_initial_joints(self):
        BL.BaseLimb.pose_initial_joints(self)
    # need to work on orienting the joints here. . . which attrs to lock (just unlock all?)   
        for i in range(len(self.revFootNames)):
            loc = cmds.spaceLocator(name="{0}_LOC".format(self.revFootNames[i]))
            cmds.xform(loc, ws=True, t=self.revFootPts[i])
            self.revFootLocs.append(loc)


    def make_limb_rig(self):
        BL.BaseLimb.make_limb_rig(self)
        self.create_reverse_foot()
# don't inehrit, redo whole thing and do rev foot before clean up (to add ctrls, grps, etc to the lists for cleanup)

    def create_reverse_foot(self):
        # for side in self.fkJoints.keys():
        # create control at ankle no rot
        # footIkCtrl = rig.createControl()
        # add attrs to ankle ctrl
        # create grp for each loc
        # parent ball to toe, toe to heel, heel to to ctrl
        # parent ik to ball grp
        # create new ik from ankle to ball, parent under 


        # connect pv to foot, 
        pass