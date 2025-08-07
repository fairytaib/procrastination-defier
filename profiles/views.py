from django.shortcuts import render
from .models import UserProfile


def view_user_profile(request):
    """View to display the user's profile."""
    user_information = UserProfile.objects.get(user=request.user)
    context = {
        'user': user_information,
    }
    return render(request, 'profiles/view_user_profile.html', context)
