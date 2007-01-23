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

from pyrfeed import __version__ as pyrfeed_version

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

    def _create_tool_bar( self ) :
        self._tool_bar = self.CreateToolBar(style=wx.TB_HORIZONTAL)

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

        self._events = {
            'SYNCHRO' : {
                'action' : self.Synchro,
                'bitmap' : 'synchro',
                'accels' : [
                    ('Ctrl','Shift','S'),
                    ('Ctrl','S'),
                    ('Shift','F5'),
                    ],
                'help' : 'Synchronize with server',
                },
            'RELOAD' : {
                'action' : self.Reload,
                'bitmap' : 'reload',
                'accels' : [
                    ('Ctrl','Shift','R'),
                    ('Ctrl','R'),
                    ('F5'),
                    ],
                'help' : 'Reload entry list',
                },
            'QUIT' : {
                'action' : self.Quit,
                'bitmap' : 'quit',
                'help' : 'Quit',
                },
            'SELECT' : {
                'action' : self._listbox_title.SelectItem,
                'bitmap' : 'select',
                'accels' : [
                    ('Ctrl','Shift','Y'),
                    ('Ctrl','SPACE'),
                    ('Ctrl','Shift','SPACE'),
                    ],
                'help' : '',
                },
            'SELECTNEXT' : {
                'action' : self._listbox_title.SelectItemNext,
                'bitmap' : 'selectnext',
                'accels' : [
                    ('Ctrl','Shift','I'),
                    ('INSERT'),
                    ],
                'help' : '',
                },
            'OPENLINK' : {
                'action' : self.OpenInWebBrowser,
                'bitmap' : 'openlink',
                'accels' : [
                    ('Ctrl','Shift','O'),
                    ('Ctrl','RETURN'),
                    ],
                'help' : '',
                },
            'OPENLINKS' : {
                'action' : self.OpenMultiInWebBrowser,
                'bitmap' : 'openlinks',
                'accels' : [
                    ('Ctrl','Alt','Shift','O'),
                    ],
                'help' : '',
                },
            'PREVIOUS' : {
                'action' : self._listbox_title.Prev,
                'bitmap' : 'previous',
                'accels' : [
                    ('Ctrl','Shift','K'),
                    ],
                'help' : '',
                },
            'NEXT' : {
                'action' : self._listbox_title.Next,
                'bitmap' : 'next',
                'accels' : [
                    ('Ctrl','Shift','J'),
                    ],
                'help' : '',
                },
            'PREVIOUSPAGE' : {
                'action' : self.OnPreviousPage,
                'bitmap' : 'previouspage',
                'accels' : [
                    ('Ctrl','Shift','L'),
                    ],
                'help' : '',
                },
            'NEXTPAGE' : {
                'action' : self.OnNextPage,
                'bitmap' : 'nextpage',
                'accels' : [
                    ('Ctrl','Shift','H'),
                    ],
                'help' : '',
                },
            'MARKASREAD' : {
                'action' : self.MarkAsRead,
                'bitmap' : 'markasread',
                'accels' : [
                    ('Ctrl','Shift','M'),
                    ],
                'help' : '',
                },
            'MARKASUNREAD' : {
                'action' : self.MarkAsUnread,
                'bitmap' : 'markasunread',
                'accels' : [
                    ('Ctrl','Shift','U'),
                    ],
                'help' : '',
                },
            'ADDSTAR' : {
                'action' : self.AddStar,
                'bitmap' : 'addstar',
                'accels' : [
                    ],
                'help' : '',
                },
            'DELSTAR' : {
                'action' : self.DelStar,
                'bitmap' : '',
                'accels' : [
                    ],
                'help' : '',
                },
            'ADDPUBLIC'      : {
                'action' : self.AddPublic,
                'bitmap' : 'addpublic',
                'accels' : [
                    ],
                'help' : 'Add public status',
                },
            'DELPUBLIC' : {
                'action' : self.DelPublic,
                'bitmap' : '',
                'accels' : [
                    ],
                'help' : 'Del public status',
                },
            'ADDFILTER' : {
                'action' : self.FocusFilter,
                'bitmap' : '',
                'accels' : [
                    ('Alt','SPACE'),
                    ],
                'help' : 'Set focus to filter component',
                },
            'HELPDOC' : {
                'action' : self.OnHelpDoc,
                'bitmap' : 'helpdoc',
                'accels' : [
                    ('F1',),
                    ],
                'help' : 'Read online doc (not much now)',
                },
            'HELPBUG' : {
                'action' : self.OnHelpIssues,
                'bitmap' : 'helpbug',
                'accels' : [
                    ],
                'help' : 'Submit a bug',
                },
            'HELPNEWFEATURE' : {
                'action' : self.OnHelpIssues,
                'bitmap' : 'helpfeature',
                'accels' : [
                    ],
                'help' : 'Request new feature',
                },
            'HELPSITE' : {
                'action' : self.OnHelpWebSite,
                'bitmap' : 'helpsite',
                'accels' : [
                    ],
                'help' : 'Web site',
                },
            'ABOUT' : {
                'action' : self.OnAbout,
                'bitmap' : 'about',
                'accels' : [
                    ('Ctrl','F1'),
                    ],
                'help' : 'About pyrfeed',
                },

            }

        for event_name in self._events :
            event = self._events[event_name]
            if 'action' not in event :
                event['action'] = None
            if 'bitmap' not in event :
                event['bitmap'] = 'none'
            if event['bitmap'] == '' :
                event['bitmap'] = 'none'
            if 'accels' not in event :
                event['accels'] = []
            if 'help' not in event :
                event['help'] = ''
            if 'id' not in event :
                event['id'] = wx.NewId()

        menu_order = [
            ('&File',                                       ),
            ('-/&Synchro',                                  'SYNCHRO' ),
            ('-/&Reload',                                   'RELOAD' ),
            ('-/-',                                         ),
            ('-/S&witch interface',                         ),
            ('-/-/-',                                       ),
            ('-/-',                                         ),
            ('-/&Quit',                                     'QUIT' ),
            ('&Edit',                                       ),
            ('-/&Select',                                   'SELECT' ),
            ('-/Select and goto ne&xt',                     'SELECTNEXT' ),
            ('-/-',                                         ),
            ('-/&Open link',                                'OPENLINK' ),
            ('-/&Open links',                               'OPENLINKS' ),
            ('-/-',                                         ),
            ('-/&Previous',                                 'PREVIOUS' ),
            ('-/&Next',                                     'NEXT' ),
            ('-/P&age',                                     ),
            ('-/P&age/&Previous',                           'PREVIOUSPAGE' ),
            ('-/P&age/&Next',                               'NEXTPAGE' ),
            ('-/-',                                         ),
            ('-/Mark as &Read',                             'MARKASREAD' ),
            ('-/Mark as &Unread',                           'MARKASUNREAD' ),
            ('-/-',                                         ),
            ('-/Add Star',                                  'ADDSTAR' ),
            ('-/Del Star',                                  'DELSTAR' ),
            ('-/-',                                         ),
            ('-/Add Public',                                'ADDPUBLIC' ),
            ('-/Del Public',                                'DELPUBLIC' ),
            ('-/-',                                         ),
            ('-/Add &Label',                                ),
            ('-/-/-',                                       ),
            ('-/Del La&bel',                                ),
            ('-/-/-',                                       ),
            ('-/-',                                         ),
            ('-/Add &Filter',                               'ADDFILTER' ),
            ('&Help',                                       ),
            ('&Help/Online &Doc (not much now)',            'HELPDOC' ),
            ('&Help/Report a bug',                          'HELPBUG' ),
            ('&Help/Ask for new features',                  'HELPNEWFEATURE' ),
            ('&Help/Website',                               'HELPSITE' ),
            ('-/-',                                         ),
            ('&Help/About',                                 'ABOUT' ),

            ]

        toolbar_order = [
            'SYNCHRO',
            'RELOAD',
            '',
            'SELECTNEXT',
            '',
            'PREVIOUS',
            'NEXT',
            '',
            'PREVIOUSPAGE',
            'NEXTPAGE',
            '',
            'OPENLINK',
            'OPENLINKS',
            '',
            'MARKASREAD',
            'MARKASUNREAD',
            '',
            'ADDSTAR',
            'DELSTAR',
            '',
            'ADDPUBLIC',
            'DELPUBLIC',
            '',
            'HELPDOC',
            'HELPBUG',
            'HELPNEWFEATURE',
            'HELPSITE',
            '',
            'QUIT',
            ]

        menu_content = []
        for menu_order_line in menu_order :
            if len(menu_order_line) == 1 :
                menu_content.append((menu_order_line[0],))
            elif len(menu_order_line) >= 2 :
                menu_path = menu_order_line[0]
                event_name = menu_order_line[1]
                event = self._events[event_name]
                accels = []
                if len(event['accels']) >= 1 :
                    accel_main = event['accels'][0]
                    for accel in event['accels'][1:] :
                        pass
                        # accels.append(accel)
                    menu_path+='\t'+'+'.join(accel_main)

                menu_content.append((menu_path,event['action'],event['help'],accels,event['id'],wx.Bitmap(os.path.join('..','res','toolbar',event['bitmap']+'.png'))))

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

        for event_name in toolbar_order :
            if event_name in self._events :
                event = self._events[event_name]
                self._tool_bar.AddTool(event['id'],wx.Bitmap(os.path.join('..','res','toolbar',event['bitmap']+'.png')),shortHelpString=event['help'])
            else :
                self._tool_bar.AddSeparator()

        self._tool_bar.Realize()

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

    def OnHelpDoc(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed/wiki/pyrfeed')

    def OnHelpIssues(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed/issues/list')

    def OnHelpWebSite(self, event=None) :
        webbrowser.open('http://code.google.com/p/pyrfeed')

    def OnAbout(self, event=None) :
        adi = wx.AboutDialogInfo()
        adi.SetCopyright('GPL')
        adi.SetDevelopers(['Gissehel'])
        adi.SetName('pyrfeed')
        adi.SetVersion(pyrfeed_version)
        adi.SetWebSite('http://code.google.com/p/pyrfeed')
        adi.SetIcon(wx.Icon(os.path.join('..','res','pyrfeed-64x64.png'),wx.BITMAP_TYPE_ANY))
        wx.AboutBox(adi)

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
