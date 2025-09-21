from pyfunclink import linkify
import tkinter as tk
from PyQt5.QtWidgets import QApplication, QLabel
import wx

def test_tkinter():
    root = tk.Tk()
    label = tk.Label(root, text="Visit https://www.python.org")
    label.pack()
    linkify(label, gui_type="tkinter")
    print("Tkinter test ready")

def test_pyqt():
    app = QApplication([])
    label = QLabel("Visit https://www.python.org")
    linkify(label, gui_type="pyqt5")
    print("PyQt test ready")

def test_wx():
    app = wx.App()
    frame = wx.Frame(None, title="Test wxPython")
    panel = wx.Panel(frame)
    text = wx.StaticText(panel, label="Visit https://www.python.org")
    linkify(text, gui_type="wx", parent=panel)
    frame.Show()
    print("wxPython test ready")

def test_html():
    html = "Check this link: https://www.python.org"
    new_html = linkify(html, gui_type="html")
    print(new_html)
