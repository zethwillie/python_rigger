import maya.cmds as cmds
import zTools.rig.zbw_rig as rig
from functools import partial

widgets = {}
def followCreatorUI():
    if cmds.window("followCreatorWin", exists = True):
        cmds.deleteUI("followCreatorWin")

    w = 500
    h = 400
    widgets["win"] = cmds.window("followCreatorWin", w=w, h=h)
    widgets["mainCLO"] = cmds.columnLayout(w=w, h=h)
    widgets["mainForm"] = cmds.formLayout(w=w, h=h)

    widgets["tgtTFG"] = cmds.textFieldGrp(l="Source Obj: ")

    nameList = []
    widgets["name1TFG"] = cmds.textFieldGrp(l="Attr 1 Name: ")
    widgets["obj1TFG"] = cmds.textFieldButtonGrp(l="Obj 1 Name: ", bc=partial(add_object_to_field, widgets["name1TFG"]))

    cmds.formLayout(widgets["mainForm"], e=True, af=[
        (widgets["name1TFG"], "top", 100),
        (widgets["name1TFG"], "left", 100),
        ])

    cmds.window(widgets["win"], e=True, w=5, h=5, rtf=True)
    cmds.showWindow(widgets["win"])


def add_object_to_field(field):
    sel = cmds.ls(sl=True, type="transform")
    if sel:
        obj = sel[0]
    cmds.textFieldGrp(field, e=True, tx=obj)


def create_follow_constraints(tgt=None, spaceNames=None, spaceObjs=None):
    if not tgt:
        tgt = cmds.ls(sl=True)[0]

    if not spaceNames or spaceObjs:
        spaceNames = ["Sphere", "Cube", "Cylinder", "Cone"]
        spaceObjs = ["sphere", "cube", "cylinder", "cone"]
    
    spaceGrps = []

    for i in range(len(spaceObjs)):
        name = "{0}_space".format(spaceObjs[i])
        space = name
        if not cmds.objExists(name):  
            space = cmds.group(em=True, name=name)
            cmds.parentConstraint(spaceObjs[i], space, mo=False)
        spaceGrps.append(space)

    # check if grp for spaces exists
    spaceGrpTest = cmds.attributeQuery("follow", node=tgt, exists=True)
    if not spaceGrpTest:
        cmds.addAttr(tgt, ln="follow", at="enum", en="{0}".format(":".join(spaceNames)), dv=1, k=True)
    cnstr = cmds.parentConstraint(spaceGrps, tgt, mo=True)[0]  

    # create setDrivenKey
    for i in range(len(spaceGrps)):
        tmpList = spaceNames[:]
        attr = tmpList.pop(i)
        index = get_enum_index_from_string(tgt, "follow", attr)
        cmds.setAttr("{0}.follow".format(tgt), i)
        cmds.setDrivenKeyframe("{0}.{1}W{2}".format(cnstr, spaceGrps[i], i), cd="{0}.follow".format(tgt), value=1)
        for a in range(len(spaceGrps)):
            if a != index:
                cmds.setDrivenKeyframe("{0}.{1}W{2}".format(cnstr, spaceGrps[a], a), cd="{0}.follow".format(tgt), value=0)

def get_enum_index_from_string(node, attr, value):
    enumList = cmds.attributeQuery(attr, node=node, listEnum=True)[0].split(":")
    index = enumList.index(value)
    return(index)

def followCreator():
    followCreatorUI()