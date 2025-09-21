import re

def linkify_html(html_content):
    """
    Detect URLs in HTML string and wrap them with <a href="..."> tags.
    """
    url_pattern = r"(https?://[^\s]+)"
    return re.sub(url_pattern, r'<a href="\1" target="_blank">\1</a>', html_content)
