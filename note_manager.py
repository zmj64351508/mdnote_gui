# -*- coding: utf-8 -*-
import os, sys, errno
import subprocess
import re
from global_manager import globalManager
from errors import *
import wx

# managers to execute with the actual commands
class MdnoteManagerBase(object):
	def __init__(self):
		self.core = None
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

	def __run_core_command(self, core_server, core_command):
		retval_banner = "<return>"
		error_banner = "<error>"
		core_server.send(core_command)
		output = []
		buf = ""
		while 1:
			data = core_server.recv(1024)
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
			wx.LogError('error occur when running command "' + core_command + '"')
			wx.LogError(buf)
			return [], None
		for string in output:
			if string.find(retval_banner) == 0 or string.find(error_banner) == 0:
				output.remove(string)
		return output, int(retval)

	def run_core_command(self, *command_strings):
		core_command = u"".encode("utf8")
		for string in command_strings:
			core_command += string.encode("utf8")
		try:
			core_server = globalManager.core_connect.GetSocket()
			return self.__run_core_command(core_server, core_command)
		except Exception as e:
			globalManager.core_connect.DisconnectServer()
			wx.LogError(e.__str__())
			return [], None

import time
# managers notespace
class NotespaceManager(MdnoteManagerBase):
	def __init__(self):
		super(NotespaceManager, self).__init__()
		mdnote_path = globalManager.GetConfig().GetMdnotePath()
		self.ValidMdnote(mdnote_path)
		# try connect first if there is a core alive
		core = globalManager.core_connect.ConnectServer()
		if not core:
			self.run_command_background("python", mdnote_path, "core", "--auto-exit")
			while not core:
				core = globalManager.core_connect.ConnectServer()
				time.sleep(0.25)

	def Initialize(self):
		notespace_path = globalManager.GetConfig().GetNotespacePath()
		self.ValidNotespace(notespace_path)

		os.chdir(notespace_path)

	def Create(self, path):
		value, retval = self.run_core_command("init ", os.path.abspath(os.path.expanduser(path)).decode(sys.getfilesystemencoding()))
		return retval;

	def Open(self, path):
		self.Initialize()
		value, retval = self.run_core_command("open ", os.path.abspath(os.path.expanduser(path)).decode(sys.getfilesystemencoding()))
		return retval

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
		self.current = None
		self.notebooks_name = None
		self.Refresh()

	def SetCurrentNotebook(self, notebook_name):
		if notebook_name in self.notebooks_name:
			self.current = notebook_name
	
	def GetCurrentNotebook(self):
		return self.current

	def Refresh(self):
		self.notebooks_name, retval = self.run_core_command("list notebook")
		return retval

	def GetAllContentName(self):
		return self.notebooks_name

# TagManager execute all commands related to target "tag"
class TagManager(NoteContainerManager):
	def __init__(self):
		super(TagManager, self).__init__()
		self.tags_name, retval = self.run_core_command("list tag")

	def GetAllContentName(self):
		return self.tags_name

class Note(object):
	def __init__(self, note_info):
		assert(note_info)
		self.id = None
		self.path = note_info["PATH"].decode("utf8").encode(sys.getfilesystemencoding())
		self.abspath = os.path.join(globalManager.GetConfig().GetNotespacePath(), self.path)
		self.notebook = note_info["NOTEBOOK"].decode("utf8").encode(sys.getfilesystemencoding())
		self.tags = note_info["TAG"].decode("utf8").encode(sys.getfilesystemencoding())
		self.create_time = note_info["CREATE TIME"]
		self.modify_time = note_info["MODIFY TIME"]

