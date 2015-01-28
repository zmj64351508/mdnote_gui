#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys, os
import wx
from wx.lib.agw import aui
#from wx import aui
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

ID_NEW_NOTESPACE = wx.NewId()

reload(sys)
sys.setdefaultencoding("ascii")
# The main window
class MainWindow(wx.Frame):
	def __init__(self, parent, id=-1, title="mdnote", pos=wx.DefaultPosition,
                 size=(1280, 800), style=wx.DEFAULT_FRAME_STYLE):

		wx.Frame.__init__(self, parent, id, title, pos, size, style)
		self.ns_mgr = NotespaceManager()
		self.note_container = None
		self.viewer = None

		# tell FrameManager to manage this frame        
		self.mgr = aui.AuiManager()
		self.mgr.SetManagedWindow(self)
	
		self.CreateMenu()

		# toolbar
		#self.toolbar = aui.AuiToolBar(self)
		#self.toolbar.SetToolBitmapSize(wx.Size(48, 48))
		#self.toolbar.AddSimpleTool(ID_TB_START, "START", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		#self.toolbar.AddSimpleTool(ID_TB_STOP,  "STOP",  wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		#self.toolbar.AddSimpleTool(ID_TB_PAUSE, "PAUSE", wx.ArtProvider.GetBitmap(wx.ART_QUESTION))
		#self.toolbar.Realize()
		#self.mgr.AddPane(self.toolbar,
		#		 aui.AuiPaneInfo().
		#		 ToolbarPane().
		#		 Top())

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
					#NotebookDockable(False).
					Name("Logging").
					Caption("Logging").
					BestSize(wx.Size(-1, 200)))

		self.Bind(EVT_NEW_NOTESPACE, self.OnNewNotespace)
		self.Bind(wx.EVT_KILL_FOCUS, self.OnLoseFocus)
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		# "commit" all changes made to FrameManager   
		self.CreateNotespacePanel()
		self.mgr.Update()
		self.Show()

	def CreateNotespacePanel(self):	
		try:
			self.ns_mgr.Open(globalManager.GetConfig().GetNotespacePath())
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

		# File menu
		file_menu = wx.Menu()
		# New sub menu
		new_submenu = wx.Menu()
		new_submenu.Append(ID_NEW_NOTESPACE, "&New Notespace")
		self.Bind(wx.EVT_MENU, self.OnCreateNotespace, id=ID_NEW_NOTESPACE)
		file_menu.AppendMenu(wx.ID_NEW, "&New", new_submenu)
		# Exit sub menu
		file_menu.Append(wx.ID_EXIT, "&Exit")
		self.Bind(wx.EVT_MENU, self.OnMenuExit, id=wx.ID_EXIT)
		# Add to menubar
		mb.Append(file_menu, "&File")

		self.SetMenuBar(mb)

	def OnCreateNotespace(self, event):
		dlg = wx.DirDialog(self, message = "Choose a directory",
				    defaultPath = os.getcwd())	

		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			wx.LogMessage('Select path: %s\n' % path)
			self.ns_mgr.Create(path)

		dlg.Destroy()

	def OnNewNotespace(self, event):
		self.DestroyNotespacePanel()
		self.CreateNotespacePanel()

		# The toolbar to input notespace path
		self.mgr.Update()
		self.Layout()
	
	def OnNewNotespace(self, event):
		self.DestroyNotespacePanel()
		self.CreateNotespacePanel()

	def OnClose(self, event):
		#globalManager.KillAllBgProcess()
		event.Skip()

	def OnMenuExit(self, event):
		self.Close()

	def OnLoseFocus(self, event):
		wx.LogInfo("main windows lose focus")

# The toolbar to input notespace path
class NotespaceToolbar(aui.AuiToolBar):
	def __init__(self, parent):
		super(NotespaceToolbar, self).__init__(parent)
		self.name1 = wx.StaticText(self, label="notespace path:")
		self.AddControl(self.name1)
		self.notespace = wx.TextCtrl(self, value=globalManager.GetConfig().GetNotespacePath(), size=wx.Size(400, -1), style=wx.TE_PROCESS_ENTER)
		self.AddControl(self.notespace)

		#self.AddSeparator()

		#self.name2 = wx.StaticText(self, label="mdnote.py path:")
		#self.AddControl(self.name2)
		#self.mdnote = wx.TextCtrl(self, value=globalManager.GetConfig().GetMdnotePath(), size=wx.Size(400, -1), style=wx.TE_PROCESS_ENTER)
		#self.AddControl(self.mdnote)

		self.button = wx.Button(self, ID_TB_NOTESPACE, label="Open Notespace")
		self.AddControl(self.button)
		self.button.Bind(wx.EVT_BUTTON, self.OnSubmit)

	def OnSubmit(self, event):
		globalManager.GetConfig().SetNotespacePath(self.notespace.GetValue())
		#globalManager.GetConfig().SetMdnotePath(self.mdnote.GetValue())
		wx.PostEvent(self.GetParent(), NewNotespaceEvent())

class App(wx.App):
	def OnInit(self):
		frame = MainWindow(None, -1)
		globalManager.SetMainWindow(frame)
		globalManager.SetApp(self)
		self.SetTopWindow(frame)
		return True

#import signal
#def signal_handler(signal, frame):
#	globalManager.KillAllBgProcess()
#	sys.exit(0)

if __name__ == "__main__":
	#signal.signal(signal.SIGINT, signal_handler)
	app = App(0)
	app.MainLoop()
