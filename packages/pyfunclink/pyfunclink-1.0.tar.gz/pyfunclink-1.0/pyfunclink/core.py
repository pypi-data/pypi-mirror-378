"""
Main functions to detect and link URLs in different GUIs
"""

def linkify(widget, gui_type="tkinter", parent=None, pos=(0,0)):
    """
    Converts URLs in a widget into clickable links.

    gui_type: "tkinter", "ctk", "ttk", "pyqt5", "pyqt6", "pyside6", "wx", "html"
    parent: required for wxPython HyperlinkCtrl
    pos: position for wxPython links
    """
    if gui_type in ["tkinter", "ttk", "ctk"]:
        from .tkinter_link import linkify_tk
        linkify_tk(widget)
    elif gui_type in ["pyqt5", "pyqt6", "pyside6"]:
        from .qt_link import linkify_qt
        linkify_qt(widget)
    elif gui_type == "wx":
        from .wx_link import linkify_wx
        linkify_wx(widget, parent=parent, pos=pos)
    elif gui_type == "html":
        from .html_link import linkify_html
        return linkify_html(widget)
