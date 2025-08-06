from django.shortcuts import render
from .models import Reward

def rewards_list(request):
    """View to display a list of rewards."""
    rewards = Reward.objects.all()
    return render(request, 'rewards/rewards_list.html', {'rewards': rewards})
