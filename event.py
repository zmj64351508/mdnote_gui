import wx

# Define some events
ID_EVT_NEW_NOTESPACE = wx.NewEventType()
EVT_NEW_NOTESPACE = wx.PyEventBinder(ID_EVT_NEW_NOTESPACE, 1)
class NewNotespaceEvent(wx.PyEvent):
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(ID_EVT_NEW_NOTESPACE)

ID_EVT_PANEL_BUTTON = wx.NewEventType()
EVT_PANEL_BUTTON = wx.PyEventBinder(ID_EVT_PANEL_BUTTON, 1)
class PanelButtonEvent(wx.PyEvent):
	def __init__(self):
		wx.PyEvent.__init__(self)
		self.SetEventType(ID_EVT_PANEL_BUTTON)

