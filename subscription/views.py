from .models import Subscription
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import datetime, timezone
from django.contrib.auth import login
from django.shortcuts import redirect, render
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

        candidate = subscription.get(plan, plan)

        if str(candidate).startswith('prod_'):
            product = stripe.Product.retrieve(candidate)
            price_id = product['default_price']
        elif str(candidate).startswith('price_'):
            price_id = candidate
        else:
            return redirect('subscription_view')

        checkout_session = stripe.checkout.Session.create(
            mode='subscription',
            payment_method_types=['card'],
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=(
                settings.DOMAIN
                + reverse('create_subscription')
                + '?session_id={CHECKOUT_SESSION_ID}'
            ),
            cancel_url=settings.DOMAIN + settings.STRIPE_CANCEL_URL,
        )
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
    email = (session.get('customer_details') or {}).get('email')
    if not email:
        customer = stripe.Customer.retrieve(session['customer'])
        email = customer.get('email')

    if not email:
        return redirect('subscription_view')

    user, created = User.objects.get_or_create(
        username=email,
        defaults={'email': email}
    )

    needs_set_password = not user.has_usable_password()

    if created:
        user.set_unusable_password()
        user.save()

    login(request, user, backend=_login_backend_path())

    sub = stripe.Subscription.retrieve(session['subscription'])
    item = sub['items']['data'][0]
    price = item['price']
    product = stripe.Product.retrieve(price['product'])

    ts_start = sub.get('current_period_start') or sub.get('created')
    ts_end = sub.get('current_period_end')
    ts_cancel = sub.get('cancel_at')
    
    start_dt = datetime.fromtimestamp(
        ts_start, tz=timezone.utc) if ts_start else timezone.now()
    end_dt = datetime.fromtimestamp(
        ts_end, tz=timezone.utc) if ts_end else None
    cancel_dt = datetime.fromtimestamp(
        ts_cancel, tz=timezone.utc) if ts_cancel else None
    
    quota = 0
    metadata = price.get('metadata') or {}
    if 'task_quota' in metadata:
        try:
            quota = int(metadata['task_quota'])
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
        return redirect('tasks/') 


def subscriptions_overview(request):
    """ A view to return the subscription overview page """
    if not request.user.is_authenticated:
        return redirect('account_login')
    subscription = Subscription.objects.filter(user=request.user).first()
    return render(
        request,
        'subscription/subscription_overview.html',
        {'subscription': subscription}
        )


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
