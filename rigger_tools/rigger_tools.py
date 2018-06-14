import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
reload(rig)
import maya.OpenMaya as om


def create_joint_chain(ptList=None, baseNames=None, alongAxis="xyz", upAxis="yup"):
    cmds.select(cl=True)
    jntList = []
    for i in range(len(ptList)):
        jnt = cmds.joint(name=baseNames[i], p=ptList[i])
        jntList.append(jnt)
    
    orient_joint_chain(jntList[0], alongAxis, upAxis)

    return(jntList)


def orient_joint_to_transform(jnt, obj):

    children = cmds.listRelatives(jnt, c=True, fullPath=True, ad=False)[0]
    newChildren = cmds.parent(children, world=True, absolute=True) # to get new names
    dupe = cmds.duplicate(obj)
    if cmds.listRelatives(jnt, p=True):
        newDupe = cmds.parent(dupe, cmds.listRelatives(jnt, p=True)[0])[0]
    else:
        newDupe = cmds.parent(dupe, world=True)[0]
    rot = cmds.xform(newDupe, q=True, objectSpace=True, rotation=True)
    cmds.delete(newDupe)
    cmds.setAttr("{0}.rotate".format(jnt), 0, 0, 0)
    cmds.setAttr("{0}.rotateAxis".format(jnt), 0, 0 , 0)
    cmds.setAttr("{0}.jointOrient".format(jnt), rot[0], rot[1], rot[2])
    cmds.parent(newChildren, jnt)


def orient_joint_chain(joint=None, alongAxis="xyz", upAxis="yup"):
    cmds.joint(joint, e=True, orientJoint=alongAxis, children=True, secondaryAxisOrient=upAxis, zso=True )


# rename joint chain
def name_object(obj, side=None, part=None, chain=None, typeSuf=None):
    """lf_shoulder_IK_JNT"""
# MAYBE JUST DO THIS WITH *ARGS AT END? 
    newName = "{0}_{1}_{2}_{3}".format(side, part, chain, typeSuf)
    name = cmds.rename(obj, newName)
    return(name)


def get_chain_hierarchy(topJoint=None):
    cmds.select(topJoint, r=True, hi=True)
    chain = cmds.ls(sl=True)
    return(chain)


def mirror_joint_chain(topJoint, oldSidePrefix=None, newSidePrefix=None, axis="yz"):
    """axis is mirror plane (xy, xz, yz)"""
    mirrored_chain = []
    if axis=="xy":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorXY=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    if axis=="xz":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorXZ=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    if axis=="yz":
        mirrored_chain = cmds.mirrorJoint(topJoint, mirrorYZ=True, searchReplace=[oldSidePrefix, newSidePrefix], mirrorBehavior=True)
    return(mirrored_chain)


def duplicate_and_rename_chain(topJnt, chain):
    """chain is string name of this chain (i.e. 'IK', 'measure', etc)"""
    dupe = cmds.duplicate(topJnt, renameChildren=True)
    newChainList = []
    for jnt in dupe:
        tokens = jnt.split("_")
        if tokens[3][-1].isdigit():
            tokens[3] = tokens[3][:-1]
        renamed = name_object(jnt, tokens[0], tokens[1], chain, tokens[3])
        newChainList.append(renamed)

    return(newChainList)


# set up blend procedures for blending joints
# THINK ABOUT HOW TO DEAL WITH INDIVIDUAL ATTRS, but not TONS of paras, do we need it?
def create_blend_network(name, oneAttr, twoAttr, blendAttr, targetAttr):
    """ 
        name is string
        targetAttr is triple
    """
    blend = cmds.shadingNode("blendColors", asUtility=True, name=name)
    cmds.connectAttr(oneAttr, "{0}.color1".format(blend))
    cmds.connectAttr(twoAttr, "{0}.color2".format(blend))
    cmds.connectAttr(blendAttr, "{0}.blender".format(blend))
    cmds.connectAttr("{0}.output".format(blend), targetAttr)

    return(blend)


