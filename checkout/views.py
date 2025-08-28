from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from tasks.forms import TaskForm
from .forms import OrderForm
from rewards.forms import RewardHistoryForm
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
    order_details = get_object_or_404(Order, id=order.id)
    form = RewardHistoryForm(instance=order)
    if request.method == "POST":
        form = RewardHistoryForm(request.POST, instance=order)
        if form.is_valid():
            order.reward_sent = True
            order.save(update_fields=["reward_sent"])
            form.save()
            messages.success(request, "Order marked as done.")
            return redirect("user_order_overview")
        else:
            form = RewardHistoryForm(instance=order)
    context = {
        'order': order,
        'order_details': order_details,
        'form': form
    }
    return render(request, 'checkout/order_details.html', context)
