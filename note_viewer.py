# -*- coding: utf-8 -*-
import time
import wx
from wx.lib.agw import aui
from wx.lib.scrolledpanel import ScrolledPanel
from panel_button import *
from global_manager import globalManager
from note_manager import NotebookManager, NoteManagerByNotebook
from ids import *

# This class generate a notebook view
class NotebookViewer(wx.Panel):
	def __init__(self, parent, note_mgr=None, notebook_mgr=None):
		super(NotebookViewer, self).__init__(parent)
		self.aui_mgr = aui.AuiManager()
		self.aui_mgr.SetManagedWindow(self)
		self.Bind(EVT_SHOW_NOTE, self.OnShowNote)
		self.Bind(EVT_DELETE_NOTE, self.OnDeleteNote)

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
				CaptionVisible(False).
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
		shown_count = self.note_select_panel.ShowSelection()
		if shown_count == 0:
			self.note_panel.DeCreate()

	def OnDeleteNote(self, event):
		is_current = False
		note = event.GetNote()
		if note == self.note_mgr.GetCurrentNote() and self.note_panel:
			is_current = True
			self.note_panel.CloseNote(False)
		if self.note_mgr.Remove([note.id]) == 0:
			current_show = self.note_select_panel.DeleteNote(note, is_current)
			# no note to show
			if current_show < 0:
				self.note_panel.DeCreate()
		elif self.note_panel:
			# if we remove it failed, reopen the note for editing
			self.note_panel.ShowNote(note)


class NoteSelectButton(PanelButton):
	def __init__(self, parent, mgr, id, button_indicator=None, label=None):
		super(NoteSelectButton, self).__init__(parent, button_indicator=button_indicator, label=label)

		menu = wx.Menu()
		menu.Append(ID_DELETE_NOTE, "&Delete")
		self.Bind(wx.EVT_MENU, self.OnDelete, id=ID_DELETE_NOTE)
		self.SetMenu(menu)

		self.mgr = mgr
		self.id = id
		self.Bind(EVT_PANEL_BUTTON, self.OnClick)

	def OnClick(self, event):
		new_event = ShowNoteEvent(self.mgr.GetNote(self.id))
		wx.PostEvent(self.GetParent(), new_event)

	def OnDelete(self, event):
		note = self.mgr.GetNote(self.id)
		wx.PostEvent(self.GetParent(), DeleteNoteEvent(note))

# The middle panel in notebook view to show notes name/info
class NoteSelectPanel(wx.Panel):
	def __init__(self, parent, mgr=None):
		super(NoteSelectPanel, self).__init__(parent)
		self.note_mgr = mgr
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)

		self.toolbar = NoteSelectToolbar(self)
		self.sizer.Add(self.toolbar, 0, wx.ALL|wx.EXPAND, 0)

		#seperator = wx.Panel(self, size=wx.Size(-1, 2))
		#seperator.SetBackgroundColour(wx.Colour(100, 100, 100))
		#self.sizer.Add(seperator, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)

		self.items = NoteSelectItemPanel(self, mgr)
		self.sizer.Add(self.items, 1, wx.LEFT|wx.RIGHT|wx.EXPAND, 0)

		self.Bind(EVT_NEW_NOTE, self.OnNewNote)

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr
		self.items.SetNoteManager(mgr)
		self.toolbar.SetNoteManager(mgr)

	def ShowSelection(self):
		return self.items.ShowSelection()
		#self.Layout()

	def OnNewNote(self, event):
		note = event.GetNote()
		self.items.ShowNewNote(note)

	def DeleteNote(self, note, is_current):
		self.items.DeleteNote(note, is_current)

class NoteSelectToolbar(wx.Panel):
	def __init__(self, parent, mgr=None):
		super(NoteSelectToolbar, self).__init__(parent)
		self.note_mgr = mgr
		self.sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(self.sizer)
		bg_color = wx.Colour(255, 255, 255)
		self.SetBackgroundColour(bg_color)

		new_notebook_tool = wx.StaticText(self, label="Select Note")
		self.sizer.Add(new_notebook_tool, 1, wx.ALL|wx.EXPAND, 5)

		new_note_image = globalManager.GetResourceManager().GetImage("new_note.png")
		new_notebook_tool = PanelButton(self, click_color=wx.Colour(100, 100, 100), background_color=bg_color,bmp=new_note_image)
		new_notebook_tool.Bind(EVT_PANEL_BUTTON, self.OnNewNote)
		self.sizer.Add(new_notebook_tool, 0, wx.RIGHT, 5)


	def SetNoteManager(self, mgr):
		self.note_mgr = mgr

	def OnNewNote(self, event):
		dlg = wx.TextEntryDialog(self, 'Please Enter Note Name', 'Note Name')
		if dlg.ShowModal() == wx.ID_OK:
			note_name = dlg.GetValue()
			note = self.note_mgr.NewNote(note_name)
			event = NewNoteEvent(note)
			wx.PostEvent(self.GetParent(), event)
		dlg.Destroy()

