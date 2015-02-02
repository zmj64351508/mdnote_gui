# -*- coding: utf-8 -*-
import wx

def NewEvent():
	evt_id = wx.NewEventType()
	evt = wx.PyEventBinder(evt_id)
	return evt_id, evt

# Define some events
ID_EVT_NEW_NOTESPACE, EVT_NEW_NOTESPACE = NewEvent()
class NewNotespaceEvent(wx.PyEvent):
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(ID_EVT_NEW_NOTESPACE)

ID_EVT_PANEL_BUTTON, EVT_PANEL_BUTTON = NewEvent()
class PanelButtonEvent(wx.PyEvent):
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(ID_EVT_PANEL_BUTTON)
		self.ResumePropagation(-1)

class NoteEvent(wx.PyEvent):
	def __init__(self, note):
		wx.PyEvent.__init__(self)
		self.ResumePropagation(-1)
		self.note = note

	def GetNote(self):
		return self.note

ID_EVT_SHOW_NOTE, EVT_SHOW_NOTE = NewEvent()
class ShowNoteEvent(NoteEvent):
	def __init__(self, note):
		NoteEvent.__init__(self, note)
		self.SetEventType(ID_EVT_SHOW_NOTE)

ID_EVT_NEW_NOTE, EVT_NEW_NOTE = NewEvent()
class NewNoteEvent(NoteEvent):
	def __init__(self, note):
		NoteEvent.__init__(self, note)
		self.SetEventType(ID_EVT_NEW_NOTE)

ID_EVT_UPDATE_NOTE, EVT_UPDATE_NOTE = NewEvent()
class UpdateNoteEvent(NoteEvent):
	def __init__(self, note):
		NoteEvent.__init__(self, note)
		self.SetEventType(ID_EVT_UPDATE_NOTE)

ID_EVT_DELETE_NOTE, EVT_DELETE_NOTE = NewEvent()
class DeleteNoteEvent(NoteEvent):
	def __init__(self, note):
		NoteEvent.__init__(self, note)
		self.SetEventType(ID_EVT_DELETE_NOTE)
