import tkinter as tk
import re
import webbrowser

def linkify_tk(widget):
    """
    Detects URLs in Tkinter/CTk/ttk widgets and makes them clickable.
    """
    url_pattern = r"(https?://[^\s]+)"

    if isinstance(widget, tk.Label):
        text = widget.cget("text")
        parts = re.split(url_pattern, text)

        widget_text = tk.Text(widget.master, wrap="word", height=1, borderwidth=0, background=widget.cget("bg"))
        widget_text.pack()
        widget.destroy()

        for part in parts:
            if re.match(url_pattern, part):
                start = widget_text.index(tk.INSERT)
                widget_text.insert(tk.END, part)
                end = widget_text.index(tk.INSERT)
                widget_text.tag_add(part, start, end)
                widget_text.tag_config(part, foreground="blue", underline=True)
                widget_text.tag_bind(part, "<Button-1>", lambda e, url=part: webbrowser.open(url))
            else:
                widget_text.insert(tk.END, part)

        widget_text.config(state=tk.DISABLED)