class NoteSelectItemPanel(ScrolledPanel):
	def __init__(self, parent, mgr=None):
		super(NoteSelectItemPanel, self).__init__(parent)
		self.SetupScrolling()

		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(self.sizer)
		self.button_indicator = PanelButtonIndicator()
		self.SetNoteManager(mgr)
		self.note_items = {}

		self.Bind(wx.EVT_LEFT_UP, self.OnClick)

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr

	def AddNoteItem(self, note):
		note_button = NoteSelectButton(self, self.note_mgr, note.id, button_indicator=self.button_indicator, label=note.path)
		self.note_items[note.id] = note_button
		self.sizer.Add(note_button, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		return note_button

	def DeleteItem(self, note):
		note_button = self.note_items.pop(note.id)
		index = self.sizer.GetItemIndex(note_button)
		self.sizer.Remove(note_button)
		note_button.Destroy()
		return index

	def ShowSelection(self):
		self.Freeze()
		self.DestroyChildren()
		self.sizer.Clear()
		if self.note_mgr:
			self.note_mgr.ClearNotes()
			notes= self.note_mgr.GetNotes()
			first_selection = None
			for note in notes:
				note_button = self.AddNoteItem(note)
				# Automatically select first option if it exists
				if not first_selection:
					first_selection = note_button
		self.FitInside()
		if first_selection:
			first_selection.Select()
		self.Thaw()
		#self.Layout()
		return len(notes)

	def ShowNewNote(self, note):
		self.Freeze()
		notebutton = self.AddNoteItem(note)
		self.FitInside()
		notebutton.Select()
		self.Thaw()

	# return current index of shown note in the select panel after deleted
	def DeleteNote(self, note, is_current):
		self.Freeze()
		index = self.DeleteItem(note)
		retval = index
		# Select next item if is current selected
		if is_current:
			try:
				self.sizer.GetItem(index).GetWindow().Select()
				retval = index
			except:
				try:
					self.sizer.GetItem(index-1).GetWindow().Select()
					retval = index - 1
				except:
					retval = -1
		self.Layout()
		self.Thaw()
		return retval
		
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

	def DeCreate(self):
		if not self.created:
			return
		self.Freeze()
		self.note_info_panel.Destroy()
		self.note_view_panel.Destroy()
		self.created = False
		self.Thaw()

	def SetNoteManager(self, mgr):
		self.note_mgr = mgr
		if self.note_info_panel:
			self.note_info_panel.SetNoteManager(mgr)
		if self.note_view_panel:
			self.note_view_panel.SetNoteManager(mgr)

	def ShowNote(self, note):
		if not self.created:
			self.Create(self.note_mgr)

		cur_note = self.note_mgr.GetCurrentNote()
		if cur_note and note.id == cur_note.id:
			# current note is already opened
			self.note_view_panel.SaveContent()
			self.note_info_panel.ShowNoteInfo(note)
		else:
			# must close it first before SetCurrentNote
			self.note_view_panel.CloseSaveContent()

			self.note_mgr.SetCurrentNote(note.id)
			self.note_info_panel.ShowNoteInfo(note)
			self.note_view_panel.ShowContent(note)
		self.Layout()

	def CloseNote(self, destroy):
		if not self.created:
			return
		self.note_view_panel.CloseSaveContent()
		if destroy:
			self.DeCreate()

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
		self.encoding = "utf8"
		self.SetWrapMode(wx.stc.STC_WRAP_CHAR)
		self.SetMarginWidth(1, 0)
		#self.SetMarginWidth(0, 50)
		self.SetNoteManager(mgr)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.note = None
		self.fd = None

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
		self.CloseFile()
		if self.note:
			self.note_mgr.CloseNote(self.note.id)
	
	def SaveContent(self):
		#if self.fd and self.IsModified():
		if self.note and self.IsModified():
			wx.LogInfo("content modified, saving it")
			self.SaveFile(self.note.abspath)
			self.SetModified(False)
			self.note_mgr.RefreshOne(self.note.id)
			wx.PostEvent(self.GetParent(), UpdateNoteEvent(self.note))
			return True
		return False

	def ShowContent(self, note):
		self.note = note
		self.LoadFile(self.note.abspath)
		wx.LogInfo("ShowConent")

	# Overwrite LoadFile and SaveFile for utf8
	def LoadFile(self, path):
		try:
			self.fd = open(path, "r+")
		except IOError:
			self.fd = open(path, "r")
		if self.fd.encoding:
			content = self.fd.read().decode(self.fd.encoding)
		else:
			content = self.fd.read().decode(self.encoding)
		self.SetText(content)
		self.SetModified(False)
		self.EmptyUndoBuffer()

	def SaveFile(self, path):
		if self.fd:
			try:
				self.fd.seek(0)
				self.fd.write(self.GetText().encode(self.encoding))
				self.fd.truncate()
				self.fd.flush()
			except IOError:
				pass

	def CloseFile(self):
		if self.fd:
			wx.LogInfo("CloseFile")
			self.fd.close()
			self.fd = None



