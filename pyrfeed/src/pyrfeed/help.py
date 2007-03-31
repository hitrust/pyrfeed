from pyrfeed.Config import config
from pyrfeed import __version__

def usage() :
    print "Pyrfeed version %s" % (__version__,)
    print ""
    print "usage : pyrfeed [--<option>[=<value>|-]]"
    print "      --<option> : Set an option"
    print "      --<option>=<value> : Set an option with value"
    print "      --<option>- : Unset an option"

    usage_command_line_options()

def usage_command_line_options() :
    config_types = config.config_types
    config_keys = config.config_keys

    keynames = config_keys.keys()

    keynames.sort()

    print "%-22s %-8s %-30s %s" % ('option','type','doc','default')
    print "%-22s %-8s %-30s %s" % ('-'*22,'-'*8,'-'*30,'-'*10)
    for keyname in keynames :
        typename = config_types[config_keys[keyname]['type']]['ihm_name']
        doc_raw = config_keys[keyname]['doc']
        default = config_types[config_keys[keyname]['type']]['from_type'](config_keys[keyname]['default'])
        doc = ''
        doc_last_line_len = 0
        for doc_word in doc_raw.split(' ') :
            if doc_last_line_len!=0 and doc_last_line_len+len(doc_word)+1 > 30 :
                doc += '\n'
                doc += doc_word
                doc_last_line_len = len(doc_word)
            else :
                doc += ' '
                doc += doc_word
                doc_last_line_len += 1
                doc_last_line_len += len(doc_word)
        doc = doc.replace('\n','\n'+' '*33)
        doc += ' '*(29-doc_last_line_len)
        print "%-22s %-8s %-30s %s" % (keyname,typename,doc,default)
        print
