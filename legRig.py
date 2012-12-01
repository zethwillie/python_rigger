import maya.cmds as cmds
import zbw_rig as rig
from baseLimb import LimbUI
from baseLimb import Limb

#----------add in offsets for feet joints for FK2IK matching


class LegUI(LimbUI):

	def __init__(self):

		#super(ArmUI,self).__init__()

		self.widgets = {}

		self.defaultLimbName = "leg"
		self.defaultJointList = ["thigh", "knee", "ankle", "ball", "legEnd"]
		self.defaultLocValues = [[3,6,0], [3,3,1], [3,1, 0], [3, 0, 2], [3, 0, 3]]

		self.buildUI()

	def buildUI(self):

		win = cmds.window("legWin", exists=True)
		if win:
			cmds.deleteUI("legWin")

		self.widgets["mainWindow"] = cmds.window("legWin", title="Leg Rig Creation Window", w=320,h=600)
		self.widgets["scrollLayout"] = cmds.scrollLayout(vst=20)

		self.widgets["mainColumn"] = cmds.columnLayout(w=300,h=600)

		self.commonLimbUI()

		self.customLimbUI()

		self.buttonUI()

		cmds.showWindow(self.widgets["mainWindow"])

	def customLimbUI(self):
		# cmds.setParent(self.widgets["mainColumn"])
		self.widgets["customFrame"] = cmds.frameLayout(l="3. Custom Limb Attributes", w=320, bgc=(0,0,0), p=self.widgets["mainColumn"])
		cmds.text("custom arms stuff here, like hand, etc")