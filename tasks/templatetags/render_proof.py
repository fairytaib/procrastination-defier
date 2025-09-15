from django import template
from django.utils.safestring import mark_safe
from cloudinary.utils import cloudinary_url


register = template.Library()


def _extract(value):
    """Return (public_id, resource_type, format, direct_url) from a
      CloudinaryField or string."""
    if not value:
        return None, None, None, None
    public_id = getattr(value, "public_id", None)
    rtype = getattr(value, "resource_type", None)
    fmt = getattr(value, "format", None)
    direct = getattr(value, "url", None)

    # Strings: could be a public_id or a full URL
    if isinstance(value, str) and not public_id:
        if value.startswith("http"):
            direct = value
        else:
            public_id = value
    return public_id, rtype, fmt, direct


def _get_public_id_and_rtype(value, fallback_rtype):
    """
    Accepts:
    - CloudinaryResource from CloudinaryField (has .public_id, .resource_type)
    - A plain public_id string
    - A full Cloudinary URL string
    Returns (public_id, resource_type) or (None, None).
    """
    if not value:
        return None, None

    # CloudinaryResource-like
    public_id = getattr(value, "public_id", None)
    rtype = getattr(value, "resource_type", None)

    # Some CloudinaryField proxies expose
    # #.public_id/.resource_type via .metadata/.data — be lenient
    if not public_id:
        data = getattr(value, "data", None)
        if isinstance(data, dict):
            public_id = data.get("public_id", public_id)
            rtype = data.get("resource_type", rtype)

    # If it's a plain string (could be public_id or a full URL)
    if not public_id and isinstance(value, str):
        if "res.cloudinary.com" in value:
            # Last path segment without extension
            # is a reasonable approximation of public_id.

            path = value.split("?")[0].rstrip("/")
            last = path.split("/")[-1]
            # strip extension if present
            if "." in last:
                last = ".".join(last.split(".")[:-1])
            # Reconstruct the folder part if present
            segments = path.split("/upload/")[-1].split("/")
            if segments and "." in segments[-1]:
                segments[-1] = ".".join(segments[-1].split(".")[:-1])
            public_id = "/".join(segments[1:]) if len(segments) > 1 else last
            rtype = rtype or fallback_rtype
        else:
            public_id = value
            rtype = rtype or fallback_rtype

    return public_id, (rtype or fallback_rtype)


@register.filter
def render_image(value):
    """
    Render an <img> for a Cloudinary image (or a URL/public_id).
    """
    public_id, rtype = _get_public_id_and_rtype(value, "image")
    if not public_id:
        return ""

    url, _ = cloudinary_url(
        public_id,
        resource_type=rtype,
        secure=True,
        crop="limit",
        width=1200,
        fetch_format="auto",
        quality="auto"
    )
    html = f'<img src="{url}" alt="uploaded image" class="img-fluid rounded border" loading="lazy" />'
    return mark_safe(html)


@register.filter
def render_textfile(value):
    public_id, rtype, fmt, direct = _extract(value)
    rtype = rtype or "raw"

    # If Cloudinary gave us a ready URL,
    # use it (safest, includes extension/version).
    if direct:
        url = direct
    else:
        # Ensure we include the format (e.g., pdf, txt, docx)
        url, _ = cloudinary_url(
            public_id, resource_type=rtype, format=(fmt or "pdf"), secure=True)

    html = f'<a href="{url}" target="_blank" rel="noopener">Open uploaded file</a>'
    return mark_safe(html)


@register.filter
def render_audio(value):
    public_id, rtype, fmt, direct = _extract(value)
    rtype = rtype or "video"  # mp3/wav are delivered as resource_type=video
    if direct:
        url = direct
    else:
        # mp3/wav need their extension in the URL
        url, _ = cloudinary_url(public_id, resource_type=rtype, format=(fmt or "mp3"), secure=True)

    html = (
        f'<audio controls preload="none" style="width:100%;">'
        f'  <source src="{url}">'
        f'  Your browser does not support the audio element.'
        f'</audio>'
    )
    return mark_safe(html)


@register.filter(name='render_video')
def render_video(filefield):
    if not filefield:
        return ''
    html = f'''
    <video controls style="max-width: 100%; height: auto;">
      <source src="{filefield.url}">
      Your browser does not support the video tag.
    </video>'''
    return mark_safe(html)
