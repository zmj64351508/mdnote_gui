import os

# This class managers all the configurations
class MdnoteConfig(object):
	mdnote_path = "~/Program/mdnote/cli/mdnote.py"
	#mdnote_path = r"\\10.3.35.112\Program\mdnote\cli\mdnote.py"
	notespace_path = "~/Program/mdnote/cli/test_dir"

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

	def IsLogging(self):
		return True


# This class managers all global objects
class GlobalManager(object):
	current_content_viewer = None
	def __init__(self):
		self.config = MdnoteConfig()

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

