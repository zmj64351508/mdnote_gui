import time
import wx
from wx.lib.agw import aui
from wx.lib.scrolledpanel import ScrolledPanel
from panel_button import *
from global_manager import globalManager
from note_manager import NotebookManager, NoteManagerByNotebook

# This class generate a notebook view
class NotebookViewer(wx.Panel):
	def __init__(self, parent, note_mgr=None, notebook_mgr=None):
		super(NotebookViewer, self).__init__(parent)
		self.aui_mgr = aui.AuiManager()
		self.aui_mgr.SetManagedWindow(self)
		self.Bind(EVT_SHOW_NOTE, self.OnShowNote)

		self.note_mgr = note_mgr

		self.note_panel = NotePanel(self)
		self.aui_mgr.AddPane(self.note_panel,
				aui.AuiPaneInfo().
				Center().
				CaptionVisible(False).
				Floatable(False))

		self.note_select_panel = NoteSelectPanel(self)
		self.aui_mgr.AddPane(self.note_select_panel,
				aui.AuiPaneInfo().Name("Note").
				DefaultPane().
				Caption("Notes").
				Left().
				BestSize(wx.Size(300, 100)).
				Floatable(False).
				#CaptionVisible(False).
				CloseButton(False))

		self.aui_mgr.Update()
		self.notebook_mgr = globalManager.GetNotebookManager()
		notebook = self.notebook_mgr.GetCurrentNotebook()
		if notebook:
			self.SetNoteManager(NoteManagerByNotebook(notebook))
			self.ShowSelection()

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr
		self.note_panel.SetNoteManager(mgr)
		self.note_select_panel.SetNoteManager(mgr)

	def GetNoteSelectPanel(self):
		return self.note_select_panel

	def OnShowNote(self, event):
		note= event.GetNote()
		#wx.LogInfo("OnShowNote: " + str(note_info))
		self.note_panel.ShowNote(note)

	def ShowSelection(self):
		self.note_select_panel.ShowSelection()

class NoteSelectButton(PanelButton):
	def __init__(self, parent, mgr, id, button_indicator=None, label=None):
		super(NoteSelectButton, self).__init__(parent, button_indicator=button_indicator, label=label)
		self.mgr = mgr
		self.id = id

	def OnClick(self, event):
		super(NoteSelectButton, self).OnClick(event)
		new_event = ShowNoteEvent(self.mgr.GetNote(self.id))
		handler = self
		parent = handler.GetParent()
		#wx.PostEvent(globalManager.GetCurrentContentViewer(), new_event)
		wx.PostEvent(self.GetParent(), new_event)

