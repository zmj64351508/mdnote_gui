# -*- coding: utf-8 -*-
import wx
from event import *

# This is the base class for buttons of tag/notebook/note etc.
class PanelButton(wx.Panel):
	def __init__(self, parent, label="", button_indicator=None, bmp=None, 
		     hover_color=wx.Colour(220, 220, 220),
		     indicator_color=wx.Colour(200, 200, 250),
		     click_color=None,
		     **kargs):
		wx.Panel.__init__(self, parent, wx.ID_ANY, **kargs)
		self.button = wx.StaticText(self, label=label)
		font = self.button.GetFont()
		font.SetPointSize(10)
		self.button.SetFont(font)
		self.button_indicator = button_indicator
		if bmp:
			self.image = wx.StaticBitmap(self, -1, bmp, (0, 0), (bmp.GetWidth(), bmp.GetHeight()))
			self.image.Bind(wx.EVT_LEFT_UP, self.__OnMouseUp)

		self.Bind(wx.EVT_LEFT_DOWN, self.__OnMouseDown)
		self.Bind(wx.EVT_LEFT_DCLICK, self.__OnMouseDown)
		self.Bind(wx.EVT_LEFT_UP, self.__OnMouseUp)

		self.button.Bind(wx.EVT_LEFT_DOWN, self.__OnMouseDown)
		self.button.Bind(wx.EVT_LEFT_DCLICK, self.__OnMouseDown)
		self.button.Bind(wx.EVT_LEFT_UP, self.__OnMouseUp)

		self.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver)
		self.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeave)

		# When mouse hovers children, it will generate EVT_LEAVE_WINDOW for the parent
		# So we need to distinguish these 2 condition:
		# parent => child
		# parent => autual_leave
		for child in self.GetChildren():
			child.Bind(wx.EVT_LEAVE_WINDOW, self.OnMouseLeaveChild)
			child.Bind(wx.EVT_ENTER_WINDOW, self.OnMouseOver)
		self.over_child = False

		self.origin_color = self.button.GetBackgroundColour()
		self.hover_color = hover_color
		self.indicator_color = indicator_color
		self.click_color = click_color

		sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(sizer)
		if bmp:
			sizer.Add(self.image, 0, wx.LEFT|wx.RIGHT|wx.ALIGN_CENTER_VERTICAL, 10)
		sizer.Add(self.button, 0, wx.TOP|wx.BOTTOM|wx.EXPAND, 5)

	def GetLabel(self):
		return self.button.GetLabel()

	def Select(self):
		self.SetFocus()
		if self.button_indicator:
			self.button_indicator.SetCurrent(self, self.origin_color, self.indicator_color)
		else:
			self.ClearBackground()
			self.SetBackgroundColour(self.hover_color)
			self.Refresh()
		wx.PostEvent(self, PanelButtonEvent())

	def __OnMouseDown(self, event):
		wx.LogInfo('Mouse Down')
		if self.click_color:
			self.ClearBackground()
			self.SetBackgroundColour(self.click_color)
			self.Refresh()

	def __OnMouseUp(self, event):
		if not self.MouseInButtonArea():
			return
		self.Select()

	def OnMouseOver(self, event):
		if not self.button_indicator or self.button_indicator.GetCurrent() != self:
			self.ClearBackground()
			self.SetBackgroundColour(self.hover_color)
			self.Refresh()

	def MouseInButtonArea(self):
		width, height = self.GetVirtualSize()
		rel_pos = wx.GetMousePosition() - self.GetScreenPosition()
		if rel_pos.x < 0 or rel_pos.x >= width or \
		   rel_pos.y < 0 or rel_pos.y >= height:
			return False
		else:
			return True

	def OnMouseLeave(self, event):
		if self.MouseInButtonArea():
			return
		if not self.button_indicator or self.button_indicator.GetCurrent() != self:
			self.ClearBackground()
			self.SetBackgroundColour(self.origin_color)
			self.Refresh()

	# When mouse leave child fast enough, it won't generate EVT_ENTER_WINDOW and EVT_LEAVE_WINDOW for the parent
	# So we just check the leave event like what parent do
	def OnMouseLeaveChild(self, event):
		self.OnMouseLeave(event)

# This class help to indicate which is selected in a singel panel
class PanelButtonIndicator(object):
	def __init__(self):
		self.last = None

	def SetCurrent(self, button, origin_color, indicator_color):
		if self.last:
			self.last.ClearBackground()
			self.last.SetBackgroundColour(origin_color)
			# Refresh for the previous button, to actually clear the background
			self.last.Refresh()
		button.ClearBackground()
		button.SetBackgroundColour(indicator_color)
		button.Refresh()
		self.last = button

	def GetCurrent(self):
		return self.last
