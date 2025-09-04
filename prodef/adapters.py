from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import get_next_redirect_url
from django.shortcuts import resolve_url
from django.utils.http import url_has_allowed_host_and_scheme
from django.conf import settings
from subscription.models import Subscription


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter to handle login redirection
    based on user subscription status.
    """
    def get_login_redirect_url(self, request):
        next_url = get_next_redirect_url(request)

        if next_url and url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=not settings.DEBUG
        ):
            return next_url

        user = request.user
        has_sub = Subscription.objects.filter(user=user).exists()
        return resolve_url(
            'user_task_overview' if has_sub else 'subscription_view')
