#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

import os
import sys

import wx
import webbrowser
from wxMenuProvider import MenuProvider

from pyrfeed.Gui.wx.Controls.HtmlWindow import HtmlClasses, HTML_SIMPLE, HTML_COMPLEX
from pyrfeed.Gui.wx.Controls.RSSHtmlListBox import RSSHtmlListBox
from pyrfeed.Gui.wx.Controls.FilterControl import FilterControl

from pyrfeed.Gui.Info import GuiInfo
from pyrfeed.Gui.InfoList import gui_info_list
from pyrfeed.Config import register_key

class RSSReaderFrame(wx.Frame,MenuProvider):
    def __init__(self, config, *args, **kwds):
        kwds["style"] = wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)

        self._config = config

        self.Maximize(True)

        self._create_components()
        self._set_properties()
        self._do_layout()
        self._bind_events()

        self._rss_reader = None
        self._loading_page = False

        self._clipboard = wx.Clipboard()

        self._pagestart = 0
        self._pagesize = 30

        self._pagesize = self._config['pagesize']

        self._labels_in_menus = []
        self._labels_by_add_id = {}
        self._labels_by_del_id = {}

        self._interface_name_by_menu_id = {}

        self._titles = []

        self.SetNextGuiMenu()

    def _create_combo_filter( self, parent ) :
        self._combo_filter = FilterControl(parent)

    def _create_listbox_title( self, parent ) :
        self._listbox_title = RSSHtmlListBox(parent, self, self._config, style=wx.LB_EXTENDED)

    def _create_window_html( self, parent ) :
        htmlwindow_name = self._config['wx/htmlwindow']
        pos = None
        if htmlwindow_name == 'simple' :
            pos = HTML_SIMPLE
        elif htmlwindow_name == 'complex' :
            pos = HTML_COMPLEX
        else :
            pos = -1
        self._window_html = HtmlClasses[pos]['class'](parent)

    def _create_listbox_categories( self, parent ) :
        self._listbox_categories = wx.ListBox(parent, style=wx.LB_EXTENDED|wx.LB_SORT)

    def _create_status_bar( self, parent ) :
        self._status_bar = wx.StatusBar(parent)

    def _set_properties(self) :
        self._status_bar.SetFieldsCount(2)
        self.SetStatusBar(self._status_bar)
        menu_content = [
            ('&File',                                       None,                               '' ),
            ('-/&Synchro'+'\tCtrl+Shift+S',                 self.Synchro,                       '', [(wx.ACCEL_CTRL, ord('S')),
                                                                                                     (wx.ACCEL_SHIFT, wx.WXK_F5)] ),
            ('-/&Reload'+'\tCtrl+Shift+R',                  self.Reload,                        '', [(wx.ACCEL_CTRL, ord('R')),
                                                                                                     (wx.ACCEL_NORMAL, wx.WXK_F5)] ),
            ('-/-',),
            ('-/S&witch interface',),
            ('-/-/-',),
            ('-/-',),
            ('-/&Quit',                                     self.Quit,                          '' ),
            ('&Edit',                                       None,                               '' ),
            ('-/&Select'+'\tCtrl+Shift+Y',                  self._listbox_title.SelectItem,     '', [(wx.ACCEL_CTRL, wx.WXK_SPACE),
                                                                                                     (wx.ACCEL_CTRL|wx.ACCEL_SHIFT, wx.WXK_SPACE)] ),
            ('-/Select and goto ne&xt'+'\tCtrl+Shift+I',    self._listbox_title.SelectItemNext, '', [(wx.ACCEL_NORMAL, wx.WXK_INSERT)] ),
            ('-/-',),
            ('-/&Open link'+'\tCtrl+Shift+O',               self.OpenInWebBrowser,              '', [(wx.ACCEL_CTRL, wx.WXK_RETURN)] ),
            ('-/&Open links'+'\tCtrl+Shift+Alt+O',          self.OpenMultiInWebBrowser,         '', [] ),
            ('-/-',),
            ('-/&Previous'+'\tCtrl+Shift+K',                self._listbox_title.Prev,           '', [] ),
            ('-/&Next'+'\tCtrl+Shift+J',                    self._listbox_title.Next,           '', [] ),
            ('-/P&age',),
            ('-/P&age/&Previous'+'\tCtrl+Shift+L',          self.OnPreviousPage,                '', [] ),
            ('-/P&age/&Next'+'\tCtrl+Shift+H',              self.OnNextPage,                    '', [] ),
            ('-/-',),
            ('-/Mark as &Read'+'\tCtrl+Shift+M',            self.MarkAsRead,                    '', [] ),
            ('-/Mark as &Unread'+'\tCtrl+Shift+U',          self.MarkAsUnread,                  '', [] ),
            ('-/-',),
            ('-/Add Star',                                  self.AddStar,                       '', [] ),
            ('-/Del Star',                                  self.DelStar,                       '', [] ),
            ('-/-',),
            ('-/Add Public',                                self.AddPublic,                     '', [] ),
            ('-/Del Public',                                self.DelPublic,                     '', [] ),
            ('-/-',),
            ('-/Add &Label',                                None,                               '', [] ),
            ('-/-/-',),
            ('-/Del La&bel',                                None,                               '', [] ),
            ('-/-/-',),
            ('-/-',),
            ('-/Add &Filter'+'\tAlt+SPACE',                 self.FocusFilter,                   '', [] ),
            ]

        self.SetMenuContent(self,menu_content)

        self.SetTitle("RSS Reader")

        self._icon = None

        if len(sys.argv) >= 1 and os.path.exists(sys.argv[0]) and sys.argv[0][-4:] == '.exe':
            self._icon = wx.Icon(sys.argv[0], wx.BITMAP_TYPE_ICO)
        else :
            icon_name = os.path.join('..','res','pyrfeed.ico')
            if os.path.exists(icon_name):
                self._icon = wx.Icon(icon_name, wx.BITMAP_TYPE_ICO)

        if self._icon :
            self.SetIcon(self._icon)

        self._combo_filter.SetValue('')

    def _bind_events(self) :
        self._listbox_title.Bind(wx.EVT_LISTBOX, self.OnTitleSelected)
        self._combo_filter.BindChange(self.OnComboChange)
        self._listbox_categories.Bind(wx.EVT_LISTBOX, self.OnCategoriesSelected)

    def Quit(self,event=None) :
        self.Close()

    def SetRssReader(self,rss_reader) :
        self._rss_reader = rss_reader
        self._combo_filter.SetValue(self._rss_reader.get_filter())

    def Populate(self,is_reload=False,same_titles=False) :
        self._listbox_title.SetChoices()

        if self._rss_reader :
            if not(same_titles) :
                self._titles = self._rss_reader.get_titles()
            self._len_titles = len(self._titles)

            if self._pagestart >= self._len_titles :
                self._pagestart = (self._len_titles/self._pagesize)*self._pagesize
            if self._pagestart < 0 :
                self._pagestart = 0

            for index in xrange(self._pagestart,self._pagestart+self._pagesize) :
                if 0<=index<len(self._titles) :
                    self._listbox_title.Append("%d - %s" % (index,self._titles[index]))
            if is_reload :
                filters = self._rss_reader.get_filters()
                self._combo_filter.ChangeDefaultFilter( filters )
                self.ChangeLabels( filter(lambda x:x.startswith('label:'),filters) )
            self._combo_filter.ChangeDiffFilter( self._rss_reader.get_filters_diff() )

            item_count = '%d items.' % self._len_titles
            if self._pagesize<self._len_titles :
                item_count += ' (page %d/%d)' % (self._pagestart/self._pagesize+1,(self._len_titles-1)/self._pagesize+1)

            self.SetCurrentStatus(item_count)
        self.OnTitleSelected()

    def OnTitleSelected (self, event=None) :
        if not(self._loading_page) :
            busy = wx.BusyCursor()
            self._loading_page = True
            if self._rss_reader :
                position = self._pagestart
                position += self._listbox_title.GetSelection()
                self._window_html.ChangePage(self._rss_reader.get_content(position))
                categories = self._rss_reader.get_categories(position)
                self._listbox_categories.Clear()
                if categories is not None :
                    for categorie in categories :
                        self._listbox_categories.Append(categorie)
                self._listbox_title.SetFocus()
            self._loading_page = False
            busy = None

    def Synchro (self, event=None) :
        busy = wx.BusyCursor()
        self.SetCurrentStatus("Synchronizing...")
        if self._rss_reader :
            synchro_result = self._rss_reader.synchro()
            if synchro_result is not None :
                self.SetCurrentStatus(synchro_result)
            else :
                self.Populate(is_reload=True)
        self._listbox_title.SetFocus()
        busy = None

    def Reload (self, event=None) :
        busy = wx.BusyCursor()
        self.SetCurrentStatus("Reloading...")
        if self._rss_reader :
            self._rss_reader.reload()
            self.Populate(is_reload=True)
        self._listbox_title.SetFocus()
        busy = None

    def _ProcessOnItems (self, action, status) :
        busy = wx.BusyCursor()
        if self._rss_reader :
            items = self._listbox_title.GetSelectedItems()
            items = map(lambda item:item+self._pagestart,items)
            self.SetCurrentStatus(status % len(items))
            action(items)
            self.Reload()
        busy = None

    def MarkAsRead (self, event=None) :
        self._ProcessOnItems( self._rss_reader.mark_as_read, 'Marking %d items as read...' )

    def MarkAsUnread(self, event=None) :
        self._ProcessOnItems( self._rss_reader.mark_as_unread, 'Marking %d items as unread...' )

    def AddStar(self, event=None) :
        self._ProcessOnItems( self._rss_reader.add_star, 'Adding star on %d items...' )

    def DelStar(self, event=None) :
        self._ProcessOnItems( self._rss_reader.del_star, 'Removing star on %d items...' )

    def AddPublic(self, event=None) :
        self._ProcessOnItems( self._rss_reader.add_public, 'Adding public status on %d items...' )

    def DelPublic(self, event=None) :
        self._ProcessOnItems( self._rss_reader.del_public, 'Removing public status on %d items...' )

    def AddLabel(self, event) :
        menu_id = event.GetId()
        if menu_id in self._labels_by_add_id :
            label = self._labels_by_add_id[menu_id]
            self._ProcessOnItems( lambda positions : self._rss_reader.add_label(positions,label), 'Adding label "%s" on %%d items...' % label )

    def DelLabel(self, event) :
        menu_id = event.GetId()
        if menu_id in self._labels_by_del_id :
            label = self._labels_by_del_id[menu_id]
            self._ProcessOnItems( lambda positions : self._rss_reader.del_label(positions,label), 'Removing label "%s" on %%d items...' % label )

    def ChangeLabels(self,labels) :
        if self._labels_in_menus != labels :
            self._labels_in_menus = labels
            self._labels_by_add_id = {}
            self._labels_by_del_id = {}

            actions_infos = [
                {
                    'menu_label' : 'Edit/Add Label',
                    'menu_ids' : self._labels_by_add_id,
                    'menu_action' : self.AddLabel,
                    },
                {
                    'menu_label' : 'Edit/Del Label',
                    'menu_ids' : self._labels_by_del_id,
                    'menu_action' : self.DelLabel,
                    },
                ]

            for action_infos in actions_infos :
                menu = self.GetMenuByPath(action_infos['menu_label'])

                if menu is not None :
                    for old_id in map(lambda x:x.GetId(),menu.GetMenuItems()) :
                        self.Unbind(wx.EVT_MENU, id=old_id )
                        menu.Delete(old_id)

                    for label in labels :
                        label_id = wx.NewId()
                        label_name = label.split(':',1)[1]
                        action_infos['menu_ids'][label_id] = label_name
                        menu.AppendMenu( label_id, label_name, None )
                        self.Bind(wx.EVT_MENU, action_infos['menu_action'], id=label_id )

    def SetNextGuiMenu(self) :
        menu = self.GetMenuByPath('File/Switch interface')

        if menu is not None :
            for old_id in map(lambda x:x.GetId(),menu.GetMenuItems()) :
                self.Unbind(wx.EVT_MENU, id=old_id )
                menu.Delete(old_id)

            for ui_name,name in gui_info_list.get_ui_names() :
                menu_id = wx.NewId()
                menu_name = ui_name
                self._interface_name_by_menu_id[menu_id] = name
                menu.AppendMenu( menu_id, menu_name, None )
                self.Bind(wx.EVT_MENU, self.SetNextGui, id=menu_id )

    def SetNextGui(self,event) :
        menu_id = event.GetId()
        if menu_id in self._interface_name_by_menu_id :
            busy = wx.BusyCursor()
            self._config['gui/next'] = self._interface_name_by_menu_id[menu_id]
            self.Close()
            busy = None

    def OpenInWebBrowser(self, event=None) :
        busy = wx.BusyCursor()
        if self._rss_reader :
            position = self._pagestart
            position += self._listbox_title.GetSelection()
            link = self._rss_reader.get_link(position)
            if link and link != '' :
                webbrowser.open(link)
        busy = None

    def OpenMultiInWebBrowser(self, event=None) :
        def openlink(positions) :
            for position in positions :
                link = self._rss_reader.get_link(position)
                if link and link != '' :
                    webbrowser.open(link)

        self._ProcessOnItems( openlink, 'Opening links for %d items...' )

    def OnComboChange(self, event=None) :
        busy = wx.BusyCursor()
        self.SetCurrentStatus("Filtering...")
        if self._rss_reader :
            self._rss_reader.set_filter(self._combo_filter.GetValue())
            self.Populate()
        busy = None

    def OnCategoriesSelected(self, event=None) :
        busy = wx.BusyCursor()
        categories_selected = ""
        for categorie_position in self._listbox_categories.GetSelections() :
            categories_selected += self._listbox_categories.GetString(categorie_position) + ' '
        categories_selected.strip(' ')

        text_data_object = wx.TextDataObject()
        text_data_object.SetText(categories_selected)
        if self._clipboard.Open() :
            self._clipboard.SetData(text_data_object)
            self._clipboard.Close()

        busy = None

    def SetCurrentStatus(self, text) :
        self._status_bar.SetStatusText(text,0)

    def SetSelectedCount(self, count) :
        self._status_bar.SetStatusText("%d selected item"%count+(count>1 and "s" or ""),1)

    def FocusFilter(self, event=None) :
        self._combo_filter.SetFocus()

    def OnNextPage(self, event) :
        busy = wx.BusyCursor()
        self.SetCurrentStatus("Changing page...")
        self._pagestart += self._pagesize
        self.Populate(same_titles=True)
        busy = None

    def OnPreviousPage(self, event) :
        busy = wx.BusyCursor()
        self.SetCurrentStatus("Changing page...")
        self._pagestart -= self._pagesize
        self.Populate(same_titles=True)
        busy = None


def get_simple_app() :
    if hasattr(get_simple_app,'_simple_app') :
        return get_simple_app._simple_app
    get_simple_app._simple_app = wx.PySimpleApp(0)
    wx.InitAllImageHandlers()
    return get_simple_app._simple_app

class GuiInfoWx(GuiInfo) :
    names = []
    priority = 50
    RSSReaderFrameClass = None

    def _start_application(self) :
        app = get_simple_app()
        rss_reader_frame = self.RSSReaderFrameClass(self._config, None)
        rss_reader_frame.SetRssReader(self._rss_reader)
        app.SetTopWindow(rss_reader_frame)
        rss_reader_frame.Show()
        rss_reader_frame.Reload()
        app.MainLoop()

    def get_doc(self) :
        return ""

register_key( 'pagesize', int, doc='Size of a page of items', default=30 )
register_key( 'wx/sashposition', int, doc='Position of the Sash seperation in pixels', default=200 )
register_key( 'wx/htmlwindow', str, doc='HTML Window component to use', default='best' )

# 'gui/next' will be handled elsewere for registration
