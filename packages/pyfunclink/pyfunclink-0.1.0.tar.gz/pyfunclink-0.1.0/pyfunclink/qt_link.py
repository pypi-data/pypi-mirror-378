try:
    from PyQt5.QtWidgets import QLabel
    from PyQt5.QtCore import Qt
except ImportError:
    from PyQt6.QtWidgets import QLabel
    from PyQt6.QtCore import Qt

def linkify_qt(widget):
    """
    Makes URLs in PyQt5/PyQt6/PySide6 QLabel clickable.
    """
    if isinstance(widget, QLabel):
        widget.setTextInteractionFlags(Qt.TextBrowserInteraction)
        widget.setOpenExternalLinks(True)
