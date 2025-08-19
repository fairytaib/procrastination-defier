# tasks/templatetags/proof_tags.py
from django import template
from django.utils.html import format_html

register = template.Library()


def _name_and_url(file_field):
    if not file_field:
        return None, None
    return getattr(file_field, "name", "").lower(), file_field.url


@register.filter
def render_textfile(file_field):
    """
    Rendert PDF/TXT/DOCX passend.
    """
    name, url = _name_and_url(file_field)
    if not url:
        return ""

    if name.endswith(".pdf"):
        return format_html(
            '<embed src="{}" type="application/pdf" width="800" height="600" />'
            '<p><a href="{}" target="_blank" rel="noopener">Open in a new Tab</a></p>',
            url, url
        )
    elif name.endswith(".txt"):
        return format_html(
            '<iframe src="{}" width="800" height="600"></iframe>'
            '<p><a href="{}" target="_blank" rel="noopener">TXT öffnen</a></p>',
            url, url
        )
    elif name.endswith(".docx"):
        return format_html(
            '<p><a href="{}" target="_blank" rel="noopener">Download DOCX</a></p>',
            url
        )
    else:
        # Fallback
        return format_html(
            '<p><a href="{}" target="_blank" rel="noopener">Open</a></p>',
            url
        )


@register.filter
def render_image(image_field):
    """
    Rendert Bilder (jpg/jpeg/png/webp) – Browser erkennt Typ selbst.
    """
    name, url = _name_and_url(image_field)
    if not url:
        return ""
    return format_html(
        '<img src="{}" alt="Task Checkup Image" style="max-width:100%;height:auto;">', url)


@register.filter
def render_audio(audio_field):
    """
    Rendert Audio (mp3/wav).
    Eine Source reicht, du kannst optional zwei angeben.
    """
    name, url = _name_and_url(audio_field)
    if not url:
        return ""
    type_attr = "audio/mpeg" if name.endswith(".mp3") else (
        "audio/wav" if name.endswith(".wav") else "")
    if type_attr:
        return format_html(
            '<audio controls><source src="{}" type="{}">Not Supported.</audio>',
            url, type_attr
        )
    return format_html(
        '<audio controls src="{}">Not Supported.</audio>',
        url
    )
