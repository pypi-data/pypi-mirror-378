import wx
import re
import webbrowser

def linkify_wx(widget, parent=None, pos=(0,0)):
    """
    Makes URLs in wxPython widgets clickable using wx.HyperlinkCtrl.
    Supports StaticText and TextCtrl.
    """
    url_pattern = r"(https?://[^\s]+)"

    if isinstance(widget, wx.StaticText):
        text = widget.GetLabel()
        parent_widget = widget.GetParent() if parent is None else parent
        widget.Destroy()

        parts = re.split(url_pattern, text)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        for part in parts:
            if re.match(url_pattern, part):
                link = wx.HyperlinkCtrl(parent_widget, id=wx.ID_ANY, label=part, url=part, style=wx.HL_DEFAULT_STYLE)
                sizer.Add(link, 0, wx.ALL, 2)
            else:
                label = wx.StaticText(parent_widget, label=part)
                sizer.Add(label, 0, wx.ALL, 2)
        parent_widget.SetSizerAndFit(sizer)

    elif isinstance(widget, wx.TextCtrl):
        text = widget.GetValue()
        matches = re.findall(url_pattern, text)
        if matches:
            def open_first_url(event, url=matches[0]):
                webbrowser.open(url)
            widget.Bind(wx.EVT_LEFT_DOWN, open_first_url)
