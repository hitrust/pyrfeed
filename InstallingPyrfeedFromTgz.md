# Installing from .tar.gz #

For now, installing pyrfeed from .tar.gz need few command lines for installations. If you don't like command line, just wait for another release.

Requierements to use pyrfeed :
  1. python 2.5 (python 2.4 will perhaps be supported in the futur)
  1. wxPython 2.8 (aui support is needed)

Actions :
  1. Download the .tar.gz file
  1. Uncompress it in the folder/directory you like
  1. start a command line interpreter (cmd under windows, bash/tcsh/whateversh under unices, idontevenknow under macos)
  1. Go to that folder/directory with command line (use "cd")
    * Note : For now, every pyrfeed command must be launched from the directory where pyrfeed.py is.
  1. Tell pyrfeed your google login/passwd (of course, replace _yourlogin_ and _yourpasswd_ with your login and your password):
    * pyrfeed.py --login=_yourlogin_ --passwd=_yourpasswd_ --save
  1. You're behing a web proxy ? Just tell pyrfeed...
    * pyrfeed.py --proxy\_host=_yourproxyhost_ --proxyport=_yourproxyport_ --save

Now pyrfeed is ready to launch ! That's that simple.

To launch [pyrfeed](pyrfeed.md), just go to the folder/directory where pyrfeed.py is, and start it.

**Note** : pyrfeed is by default configure to start in [GoogleCache](GoogleCache.md) mode, and with [wxauiInterface](wxauiInterface.md). You can change userinterface and logical layer with command line option, or within pyrfeed.
