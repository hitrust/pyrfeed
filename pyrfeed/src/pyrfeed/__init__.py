import sys
from pyrfeed.Config import Config

__version__ = '0.5.0'

# this is not a plugin based yet because of those imports.
import pyrfeed.Gui.commandline
import pyrfeed.Gui.wx

import pyrfeed.RssReader.Google
import pyrfeed.RssReader.GoogleCache
import pyrfeed.RssReader.Fake

from pyrfeed.Gui.InfoList import gui_info_list
from pyrfeed.RssReader.InfoList import rssreader_info_list

from pyrfeed.Config import register_key
from pyrfeed.help import usage

def main(argv=None) :
    if argv==None :
        argv = sys.argv[1:]
    config = Config(argv)
    if config['help'] :
        usage()
    elif config['save'] :
        del config['save']
        config.save_non_persistant()
    else :
        rss_reader = rssreader_info_list.get_rss_reader(config)

        if config['forcesynchro'] :
            rss_reader.synchro()
        else :
            gui_info_list.mainloop(config,rss_reader)

register_key('help',bool,doc='Show help')
register_key('save',bool,doc='Save the options in command line into configuration file')
register_key('forcesynchro',bool,doc='Force synchronisation and stop without interactive GUI.')

if __name__ == '__main__' :
    main()
