import sys
import webbrowser

from html2text import html2text_file

from pyrfeed.gui.info import GuiInfo
from pyrfeed.gui.info_list import gui_info_list
from pyrfeed.config import register_key


class ExceptionCommandDoesntExist(Exception) :
    pass

class ExceptionMissingMethod(Exception) :
    pass

class ExceptionNoCommand(Exception) :
    pass

class TTYCommands(object) :
    _commands = {
        'QUIT'              : { 'names' : [ 'q',          ], 'importance' : 10, 'comment' : 'Quit' },
        'SEARCH'            : { 'names' : [ '/',          ], 'importance' : 10, 'comment' : 'Search' },
        'SHOW'              : { 'names' : [ 's',          ], 'importance' : 10, 'comment' : 'Show an item' },
        'RELOAD'            : { 'names' : [ 'R',          ], 'importance' : 10, 'comment' : 'Reload' },
        'SYNCHRO'           : { 'names' : [ 'S',          ], 'importance' : 10, 'comment' : 'Synchro' },
        'VIEW'              : { 'names' : [ 'v',          ], 'importance' : 10, 'comment' : 'View an item' },
        'VIEWDETAILS'       : { 'names' : [ 'V',          ], 'importance' : 10, 'comment' : 'View details of an item' },
        'OPEN'              : { 'names' : [ 'o',          ], 'importance' : 10, 'comment' : 'Open an item' },
        'ENCODE'            : { 'names' : [ 'e',          ], 'importance' :  0, 'comment' : 'Set the current tty encoding' },
        'MARKASREAD'        : { 'names' : [ 'r',          ], 'importance' : 10, 'comment' : 'Mark an item as read' },
        'MARKASUNREAD'      : { 'names' : [ 'u',          ], 'importance' : 10, 'comment' : 'Mark an item as unread' },
        'SAVE'              : { 'names' : [ 'save',       ], 'importance' :  0, 'comment' : 'Save configuration' },
        'SET'               : { 'names' : [ 'set',        ], 'importance' :  0, 'comment' : 'Set a configuration key' },
        'GET'               : { 'names' : [ 'get',        ], 'importance' :  0, 'comment' : 'Get a configuration key' },
        'DEL'               : { 'names' : [ 'del',        ], 'importance' :  0, 'comment' : 'Delete a configuration key' },
        'SHOWFILTERS'       : { 'names' : [ 'f',          ], 'importance' :  0, 'comment' : 'Show all filters' },
        'SHOWFILTERSDIFF'   : { 'names' : [ 'F',          ], 'importance' :  0, 'comment' : 'Show filters applicable over the current filter' },
        'ADDSTAR'           : { 'names' : [ 'addstar',    ], 'importance' :  5, 'comment' : 'Add star to an item' },
        'DELSTAR'           : { 'names' : [ 'delstar',    ], 'importance' :  5, 'comment' : 'Delete star from an item' },
        'ADDPUBLIC'         : { 'names' : [ 'addpublic',  ], 'importance' :  5, 'comment' : 'Add public status to an item' },
        'DELPUBLIC'         : { 'names' : [ 'delpublic',  ], 'importance' :  5, 'comment' : 'Remove public status from an item' },
        'ADDLABEL'          : { 'names' : [ 'addlabel',   ], 'importance' :  5, 'comment' : 'Add label to an item' },
        'DELLABEL'          : { 'names' : [ 'dellabel',   ], 'importance' :  5, 'comment' : 'Remove label from an item' },
        'SWITCHWX'          : { 'names' : [ 'wx',         ], 'importance' :  0, 'comment' : 'Switch to wx user interface' },
        'SWITCH'            : { 'names' : [ 'switch',     ], 'importance' :  0, 'comment' : 'Switch to another user interface' },
        'HELP'              : { 'names' : [ 'help', '?',  ], 'importance' : 10, 'comment' : 'Show help' },
        }

    def __init__(self) :
        self._command_id_by_name = {}
        for command_id in self._commands :
            for command_name in self._commands[command_id]['names'] :
                self._command_id_by_name[command_name] = command_id
            setattr(self,command_id,command_id)

    def parse_line(self,line,executor) :
        '''This method execute the command specified in the 'line' assuming executor implement command do_XXXXX if XXXXX is a valid command and have been specified in the line'''
        
        action = line.strip('\r\n')
        action_list = filter(len,action.split(' '))
        
        result = None

        if len(action_list)>0 :
            arguments = action_list[1:]
            command_name = action_list[0]
            if command_name in self._command_id_by_name :
                # Ok, the command is valid
                
                command_id = self._command_id_by_name[command_name]
                
                method_name = 'do_'+command_id
                if hasattr(executor,method_name) :
                    # Everything is ok here... We call the method...
                    method = getattr(executor,method_name)
                    # No return here : return always at the end of the code
                    result = method(command_name,*arguments)
                else :
                    # The command exists, but the method is not implemented
                    raise ExceptionMissingMethod()
            else :
                # Invalid command
                raise ExceptionCommandDoesntExist()
        else :
            # No command
            raise ExceptionNoCommand()

        return result        

    def get_help(self) :
        commands_list = list(self._commands.iteritems())
        commands_list.sort(key=lambda x:-x[1]['importance'])
        
        help_lines = []
        
        for command_id,command_info in commands_list :
            help_lines.append( ' %-20s %s'%(', '.join(command_info['names']),command_info['comment'] ) )

        return '\n'.join(help_lines)

