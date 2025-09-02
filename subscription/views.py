from prodef.settings import STRIPE_SUCCESS_URL
from .models import Subscription
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timezone
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .utils import get_current_subscription
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_view(request):
    """ A view to return the subscription page """
    subscription = {
        'standard': 'price_1S0mDxALgEprtAEcMgbbm4ua',
        'premium': 'price_1S0mEeALgEprtAEctIhtB5JX',
    }
    if request.method == 'POST':
        plan = request.POST.get('plan_id')
        price_id = subscription.get(plan, plan)

        kwargs = {
            "mode": "subscription",
            "payment_method_types": ["card"],
            "line_items": [{"price": price_id, "quantity": 1}],
            "success_url": settings.DOMAIN + reverse(
                'create_subscription'
                ) + '?session_id={CHECKOUT_SESSION_ID}',
            "cancel_url": settings.DOMAIN + settings.STRIPE_CANCEL_URL,
            }

        if request.user.is_authenticated:
            sub = get_current_subscription(request.user)
            if sub and sub.customer_id:
                kwargs["customer"] = sub.customer_id
            kwargs["client_reference_id"] = str(request.user.id)

        checkout_session = stripe.checkout.Session.create(**kwargs)
        return redirect(checkout_session.url, code=303)

    return render(request, 'subscription/subscription.html')


def create_subscription(request):
    """
    Called via success_url after Stripe Checkout (guest-friendly).
    Creates/gets the user from Stripe email, logs them in,
    stores Subscription, then sends them to set a password.
    """
    checkout_session_id = request.GET.get('session_id')
    if not checkout_session_id:
        return redirect('subscription_view')

    session = stripe.checkout.Session.retrieve(checkout_session_id)
    client_ref = session.get("client_reference_id")

    email = (session.get('customer_details') or {}).get('email')
    if not email and session.get('customer'):
        customer = stripe.Customer.retrieve(session['customer'])
        email = customer.get('email')

    if not email:
        return redirect('subscription_view')

    user = None
    login_allowed = False
    needs_set_password = False

    if client_ref:
        try:
            user = User.objects.get(pk=int(client_ref))
            login_allowed = (
                request.user.is_authenticated and request.user.id == user.id)
        except (User.DoesNotExist, ValueError):
            user = None

    if user is None and request.user.is_authenticated:
        user = request.user
        login_allowed = True

    if user is None:
        if not email:
            return redirect('subscription_view')

        try:
            user = User.objects.get(username=email)
            login_allowed = False  # wichtig!
        except User.DoesNotExist:
            user = User.objects.create(username=email, email=email)
            user.set_unusable_password()
            user.save()
            login_allowed = True
            needs_set_password = True

    if login_allowed and not request.user.is_authenticated:
        login(request, user, backend=_login_backend_path())

    sub = stripe.Subscription.retrieve(session['subscription'],
                                       expand=["items.data.price.product"])
    item = sub['items']['data'][0]
    price = item['price']
    product = price['product']

    md_price = dict(price.get("metadata") or {})
    md_prod = dict(product.get("metadata") or {})
    quota_raw = md_price.get("task_quota") or md_price.get("tasks_quota") \
        or md_prod.get("task_quota") or md_prod.get("tasks_quota")

    ts_start = sub.get('current_period_start') or sub.get('created')
    ts_end = sub.get('current_period_end')
    ts_cancel = sub.get('cancel_at')

    start_dt = datetime.fromtimestamp(
        ts_start, tz=timezone.utc) if ts_start else timezone.now()
    end_dt = datetime.fromtimestamp(
        ts_end, tz=timezone.utc) if ts_end else None
    cancel_dt = datetime.fromtimestamp(
        ts_cancel, tz=timezone.utc) if ts_cancel else None

    try:
        quota = int(str(quota_raw))
    except (TypeError, ValueError):
        quota = 0

    Subscription.objects.create(
        user=user,
        customer_id=session['customer'],
        stripe_subscription_id=session['subscription'],
        product_name=product['name'],
        price=price['unit_amount'] // 100,
        interval=price['recurring']['interval'],
        start_date=start_dt,
        tasks_quota=quota
    )

    if needs_set_password:
        return redirect('account_set_password')
    else:
        return redirect(STRIPE_SUCCESS_URL)


def subscriptions_overview(request):
    """ A view to return the subscription overview page """
    if not request.user.is_authenticated:
        return redirect('account_login')

    subscription = get_current_subscription(request.user)
    if subscription:
        _sync_local_from_stripe(subscription)

    return render(request, 'subscription/subscription_overview.html', {
        'subscription': subscription
    })


def _login_backend_path() -> str:
    """
    Select an auth backend path for login():
    - Prefer allauth if available
    - Otherwise take the first configured backend
    - Fallback: Django ModelBackend
    """
    backends = list(getattr(settings, "AUTHENTICATION_BACKENDS", []))
    preferred = "allauth.account.auth_backends.AuthenticationBackend"
    if preferred in backends:
        return preferred
    if backends:
        return backends[0]
    return "django.contrib.auth.backends.ModelBackend"


def _resolve_price_id(candidate: str):
    """
    candidate can upgrade/downgrade his subscription
    Returns the specific price_... ID or None if unknown.
    """
    subscription_map = {
        'standard': 'price_1S0mDxALgEprtAEcMgbbm4ua',
        'premium': 'price_1S0mEeALgEprtAEctIhtB5JX',
    }

    if not candidate:
        return None

    cand = subscription_map.get(candidate, candidate)
    if str(cand).startswith('price_'):
        return cand
    if str(cand).startswith('prod_'):
        product = stripe.Product.retrieve(cand)
        return product.get('default_price')
    return None


def _sync_local_from_stripe(sub):
    """Sync local subscription data with Stripe."""
    s = stripe.Subscription.retrieve(
        sub.stripe_subscription_id,
        expand=["items.data.price.product"]
    )
    item = s["items"]["data"][0]
    price = item["price"]
    product = price["product"]

    md_price = dict(price.get("metadata") or {})
    md_prod = dict(product.get("metadata") or {})
    quota_raw = (md_price.get("task_quota") or md_price.get("tasks_quota")
                 or md_prod.get("task_quota") or md_prod.get("tasks_quota"))
    try:
        quota = int(str(quota_raw))
    except (TypeError, ValueError):
        quota = sub.tasks_quota

    sub.product_name = product["name"]
    sub.price = price["unit_amount"] // 100
    sub.interval = price["recurring"]["interval"]
    sub.tasks_quota = quota

    # Kündigungsstatus/Periodenende abbilden
    if s.get("cancel_at_period_end"):
        # Plan endet am Periodenende
        ts_end = s.get("current_period_end")
        sub.end_date = datetime.fromtimestamp(ts_end, tz=timezone.utc) if ts_end else None
        sub.cancel_at = sub.end_date
    else:
        sub.end_date = None
        sub.cancel_at = None

    sub.save()


def manage_in_stripe(request):
    """Sync local subscription data with Stripe."""
    if not request.user.is_authenticated:
        return redirect('account_login')

    sub = get_current_subscription(request.user)
    if not sub:
        return redirect('subscription_view')

    session = stripe.billing_portal.Session.create(
        customer=sub.customer_id,
        return_url=settings.DOMAIN + reverse('subscriptions_overview')
    )
    return redirect(session.url, code=303)
