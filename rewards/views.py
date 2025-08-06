from django.shortcuts import render, get_object_or_404
from .models import Reward


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
