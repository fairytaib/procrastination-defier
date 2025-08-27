from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import OrderForm
from rewards.models import Reward
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
                item = reward.objects.create(
                    order=order,
                    reward=reward,
                    quantity=1,
                    unit_price=reward.cost,
                )
                order.order_item = item
                order.save(update_fields=["order_item"])

                user_points.points -= reward.cost
                user_points.save(update_fields=["points"])
                messages.success(request, "Order placed successfully.")
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
