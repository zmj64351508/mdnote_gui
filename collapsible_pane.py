import wx
from panel_button import *
from event import *

class CollapsiblePane(wx.Panel):
	def __init__(self, parent, label=""):
		super(CollapsiblePane, self).__init__(parent)
		self.button = PanelButton(self, label=label)
		self.Bind(EVT_PANEL_BUTTON, self.OnPaneChange)

		self.pane = wx.Panel(self)
		self.pane.Hide()

		self.panel_sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.panel_sizer)
		self.panel_sizer.Add(self.button, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)

		self.is_collapse = True

	def GetPane(self):
		return self.pane

	def IsCollapse(self):
		return self.is_collapse

	def Expand(self):
		if self.IsCollapse():
			self.is_collapse = False
			self.panel_sizer.Add(self.GetPane(), 0, wx.ALL|wx.EXPAND, 0)
			self.GetPane().Show()
		self.Layout()
	
	def Collapse(self):
		if not self.IsCollapse():
			self.is_collapse = True
			self.panel_sizer.Detach(self.GetPane())
			self.GetPane().Hide()
		self.Layout()

	def OnPaneChange(self, event):
		if self.IsCollapse():
			self.Expand()
		else:
			self.Collapse()
		event.Skip()
		
# Collapsible panel with some buttons to show notebooks and tags
class NoteContainerCollapsiblePane(CollapsiblePane):
	def __init__(self, parent, manager, button_indicator=None, label=""):
		super(NoteContainerCollapsiblePane, self).__init__(parent, label=label)

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.GetPane().SetSizer(self.sizer)

		self.button_indicator = button_indicator
		self.mgr = manager

	def GetManager(self):
		return self.mgr

	def OnPaneChange(self, event):
		super(NoteContainerCollapsiblePane, self).OnPaneChange(event)
		# redo the layout
		self.GetParent().FitInside()
		self.GetParent().Layout

	def CreateButton(self, parent, indicator=None, label=None):
		return None

	def ShowContent(self, select_first):
		contents_name = self.mgr.GetAllContentName()
		first = None
		for name in contents_name:
			button = self.CreateButton(self.GetPane(), indicator=self.button_indicator, label=name)
			if not first:
				first = button
			self.sizer.Add(button, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		self.Expand()
		if select_first:
			first.Select()

