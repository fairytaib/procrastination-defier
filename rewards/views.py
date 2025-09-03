from django.shortcuts import render, get_object_or_404
from .models import Reward, RewardHistory
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator


def rewards_list(request):
    """View to display a list of rewards."""
    rewards = Reward.objects.all()
    return render(request, 'rewards/rewards_list.html', {'rewards': rewards})


def view_details(request, reward_id):
    """Display the details of a reward."""
    reward = get_object_or_404(Reward, id=reward_id)

    context = {
        "reward": reward,
        "reward_id": reward_id,
    }

    return render(request, "rewards/view_reward_details.html", context)


@login_required
def order_history(request):
    """"""
    qs = (RewardHistory.objects.filter(
            reward_sent=False).order_by('-bought_at'))

    paginator = Paginator(qs, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        "rewards": page_obj.object_list,
        "page_obj": page_obj,
        "is_paginated": page_obj.has_other_pages()
    }
    return render(request, "rewards/reward_history.html", context)
