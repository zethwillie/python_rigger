import maya.cmds as cmds
import zTools.rig.zbw_rig as rig

# start w joint chain
def create_joint_chain(ptList=None, baseNames=None, alongAxis="xyz", upAxis="yup"):
    cmds.select(cl=True)
    jntList = []
    for i in range(len(ptList)):
        jnt = cmds.joint(name=baseNames[i], p=ptList[i])
        jntList.append(jnt)
    
    orient_joint_chain(jntList[0], alongAxis, upAxis)

    return(jntList)

# create controls and parent under joint - should these go into the FK dict key?

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


# orient the joints (freeze transforms, then orient via options)
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


# mirror stuff
# mirror joint chains across given axis, with given prefixes. . .  
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


# this is temp simple version to just replace FK
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


def create_reverse_network(name,  inputAttr, revAttr, targetAttr):
    """revAttr should be 'all', 'x', 'y' or 'z'"""
    reverse = cmds.shadingNode("reverse", asUtility=True, name=name)
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


# create controls on joints - group orient
def create_controls_at_joints(jntList, ctrlType, axis, suffix):
    """orient will create a new control UNDER the ctrl that we can use to  orient pose joints"""
    ctrls = []
    groups = []
    for jnt in jntList:
        # pos = cmds.xform(jnt, q=True, ws=True, rp=True)
        # rot = cmds.xform(jnt, q=True, ws=True, ro=True)
        if "_" in jnt:
            name = "_".join(jnt.split("_")[:-1]) + "_{0}".format(suffix)
        else:
            name = "{0}_{1}".format(jnt, suffix)
        ctrl = rig.createControl(name, ctrlType, axis)
        grp = rig.groupFreeze(ctrl)
        rig.snapTo(jnt, grp)
        ctrls.append(ctrl)
        groups.append(grp)

    return(ctrls, groups)


def create_controls_and_orients_at_joints(jntList, ctrlType, axis, suffix, orient=False, upAxis="y"):
    """orient will create a new control UNDER the ctrl that we can use to  orient pose joints"""
    ctrls = []
    groups = []
    octrls = []
    ogrps = []
    for jnt in jntList:
        # pos = cmds.xform(jnt, q=True, ws=True, rp=True)
        # rot = cmds.xform(jnt, q=True, ws=True, ro=True)
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
    if not len(ctrls)==len(grps) or len(ctrls)<1:
        cmds.warning("riggerTools.parent_hierarchy_grouped_controls: lists don't match in length or aren't long enough")
        return()

    for x in range(1, len(grps)):
        cmds.parent(grps[x], ctrls[x-1])


# create Fk controls
# # create control, group freeze, snap to, contrain to . . . 

# create control hierarchy (from group oriented controls)

# create Ik controls 

# create fkIK switch
# hook blends and controls vis into swtich

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