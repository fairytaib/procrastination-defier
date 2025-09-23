from emails.emails import send_subscription_email
from .models import Subscription
from django.db.models import Q
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timezone
from django.contrib.auth import login
from django.shortcuts import redirect, render
from .utils import get_current_subscription
import stripe
from django.conf import settings
from django.utils import timezone as dj_timezone
from django.utils.translation import get_language
from decimal import Decimal


stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_view(request):
    """ A view to return the subscription page """
    subscription = {
        'standard': 'price_1S0mDxALgEprtAEcMgbbm4ua',
        'premium': 'price_1S0mEeALgEprtAEctIhtB5JX',
    }
    user = request.user if request.user.is_authenticated else None
    active_sub = get_current_subscription(user) if user else None
    if request.user.is_authenticated:
        if not active_sub:
            if request.method == 'POST':
                plan = request.POST.get('plan_id')
                price_id = subscription.get(plan, plan)

                email = request.user.email if request.user.is_authenticated else None

                kwargs = {
                    "mode": "subscription",
                    "payment_method_types": ['card'],
                    "line_items": [{"price": price_id, "quantity": 1}],
                    "success_url": settings.DOMAIN + reverse('create_subscription') + '?session_id={CHECKOUT_SESSION_ID}',
                    "cancel_url": settings.DOMAIN + settings.STRIPE_CANCEL_URL,
                    "client_reference_id": str(request.user.pk)
                }
                if request.user.is_authenticated:
                    kwargs["client_reference_id"] = str(request.user.id)

                sub = get_current_subscription(request.user)

                if sub and getattr(sub, "customer_id", None):
                    kwargs["customer"] = sub.customer_id
                elif request.user.email:
                    kwargs["customer_email"] = request.user.email
                else:
                    email = request.POST.get("email")
                    if email:
                        kwargs["customer_email"] = email

                checkout_session = stripe.checkout.Session.create(**kwargs)
                return redirect(checkout_session.url, code=303)
        else:
            # If User already has an active subscription
            session = stripe.billing_portal.Session.create(
                customer=active_sub.customer_id,
                return_url=settings.DOMAIN + reverse('subscriptions_overview')
                )
            return redirect(session.url, code=303)

    return render(request, 'subscription/subscription.html')


def create_subscription(request):
    """Handle successful Stripe Checkout for subscriptions."""
    session_id = request.GET.get('session_id')
    if not session_id:
        return redirect('subscription_view')

    try:
        session = stripe.checkout.Session.retrieve(session_id)
    except stripe.error.StripeError:
        return redirect('subscription_view')

    if session.get('mode') != 'subscription' or not session.get(
                                'subscription'
                                ):
        return redirect('subscription_view')

    user = request.user if request.user.is_authenticated else None
    client_ref = session.get('client_reference_id')
    if client_ref:
        try:
            ref_user = User.objects.get(pk=client_ref)
            if not user or user.pk != ref_user.pk:
                login(request, ref_user, backend=_login_backend_path())
                user = ref_user
        except User.DoesNotExist:
            return redirect('account_login')
    elif not user:
        return redirect('account_login')

    s = stripe.Subscription.retrieve(session['subscription'],
                                     expand=["items.data.price.product"])
    item = s['items']['data'][0]
    price = item['price']
    product = price['product']

    md_price = dict(price.get("metadata") or {})
    md_prod = dict(product.get("metadata") or {})
    quota_raw = (md_price.get("task_quota") or md_price.get("tasks_quota")
                 or md_prod.get("task_quota") or md_prod.get("tasks_quota"))
    try:
        quota = int(str(quota_raw))
    except (TypeError, ValueError):
        quota = 0

    ts_start = s.get('current_period_start') or s.get('created')
    ts_end = s.get('current_period_end')
    ts_cancel = s.get('cancel_at')

    start_dt = datetime.fromtimestamp(
        ts_start, tz=timezone.utc) if ts_start else dj_timezone.now()
    end_dt = datetime.fromtimestamp(
        ts_end, tz=timezone.utc) if ts_end else None
    cancel_dt = datetime.fromtimestamp(
        ts_cancel, tz=timezone.utc) if ts_cancel else None

    Subscription.objects.update_or_create(
        stripe_subscription_id=s['id'],
        defaults={
            'user': user,
            'customer_id': session['customer'],
            'product_name': product['name'],
            'price': (price.get('unit_amount') or 0) / Decimal(100),
            'interval': (
                price.get('recurring') or {}).get('interval', 'month'),
            'tasks_quota': quota,
            'start_date': start_dt,
            'end_date': end_dt,
            'cancel_at': cancel_dt,
        }
    )
    lang = get_language()
    send_subscription_email(
        user=user,
        subscription=get_current_subscription(user),
        language=lang
    )

    return redirect('/tasks/')


def subscriptions_overview(request):
    """ A view to return the subscription overview page """
    if not request.user.is_authenticated:
        return redirect('account_login')

    subscription = Subscription.objects.filter(
        user=request.user,
        ).filter(
        Q(stripe_subscription_id__isnull=False) |
        Q(product_name__isnull=False) |
        Q(price__isnull=False) |
        Q(interval__isnull=False) |
        Q(tasks_quota__isnull=False) |
        Q(start_date__isnull=False) |
        Q(end_date__isnull=False) |
        Q(cancel_at__isnull=False)
    ).first()

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

    old_snapshot = (sub.product_name, sub.price, sub.interval,
                    sub.tasks_quota, sub.end_date, sub.cancel_at)

    sub.product_name = product["name"]
    sub.price = price["unit_amount"] / Decimal(100)
    sub.interval = price["recurring"]["interval"]
    sub.tasks_quota = quota

    # Deal with dates
    if s.get("cancel_at_period_end"):
        # Plan endet am Periodenende
        ts_end = s.get("current_period_end")
        sub.end_date = datetime.fromtimestamp(
            ts_end, tz=timezone.utc
            ) if ts_end else None
        sub.cancel_at = sub.end_date
    else:
        sub.end_date = None
        sub.cancel_at = None

    sub.save()

    new_snapshot = (sub.product_name, sub.price, sub.interval,
                    sub.tasks_quota, sub.end_date, sub.cancel_at)

    if new_snapshot != old_snapshot:
        send_subscription_email(
            user=sub.user,
            subscription=sub,
            language=get_language()
        )


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
