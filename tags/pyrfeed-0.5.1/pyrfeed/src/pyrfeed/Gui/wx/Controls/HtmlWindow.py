import wx
import wx.html
import webbrowser

from cStringIO import StringIO

HTML_SIMPLE = 0
HTML_COMPLEX = 1

HtmlClasses = []

__all__ = ['HtmlClasses','HTML_SIMPLE','HTML_COMPLEX']

class HtmlSimple(wx.html.HtmlWindow) :

    def __init__(self,*args,**kwargs) :
        wx.html.HtmlWindow.__init__(self,*args,**kwargs)
        self.Bind(wx.html.EVT_HTML_LINK_CLICKED,self.OnUrlClicked,id=self.GetId())

    def ChangePage(self,content) :
        self.SetPage(content)

    def OnUrlClicked(self,event) :
        webbrowser.open(event.GetLinkInfo().GetHref())

HtmlClasses.append({'class':HtmlSimple,'name':'wx Classic'})

if wx.Platform == '__WXMSW__':
    import wx.lib.iewin

    class HtmlComplex(wx.lib.iewin.IEHtmlWindow) :

        def __init__(self,*args,**kwargs) :
            wx.lib.iewin.IEHtmlWindow.__init__(self,*args,**kwargs)
            self.Bind(wx.lib.iewin.EVT_BeforeNavigate2,self.OnUrlClicked,id=self.GetId())

        def ChangePage(self,content) :
            self.LoadStream(StringIO("<html><head><meta HTTP-EQUIV='Content-Type' CONTENT='text/html;charset=utf-8' /><style type='text/css'><!-- body,th,td,p { font-family:'Verdana, Arial, Helvetica, sans-serif'; } --></style></head><body>"+unicode(content).encode('utf-8')+"</body>"))

        def OnUrlClicked(self,event) :
            event.Cancel = True
            webbrowser.open(event.URL)

    HtmlClasses.append({'class':HtmlComplex,'name':'IE Component'})
