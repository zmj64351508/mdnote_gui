#!/usr/bin/python
import sys, os
import wx
from wx.lib.agw import aui
import wx.grid
import wx.lib.platebtn as platebtn
from event import *
from note_viewer import NotebookViewer
from note_container_panel import NoteConatinerPanel
from global_manager import globalManager
from note_manager import NotespaceManager

# Define some IDs
ID_TB_START = wx.NewId()
ID_TB_STOP = wx.NewId()
ID_TB_PAUSE = wx.NewId()
ID_TB_NOTESPACE = wx.NewId()

# The main window
class MainWindow(wx.Frame):
	def __init__(self, parent, id=-1, title="mdnote", pos=wx.DefaultPosition,
                 size=(1280, 800), style=wx.DEFAULT_FRAME_STYLE):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self.note_container = None
		self.viewer = None

		# tell FrameManager to manage this frame        
		self.mgr = aui.AuiManager()
		self.mgr.SetManagedWindow(self)
	
		self.CreateMenu()

		# toolbar
		self.toolbar = aui.AuiToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
				     agwStyle=aui.AUI_TB_DEFAULT_STYLE)
		self.toolbar.SetToolBitmapSize(wx.Size(48, 48))
		self.toolbar.AddSimpleTool(ID_TB_START, "START", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		self.toolbar.AddSimpleTool(ID_TB_STOP,  "STOP",  wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		self.toolbar.AddSimpleTool(ID_TB_PAUSE, "PAUSE", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		self.toolbar.Realize()
		self.mgr.AddPane(self.toolbar,
				 aui.AuiPaneInfo().
				 ToolbarPane().
				 Top())

		notespace_tb = NotespaceToolbar(self)
		notespace_tb.Realize()
		self.mgr.AddPane(notespace_tb,
				 aui.AuiPaneInfo().
				 ToolbarPane().
				 Top())

		# Creating the LogWindow as soon as possible
		if globalManager.GetConfig().IsLogging():
			log_text = wx.TextCtrl(self, style=wx.TE_MULTILINE)
			log_win = wx.LogTextCtrl(log_text)
			wx.Log.SetActiveTarget(log_win)
			wx.Log.SetLogLevel(wx.LOG_Info)
			# for debugging
			wx.Log.SetVerbose(True)
			wx.Log.EnableLogging()

			self.mgr.AddPane(log_text,
					aui.AuiPaneInfo().
					DefaultPane().
					#Float().
					Bottom().
					FloatingSize(wx.Size(600, 200)).
					FloatingPosition(wx.Point(200, 200)).
					Show().
					NotebookDockable(False).
					Name("Logging").
					Caption("Logging").
					BestSize(-1, 200))

		self.Bind(EVT_NEW_NOTESPACE, self.OnNewNotespace)
		# "commit" all changes made to FrameManager   
		self.CreateNotespacePanel()
		self.mgr.Update()
		self.Show()

	def CreateNotespacePanel(self):	
		try:
			self.ns_mgr = NotespaceManager()
		except Exception as e:
			wx.LogError("Can not create notespace -- " + e.__str__())
			return None

		self.note_container = NoteConatinerPanel(self)
		self.mgr.AddPane(self.note_container,
				aui.AuiPaneInfo().Name("NoteContainer").
				DefaultPane().
				Left().
				Caption("None").
				BestSize(wx.Size(300, 100)).
				Floatable(False).
				CaptionVisible(False).
				CloseButton(False))

		self.viewer = NotebookViewer(self)
		globalManager.SetCurrentContentViewer(self.viewer)
		self.mgr.AddPane(self.viewer,
				aui.AuiPaneInfo().Name("Viewer").
				DefaultPane().
				Center().
				CaptionVisible(False).
				Floatable(False).
				PaneBorder(False))
	
		self.mgr.Update()
		self.Layout()

	def DestroyNotespacePanel(self):
		self.mgr.DetachPane(self.note_container)
		if self.note_container:
			self.note_container.Destroy()
		self.mgr.DetachPane(self.viewer)
		if self.viewer:
			self.viewer.Destroy()
		self.mgr.Update()
		self.Layout()
	
	def CreateMenu(self):
		# create menu
		mb = wx.MenuBar()

		file_menu = wx.Menu()
		file_menu.Append(wx.ID_EXIT, "&Exit")
		mb.Append(file_menu, "&File")

		self.SetMenuBar(mb)

	def OnNewNotespace(self, event):
		self.DestroyNotespacePanel()
		self.CreateNotespacePanel()

		# The toolbar to input notespace path
		self.mgr.Update()
		self.Layout()
	
	def CreateMenu(self):
		# create menu
		mb = wx.MenuBar()

		file_menu = wx.Menu()
		file_menu.Append(wx.ID_EXIT, "&Exit")
		mb.Append(file_menu, "&File")

		self.SetMenuBar(mb)

	def OnNewNotespace(self, event):
		self.DestroyNotespacePanel()
		self.CreateNotespacePanel()

# The toolbar to input notespace path
class NotespaceToolbar(aui.AuiToolBar):
	def __init__(self, parent):
		super(NotespaceToolbar, self).__init__(parent, -1, wx.DefaultPosition, wx.DefaultSize,
				     agwStyle=aui.AUI_TB_DEFAULT_STYLE)
		self.text = wx.TextCtrl(self, -1, globalManager.GetConfig().GetNotespacePath(), size=wx.Size(400, 32), style=wx.TE_PROCESS_ENTER)
		self.AddControl(self.text)
		self.button = wx.Button(self, ID_TB_NOTESPACE, label="OK", size=wx.Size(50, 32))
		self.AddControl(self.button)
		self.button.Bind(wx.EVT_BUTTON, self.OnSubmit)

	def OnSubmit(self, event):
		globalManager.GetConfig().SetNotespacePath(self.text.GetValue())
		wx.PostEvent(self.GetParent(), NewNotespaceEvent())

class App(wx.App):
	def OnInit(self):
		frame = MainWindow(None, -1)
		globalManager.SetMainWindow(frame)
		self.SetTopWindow(frame)
		return True

if __name__ == "__main__":
	app = App(0)
	app.MainLoop()
