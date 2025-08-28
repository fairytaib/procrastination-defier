from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from .models import Order
from rewards.models import Reward, RewardHistory
from tasks.models import UserPoints


@login_required
def place_order(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id)
    user_points = get_object_or_404(UserPoints, user=request.user)
    form = OrderForm()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            if reward.stock <= 0:
                messages.warning(
                    request, "This reward is currently out of stock.")
            elif reward.cost > user_points.points:
                messages.warning(
                    request,
                    "You do not have enough points to redeem this reward"
                )
            else:
                order = form.save(commit=False)
                order.user = request.user
                item = reward
                order.order_item = item
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
                    request, "Order placed successfully."
                    "We will send it to you shortly."
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
    orders = RewardHistory.objects.all().order_by(
            '-bought_at'
            )
    context = {
        'orders': orders
    }
    return render(request, 'checkout/all_orders.html', context)


@login_required
def view_order_details(request, order_id):
    """Render a specific order's details."""
    order = get_object_or_404(RewardHistory, id=order_id, user=request.user)
    order_details = get_object_or_404(Order, id=order.id)
    context = {
        'order': order,
        'order_details': order_details
    }
    return render(request, 'checkout/order_details.html', context)
