from pyexpat.errors import messages
from django.shortcuts import render, redirect, get_object_or_404
from .forms import OrderForm
from rewards.models import Reward


def place_order(request, reward_id):
    reward = get_object_or_404(Reward, id=reward_id)
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            messages.success(request, "Order placed successfully.")
            return redirect("rewards_list")
    else:
        form = OrderForm()
    return render(
        request, "checkout/checkout.html", {
            "form": form, "reward": reward}
    )
