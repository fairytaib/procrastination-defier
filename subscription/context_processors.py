from subscription.models import Subscription


def subscription_context(request):
    has_subscription = False
    subscription = None

    if request.user.is_authenticated:
        subscription = (
            Subscription.objects
            .filter(user=request.user)
            .first()
        )
        has_subscription = subscription is not None

    return {
        "subscription": subscription,
        "has_subscription": has_subscription,
        "subscription_check": has_subscription,
    }
