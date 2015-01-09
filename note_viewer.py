import wx
from wx.lib.agw import aui
from wx.lib.scrolledpanel import ScrolledPanel
from panel_button import *

# This class generate a notebook view
class NotebookViewer(wx.Panel):
	def __init__(self, parent):
		super(NotebookViewer, self).__init__(parent)
		self.mgr = aui.AuiManager()
		self.mgr.SetManagedWindow(self)

		self.mgr.AddPane(wx.StaticText(self, label="HAHAHA"),
				aui.AuiPaneInfo().
				Center().
				CaptionVisible(False).
				Floatable(False))

		self.note_panel = NotePanel(self)
		self.mgr.AddPane(self.note_panel,
				aui.AuiPaneInfo().Name("Note").
				DefaultPane().
				Caption("Notes").
				Left().
				BestSize(wx.Size(300, 100)).
				Floatable(False).
				#CaptionVisible(False).
				CloseButton(False))

		self.mgr.Update()

	def GetNotePanel(self):
		return self.note_panel

# The middle panel in notebook view to show notes name/info
class NotePanel(ScrolledPanel):
	def __init__(self, parent, mgr=None):
		super(NotePanel, self).__init__(parent)
		self.SetupScrolling()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.button_indicator = PanelButtonIndicator()
		self.SetManager(mgr)

	def SetManager(self, mgr):
		self.note_mgr = mgr

	def ShowNotes(self):
		self.DestroyChildren()
		self.sizer.Clear()
		if self.note_mgr:
			notes_path = self.note_mgr.GetAllNotesPath()
			for path in notes_path:
				note_button = PanelButton(self, button_indicator=self.button_indicator, label=path)
				self.sizer.Add(note_button, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		self.FitInside()
		self.Layout()
