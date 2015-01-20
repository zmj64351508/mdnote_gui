import os
import subprocess
import re
from global_manager import globalManager
from errors import *
import wx

# managers to execute with the actual commands
class MdnoteManagerBase(object):
	def __init__(self):
		self.server = None
		self.mdnote = globalManager.GetConfig().GetMdnotePath()
		if not self.mdnote:
			raise NoSuchFile("No mdnote specified")

	def run_command(self, command):
		wx.LogMessage(command)
		output = subprocess.check_output(command, shell=True)
		match = re.findall(r'^[^(\[A-Z.*\])].*$', output, re.M)
		return match

	def run_command_background(self, *command):
		process = subprocess.Popen(command)
		if process:
			globalManager.AddBgProcess(process)

	def run_sub_command(self, sub_command):
		return self.run_command(self.mdnote + " " + sub_command)

	def run_server_command(self, server, server_command):
		retval_banner = "<return>"
		error_banner = "<error>"
		server.send(server_command)
		output = []
		buf = ""
		while 1:
			data = server.recv(1024)
			buf += data
			if not data:
				output = buf.strip().split("\n")
				break
			#sys.stdout.write(data)
			last_packet = data.strip().split("\n")[-1]
			if last_packet.find(retval_banner) == 0:
				output = buf.strip().split("\n")
				break
		retval = last_packet.replace(retval_banner, "")
		if cmp(retval, "None") != 0 and int(retval) != 0:
			wx.LogError('error occur when running command "' + server_command + '"')
			wx.LogError(buf)
			return []
		for string in output:
			if string.find(retval_banner) == 0 or string.find(error_banner) == 0:
				output.remove(string)
		return output

	def run_local_server_command(self, server_command):
		try:
			server = globalManager.local_connect.GetSocket()
			return self.run_server_command(server, server_command)
		except Exception as e:
			globalManager.local_connect.DisconnectServer()
			wx.LogError(e.__str__())
			return []

import time
# managers notespace
class NotespaceManager(MdnoteManagerBase):
	def __init__(self):
		super(NotespaceManager, self).__init__()
		mdnote_path = globalManager.GetConfig().GetMdnotePath()
		self.ValidMdnote(mdnote_path)
		self.run_command_background("python", mdnote_path, "server")
		server = globalManager.local_connect.ConnectServer()
		while not server:
			server = globalManager.local_connect.ConnectServer()
			time.sleep(0.25)

	def Initialize(self):
		notespace_path = globalManager.GetConfig().GetNotespacePath()
		self.ValidNotespace(notespace_path)

		os.chdir(notespace_path)

	def Create(self, path):
		self.run_local_server_command("init " + os.path.abspath(os.path.expanduser(path)))

	def Open(self, path):
		self.Initialize()
		self.run_local_server_command("open " + os.path.abspath(os.path.expanduser(path)))

	def ValidMdnote(self, mdnote_path):
		if not os.path.isfile(mdnote_path):
			raise NotespaceError("excutable " + mdnote_path.__str__() + " not exists")
	
	def ValidNotespace(self, ns_path):
		path = os.path.join(ns_path, ".mdnote/note.db")
		result = os.path.exists(path)
		if not result:
			raise NotespaceError(path.__str__() + " not exists")
	
class NoteContainerManager(MdnoteManagerBase):
	def __init__(self):
		super(NoteContainerManager, self).__init__()

	def GetAllContentName(self):
		pass

# NotebookManager execute all commands related to target "notebook"
class NotebookManager(NoteContainerManager):
	def __init__(self):
		super(NotebookManager, self).__init__()
		self.notebooks_name = self.run_local_server_command("list notebook")

	def GetAllContentName(self):
		return self.notebooks_name

# TagManager execute all commands related to target "tag"
class TagManager(NoteContainerManager):
	def __init__(self):
		super(TagManager, self).__init__()
		self.tags_name = self.run_local_server_command("list tag")

	def GetAllContentName(self):
		return self.tags_name

# NoteManager execute all commands related to target "note"
class NoteManager(MdnoteManagerBase):
	def __init__(self, container_name):
		super(NoteManager, self).__init__()
		assert(container_name)
		self.container = container_name

	def GetNoteInfo(self, note_path):
		info = {}
		result = self.run_local_server_command("list note -d " + note_path)
		for line in result:
			try:
				label, value = line.split(':')
				if label:
					info[label.strip()] = value.strip()
			except:
				pass
		wx.LogInfo("get note info " + str(info))
		return info

	def SetCurrentNote(self, note_info):
		if note_info is None:
			self.path = None
			self.tags = None
			self.create_time = None
			self.modify_time = None
		else:
			self.path = note_info["PATH"]
			self.notebook = note_info["NOTEBOOK"]
			self.tags = note_info["TAG"]
			self.create_time = note_info["CREATE TIME"]
			self.modify_time = note_info["MODIFY TIME"]

	def OpenContent(self):
		abspath = os.path.join(globalManager.GetConfig().GetNotespacePath(), self.path)
		return open(abspath, "r")

	def CloseContent(self, fd):
		return fd.close()

# All notes managers by this is in the same notebook
class NoteManagerByNotebook(NoteManager):
	def __init__(self, name):
		super(NoteManagerByNotebook, self).__init__(name)

	def GetAllNotesPath(self):
		return self.run_local_server_command('list note -n "' + self.container + '"')

# All notes managers by this is in the same tag
class NoteManagerByTag(NoteManager):
	def __init__(self, name):
		super(NoteManagerByTag, self).__init__(name)

	def GetAllNotesPath(self):
		return self.run_local_server_command('list note -t "' + self.container + '"')

