import wx
from pyrfeed.Config import register_key

class RSSHtmlListBox(wx.HtmlListBox) :
    def __init__(self, parent, frame, config, *args, **kwargs) :
        self._choices=[]
        self._selected_items = set()
        kwargs['style'] = wx.WANTS_CHARS
        wx.HtmlListBox.__init__(self, parent, *args, **kwargs)
        self.SetItemCount(0)

        self._frame = frame

        self._config = config

        self._checked_pattern = '%s'
        self._unchecked_pattern = '%s'

        self._checked_pattern = "<font color='red'><font size='-1'>%s</font></font>"
        if self._config['wx/htmllistbox/usebold'] :
            self._checked_pattern = "<b>" + self._checked_pattern + "</b>"
        self._unchecked_pattern = "<font size='-1'>%s</font>"

        if self._config['wx/htmllistbox/useimage'] :
            self._checked_pattern = "<img src='../res/checked.png'>&nbsp;" + self._checked_pattern
            self._unchecked_pattern = "<img src='../res/unchecked.png'>&nbsp;" + self._unchecked_pattern

    def Create(self, *args, **kwargs) :
        self.SetChoices()

    def SetChoices(self, choices=None) :
        self.Clear()
        self.Refresh()
        if choices == None :
            choices = []
        self._choices = choices
        self._selected_items = set()
        self._frame.SetSelectedCount(len(self._selected_items))
        self.SetItemCount(len(self._choices))


    def Append(self, string) :
        self._choices.append(string)
        self.SetItemCount(len(self._choices))

    def GetSelectedTextColour(self, color) :
        pos = self.GetSelection()
        if pos in self._selected_items :
            return color.Set(0xff,0x00,0x00)
        return color.Set(0x00,0xff,0x00)

    def OnGetItem(self, n) :
        if 0 <= n < len(self._choices) :
            item_content = self._choices[n]
            if n in self._selected_items :
                item_content = self._checked_pattern % item_content
            else :
                item_content = self._unchecked_pattern % item_content
            return item_content
        return ""

    def SelectItem(self,event=None) :
        pos = self.GetSelection()
        if pos in self._selected_items :
            self._selected_items.remove(pos)
        else :
            self._selected_items.add(pos)
        self._frame.SetSelectedCount(len(self._selected_items))
        self.RefreshAll()

    def SelectItemNext(self,event=None) :
        self.SelectItem(event)
        self.Next(event)

    def Prev(self,event=None) :
        pos = self.GetSelection()
        pos -= 1
        if pos<0 :
            pos=0
        elif pos>=len(self._choices) :
            pos = len(self._choices)-1
        self.SetSelection(pos)
        self._frame.OnTitleSelected(None)


    def Next(self,event=None) :
        pos = self.GetSelection()
        pos += 1
        if pos<0 :
            pos=0
        elif pos>=len(self._choices) :
            pos = len(self._choices)-1
        self.SetSelection(pos)
        self._frame.OnTitleSelected(None)

    def GetSelectedItems(self) :
        if len(self._selected_items) == 0 :
            self.SelectItem()
        return list(self._selected_items)

register_key( 'wx/htmllistbox/useimage', bool, doc='Use image for check/uncheck', default=False )
register_key( 'wx/htmllistbox/usebold', bool, doc='Use bold for check', default=True )

