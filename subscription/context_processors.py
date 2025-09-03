from subscription.models import Subscription


def subscription_context(request):
    """Check if the user has an active subscription."""
    if Subscription.objects.filter(user=request.user).exists():
        return {"subscription_check": True}
    else:
        return {"subscription_check": False}

    return {"subscription_check": False}
