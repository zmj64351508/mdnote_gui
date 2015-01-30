# -*- coding: utf-8 -*-
import os, socket, sys
import wx

# This class managers all the configurations
class MdnoteConfig(object):
	self_path = os.path.join(os.path.abspath(os.path.join(sys.argv[0], os.path.pardir)))
	#parent_path = os.path.join(self_path, os.path.pardir)
	mdnote_path = os.path.join(self_path, "cli/mdnote.py")
	notespace_path = os.path.join(self_path, "cli/test_dir")
	res_path = os.path.join(self_path, "res")
	core_addr = ("127.0.0.1", 46000)
	sync_server_addr = ("127.0.0.1", 46000)

	def __init__(self):
		self.SetMdnotePath(self.mdnote_path)
		self.SetNotespacePath(self.notespace_path)

	def SetNotespacePath(self, path):
		self.notespace_path = os.path.abspath(os.path.expanduser(path))

	def GetNotespacePath(self):
		return os.path.abspath(os.path.expanduser(self.notespace_path))

	def SetMdnotePath(self, path):
		self.mdnote_path = os.path.abspath(os.path.expanduser(path))

	def GetMdnotePath(self):
		return os.path.abspath(os.path.expanduser(self.mdnote_path))

	def GetResourcePath(self):
		return os.path.abspath(os.path.expanduser(self.res_path))
	
	def GetCoreAddr(self):
		return self.core_addr

	def GetSyncServerAddr(self):
		return self.sync_server_addr

	def IsLogging(self):
		return True

class ConnectManager(object):
	def __init__(self):
		self.socket = None

	def GetServerAddr(self):
		return None

	def ConnectServer(self):
		if not self.socket:
			wx.LogInfo("connecting " + self.GetServerAddr().__str__())
			self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			try:
				self.socket.connect(self.GetServerAddr())
			except Exception:
				self.socket = None
			return self.socket
	
	def GetSocket(self):
		if self.socket:
			return self.socket
		else:
			return self.ConnectServer()

	def DisconnectServer(self):
		if self.socket:
			self.socket.close()
			self.socket = None

class CoreConnectManager(ConnectManager):
	def GetServerAddr(self):
		return globalManager.GetConfig().GetCoreAddr()

class SyncServerConnectManager(ConnectManager):
	def GetServerAddr(self):
		return globalManager.GetConfig().GetSyncServerAddr()

class ResourceManager(object):
	def __init__(self, path):
		self.path = path.encode(sys.getfilesystemencoding())
		self.image_path = os.path.join(self.path, "image")

	def GetImage(self, name):
		try:
			png_path = os.path.join(self.image_path, name.encode(sys.getfilesystemencoding()))
			return wx.Image(png_path, wx.BITMAP_TYPE_ANY).ConvertToBitmap()
		except:
			return None

# This class managers all global objects
class GlobalManager(object):
	def __init__(self):
		self.config = MdnoteConfig()
		self.core_connect = CoreConnectManager()
		self.remote_connect = SyncServerConnectManager()
		self.notebook_manager = None
		self.bg_process = []
		self.app = None
		self.current_content_viewer = None
		self.resource_manager = ResourceManager(self.config.GetResourcePath())

	def GetConfig(self):
		return self.config

	def GetResourceManager(self):
		return self.resource_manager

	def MakeNoteAbsPath(self, path):
		return os.path.join(self.config.GetNotespacePath(), path)

	def MakeNoteRelPath(self, path):
		return os.path.relpath(path, self.config.GetNotespacePath())

	def SetCurrentContentViewer(self, viewer):
		self.current_content_viewer = viewer

	def GetCurrentContentViewer(self):
		return self.current_content_viewer

	def GetNotebookManager(self):
		from note_manager import NotebookManager
		if not self.notebook_manager:
			self.notebook_manager = NotebookManager()
		return self.notebook_manager

	def SetMainWindow(self, win):
		self.main_window = win

	def GetMainWindow(self):
		return self.main_window

	def SetApp(self, app):
		self.app = app

	def GetApp(self):
		return self.app

	def AddBgProcess(self, process):
		self.bg_process.append(process)

	def GetAllBgProcess(self):
		return self.bg_process

	def KillAllBgProcess(self):
		print "Killing all background process"
		for process in self.bg_process:
			process.terminate()
			print process, "killed"

# So this is a global object itself
globalManager = GlobalManager()

