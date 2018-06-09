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

# a control on the switch that can drive the rotation order of all the things for each "part" (shldr, elbow, etc-->xyz changes all of the parts of that rig)
# MAYBE COMBINE THOUGHTS: self.fkCtrls = {[lf_fk-Ctrls], [rt_fk_ctrls]}
    def set_values_UI(self):
        """ grab all relevant values from UI"""
        #from ui. . . 
        self.pts=[(5,20, 0),(15, 20, -1), (25, 20, 0), (27, 20, 0)]
        self.part = "arm"
        self.baseNames=["shoulder", "elbow", "wrist", "wristEnd"]
        self.origPrefix = "lf"
        self.mirror = True
        if self.mirror:
            self.mirPrefix = "rt"
        self.primaryAxis = "x"
        self.upAxis = "y"
        self.tertiaryAxis = "z"
        # below needs to be created from main axis (ie. "x")
        self.orientOrder = "xyz"
        self.upOrientAxis = "yup"

        # initialize variables
        self.side = {}
        self.fkJoints = {}
        self.fkCtrls = {}
        self.fkCtrlGrps = {}
        self.ikJoints = {}
        self.ikCtrls = {}
        self.ikCtrlGrps = {}
        self.measureJoints = {}
        self.deformJoints = {}
        self.switchCtrls = {}

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

        self.poseCtrls, self.poseGrps, self.octrls, self.ogrps = zrt.create_controls_and_orients_at_joints(self.joints[:-1], "sphere", self.primaryAxis, "poseCTRL", orient=True, upAxis="y")
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

            cmds.setAttr("{0}.t{1}".format(ctrlHierList[i][0], self.primaryAxis), l=False)

            oc1 = cmds.orientConstraint(self.joints[i], ctrlHierList[i][4], mo=False)
            cmds.delete(oc1)
            const = cmds.parentConstraint(ctrlHierList[i][0], ctrlHierList[i][2], mo=True)[0]
            self.poseConstraints.append(const)

        zrt.parent_hierarchy_grouped_controls(self.poseCtrls, self.poseGrps)

    def make_limb_rig(self):
        """
        instructions to make the limb
        """
        self.create_initial_components()
        self.clean_initial_joints()
        # add manual adjust joint orientation here. . .
        if self.mirror:
            self.mirror_joints()
        self.setup_dictionaries()        
        self.create_duplicate_chains()
        self.setup_fk_rig()
        self.create_fkik_switch()

    def create_initial_components(self):
        # create groups and hierarchy
        pass


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

# delete end joint and remove from lists (maybe don't do this? )
        cmds.delete(self.joints[-1])
        self.joints = self.joints[:-1]

    # maybe store the scale on the joint itself? Then delete it later. . . 
        for jnt in self.joints:
            name = zrt.name_object(jnt, self.origPrefix, jnt, "FK", self.jntSuffix)
            self.origFkJnts.append(name)
            
    # set rotate orders on listed jnts
        for i in self.zyx:
            cmds.joint(self.origFkJnts[i], edit=True, rotationOrder="zyx")

    # store orient data on joints for serialization. . . ?

    def mirror_joints(self):
        self.mirrorFkJnts = zrt.mirror_joint_chain(self.origFkJnts[0], self.origPrefix, self.mirPrefix, self.mirrorAxis)


    def setup_dictionaries(self):
        """initialize dictionaries for the actual rig content"""
        self.side["orig"] = self.origPrefix
        self.fkJoints["orig"] = self.origFkJnts
        self.fkCtrls["orig"] = None
        self.fkCtrlGrps["orig"] = None
        self.switchCtrls["orig"] = None
        if self.mirror:
            self.side["mir"] = self.mirPrefix
            self.fkJoints["mir"] = self.mirrorFkJnts
            self.fkCtrls["mir"] = None
            self.fkCtrlGrps["mir"] = None
            self.switchCtrls["mir"] = None


    def create_duplicate_chains(self):
        # for key in jntDict, make duplicates. . . (put into dictionary)
        for side in self.fkJoints.keys():
            topJnt = self.fkJoints[side][0] 
            #self.jntDict[side]["fk"][0]
            
            # make deform jnts
            deforms = zrt.duplicate_and_rename_chain(topJnt, "deform")
            self.deformJoints[side] = deforms
            # self.jntDict[side]["deform"] = deforms   
            
            # if we're making IK stuff
            if self.createIK:
                # make IK
                iks = zrt.duplicate_and_rename_chain(topJnt, "IK")
                self.ikJoints[side] = iks
                # self.jntDict[side]["ik"] = iks
                # make measure
                measures = zrt.duplicate_and_rename_chain(topJnt, "measure")
                self.measureJoints[side] = measures
                # self.jntDict[side]["measure"] = measures


    def setup_fk_rig(self):

        for side in self.fkJoints.keys():
            fkJoints = self.fkJoints[side]
            ctrls = []
            grps = []
            for jnt in fkJoints:
                ctrl, grp = zrt.create_control_at_joint(jnt, "cube", self.primaryAxis, "{0}_FK_{1}_CTRL".format(self.side[side], jnt.split("_")[1]))
                ctrls.append(ctrl)
                grps.append(grp)
            zrt.parent_hierarchy_grouped_controls(ctrls, grps)

            #add to dictionaries
            self.fkCtrls[side] = ctrls
            self.fkCtrlGrps[side] = grps

        # should we keep track of these constraints?
            for i in range(len(fkJoints)):
                pc = cmds.parentConstraint(ctrls[i], fkJoints[i])
                sc = cmds.scaleConstraint(ctrls[i], fkJoints[i])
        # create group for arm to go in


    def create_fkik_switch(self):
        for side in self.deformJoints.keys():
            # this defaults to the third joint in chain
            targetJnt = self.deformJoints[side][2]
            ctrl, grp = zrt.create_control_at_joint([targetJnt], "star", self.primaryAxis, "{0}_{1}_IkFkSwitch_CTRL".format(self.side[side], self.part))

            # offset it to the side (based on scale from FK wrist ctrl)
            #get scale factor
            amt = -5
            if self.tertiaryAxis=="x":
                mv=(amt, 0 , 0)
            if self.tertiaryAxis=="y":
                mv=(0, amt, 0)
            else:
                mv=(0, 0, amt)
            cmds.xform(grp, r=True, ws=True, t=mv)
            rig.stripTransforms(ctrl)
            cmds.addAttr(ctrl, ln="fkik", at="float", min=0.0, max=1.0, defaultValue=0.0, keyable=True)

        # save this constraint?
            pc = cmds.parentConstraint(self.deformJoints[side][2], grp, mo=True)

            self.switchCtrls[side] = ctrl


    def build_ik_rig(self):
        pass


    def connect_deform_joints(self):
        pass
    # build IK ctrls - put into ik dict key (pv and ik ctrl)
    # set up IK - should it be translate? 
    # setup twist attributes - connect them

    # option for ribbon setup in here? 

    #set up blends for all self.joints (traslate, rotate, scale)

    # package up components

    # bind joints for QSS (different if ribbon or just twist)
    # add option for game exportable joints QSS 
