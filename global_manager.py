import os, socket
import wx

# This class managers all the configurations
class MdnoteConfig(object):
	mdnote_path = "~/Program/mdnote/cli/mdnote.py"
	#mdnote_path = r"\\10.3.35.112\Program\mdnote\cli\mdnote.py"
	notespace_path = "~/Program/mdnote/cli/test_dir"
	local_server_addr = ("127.0.0.1", 46000)
	remote_server_addr = ("127.0.0.1", 46000)

	def __init__(self):
		self.SetMdnotePath(self.mdnote_path)
		self.SetNotespacePath(self.notespace_path)

	def SetNotespacePath(self, path):
		self.notespace_path = os.path.expanduser(path)

	def GetNotespacePath(self):
		return os.path.expanduser(self.notespace_path)

	def SetMdnotePath(self, path):
		self.mdnote_path = os.path.expanduser(path)

	def GetMdnotePath(self):
		return os.path.expanduser(self.mdnote_path)
	
	def GetLocalServerAddr(self):
		return self.local_server_addr

	def GetRemoteServerAddr(self):
		return self.remote_server_addr

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

class LocalConnectManager(ConnectManager):
	def GetServerAddr(self):
		return globalManager.GetConfig().GetLocalServerAddr()

class RemoteConnectManager(ConnectManager):
	def GetServerAddr(self):
		return globalManager.GetConfig().GetRemoteServerAddr()

# This class managers all global objects
class GlobalManager(object):
	current_content_viewer = None
	def __init__(self):
		self.config = MdnoteConfig()
		self.local_connect = LocalConnectManager()
		self.remote_connect = RemoteConnectManager()

	def GetConfig(self):
		return self.config

	def SetCurrentContentViewer(self, viewer):
		self.current_content_viewer = viewer

	def GetCurrentContentViewer(self):
		return self.current_content_viewer

	def SetMainWindow(self, win):
		self.main_window = win

	def GetMainWindow(self):
		return self.main_window
# So this is a global object itself
globalManager = GlobalManager()