class BasicTTY(object):
    def __init__(self,config) :
        self._config = config
        self._rss_reader = None
        self._filters = []
        self._filters_diff = []
        self._titles = []
        self._encoding = self._config['tty/encoding']
        
        self._need_quit = False

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
                self._print(" %3d. - %s\n" % (position+1,self._titles[position][:screensize-5]))
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
                    interval[0] = int(interval[0])-1

                if interval[1] == '' :
                    interval[1] = len(self._titles)-1
                else :
                    # TODO : Check interval[1] is an int
                    interval[1] = int(interval[1])-1
                int_list += range(interval[0],interval[1]+1)
            else :
                # TODO : Check arg is an int
                int_list.append(int(arg)-1)
        return int_list

    def main_loop(self) :
        self._commands = TTYCommands()
        
        while not(self._need_quit) :
            self._print("\nAction? ")
            line = self._get_line().strip('\r\n')

            # This will parse the line, and execute on "self" (this will execute commands like do_XXXXX if XXXXX is the "id" of the command in the line)            
            try :
                self._commands.parse_line(line,executor=self)

            except ExceptionNoCommand :
                # No command is ok, no problem here...
                pass

            except ExceptionCommandDoesntExist :
                # Wrong command typed. We just inform that the command doesn't exists...
                self._print("Don't understand [%s]\nType ? for help." % line)

            except ExceptionMissingMethod :
                # This is quite a problem...
                self._print("The command [%s] is recognized as a command, but is not implemented.\nPlease, report this problem. http://code.google.com/p/pyrfeed/issues/entry" % line)


    def do_QUIT(self,command_name,*args) :
        self._need_quit = True

    def do_RELOAD(self,command_name,*args) :
        self.reload()

    def do_SYNCHRO(self,command_name,*args) :
        self.synchro()

    def do_SHOW(self,command_name,*args) :
        if len(args)==0 :
            self.print_title()
        else :
            self.print_title(self.get_int_list(args))

    def do_VIEW_DETAILS_OR_NOT(self,command_name,details,*args) :
        for position in self.get_int_list(args) :
            self._print('\n')
            self._print('='*3+' [ '+('%3d'%(position+1,))+' ] '+'='*58+'\n')
            self._print(self._titles[position]+'\n')
            self._print('-'*65+'\n')
            if details :
                link = self._rss_reader.get_link(position)
                if link and link != '' :
                    self._print(link+'\n')
                    self._print('-'*65+'\n')
            self._print(html2text_file(self._rss_reader.get_content(position),None))
            if details :
                categories = self._rss_reader.get_categories(position)
                if categories is not None :
                    if len(categories)>0 :
                        self._print('-'*65+'\n')
                    for categorie in categories :
                        self._print('  %s\n' % categorie)
                    if len(categories)>0 :
                        self._print('-'*65+'\n')

    def do_VIEWDETAILS(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,True,*args)

    def do_VIEW(self,command_name,*args) :
        self.do_VIEW_DETAILS_OR_NOT(command_name,False,*args)

    def do_ENCODE(self,command_name,*args) :
        # test on len(args) ? or let crash ?
        self._encoding = args[0]

    def do_OPEN(self,command_name,*args) :
        for position in self.get_int_list(args) :
            link = self._rss_reader.get_link(position)
            if link and link != '' :
                webbrowser.open(link)

    def do_MARKASREAD(self,command_name,*args) :
        self._rss_reader.mark_as_read(self.get_int_list(args))
        self.reload()

    def do_MARKASUNREAD(self,command_name,*args) :
        self._rss_reader.mark_as_unread(self.get_int_list(args))
        self.reload()

    def do_SEARCH(self,command_name,*args) :
        self._rss_reader.set_filter(' '.join(args))
        self.print_title()

    def do_SAVE(self,command_name,*args) :
        self._config.save()

    def do_SET(self,command_name,*args) :
        if len(args) > 1 :
            self._config[args[0]] = args[1]
        else :
            for key in self._config.keys() :
                value = self._config[key]
                if key == 'passwd' :
                    # Urk ! not nice !
                    value = '*' * 16
                self._print('%s=%s\n' % (key,value))

    def do_GET(self,command_name,*args) :
        self._print('%s=%s\n' % (args[0],self._config[args[0]]))

    def do_DEL(self,command_name,*args) :
        del self._config[args[0]]

    def do_SHOWFILTERS(self,command_name,*args) :
        self._print('Filters :\n')
        for filter_command in self._filters :
            self._print('  %s\n' % filter_command)

    def do_SHOWFILTERSDIFF(self,command_name,*args) :
        self._print('Filters diff :\n')
        for filter_command in self._filters_diff :
            self._print('  %s\n' % filter_command)

    def do_ADDSTAR(self,command_name,*args) :
        self._rss_reader.add_star(self.get_int_list(args))

    def do_DELSTAR(self,command_name,*args) :
        self._rss_reader.del_star(self.get_int_list(args))

    def do_ADDPUBLIC(self,command_name,*args) :
        self._rss_reader.add_public(self.get_int_list(args))

    def do_DELPUBLIC(self,command_name,*args) :
        self._rss_reader.del_public(self.get_int_list(args))

    def do_ADDLABEL(self,command_name,*args) :
        self._rss_reader.add_label(self.get_int_list(args[1:]),args[0])

    def do_DELLABEL(self,command_name,*args) :
        self._rss_reader.del_label(self.get_int_list(args[1:]),args[0])

    def do_SWITCH(self,command_name,*args) :
        if len(args) > 0 :
            for ui_name,name in gui_info_list.get_ui_names() :
                if name == args[0] or ui_name == args[0] :
                    self._config['gui/next'] = name
                    self._need_quit = True
                    break
            else :
                if name in gui_info_list :
                    self._config['gui/next'] = name
                    self._need_quit = True
                else :
                    self._print("Don't know [%s] as an interface name\n" % name)
        else :
            for ui_name,name in gui_info_list.get_ui_names() :
                self._print("    %s - %s\n" % (name,ui_name))

    def do_HELP(self,command_name,*args) :
        self._print(self._commands.get_help())

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

