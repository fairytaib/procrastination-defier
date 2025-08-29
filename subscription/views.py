from django.shortcuts import redirect, render
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_SECRET_KEY


def subscription_view(request):
    """ A view to return the subscription page """
    subscription = {
        'standard': 'prod_SwfZ8i9q9xhOm6',
        'premium': 'prod_SwfZw5ngDxAyiv',
    }
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
        {'subscription': subscription}
    )


def create_subscription(request):
    checkout_session_id = request.GET.get('session_id', None)

    #create the subscription in model