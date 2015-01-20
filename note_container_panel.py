import wx
from wx.lib.scrolledpanel import ScrolledPanel
from collapsible_pane import *
from panel_button import *
from note_manager import *
from global_manager import globalManager

# The left panel, showing notebooks/tags etc.
class NoteConatinerPanel(ScrolledPanel):
	def __init__(self, parent):
		super(NoteConatinerPanel, self).__init__(parent)
		self.button_indicator = PanelButtonIndicator()
		self.SetupScrolling(scrollToTop=False)

		# Add notebook panel
		nb_panel = NotebookCollapsiblePane(self, self.button_indicator)
		nb_panel.ShowContent()

		# tags pane
		tag_panel = TagCollapsiblePane(self, self.button_indicator)
		tag_panel.ShowContent()

		# set sizer
		sizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(sizer)
		sizer.Add(nb_panel, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)
		sizer.Add(tag_panel, 0, wx.RIGHT|wx.LEFT|wx.EXPAND, 0)

from wx.lib.embeddedimage import PyEmbeddedImage
IMG_TAG = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAkdJ"
    "REFUOI2VkslrU1EUh787vJeXNNpMGA01DlECrd0UWrD+A06oIIoLwY24FwQRNIu6EBeKy4Jb"
    "XRS6dEK0WrC2XSgFFZq0RUoHmg4WYslrxuuiGpJWKv4295zLOd/vnssR/FbX8ZvXQTzAGPPn"
    "ziAMgJAie//ifKL7ZC6pjOwylJc01WGiHUsaoLe3tz+bzZ6fmJwisxQTd25d3iAIwMDde09i"
    "L76W3GhbjL37jyLtfaysvP0QXf52VQF0dnb2pVIpdvj9DAx/JxiN8Dk9x+TMMm6hxMT4NDeu"
    "HaG97RB281ksZz9Se+OyNDqvqVMul6NcyrOyukp2cRUAR1cpl/LkfpYpV8voiotQkmJ+Bo+U"
    "OVkPqFQqVErrFAsuBXeNortGad2lXHT5Ml5gZk5QyQ9g8q+ZnR6magqfGgAAQtlobWPZHpTl"
    "QWkLIS32xOKEdp/ArbYjrBijYxaW+2OsASCEQFteLMeH7fjxeJuwHC/a8jI3O0c6M4URMbA7"
    "mF9sQhwYXNebXyClQkqF0hYASllIpWlpaSGZTIIQCKExRgDQALBtuxbvCvmpVmsrgeNVm702"
    "DOsTn88HgDHw8c0IIwOjtb1q8jUjhNge4PF4AHj/aoh4bCcH4wHevRzCGMPCwgLpdHoLoGEE"
    "x3EAuHLhGJfOdSOlpP/ZCI+fDtLa2koikdgeEIlEeHj7NEopMpkMQgjaDwd5lDpDMBgE2DJG"
    "AyAQCBAIBBBC1Arrz7/9QQMgFAptKfiXNEA4HH7e09Nz6n8aw+FwH8AvVXjA30OIWrcAAAAA"
    "SUVORK5CYII=")

IMG_NOTEBOOK = PyEmbeddedImage(
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAmtJ"
    "REFUOI19kstLlFEYxn/nfN+ZizPOeBnHS1OklmQSFVjRH9CiTUKbIKRl4V8QuFBwIUTtgqBF"
    "u3BfuW0XtAhsYWk6BqOZl7mgc/+c73JafKmZ1gNnc+D9ned5ziu0fqievep/Hg83HpXqAVa2"
    "2inXgmgE/9HUzPToJICYfvn0xe0r22MXL9wEM0WusEQ6N8DmbjMaiZQ+aB9XtRqUNmd5cH2c"
    "eMfIY1NJPTbQP4QZuQUiRDJhkC/OsZrrI7haQdX38JRBpStBPRGnsy1CCYh3jFDMvXliWrbC"
    "A/AskBLX3sauS2KrWQo9Z2hEmzCtPeKZTVxlQFuEpmDjIIu5stlGrtxGB+9xXYHjZimmY+wk"
    "ezAaNsn5FbQQ7JxLEfuRhd5OwgH7EGC7BmU9jFXcIp9dIpG8RimTYW8wSmIhQymVJLpVwAkF"
    "UDULgI/fLGy1zNe5JiRAQIWxvG62iuepub14tkQLgXRctGGAEATLNZxw4Nh3SAAh/I61MPyr"
    "SAhVtbBam/3XA4rY2jal050AeEQPIxzl+SCvt4tY+ifFs9044SCIozsRyijuzsDlxZoP0GjQ"
    "kGyP+046WijtOcTWs6hqHTegyA/1nbhRvgMNSpm0tESxbIfO1gixcBAGTh34ih/x+BegUq3z"
    "bvYDptR42j+OoxFSEFAGQggE4LoemfW811Ury++LiwD3TIAv8yvcGIwcrO1JklJSEy0sFxpy"
    "rfcSw7/NmAC7lSp9yWZSqZ5jg+KPAhfSGyd2MPUpnZ9w6jVvI9+QoZDCsZ0jgfcRjutx52q7"
    "fvu5cEAVgLw//noSmPin/xM0Mz0qAH4B9vTxRRZgeg8AAAAASUVORK5CYII=")

class NotebookButton(PanelButton):
	def OnClick(self, event):
		super(NotebookButton, self).OnClick(event)
		viewer = globalManager.GetCurrentContentViewer()
		viewer.SetNoteManager(NoteManagerByNotebook(self.button.GetLabel()))
		viewer.ShowSelection()

class TagButton(PanelButton):
	def OnClick(self, event):
		super(TagButton, self).OnClick(event)
		viewer = globalManager.GetCurrentContentViewer()
		viewer.SetNoteManager(NoteManagerByTag(self.button.GetLabel()))
		viewer.ShowSelection()

class NotebookCollapsiblePane(NoteContainerCollapsiblePane):
	def __init__(self, parent, button_indicator=None):
		super(NotebookCollapsiblePane, self).__init__(parent, NotebookManager(), button_indicator, label="Notebook")

	def CreateButton(self, parent, indicator=None, label=None):
		return NotebookButton(parent, button_indicator=indicator, label=label, bmp=IMG_NOTEBOOK.GetBitmap())

	def GetLogoBitmap(self):
		return IMG_NOTEBOOK.GetBitmap()

class TagCollapsiblePane(NoteContainerCollapsiblePane):
	def __init__(self, parent, button_indicator=None):
		super(TagCollapsiblePane, self).__init__(parent, TagManager(), button_indicator, label="Tag")

	def CreateButton(self, parent, indicator=None, label=None):
		return TagButton(parent, button_indicator=indicator, label=label, bmp=IMG_TAG.GetBitmap())

	def GetLogoBitmap(self):
		return IMG_TAG.GetBitmap()

