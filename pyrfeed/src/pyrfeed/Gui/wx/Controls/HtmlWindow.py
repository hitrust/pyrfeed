import wx
import wx.html
from cStringIO import StringIO

HTML_SIMPLE = 0
HTML_COMPLEX = 1

HtmlClasses = []

__all__ = ['HtmlClasses','HTML_SIMPLE','HTML_COMPLEX']

class HtmlSimple(wx.html.HtmlWindow) :
    def ChangePage(self,content) :
        self.SetPage(content)

HtmlClasses.append({'class':HtmlSimple,'name':'wx Classic'})

if wx.Platform == '__WXMSW__':
    import wx.lib.iewin

    class HtmlComplex(wx.lib.iewin.IEHtmlWindow) :
        def ChangePage(self,content) :
            self.LoadStream(StringIO("<html><head><meta HTTP-EQUIV='Content-Type' CONTENT='text/html;charset=utf-8' /><style type='text/css'><!-- body,th,td,p { font-family:'Verdana, Arial, Helvetica, sans-serif'; } --></style></head><body>"+unicode(content).encode('utf-8')+"</body>"))

    HtmlClasses.append({'class':HtmlComplex,'name':'IE Component'})
