import os
import subprocess
import re
from global_manager import globalManager

# managers to execute with the actual commands
class MdnoteManagerBase(object):
	def __init__(self):
		self.mdnote = globalManager.GetConfig().GetMdnotePath()
		if not self.mdnote:
			raise NoSuchFile("No mdnote specified")

	def run_command(self, command):
		output = subprocess.check_output(command, shell=True)
		match = re.findall(r'^[^(\[A-Z.*\])].*$', output, re.M)
		return match

	def run_sub_command(self, sub_command):
		return self.run_command(self.mdnote + " " + sub_command)

# managers notespace
class NotespaceManager(MdnoteManagerBase):
	def __init__(self):
		super(NotespaceManager, self).__init__()
		os.chdir(os.path.expanduser(globalManager.GetConfig().GetNotespacePath()))
	
class NoteContainerManager(MdnoteManagerBase):
	def __init__(self):
		super(NoteContainerManager, self).__init__()

	def GetAllContentName(self):
		pass

# NotebookManager execute all commands related to target "notebook"
class NotebookManager(NoteContainerManager):
	def __init__(self):
		super(NotebookManager, self).__init__()
		self.notebooks_name = self.run_sub_command("list notebook")

	def GetAllContentName(self):
		return self.notebooks_name

# TagManager execute all commands related to target "tag"
class TagManager(NoteContainerManager):
	def __init__(self):
		super(TagManager, self).__init__()
		self.tags_name = self.run_sub_command("list tag")

	def GetAllContentName(self):
		return self.tags_name

# NoteManager execute all commands related to target "note"
class NoteManager(MdnoteManagerBase):
	def __init__(self, container_name):
		super(NoteManager, self).__init__()
		assert(container_name)
		self.container = container_name

# All notes managers by this is in the same notebook
class NoteManagerByNotebook(NoteManager):
	def __init__(self, name):
		super(NoteManagerByNotebook, self).__init__(name)

	def GetAllNotesPath(self):
		return self.run_sub_command('list note -n "' + self.container + '"')

# All notes managers by this is in the same tag
class NoteManagerByTag(NoteManager):
	def __init__(self, name):
		super(NoteManagerByTag, self).__init__(name)

	def GetAllNotesPath(self):
		return self.run_sub_command('list note -t "' + self.container + '"')

