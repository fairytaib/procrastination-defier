# rewards/templatetags/rewards_extras.py
from django import template
from ..models import Reward

register = template.Library()

FALLBACK_LABELS = {
    'NOLIMIT': 'Everywhere',
    'DE': 'Germany', 'FR': 'France', 'BE': 'Belgium', 'CH': 'Switzerland',
    'DK': 'Denmark', 'FI': 'Finland', 'SE': 'Sweden', 'NO': 'Norway',
    'NL': 'Netherlands', 'IT': 'Italy', 'ES': 'Spain',
}


def _choices_map():
    """Return a dictionary mapping country codes to labels from the model field choices."""
    try:
        field = Reward._meta.get_field('available_countries')
        choices = dict(field.choices or [])
        if choices:
            return choices
    except Exception:
        pass
    return {}


def _normalize_codes(value):
    """Normalize the input value into a list of unique country codes."""
    if isinstance(value, (list, tuple)):
        parts = list(value)
    else:
        s = str(value or '').strip()
        if s.startswith('[') and s.endswith(']'):
            s = s[1:-1]
        s = s.replace("'", "").replace('"', '')
        parts = [p.strip() for p in s.split(',') if p.strip()]
    seen, out = set(), []
    for p in parts:
        if p and p not in seen:
            seen.add(p)
            out.append(p)
    return out


def _code_to_label(code, choices):
    c = str(code).strip().upper()
    return choices.get(c) or FALLBACK_LABELS.get(c) or c


@register.filter(name='country_labels')
def country_labels(value):
    """Convert country codes to their corresponding labels."""
    code_to_label = _choices_map()
    codes = _normalize_codes(value)
    labels = []
    for code in codes:
        label = code_to_label.get(code) or FALLBACK_LABELS.get(code) or code
        labels.append(label)
    return ", ".join(labels)


@register.filter(name='country_labels_preview')
def country_labels_preview(value, n=3):
    """Convert country codes to their corresponding labels,
    limiting to n labels."""
    try:
        n = int(n)
    except Exception:
        n = 3
    choices = _choices_map()
    labels = [_code_to_label(c, choices) for c in _normalize_codes(value)]
    if len(labels) <= n:
        return ", ".join(labels)
    return ", ".join(labels[:n]) + ", ..."