# The middle panel in notebook view to show notes name/info
class NoteSelectPanel(ScrolledPanel):
	def __init__(self, parent, mgr=None):
		super(NoteSelectPanel, self).__init__(parent)
		self.SetupScrolling()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.button_indicator = PanelButtonIndicator()
		self.SetNoteManager(mgr)

		self.Bind(wx.EVT_LEFT_UP, self.OnClick)

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr

	def ShowSelection(self):
		self.DestroyChildren()
		self.sizer.Clear()
		self.Freeze()
		if self.note_mgr:
			self.note_mgr.ClearNotes()
			notes= self.note_mgr.GetNotes()
			first_selection = None
			for note in notes:
				note_button = NoteSelectButton(self, self.note_mgr, note.id, button_indicator=self.button_indicator, label=note.path)
				# Automatically select first option if it exists
				if not first_selection:
					first_selection = note_button
				self.sizer.Add(note_button, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		self.FitInside()
		first_selection.Select()
		self.Thaw()
		#self.Layout()

	def OnClick(self, event):
		self.SetFocus()
		event.Skip()

class NotePanel(wx.Panel):
	def __init__(self, parent, mgr=None):
		super(NotePanel, self).__init__(parent)
		self.note_mgr = mgr
		self.note_info_panel = None
		self.note_view_panel = None
		self.created = False

	def Create(self, mgr):
		self.note_info_panel = NoteInfoPanel(self, mgr)
		self.note_view_panel = NoteViewPanel(self, mgr)

		self.Freeze()
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		sizer.Add(self.note_info_panel, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		sizer.Add(self.note_view_panel, 1, wx.ALL|wx.EXPAND, 10)
		self.Thaw()
		self.SetNoteManager(mgr)
		self.created = True

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr
		if self.note_info_panel:
			self.note_info_panel.SetNoteManager(mgr)
		if self.note_view_panel:
			self.note_view_panel.SetNoteManager(mgr)

	def ShowNote(self, note):
		if not self.created:
			self.Create(self.note_mgr)
		# must close it first before SetCurrentNote
		self.note_view_panel.CloseSaveContent()

		self.note_mgr.SetCurrentNote(note.id)
		self.note_info_panel.ShowNoteInfo(note)
		self.note_view_panel.ShowContent(note)
		self.Layout()

class NoteInfoPanel(wx.Panel):
	def __init__(self, parent, mgr=None):
		super(NoteInfoPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
		self.notebook_info = None
		self.tag_info = None
		self.create_time = None
		self.modify_time = None
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.line_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.line_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(sizer)
		sizer.Add(self.line_sizer1, 0, wx.LEFT|wx.RIGHT, 0)
		sizer.Add(self.line_sizer2, 0, wx.LEFT|wx.RIGHT, 0)

		self.notebook_info = wx.StaticText(self)
		font = self.notebook_info.GetFont()
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		self.notebook_info.SetFont(font)
		self.tag_info = wx.StaticText(self)
		self.line_sizer1.Add(self.notebook_info, 0, wx.ALL, 5)
		self.line_sizer1.Add(self.tag_info, 0, wx.ALL, 5)

		self.create_time = wx.StaticText(self)
		self.modify_time = wx.StaticText(self)
		self.line_sizer2.Add(self.create_time, 0, wx.ALL, 5)
		self.line_sizer2.Add(self.modify_time, 0, wx.ALL, 5)
		self.info_container = True

		self.SetNoteManager(mgr)

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr

	def ShowNoteInfo(self, note):
		if not note:
			wx.LogWarning("no current note")
			return
		create_time = time.strftime("%H:%M:%S %Y-%m-%d", time.localtime(float(note.create_time)))
		modify_time = time.strftime("%H:%M:%S %Y-%m-%d", time.localtime(float(note.modify_time)))
		self.notebook_info.SetLabel(note.notebook)
		self.tag_info.SetLabel("tags: " + note.tags)
		self.create_time.SetLabel("create time: " + create_time)
		self.modify_time.SetLabel("modify time: " + modify_time)

import wx.stc
class NoteViewPanel(wx.stc.StyledTextCtrl):
	def __init__(self, parent, mgr=None):
		super(NoteViewPanel, self).__init__(parent, style=wx.SIMPLE_BORDER)
		self.SetWrapMode(wx.stc.STC_WRAP_CHAR)
		self.SetMarginWidth(1, 0)
		#self.SetMarginWidth(0, 50)
		self.SetNoteManager(mgr)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.note = None

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr

	def OnClose(self, event):
		self.CloseSaveContent()
		event.Skip()

	def CloseSaveContent(self):
		self.SaveContent()
		self.CloseContent()

	# This will directly close the content without saving it
	def CloseContent(self):
		self.ClearAll()
		if self.note:
			self.note_mgr.CloseNote(self.note.id)
	
	def SaveContent(self):
		#if self.fd and self.IsModified():
		if self.note and self.IsModified():
			wx.LogInfo("content modified, saving it")
			self.SaveFile(self.note.abspath)
			self.SetModified(False)

	def ShowContent(self, note):
		self.note = note
		self.LoadFile(self.note.abspath)
		wx.LogInfo("ShowConent")


