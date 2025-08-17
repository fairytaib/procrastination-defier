from django.shortcuts import render
from .models import UserProfile
from django.contrib.auth.decorators import login_required


@login_required
def view_user_profile(request):
    """View to display the user's profile."""
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'profile': profile,
    }
    return render(request, 'profiles/view_user_profile.html', context)
