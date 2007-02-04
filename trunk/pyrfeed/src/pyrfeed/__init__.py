import sys
import cProfile
from pyrfeed.Config import config
from pyrfeed.Config import register_key

__version__ = '0.5.1'

# ------------------------------------------------------------
# This is not a plugin based yet because of those imports.
# Those imports will auto-register pseudo-plugins to the
# pyrfeed framework. A run-time import would also work
# (and this would be real plugin)
# ------------------------------------------------------------
import pyrfeed.Gui.commandline
import pyrfeed.Gui.wx

import pyrfeed.RssReader.Google
import pyrfeed.RssReader.GoogleCache
import pyrfeed.RssReader.Fake
# ------------------------------------------------------------

def pyrfeed_main() :
    # Due to profiling usage, those import should be done here and not
    # on the global space.

    from pyrfeed.help import usage
    from pyrfeed.Config import config
    from pyrfeed.Gui.InfoList import gui_info_list
    from pyrfeed.RssReader.InfoList import rssreader_info_list

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

def main(argv=None) :
    if argv==None :
        argv = sys.argv[1:]
    config.process_argv(argv)

    if config['profile'] :
        cProfile.run(pyrfeed_main.func_code)
    else :
        pyrfeed_main(config)

register_key('help',bool,doc='Show help')
register_key('save',bool,doc='Save the options in command line into configuration file')
register_key('forcesynchro',bool,doc='Force synchronisation and stop without interactive GUI.')
register_key('profile',bool,doc='Profile the current application. Developer only.')

if __name__ == '__main__' :
    main()
