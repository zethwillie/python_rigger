import maya.cmds as cmds
import python_rigger.rigger_tools.rigger_tools as zrt
reload(zrt)
import zTools.rig.zbw_rig as rig
reload(rig)

# make a class for ctrls? ? so we can get groups with .attrs ?
class BaseLimbUI(object):
    def __init__(self):
        # call BaseLimb from here. . . first call is to pose_initial_joints(w args)
        # second call is to set values for instance variables from here (ie. limb.origPrefix="lf", etc)
        # third call is to CREATE_LIMB method to actually go through the process
        # buttons will call the methods
        pass


class BaseLimb(object):

    def __init__(self, fromUI=True):
        self.dataFromUI = True
        self.origFkJnts = []
        self.mirrorFkJnts = []
        
        # delete this
        self.set_values_UI()
        # this will be what the actual code is. We'll just set all the values from the UI in the other case
        # if not fromUI:
        #     self.set_values_code()


    def set_values_UI(self):
        """ grab all relevant values from UI"""
        #from ui. . . 
        self.pts=[(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)]
        self.baseNames=["shoulder", "elbow", "wrist", "wristEnd"]
        self.origPrefix = "lf"
        self.mirPrefix = "rt"
        self.mainAxis = "x"
        self.upAxis = "y"
        # below needs to be created from main axis (ie. "x")
        self.orientOrder = "xyz"
        self.upOrientAxis = "yup"

        self.jntSuffix = "JNT"
        self.mirrorAxis = "yz"
        # this can be gotten in UI or Code later - this is which joint to add diff rotate orders to 
        self.zyx = [2]
        self.createIK = True

    def set_values_code(self):
        """set all relevant values from code"""
        pass

    # add pts here as args instead of in init ( this is so we can call this from code)
    # add basenames here instead of in init
    # clean up options for wrist (instead of just zyx, make it more general)
    def pose_initial_joints(self):
    # get and pass values for orient order and uporient axis
    # put joint in ref display layer temporarily
        self.joints = zrt.create_joint_chain(self.pts, self.baseNames, self.orientOrder, self.upOrientAxis)

        self.poseCtrls, self.poseGrps, self.octrls, self.ogrps = zrt.create_controls_at_joints(self.joints[:-1], "sphere", self.mainAxis, "poseCTRL", orient=True, upAxis="y")
        lockAttrs = ["s","tx", "ty", "tz"]

        ctrlHierList = zip(self.poseCtrls, self.poseGrps, self.joints, self.octrls, self.ogrps)
        self.poseConstraints = []
        for i in range(len(ctrlHierList)):
            if i>0:
                oc = cmds.orientConstraint(ctrlHierList[i-1][2], ctrlHierList[i][1], mo=False)[0]
                self.poseConstraints.append(oc)
            for attr in lockAttrs:
                cmds.setAttr("{0}.{1}".format(ctrlHierList[i][0], attr), l=True)
            if i==1:
                cmds.setAttr("{0}.rx".format(ctrlHierList[i][0]), l=True)
                cmds.setAttr("{0}.ry".format(ctrlHierList[i][0]), l=True)
                cmds.setAttr("{0}.rz".format(ctrlHierList[i][0]), l=True)
                cmds.setAttr("{0}.r{1}".format(ctrlHierList[i][0], self.upAxis), l=False)

            cmds.setAttr("{0}.t{1}".format(ctrlHierList[i][0], self.mainAxis), l=False)

            oc1 = cmds.orientConstraint(self.joints[i], ctrlHierList[i][4], mo=False)
            cmds.delete(oc1)
            const = cmds.parentConstraint(ctrlHierList[i][0], ctrlHierList[i][2], mo=True)[0]
            self.poseConstraints.append(const)

        zrt.parent_hierarchy_grouped_controls(self.poseCtrls, self.poseGrps)

    def make_limb_rig(self):
        self.clean_initial_joints()
        # add manual adjust joint orientation here. . .
        self.mirror_joints()
        self.setup_dictionary()        
        self.create_duplicate_chains()
        self.setup_fk_rig()


    def clean_initial_joints(self):

    #take joints out of display layer and delete display layer

        #delete all constraints from the pose
        cmds.delete(self.poseConstraints)
        # unlock octrl attrs
        attrs = ["t", "rx", "ry", "rz"]

        for i in range(len(self.octrls)):
            for attr in attrs:
                cmds.setAttr("{0}.{1}".format(self.octrls[i], attr), l=False)
            zrt.orient_joint_to_transform(self.joints[i], self.octrls[i])

    # save scale info from ctrls - still need to make a scalable control
        cmds.delete(self.poseGrps[0])

        for jnt in self.joints:
            cmds.makeIdentity(jnt, apply=True)

        # delete end joint and remove from lists
        cmds.delete(self.joints[-1])
        self.joints = self.joints[:-1]

        # maybe store the scale on the joint itself? Then delete it later. . . 
        for jnt in self.joints:
            name = zrt.name_object(jnt, self.origPrefix, jnt, "FK", self.jntSuffix)
            self.origFkJnts.append(name)
            
        # set rotate orders on listed jnts
        for i in self.zyx:
            cmds.joint(self.origFkJnts[i], edit=True, rotationOrder="zyx")


    def mirror_joints(self):

    # if mirror. . . 
    # get prefixes. . . 
        self.mirrorFkJnts = zrt.mirror_joint_chain(self.origFkJnts[0], self.origPrefix, self.mirPrefix, self.mirrorAxis)


    def setup_dictionary(self):

        self.jntDict = {}
        self.jntDict["orig"] = {}
        self.jntDict["orig"]["fk"] = self.origFkJnts
        if self.mirrorFkJnts:
            self.jntDict["mir"] = {}
            self.jntDict["mir"]["fk"] = self.mirrorFkJnts


    def create_duplicate_chains(self):

        # for key in jntDict, make duplicates. . . (put into dictionary)
        for side in self.jntDict.keys():
            topJnt = self.jntDict[side]["fk"][0]
            
            # make deform jnts
            deforms = zrt.duplicate_and_rename_chain(topJnt, "deform")
            self.jntDict[side]["deform"] = deforms   
            
            # if we're making IK stuff
            if self.createIK:
                # make IK
                iks = zrt.duplicate_and_rename_chain(topJnt, "IK")
                self.jntDict[side]["ik"] = iks
                # make measure
                measures = zrt.duplicate_and_rename_chain(topJnt, "measure")
                self.jntDict[side]["measure"] = measures


    def setup_fk_rig(self):
        pass


    def connect_deform_joints(self):
        # create fkik switch
        for side in self.jntDict.keys():
            targetJnt = jntDict[side]["deform"][2]

        pass

    # build FKIK switch
    # bulld FK ctrls - put into fk dict key - use zip to connect?
    # build IK ctrls - put into ik dict key (pv and ik ctrl)
    # set up IK
    # setup twist attributes - connect them

    #set up blends for all self.joints (traslate, rotate, scale)

    # package up components