# NoteManager execute all commands related to target "note"
class NoteManager(MdnoteManagerBase):
	def __init__(self, container_name):
		super(NoteManager, self).__init__()
		assert(container_name)
		self.container = container_name
		self.ClearNotes()

	def GetNote(self, id):
		if type(id) is int:
			return self.notes[id]
		else:
			raise TypeError

	def GetOpenedNotes(self):
		return [self.note[id] for id in self.opened_id]

	def Add(self, note):
		if len(self.removed_id) > 0:
			id = self.removed_id.pop()
			note.id = id
			self.notes[id] = note
			return note.id
		else:
			self.notes.append(note)
			self.notes[-1].id = len(self.notes) - 1
			return self.notes[-1].id

	def Remove(self, ids):
		notes_path = []
		for id in ids:
			notes_path.append(self.GetNote(id).path.decode(sys.getfilesystemencoding()))
			self.removed_id.append(id)
			wx.LogInfo("removed id %d" % id)
		return self.RemoveNotesCommond(notes_path)

	def ReplaceNote(self, id, note):
		if id:
			note.id = id
		if note.id:
			self.notes[id] = note
			return True
		else:
			return False
			
	def ClearNotes(self):
		self.notes = []
		self.opened_id = []
		self.current_id = None
		self.removed_id = []

	def SetCurrentNote(self, id):
		if id < 0 or id >= len(self.notes):
			wx.LogWarning("SetCurrentNote: note id is out of range, ignoring")
			return
		self.opened_id.append(id)
		self.current_id = id

	def GetCurrentNote(self):
		return self.notes[self.current_id]

	def OpenNote(self, id):
		if id < 0 or id >= len(self.notes):
			wx.LogWarning("SetCurrentNote: note id is out of range, ignoring")
			return
		self.opened_id.append(id)

	def CloseNote(self, id):
		if id in self.opened_id:
			self.opened_id.remove(id)
		if id == self.current_id:
			self.current_id = None

	def GetNotesCommand(self):
		pass

	def ParseNoteInfo(self, to_parse):
		# each record sent has format like:
		# PATH:xxx\n
		# TAG:xxx;xxx;\n
		# CREATE TIME:xxx\n
		# MODIFY TIME:xxx\n
		#  \n
		info = {}
		for line in to_parse:
			try:
				label, value = line.split(':')
				if label:
					info[label.strip()] = value.strip()
			except:
				if cmp(line, " ") == 0:
					yield Note(info)
					info = {}

	def RefreshOne(self, id):
		result = self.GetOneNoteCommand(self.notes[id].path)
		try:
			note = self.ParseNoteInfo(result).next()
			if note:
				self.ReplaceNote(id, Note(info))
			return note
		except StopIteration:
			return None

	def RefreshAll(self):
		self.ClearNotes()
		result = self.GetNotesCommand()
		for note in self.ParseNoteInfo(result):
			self.Add(note)
		return self.notes

	def GetNotes(self):	
		if self.notes:
			return self.notes
		else:
			return self.RefreshAll()
			

# All notes managers by this is in the same notebook
class NoteManagerByNotebook(NoteManager):
	def __init__(self, name):
		super(NoteManagerByNotebook, self).__init__(name)

	def GetNotesCommand(self):
		value, retval = self.run_core_command('list note -d -n "', self.container, '"')
		return value

	def GetOneNoteCommand(self, note_path):
		value, retval = self.run_core_command('list note -d "', note_path, '"')
		return value

	def RemoveNotesCommond(self, notes_path):
		paths = ""
		for path in notes_path:
			paths += ' "' + path + '" '
		value, retval = self.run_core_command('rm note --purge ' + paths)
		return retval

	def NewNote(self, path):
		abs_path, rel_path = self.BuildPath(path)
		fd = open(abs_path, "w")
		fd.close()
		value, retval = self.run_core_command('add note -n "', self.container, '" "', rel_path, '"')
		result = self.GetOneNoteCommand(rel_path)
		try:
			note = self.ParseNoteInfo(result).next()
			if note:
				self.Add(note)
			return note
		except StopIteration:
			return None

	# path ascii in ascii out
	def BuildPath(self, path):
		path = path.encode(sys.getfilesystemencoding())
		dirname = os.path.dirname(path)
		dirname = globalManager.MakeNoteAbsPath(dirname)

		basename = os.path.basename(path)
		name = basename.split(".")[0]
		if len(name) != len(basename):
			extname = basename[len(name):]
		else:
			extname = ""

		new_path = os.path.join(dirname, basename)
		i = 1
		while os.path.exists(new_path):
			new_path = os.path.join(dirname, "%s(%d)%s" % (name, i, extname))
			i += 1
		wx.LogInfo("New Note path is %s" % new_path)
		return new_path.decode(sys.getfilesystemencoding()),\
			globalManager.MakeNoteRelPath(new_path).decode(sys.getfilesystemencoding()) 

# All notes managers by this is in the same tag
class NoteManagerByTag(NoteManager):
	def __init__(self, name):
		super(NoteManagerByTag, self).__init__(name)

	def GetNotesCommand(self):
		value, retval = self.run_core_command('list note -d -t "', self.container, '"')
		return value

