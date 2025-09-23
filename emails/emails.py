from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import gettext as _


def send_reward_purchase_email(*, order, reward, history, language):
    ctx = {"order": order,
           "reward": reward,
           "history": history,
           "language": language
           }

    with translation.override(language):
        subject = _("Your Order Confirmation")
        text_body = render_to_string("emails/reward_notification.txt", ctx)
        html_body = render_to_string("emails/reward_notification.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[order.email or order.user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()


def send_subscription_email(*, user, subscription, language):
    ctx = {"user": user, "subscription": subscription, "language": language}

    with translation.override(language):
        subject = _("Subscription Confirmation")
        text_body = render_to_string(
            "emails/subscription_notification.txt", ctx
            )
        html_body = render_to_string(
            "emails/subscription_notification.html", ctx
            )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[user.email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
