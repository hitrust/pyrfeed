import sys
import webbrowser
from html2text import html2text_file

from pyrfeed.Gui.Info import GuiInfo
from pyrfeed.Gui.InfoList import gui_info_list
from pyrfeed.Config import register_key

class BasicTTY(object):
    def __init__(self,config) :
        self._config = config
        self._rss_reader = None
        self._filters = []
        self._filters_diff = []
        self._titles = []
        self._encoding = self._config['tty/encoding']

    def set_rss_reader(self,rss_reader) :
        self._rss_reader = rss_reader
        self.reload()

    def _get_line(self) :
        return sys.stdin.readline()

    def _print(self,line) :
        return sys.stdout.write(line.encode(self._encoding,'replace'))

    def synchro(self) :
        if self._rss_reader is not None :
            synchro_result = self._rss_reader.synchro()
            if synchro_result is not None :
                print synchro_result
            self.print_title()

    def reload(self) :
        if self._rss_reader is not None :
            self._rss_reader.reload()
            self.print_title()

    def print_title(self,positions=None):
        if self._rss_reader :
            pagesize = self._config['pagesize']
            screensize = self._config['tty/screensize']

            self._titles = map(lambda title:html2text_file(title,None).strip('\r\n ').replace('\n',' '),self._rss_reader.get_titles())
            self._print("Current filter : [%s]\n" % (self._rss_reader.get_filter(),))
            self._print("\n")
            if positions == None :
                positions = xrange(len(self._titles))
            for position in list(positions)[:pagesize] :
                self._print(" %3d. - %s\n" % (position,self._titles[position][:screensize-5]))
            self._filters = self._rss_reader.get_filters()
            self._filters_diff = self._rss_reader.get_filters_diff()
            self._print("\n")
            self._print("%d items\n" % len(self._titles))

    def get_int_list(self,args) :
        int_list = []
        for arg in args :
            if '-' in arg :
                interval = arg.split('-')
                # TODO : Check len(interval) == 2
                if interval[0] == '' :
                    interval[0] = 0
                else :
                    # TODO : Check interval[0] is an int
                    interval[0] = int(interval[0])

                if interval[1] == '' :
                    interval[1] = len(self._titles)-1
                else :
                    # TODO : Check interval[1] is an int
                    interval[1] = int(interval[1])
                int_list += range(interval[0],interval[1]+1)
            else :
                # TODO : Check arg is an int
                int_list.append(int(arg))
        return int_list

    def main_loop(self) :
        QUIT = 'q'
        SEARCH = '/'
        SHOW = 's'
        RELOAD = 'R'
        SYNCHRO = 'S'
        VIEW = 'v'
        VIEWDETAILS = 'V'
        OPEN = 'o'
        ENCODE = 'e'
        MARKASREAD = 'r'
        MARKASUNREAD = 'u'
        SAVE = 'save'
        SET = 'set'
        GET = 'get'
        DEL = 'del'
        SHOWFILTERS = 'f'
        SHOWFILTERSDIFF = 'F'

        ADDSTAR = 'addstar'
        DELSTAR = 'delstar'

        ADDPUBLIC = 'addpublic'
        DELPUBLIC = 'delpublic'

        ADDLABEL = 'addlabel'
        DELLABEL = 'dellabel'

        SWITCHWX = 'wx'
        SWITCH = 'switch'

        need_quit = False
        while not(need_quit) :
            self._print("\nAction? ")
            action = self._get_line().strip('\r\n')
            action_list = filter(len,action.split(' '))

            if len(action_list)>0 :
                if action_list[0] == QUIT :
                    need_quit = True
                elif action_list[0] == RELOAD :
                    self.reload()
                elif action_list[0] == SYNCHRO :
                    self.synchro()
                elif action_list[0] == SHOW :
                    if len(action_list)==1 :
                        self.print_title()
                    else :
                        self.print_title(self.get_int_list(action_list[1:]))
                elif action_list[0] in (VIEW,VIEWDETAILS) :
                    for position in self.get_int_list(action_list[1:]) :
                        self._print('\n')
                        self._print('='*3+' [ '+('%3d'%position)+' ] '+'='*58+'\n')
                        self._print(self._titles[position]+'\n')
                        self._print('-'*65+'\n')
                        if action_list[0] == VIEWDETAILS :
                            link = self._rss_reader.get_link(position)
                            if link and link != '' :
                                self._print(link+'\n')
                                self._print('-'*65+'\n')
                        self._print(html2text_file(self._rss_reader.get_content(position),None))
                        if action_list[0] == VIEWDETAILS :
                            categories = self._rss_reader.get_categories(position)
                            if categories is not None :
                                if len(categories)>0 :
                                    self._print('-'*65+'\n')
                                for categorie in categories :
                                    self._print('  %s\n' % categorie)
                                if len(categories)>0 :
                                    self._print('-'*65+'\n')
                elif action_list[0] == ENCODE :
                    # test on len(action_list) ? or let crash ?
                    self._encoding = action_list[1]
                elif action_list[0] == OPEN :
                    for position in self.get_int_list(action_list[1:]) :
                        link = self._rss_reader.get_link(position)
                        if link and link != '' :
                            webbrowser.open(link)
                elif action_list[0] == MARKASREAD :
                    self._rss_reader.mark_as_read(self.get_int_list(action_list[1:]))
                    self.reload()
                elif action_list[0] == MARKASUNREAD :
                    self._rss_reader.mark_as_unread(self.get_int_list(action_list[1:]))
                    self.reload()
                elif action_list[0] == SEARCH :
                    self._rss_reader.set_filter(' '.join(action_list[1:]))
                    self.print_title()
                elif action_list[0] == SAVE :
                    self._config.save()
                elif action_list[0] == SET :
                    if len(action_list) > 2 :
                        self._config[action_list[1]] = action_list[2]
                    else :
                        for key in self._config.keys() :
                            value = self._config[key]
                            if key == 'passwd' :
                                # Urk ! not nice !
                                value = '*' * 16
                            self._print('%s=%s\n' % (key,value))
                elif action_list[0] == GET :
                    self._print('%s=%s\n' % (action_list[1],self._config[action_list[1]]))
                elif action_list[0] == DEL :
                    del self._config[action_list[1]]
                elif action_list[0] == SHOWFILTERS :
                    self._print('Filters :\n')
                    for filter_command in self._filters :
                        self._print('  %s\n' % filter_command)
                elif action_list[0] == SHOWFILTERSDIFF :
                    self._print('Filters diff :\n')
                    for filter_command in self._filters_diff :
                        self._print('  %s\n' % filter_command)
                elif action_list[0] == ADDSTAR :
                    self._rss_reader.add_star(self.get_int_list(action_list[1:]))
                elif action_list[0] == DELSTAR :
                    self._rss_reader.del_star(self.get_int_list(action_list[1:]))
                elif action_list[0] == ADDPUBLIC :
                    self._rss_reader.add_public(self.get_int_list(action_list[1:]))
                elif action_list[0] == DELPUBLIC :
                    self._rss_reader.del_public(self.get_int_list(action_list[1:]))
                elif action_list[0] == ADDLABEL :
                    self._rss_reader.add_label(self.get_int_list(action_list[2:]),action_list[1])
                elif action_list[0] == DELLABEL :
                    self._rss_reader.del_label(self.get_int_list(action_list[2:]),action_list[1])
                elif action_list[0] == SWITCH :
                    if len(action_list) > 1 :
                        for ui_name,name in gui_info_list.get_ui_names() :
                            if name == action_list[1] or ui_name == action_list[1] :
                                self._config['gui/next'] = name
                                need_quit = True
                                break
                        else :
                            if name in gui_info_list :
                                self._config['gui/next'] = name
                                need_quit = True
                            else :
                                self._print("Don't know [%s] as an interface name\n" % name)
                    else :
                        for ui_name,name in gui_info_list.get_ui_names() :
                            self._print("    %s - %s\n" % (name,ui_name))

class GuiInfoTTY(GuiInfo) :
    names = ['tty','BasicTTY','cl']
    priority = 10
    ui_name = 'TTY interface'

    def _start_application(self) :
        commandline = BasicTTY(self._config)
        commandline.set_rss_reader(self._rss_reader)
        commandline.main_loop()

    def get_doc(self) :
        return ""

register_key( 'pagesize', int, doc='Size of a page of items', default=30 )
register_key( 'tty/encoding', str, doc='TTY Encoding', default='iso-8859-1' )
register_key( 'tty/screensize', int, doc='Width of the TTY', default=80 )

# 'gui/next' will be handled elsewere for registration

