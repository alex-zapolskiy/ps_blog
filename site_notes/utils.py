import markdown2

def render_markdown(text):
    if not text:
        return ""
    
    #расширения для markdown
    extras = [
        'fenced-code-blocks',
        'tables',
        'footnotes',
        'code-friendly',
    ]
    
    html = markdown2.markdown(text, extras=extras)
    
    return html