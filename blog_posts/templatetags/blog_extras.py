from django import template
from django.utils.html import strip_tags

register = template.Library()


@register.filter(name='content_preview')
def content_preview(value, n=30):
    """Limit content to n words."""
    try:
        n = int(n)
    except Exception:
        n = 30

    text = strip_tags(value or "")
    # Normalize whitespace
    text = " ".join(text.split())

    if not text:
        return ""

    words = text.split(" ")
    if len(words) <= n:
        return text

    return " ".join(words[:n]) + " ..."
