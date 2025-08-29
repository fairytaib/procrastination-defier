from .models import Subscription
from django.contrib.auth.models import User
from datetime import datetime
from django.shortcuts import redirect, render, get_object_or_404
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_view(request):
    """ A view to return the subscription page """
    subscription = {
        'standard': 'prod_SwfZ8i9q9xhOm6',
        'premium': 'prod_SwfZw5ngDxAyiv',
    }
    active_subscription = get_object_or_404(Subscription, user=request.user)
    if request.method == 'POST':
        plan_id = request.POST.get('plan_id')
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': subscription[plan_id],
                    'quantity': 1,
                }
            ],
            payment_method_types=['card'],
            mode='subscription',
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            customer_email=request.user.email,
            metadata={
                'user_id': request.user.id,
                'email': request.user.email,
            }
        )
        return redirect(checkout_session.url, code=303)

    return render(
        request, 'subscription/subscription.html',
        {
            'subscription': subscription,
            'active_subscription': active_subscription
        }
    )


def create_subscription(request):
    """ A view to create a subscription after checkout """
    checkout_session_id = request.GET.get('session_id', None)

    session = stripe.checkout.Session.retrieve(checkout_session_id)
    user_id = session.metadata.get('user_id')
    user = User.objects.get(id=user_id)
    subscription = stripe.Subscription.retrieve(session.subscription)
    price = subscription['items']['data'][0]['price']
    product_id = price['product']
    product = stripe.Product.retrieve(product_id)

    if checkout_session_id:
        Subscription.objects.create(
            user=user,
            customer_id=session.customer,
            subscription_id=session.subscription,
            product_name=product.name,
            price=price['unit_amount'] / 100,
            interval=price['recurring']['interval'],
            start_date=datetime.fromtimestamp(subscription['current_period_start']),

        )
    return redirect('tasks')


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
