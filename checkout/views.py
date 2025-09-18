from django.contrib import messages
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderForm, RewardHistoryForm
from .models import Order
from rewards.models import Reward, RewardHistory
from tasks.models import UserPoints
from django.utils.translation import gettext as _
from emails.email import send_reward_purchase_email


@login_required
def place_order(request, reward_id):
    """Render the checkout page and handle order placement."""
    reward = get_object_or_404(Reward, id=reward_id)
    user_points = get_object_or_404(UserPoints, user=request.user)
    form = OrderForm()

    if request.method == "GET":
        default_addr = Order.objects.filter(
            user=request.user, is_default=True
        ).order_by('-id').first()

        if default_addr:
            initial = {
                'first_name': default_addr.first_name,
                'last_name': default_addr.last_name,
                'email': default_addr.email,
                'phone_number': default_addr.phone_number,
                'street_address': default_addr.street_address,
                'apartment': default_addr.apartment,
                'city': default_addr.city,
                'postal_code': default_addr.postal_code,
                'country': default_addr.country,
                'is_default': True,
            }
            form = OrderForm(initial=initial)
        else:
            form = OrderForm()

    elif request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            if reward.stock <= 0:
                messages.warning(
                    request, _("This reward is currently out of stock."))
            elif reward.cost > user_points.points:
                messages.warning(
                    request,
                    _("You do not have enough points to redeem this reward")
                )
            else:
                order = form.save(commit=False)
                order.user = request.user
                item = reward
                order.order_item = item
                if form.cleaned_data.get('is_default'):
                    Order.objects.filter(
                        user=request.user, is_default=True
                        ).update(is_default=False)
                order.save()
                reward.stock -= 1
                reward.save(update_fields=["stock"])
                user_points.points -= reward.cost
                user_points.save(update_fields=["points"])
                RewardHistory.objects.create(
                    user=request.user,
                    reward=reward
                )
                messages.success(
                    request, _(
                        "Order placed successfully. We will send it to you shortly."
                        )
                )
                lang = getattr(request, "LANGUAGE_CODE", None)
                send_reward_purchase_email(
                    order=order,
                    reward=reward,
                    history=RewardHistory,
                    language=lang
                )

                return redirect("rewards_list")
    return render(
        request, "checkout/checkout.html", {
            "form": form, "reward": reward, "user_points": user_points
        }
    )


@login_required
def user_order_overview(request):
    """Render all ordered rewards."""
    if request.user.has_perm('tasks.mark_done'):
        orders_undone = RewardHistory.objects.filter(
            reward_sent=False).order_by('-bought_at')
        orders_done = RewardHistory.objects.filter(
            reward_sent=True).order_by('-bought_at')
    else:
        orders_undone = RewardHistory.objects.filter(
            user=request.user, reward_sent=False).order_by(
            '-bought_at'
            )
        orders_done = RewardHistory.objects.filter(
            user=request.user, reward_sent=True).order_by('-bought_at')
    context = {
        'orders_undone': orders_undone,
        'orders_done': orders_done
    }
    return render(request, 'checkout/all_orders.html', context)


@login_required
def view_order_details(request, order_id):
    """Render a specific order's details."""
    if not request.user.has_perm('tasks.mark_done'):
        order = get_object_or_404(
            RewardHistory, id=order_id, user=request.user)
    else:
        order = get_object_or_404(RewardHistory, id=order_id)
    order_details = (
        Order.objects
        .filter(user=order.user, order_item=order.reward)
        .order_by('-id')
        .first()
    )

    form = RewardHistoryForm(instance=order)
    if request.method == "POST":
        form = RewardHistoryForm(request.POST, instance=order)
        if form.is_valid():
            order.reward_sent = True
            order.save(update_fields=["reward_sent"])
            form.save()
            messages.success(request, _("Order marked as done."))
            return redirect("user_order_overview")
        else:
            form = RewardHistoryForm(instance=order)
    context = {
        'order': order,
        'order_details': order_details,
        'form': form
    }
    return render(request, 'checkout/order_details.html', context)


@login_required
def order_history(request):
    """Display a paginated list of user's order history with full details."""
    # Get all orders with their related reward details
    orders_list = RewardHistory.objects.select_related(
        'reward', 'user'
    ).filter(
        user=request.user
    ).order_by('-bought_at')

    # Get shipping details for each order
    orders_with_details = []
    for order in orders_list:
        shipping_details = Order.objects.filter(
            user=request.user,
            order_item=order.reward
        ).order_by('-id').first()

        orders_with_details.append({
            'history': order,
            'shipping': shipping_details,
            'total_points': order.reward.cost if order.reward else 0,
        })

    # Setup pagination
    paginator = Paginator(orders_with_details, 5)  # Show 5 orders per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'total_orders': orders_list.count(),
    }
    return render(request, 'checkout/order_history.html', context)
