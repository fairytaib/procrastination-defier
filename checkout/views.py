from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
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
            if reward.cost <= user_points.points:
                order = form.save(commit=False)
                order.user = request.user
                order.reward = reward
                order.save()
                item = reward
                order.order_item = item
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
            else:
                messages.warning(
                    request,
                    "You do not have enough points to redeem this reward"
                )
    return render(
        request, "checkout/checkout.html", {
            "form": form, "reward": reward, "user_points": user_points
        }
    )


@login_required
def user_order_overview(request):
    """Render a user's task overview page."""
    order = RewardHistory.objects.all().order_by(
            '-bought_at'
            )
    context = {
        'order': order
    }
    return render(request, 'checkout/all_orders.html', context)
