class GuiErrorBase(Exception):
	def __init__(self, message=""):
		self.message = message
	def __str__(self):
		return self.message

class NoSuchFile(GuiErrorBase):
	pass

class NotespaceError(GuiErrorBase):
	pass
