import maya.cmds as cmds
import python_rigger.rigger_tools.rigger_tools as zrt
reload(zrt)
import zTools.rig.zbw_rig as rig
reload(rig)
import maya.OpenMaya as om

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
        
        # turn on decompose matrix plugin

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
        self.twist = True
        self.twistNum = 2

        # initialize variables
        self.side = {}
        self.fkJoints = {}
        self.fkCtrls = {}
        self.fkCtrlGrps = {}
        self.ikJoints = {}
        self.ikCtrls = {}
        self.ikCtrlGrps = {}
        self.ikHandles = {}
        self.measureJoints = {}
        self.deformJoints = {}
        self.switchCtrls = {}
        self.twistJoints = {}
        self.sideGroups = {}

        self.jntSuffix = "JNT"
        self.mirrorAxis = "yz"
        # this can be gotten in UI or Code later - this is which joint to add diff rotate orders to 
        self.zyx = [2]
        self.createIK = True

    def set_values_code(self):
        """set all relevant values from code"""
    # add pts here as args instead of in init ( this is so we can call this from code)
    # add basenames here instead of in init
    # clean up options for wrist (instead of just zyx, make it more general)
        pass


    def pose_initial_joints(self):
    # get and pass values for orient order and uporient axis
    # put joint in ref display layer temporarily
        self.joints, self.poseCtrls, self.poseGrps, self.octrls, self.ogrps, self.poseConstraints = zrt.initial_pose_joints(ptsList=self.pts, baseNames=self.baseNames, orientOrder=self.orientOrder, upOrientAxis=self.upOrientAxis, primaryAxis=self.primaryAxis, upAxis=self.upAxis)

        # put tmp joints in a display layer and set to reference
        cmds.select(self.joints, r=True)
        self.dl = cmds.createDisplayLayer(name="tmp_{0}_jnt_DL".format(self.part))
        cmds.setAttr("{0}.displayType".format(self.dl), 2)


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
        self.create_fk_rig()
        self.create_fkik_switch()
        self.connect_deform_joints()
        self.create_ik_rig()
        self.create_ik_stretch()
        self.create_rigSide_groups()
        if self.twist:
            self.create_twist_extraction_rig()
        self.create_ik_group()
        self.clean_up_rig()
        self.create_sets()


    def create_initial_components(self):
        # create groups and hierarchy
        pass


    def clean_initial_joints(self):
        cmds.delete(self.dl)

        self.origFkJnts = zrt.clean_pose_joints(self.joints, self.poseConstraints, self.octrls, self.poseGrps[0], self.origPrefix, self.jntSuffix, deleteEnd=True)

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
        self.ikCtrls["orig"] = None
        self.ikCtrlGrps["orig"] = None
        self.sideGroups["orig"] = None
        self.twistJoints["orig"] = []
        if self.mirror:
            self.side["mir"] = self.mirPrefix
            self.fkJoints["mir"] = self.mirrorFkJnts
            self.fkCtrls["mir"] = None # []
            self.fkCtrlGrps["mir"] = None
            self.switchCtrls["mir"] = None # []
            self.ikCtrls["mir"] = None # [ikCtrl, pvCtrl, pvLine]
            self.ikCtrlGrps["mir"] = None  # [ikCtrlGrp, pvCtrlGrp, pvLineGrp]
            self.sideGroups["mir"] = None   # [lf_arm_GRP, lf_arm_attach_GRP]
            self.twistJoints["mir"] = []   # [lf_arm_upTwist1_JNT, etc]


    def create_duplicate_chains(self):
        # for key in jntDict, make duplicates. . . (put into dictionary)
        for side in self.fkJoints.keys():
            topJnt = self.fkJoints[side][0] 
          
            # make deform jnts
            deforms = zrt.duplicate_and_rename_chain(topJnt, "deform")
            self.deformJoints[side] = deforms
            
            # if we're making IK stuff
            if self.createIK:
                # make IK
                iks = zrt.duplicate_and_rename_chain(topJnt, "IK")
                self.ikJoints[side] = iks
                # make measure
                measures = zrt.duplicate_and_rename_chain(topJnt, "measure")
                self.measureJoints[side] = measures


    def create_fk_rig(self):
        for side in self.fkJoints.keys():
            fkJoints = self.fkJoints[side]
            ctrls = []
            grps = []
            for jnt in fkJoints:
                ctrl, grp = zrt.create_control_at_joint(jnt, "cube", self.primaryAxis, "{0}_FK_{1}_CTRL".format(self.side[side], jnt.split("_")[1]))
                ctrls.append(ctrl)
                grps.append(grp)
            zrt.parent_hierarchy_grouped_controls(ctrls, grps)

            self.fkCtrls[side] = ctrls
            self.fkCtrlGrps[side] = grps

        # should we keep track of these constraints?
            for i in range(len(fkJoints)):
                pc = cmds.parentConstraint(ctrls[i], fkJoints[i])
                sc = cmds.scaleConstraint(ctrls[i], fkJoints[i])
        
        # add gimble ctrls? just a group and control above each ctrl 
        # create group for arm to go in


    def create_fkik_switch(self):
        for side in self.deformJoints.keys():
            # this defaults to the third joint in chain
            ctrl = rig.createControl(name="{0}_{1}_IkFkSwitch_CTRL".format(self.side[side], self.part), type="star", axis=self.primaryAxis)
            grp = rig.groupFreeze(ctrl)
        #get scale factor
            root = cmds.xform(self.deformJoints[side][0], q=True, ws=True, rp=True)
            mid = cmds.xform(self.deformJoints[side][1], q=True, ws=True, rp=True)
            end = cmds.xform(self.deformJoints[side][2], q=True, ws=True, rp=True)
            distVec = om.MVector(mid[0]-end[0], mid[1]-end[1], mid[2]-end[2])
            dist = distVec.length()
            mv = zrt.get_planar_position(root, mid, end, percent=0.05, dist=dist)
            rig.snapTo(self.deformJoints[side][2], grp)
            cmds.xform(grp, ws=True, t=(mv.x, mv.y, mv.z))
            
            rig.stripTransforms(ctrl)
            cmds.addAttr(ctrl, ln="fkik", at="float", min=0.0, max=1.0, defaultValue=0.0, keyable=True)

        # save this constraint?
            pc = cmds.parentConstraint(self.deformJoints[side][2], grp, mo=True)

            self.switchCtrls[side] = ctrl


    def create_ik_rig(self):
        for side in self.ikJoints.keys():
            jnts = self.ikJoints[side]
            if side == "orig":
                name = "{0}_{1}_IK".format(self.origPrefix, self.part)
            elif side == "mir":
                name = "{0}_{1}_IK".format(self.mirPrefix, self.part)

            handle = cmds.ikHandle(startJoint=jnts[0], endEffector=jnts[2], name=name, solver="ikRPsolver")[0]
            cmds.setAttr("{0}.visibility".format(handle), 0)
            ctrl, grp = zrt.create_control_at_joint(jnts[2], "arrowCross", self.primaryAxis, "{0}_CTRL".format(name))
            cmds.parent(handle, ctrl)
            oc = cmds.orientConstraint(ctrl, jnts[2], mo=True)
            self.ikCtrls[side] = [ctrl]
            self.ikCtrlGrps[side] = [grp] 
        # scale the control
            # create pole vec
            if side == "orig":
                pvname = "{0}_{1}_poleVector_CTRL".format(self.origPrefix, self.part)
            elif side == "mir":
                pvname = "{0}_{1}_poleVector_CTRL".format(self.mirPrefix, self.part)
            pv = rig.createControl(name=pvname, type="sphere", color="red", axis="x")
            self.ikCtrls[side].append(pv)
            pvgrp = rig.groupFreeze(pv)
            self.ikCtrlGrps[side].append(pvgrp)

            # place and constrain pole vec
            cmds.select(handle, r=True)
            pos = zrt.find_pole_vector_location(handle)
            cmds.xform(pvgrp, ws=True, t=(pos[0], pos[1], pos[2]))
            pvc = cmds.poleVectorConstraint(pv, handle)
        # save constraint?
            # add crv lines from shoulder to pv
            if side == "orig":
                pvline = "{0}_{1}_poleVec_Line".format(self.origPrefix, self.part)
            elif side == "mir":
                pvline = "{0}_{1}_poleVec_Line".format(self.mirPrefix, self.part)        
            pvLine = zrt.create_line_between(pv, jnts[1], "{0}".format(pvline))
            pvGrp = cmds.group(em=True, name="{0}_GRP".format(pvLine))
            cmds.parent(pvLine, pvGrp)
            self.ikCtrls[side].append(pvLine)
            self.ikCtrlGrps[side].append(pvGrp)
            # set line as reference override
            shp = cmds.listRelatives(pvLine, s=True)[0]
            cmds.setAttr("{0}.overrideEnabled".format(shp), 1)
            cmds.setAttr("{0}.overrideDisplayType".format(shp), 2)
            #connect to switch
            cmds.addAttr(self.switchCtrls[side], ln="poleVecLine", at="short", min=0, max=1, dv=1, k=True)
            cmds.connectAttr("{0}.poleVecLine".format(self.switchCtrls[side]), "{0}.overrideVisibility".format(shp))
        # option for no flip pv?
        # option to create follow spaces? (pv follow ik ctrl)

    def connect_deform_joints(self):
        # zip up fk, ik and deform joints for easier stuff
        for side in self.fkJoints.keys():
            joints = zip(self.fkJoints[side], self.ikJoints[side], self.deformJoints[side])
            # should we parent constraint these? 
            for grp in joints:
                zrt.create_parent_reverse_network(grp[:-1], grp[-1], "{0}.fkik".format(self.switchCtrls[side]), index=0)

    # a way to do gimbles in both ik and fk? create gimbel ctrl under grp. grp is parent constrained to ik/fk ctrls (like deform joint). ctrl then is what parent constrains to the deform joints

    def create_ik_stretch(self):
        # LET"S DO THIS SCALE-WISE FOR NOW
        for side in self.ikJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            self.upMult, self.loMult = zrt.create_stretch_setup(self.measureJoints[side], self.ikCtrls[side][0], "{0}_{1}".format(sideName, self.part))
        # should do twist stuff first? Need to add twist joints to ik? or just have a separate twist dict?
            cmds.connectAttr("{0}.output.outputX".format(self.upMult), "{0}.sx".format(self.ikJoints[side][0]))
            cmds.connectAttr("{0}.output.outputX".format(self.loMult), "{0}.sx".format(self.ikJoints[side][1]))


    def create_rigSide_groups(self):
        for side in self.fkJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix
            sideGrp = cmds.group(em=True, name="{0}_{1}_GRP".format(sideName, self.part))
            pos = cmds.xform(self.fkJoints[side][0], q=True, ws=True, rp=True)
            rot = cmds.xform(self.fkJoints[side][0], q=True, ws=True, ro=True)
            cmds.xform(sideGrp, ws=True, t=pos)
            cmds.xform(sideGrp, ws=True, ro=rot)

            attachGrp = cmds.duplicate(sideGrp, name="{0}_{1}_attach_GRP".format(sideName, self.part))[0]

            cmds.parent(sideGrp, attachGrp)
            sideList =[self.fkJoints[side][0], self.ikJoints[side][0], self.measureJoints[side][0], self.deformJoints[side][0], self.fkCtrlGrps[side][0]]

            cmds.parent(sideList, sideGrp)

            self.sideGroups[side] = [sideGrp, attachGrp]


    def create_twist_extraction_rig(self):
        for side in self.deformJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            upTwistAttr = zrt.create_twist_extractor(rotJnt=self.deformJoints[side][0], tgtCtrl=self.switchCtrls[side], parObj=self.sideGroups[side][0], tgtAttr="upperTwist")

            twistJointsUp = zrt.create_twist_joints(self.twistNum, self.deformJoints[side][0], self.deformJoints[side][0], self.deformJoints[side][1], upTwistAttr, "{0}_{1}_up".format(sideName, self.part), self.primaryAxis, reverse=True)
            for jnt in twistJointsUp:
                self.twistJoints[side].append(jnt)
            # add locator parented to elbow

            loTwistAttr = zrt.create_twist_extractor(rotJnt=self.deformJoints[side][2], tgtCtrl=self.switchCtrls[side], parObj=self.deformJoints[side][1], tgtAttr="lowerTwist")

            twistJointsLo = zrt.create_twist_joints(self.twistNum, self.deformJoints[side][2], self.deformJoints[side][1], self.deformJoints[side][2], loTwistAttr, "{0}_{1}_low".format(sideName, self.part), self.primaryAxis, reverse=False)
            for jnt in twistJointsLo:
                self.twistJoints[side].append(jnt)
            # add locator parented to elbow twist of each

        # add locator at actual elbow that is parent of other two

        # connect twist joints into scale? or not necessary?
        # add twist joints to deform joints list? 


    # mult stretch stuff by all ik joints?

    # add attr for switch ctrl to drive the rot orders of each part (all the ctrls and joints)



    # figure out how to tie up master ctrl (scale)

    # package up cmponents, color controls, hide jnts, etc
    def create_ik_group(self):
        ikName = "ik_world_rig_GRP"
        if not cmds.objExists(ikName):
            ikGrp = cmds.group(em=True, name=ikName)

        for side in self.fkJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            ikStuff = [self.ikCtrlGrps[side], cmds.listRelatives(self.switchCtrls[side], p=True)[0]]

            for stuff in ikStuff:
                cmds.parent(stuff, ikGrp)


    def clean_up_rig(self):
    # clean up rig (hide jnts, connect vis, etc)
        # hide jnts
        for side in self.fkJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            hideJnts = [self.ikJoints[side][0], self.fkJoints[side][0], self.measureJoints[side][0]]
            for obj in hideJnts:
                cmds.setAttr("{0}.v".format(obj), 0)
        # no inherit stuff? 
            if not cmds.objExists("rig_noInherit_GRP"):
                noInher = cmds.group(em=True, name="rig_noInherit_GRP")
                cmds.setAttr("{0}.inheritsTransform".format(noInher), 0)
            cmds.parent(self.ikCtrlGrps[side][2], noInher)
        
        # color controls
            #how to do this? color attr from UI? 
            if side == "orig":
                color = "red"
                secColor = "pink"
            if side == "mir":
                color = "blue"
                secColor = "lightBlue"

            primColor = [self.fkCtrls[side], [self.ikCtrls[side][0]]]
            lightColor = [self.ikCtrls[side][1:], [self.switchCtrls[side]]]

            for obj in primColor:
                for ctrl in obj: 
                    rig.assignColor(obj=ctrl, clr=color)
            for obj in lightColor:
                for ctrl in obj:
                    rig.assignColor(obj=ctrl, clr=secColor)

        # set up visibility switching
            ikStuff = [self.ikCtrlGrps[side][0], self.ikCtrlGrps[side][1], self.ikCtrlGrps[side][2]]
            fkStuff = [self.fkCtrlGrps[side][0]]

            self.switchReverse = cmds.shadingNode("reverse", asUtility=True, name="{0}_{1}_ikfkVis_reverse".format(sideName, self.part))
            cmds.connectAttr("{0}.fkik".format(self.switchCtrls[side]), "{0}.input.inputX".format(self.switchReverse))
            for obj in fkStuff:
                cmds.connectAttr("{0}.output.outputX".format(self.switchReverse), "{0}.v".format(obj))
            for obj in ikStuff:
                cmds.connectAttr("{0}.fkik".format(self.switchCtrls[side]), "{0}.v".format(obj))


    def create_sets(self):
        # set for all controls
        ctrlSet = "CTRL_SET"
        bindSet = "BIND_SET"
        if not cmds.objExists(ctrlSet):
            cmds.sets(name="CTRL_SET", em=True)
        if not cmds.objExists(bindSet):
            cmds.sets(name="BIND_SET", em=True)

        for side in self.fkJoints.keys():
            if side == "orig":
                sideName = self.origPrefix
            if side == "mir":
                sideName = self.mirPrefix

            ctrls = [self.fkCtrls[side], self.ikCtrls[side][:2], self.switchCtrls[side]]
            for ctrlList in ctrls:
                cmds.sets(ctrlList, addElement="CTRL_SET")
            # bind joints set
    # if ribbon or ikSpline is added, remove these joints and add those
            jnts = [self.deformJoints[side][2:], self.twistJoints[side]]
            for jntList in jnts:
                cmds.sets(jntList, addElement="BIND_SET")



    # add in game export rig
    # add option for game exportable joints QSS 
    # option for ribbon setup in here? 