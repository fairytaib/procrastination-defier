from django import template
from django.utils.html import format_html
from urllib.parse import urlparse
import os


register = template.Library()


def _name_url_ct(file_field):
    if not file_field:
        return "", "", ""
    url = getattr(file_field, "url", "") or ""
    parsed = urlparse(url)
    filename = os.path.basename(parsed.path).lower()
    content_type = getattr(file_field, "content_type", "") or ""
    return filename, url, content_type


@register.filter
def render_textfile(file_field):
    filename, url, ct = _name_url_ct(file_field)
    if not url:
        return ""

    is_pdf = filename.endswith(".pdf") or ct == "application/pdf"
    is_txt = filename.endswith(".txt") or ct == "text/plain"
    is_docx = filename.endswith(".docx") or ct == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

    if is_pdf:
        return format_html(
            '<embed src="{}" type="application/pdf" width="800" height="600" />'
            '<p><a href="{}" target="_blank" rel="noopener">PDF in neuem Tab öffnen</a></p>',
            url, url
        )
    if is_txt:
        return format_html(
            '<iframe src="{}" width="800" height="600"></iframe>'
            '<p><a href="{}" target="_blank" rel="noopener">TXT öffnen</a></p>',
            url, url
        )
    if is_docx:
        return format_html(
            '<p><a href="{}" target="_blank" rel="noopener">DOCX herunterladen</a></p>',
            url
        )
    # Fallback
    return format_html(
        '<p><a href="{}" target="_blank" rel="noopener">Datei öffnen</a></p>',
        url
    )


@register.filter
def render_image(image_field):
    """
    Rendert Bilder (jpg/jpeg/png/webp) – Browser erkennt Typ selbst.
    """
    name, url = _name_url_ct(image_field)
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
    name, url = _name_url_ct(audio_field)
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