def create_orient_reverse_network(srcList, tgt, switchAttr, index=0):
    """
    create orient constraint to A, B, which is reversed
    """
    oc = cmds.orientConstraint(srcList, tgt, mo=False)[0]
    if index == 0:
        cmds.connectAttr(switchAttr, "{0}.w1".format(oc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w0".format(oc))
    elif index == 1:
        cmds.connectAttr(switchAttr, "{0}.w0".format(oc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w1".format(oc))
    return(oc)


def create_parent_reverse_network(srcList, tgt, switchAttr, index=0):
    """
    create parent constraint to A, B, which is reversed
    """
    pc = cmds.parentConstraint(srcList, tgt, mo=False)[0]
    if index == 0:
        cmds.connectAttr(switchAttr, "{0}.w1".format(pc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w0".format(pc))
    elif index == 1:
        cmds.connectAttr(switchAttr, "{0}.w0".format(pc))
        create_reverse_network(tgt, switchAttr, "x", "{0}.w1".format(pc))
    return(pc)


def create_scale_reverse_network():
    pass


def create_reverse_network(name,  inputAttr, revAttr, targetAttr):
    """revAttr should be 'all', 'x', 'y' or 'z'"""
    reverse = cmds.shadingNode("reverse", asUtility=True, name=name+"_reverse")
    if revAttr=="all":
        cmds.connectAttr(inputAttr, "{0}.input".format(reverse))
        cmds.connectAttr("{0}.output".format(reverse), targetAttr)
    if revAttr=="x":
        cmds.connectAttr(inputAttr, "{0}.input.inputX".format(reverse))
        cmds.connectAttr("{0}.output.outputX".format(reverse), targetAttr)
    if revAttr=="y":
        cmds.connectAttr(inputAttr, "{0}.input.inputY".format(reverse))        
        cmds.connectAttr("{0}.output.outputY".format(reverse), targetAttr)
    if revAttr=="z":
        cmds.connectAttr(inputAttr, "{0}.input.inputZ".format(reverse))
        cmds.connectAttr("{0}.output.outputZ".format(reverse), targetAttr)
    return(reverse)


def create_control_at_joint(jnt, ctrlType, axis, name):
    """orient will create a new control UNDER the ctrl that we can use to  orient pose joints"""
    ctrl = rig.createControl(name, ctrlType, axis)
    grp = rig.groupFreeze(ctrl)
    rotOrder = cmds.xform(jnt, q=True, roo=True)
    cmds.xform(ctrl, roo=rotOrder)
    cmds.xform(grp, roo=rotOrder)
    rig.snapTo(jnt, grp)

    return(ctrl, grp)


def create_controls_and_orients_at_joints(jntList, ctrlType, axis, suffix, orient=False, upAxis="y"):
    """orient will create a new control UNDER the ctrl that we can use to  orient pose joints"""
    ctrls = []
    groups = []
    octrls = []
    ogrps = []
    for jnt in jntList:
        if "_" in jnt:
            name = "_".join(jnt.split("_")[:-1]) + "_{0}".format(suffix)
            oname = "_".join(jnt.split("_")[:-1]) + "_{0}".format("ORIENT"+suffix)
        else:
            name = "{0}_{1}".format(jnt, suffix)
            oname = "{0}_{1}".format(jnt, "ORIENT"+suffix)
        ctrl = rig.createControl(name, ctrlType, axis)
        grp = rig.groupFreeze(ctrl)
        rig.snapTo(jnt, grp)
        ctrls.append(ctrl)
        groups.append(grp)
        if orient:
            octrl = rig.createControl(oname, "arrow", upAxis) # FLIP THIS IN AXIS
            rig.stripToRotate(octrl)
            cmds.setAttr("{0}.ry".format(octrl), l=True)
            cmds.setAttr("{0}.rz".format(octrl), l=True)
            ogrp = rig.groupFreeze(octrl)
            rig.snapTo(jnt, ogrp)
            cmds.parent(ogrp, ctrl)
            octrls.append(octrl)
            ogrps.append(ogrp)

    if not orient:
        return(ctrls, groups)
    else:
        return(ctrls, groups, octrls, ogrps)


def parent_hierarchy_grouped_controls(ctrls, grps):
    """assumes in order from top to bottom, groups are parents of controls"""
    if not len(ctrls)==len(grps) or len(ctrls)<2:
        cmds.warning("riggerTools.parent_hierarchy_grouped_controls: lists don't match in length or aren't long enough")
        return()

    for x in range(1, len(grps)):
        cmds.parent(grps[x], ctrls[x-1])


# SEPARATE THIS INTO TWO FUNCTIONS (ONE FOR PV SPECIFICALLY, THE OTHER TO JUST FIND THE PLANE)
def find_pole_vector_location(handle):
    # arg is ikHandle
    ikJntList = cmds.ikHandle(handle, q=True, jointList=True)
    ikJntList.append(cmds.listRelatives(ikJntList[-1], children=True, type="joint")[0])

    # get jnt positions
    rootPos = cmds.xform(ikJntList[0], q=True, ws=True, rp=True)
    midPos = cmds.xform(ikJntList[1], q=True, ws=True, rp=True)
    endPos = cmds.xform(ikJntList[2], q=True, ws=True, rp=True)

    poleVecPos = get_planar_position(rootPos, midPos, endPos)

    return(poleVecPos) 
    

def get_planar_position(rootPos, midPos, endPos, percent=None, dist=None):
    # convert to vectors
    rootVec = om.MVector(rootPos[0], rootPos[1], rootPos[2])
    midVec = om.MVector(midPos[0], midPos[1], midPos[2])
    endVec = om.MVector(endPos[0], endPos[1], endPos[2])
    
    # get vectors
    line = (endVec - rootVec)
    point = (midVec - rootVec)

    # get center-ish of rootEnd (relative to midjoint)
    if not percent:
        percent = (line*point)/(line*line)
    projVec = line * percent + rootVec
    
    if not dist:
        dist = (midVec-rootVec).length() + (endVec-midVec).length()
    poleVecPos = (midVec - projVec).normal() * dist + midVec
    
    return(poleVecPos)


def create_line_between(startXform, endXform, name):
    pos1 = [0,0,0]
    pos2 = [1,1,1]
    crv = cmds.curve(d=1, p=[pos1, pos2])
    crv = cmds.rename(crv, "{0}_CRV".format(name))

    dm1 = cmds.createNode("decomposeMatrix", name="{0}0_DM".format(name))
    dm2 = cmds.createNode("decomposeMatrix", name="{0}1_DM".format(name))

    cmds.connectAttr("{0}.worldMatrix".format(startXform), "{0}.inputMatrix".format(dm1))
    cmds.connectAttr("{0}.worldMatrix".format(endXform), "{0}.inputMatrix".format(dm2))

    cmds.connectAttr("{0}.outputTranslate".format(dm1), "{0}.controlPoints[0]".format(crv))
    cmds.connectAttr("{0}.outputTranslate".format(dm2), "{0}.controlPoints[1]".format(crv))

    return(crv)

def measure_chain_length(chainList, name):
    
    num = len(chainList)
    distNodes = []
    dmNodes = []
    for i in range(len(chainList)-1):
        if i==0:
            dm0 = cmds.createNode("decomposeMatrix", name="{0}{1}_0_DM".format(name, i))
            dmNodes.append(dm0)
            dm1 = cmds.createNode("decomposeMatrix", name="{0}{1}_1_DM".format(name, i))
            dmNodes.append(dm1)
        else:
            dm0 = dmNodes[-1]
            dm1 = cmds.createNode("decomposeMatrix", name="{0}{1}_0_DM".format(name, i))
            dmNodes.append(dm1)
            
        db = cmds.createNode("distanceBetween", name="{0}{1}_DB".format(name, i))
        
        if i==0:
            cmds.connectAttr("{0}.worldMatrix".format(chainList[i]), "{0}.inputMatrix".format(dm0))
        cmds.connectAttr("{0}.worldMatrix".format(chainList[i+1]), "{0}.inputMatrix".format(dm1))
        cmds.connectAttr("{0}.outputTranslate".format(dm0), "{0}.point1".format(db))
        cmds.connectAttr("{0}.outputTranslate".format(dm1), "{0}.point2".format(db))        

        distNodes.append(db)
        
    add = cmds.shadingNode("plusMinusAverage", asUtility=True, name="{0}_PMA".format(name))
    for i in range(len(distNodes)):
        cmds.connectAttr("{0}.distance".format(distNodes[i]), "{0}.input1D[{1}]".format(add, i))
    
    # returns the plusMinusAvg node, and the distance nodes
    return(add, distNodes)


def create_stretch_setup(measureJnts, ikCtrl, limbName):
    """
    note: returs only the mult nodes that you need to hook up to your joints
    """
    # get measure distances (x2)
    msrAdd, msrDists = measure_chain_length(measureJnts, "{0}_measure".format(limbName))
    # get ik to measure shoulder distance
    ikAdd, ikDist = measure_chain_length([measureJnts[0], ikCtrl], "{0}_ik".format(limbName))

    # check if ikCtrl has necessary attrs
    divider = cmds.attributeQuery("__stretch__", node=ikCtrl, exists=True)    
    upScale = cmds.attributeQuery("upScale", node=ikCtrl, exists=True)
    loScale = cmds.attributeQuery("loScale", node=ikCtrl, exists=True)
    autostretch = cmds.attributeQuery("autostretch", node=ikCtrl, exists=True)    
    
    if not divider:
        cmds.addAttr(ikCtrl, sn="__stretch__", at="enum", enumName="------", k=True)
        cmds.setAttr("{0}.__stretch__".format(ikCtrl), l=True)
    if not upScale:
        cmds.addAttr(ikCtrl, ln="upScale", at="float", dv=1, min=0.1, max=3, k=True)
    if not loScale:
        cmds.addAttr(ikCtrl, ln="loScale", at="float", dv=1, min=0.1, max=3, k=True)
    if not autostretch:
        cmds.addAttr(ikCtrl, ln="autostretch", at="float", dv=1, min=0, max=1.0, k=True)

    # create mult for up and down limb
    upMult1 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_up1_mult".format(limbName))
    loMult1 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_lo1_mult".format(limbName))
    
    # connect distance up/down to mults, connect ik ctrl up/down attrs to mults
    cmds.connectAttr("{0}.distance".format(msrDists[0]), "{0}.input1X".format(upMult1))
    cmds.connectAttr("{0}.distance".format(msrDists[1]), "{0}.input1X".format(loMult1))
    cmds.connectAttr("{0}.upScale".format(ikCtrl), "{0}.input2X".format(upMult1))
    cmds.connectAttr("{0}.loScale".format(ikCtrl), "{0}.input2X".format(loMult1))
    
    # connect mults to addNode (up/down)
    cmds.connectAttr("{0}.outputX".format(upMult1), "{0}.input1D[0]".format(msrAdd), f=True)
    cmds.connectAttr("{0}.outputX".format(loMult1), "{0}.input1D[1]".format(msrAdd), f=True)

    # create blend color, connect ikCtrl.autostretch to blender, add nodes out to blend.x (x2)
    asBlend = cmds.shadingNode("blendColors", asUtility=True, name="{0}_autostretchBlend".format(limbName))
    cmds.connectAttr("{0}.autostretch".format(ikCtrl), "{0}.blender".format(asBlend))
    cmds.connectAttr("{0}.output1D".format(msrAdd), "{0}.color2.color2R".format(asBlend))
    cmds.connectAttr("{0}.output1D".format(ikAdd), "{0}.color1.color1R".format(asBlend))

    # create multdiv ratio,blend.out to ratio1.x,up/down measure add to ratio2.x
    ratio = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_ratio_mult".format(limbName))
    cmds.setAttr("{0}.operation".format(ratio), 2)
    cmds.connectAttr("{0}.output.outputR".format(asBlend), "{0}.input1.input1X".format(ratio))
    cmds.connectAttr("{0}.output1D".format(msrAdd), "{0}.input2.input2X".format(ratio))

    # create condition node
    # ratio out x to cond first term, color if true
    # second term=1, color if Flase = 1
    cond = cmds.shadingNode("condition", asUtility=True, name="{0}_stretchCond".format(limbName))
    cmds.connectAttr("{0}.output.outputX".format(ratio), "{0}.firstTerm".format(cond))
    cmds.connectAttr("{0}.output.outputX".format(ratio), "{0}.colorIfTrue.colorIfTrueR".format(cond))
    cmds.setAttr("{0}.operation".format(cond), 2)
    cmds.setAttr("{0}.secondTerm".format(cond), 1)
    cmds.setAttr("{0}.colorIfFalse.colorIfFalseR".format(cond), 1)

    # create mult for up/down limbs
    upMult2 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_up2_mult".format(limbName))
    loMult2 = cmds.shadingNode("multiplyDivide", asUtility=True, name="{0}_lo2_mult".format(limbName))
    # out color of cond to mults 1x,up/down scale from ikCtrl to mult2
    cmds.connectAttr("{0}.outColor.outColorR".format(cond), "{0}.input1.input1X".format(upMult2))
    cmds.connectAttr("{0}.outColor.outColorR".format(cond), "{0}.input1.input1X".format(loMult2))
    cmds.connectAttr("{0}.upScale".format(ikCtrl), "{0}.input2.input2X".format(upMult2))
    cmds.connectAttr("{0}.loScale".format(ikCtrl), "{0}.input2.input2X".format(loMult2))

    # returns 2 mults go to the up/down jnts
    return(upMult2, loMult2)

# hook controls vis into swtich

# setup stretch (measure jtns, ik jnts, ik ctrl)

# create twist extractors (option for upper, lower [or more accurately forward, reverse]) and twist joints under combo rig

# **rewrite ribbon stuff. . . 

# *mocap stuff should be put ON TOP of these controls
# *export rig should be put UNDER all of these things

# package it all up


# -- arm 
# deal wtih orienting ik handle
# hand stuff (locators, etc)

# -- leg
# deal wtih orienting ik handle
# reverse foot stuff (locators, etc)