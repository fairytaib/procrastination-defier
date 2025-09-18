from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _


def send_reward_purchase_email(*, order, reward, history, language=None):
    lang = language or settings.LANGUAGE_CODE
    ctx = {"order": order, "reward": reward, "history": history}

    with translation.override(lang):
        subject = _("Deine Reward-Bestellung")
        text_body = render_to_string("emails/reward_purchased.txt", ctx)
        html_body = render_to_string("emails/reward_purchased.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[order.email or order.user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
