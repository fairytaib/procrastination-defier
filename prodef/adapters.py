# from allauth.account.adapter import DefaultAccountAdapter
# from allauth.account.utils import get_next_redirect_url
# from django.shortcuts import resolve_url
# from subscription.models import Subscription


# class CustomAccountAdapter(DefaultAccountAdapter):
#     """Custom account adapter for handling login redirects."""
#     def get_login_redirect_url(self, request):
#         next_url = get_next_redirect_url(request)
#         if next_url:
#             return next_url

#         user = request.user
#         has_sub = Subscription.objects.filter(user=user).exists()

#         return resolve_url(
#             'user_task_overview' if has_sub else 'subscription_view')
