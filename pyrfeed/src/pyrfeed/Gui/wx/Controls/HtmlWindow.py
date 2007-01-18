import wx
import wx.html

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
            self.LoadString("<html><head><style type='text/css'><!-- body,th,td,p { font-family:'Verdana, Arial, Helvetica, sans-serif'; } --></style></head><body>"+content+"</body>")

    HtmlClasses.append({'class':HtmlComplex,'name':'IE Component'})
