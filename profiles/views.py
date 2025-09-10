from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from .forms import AccountForm, ProfilePictureForm
from tasks.models import UserPoints
from django.utils.translation import gettext_lazy as _


@login_required
def view_user_profile(request):
    """View to display the user's profile."""
    profile = UserProfile.objects.get(user=request.user)
    user_points, _ = UserPoints.objects.get_or_create(user=request.user)
    context = {
        'profile': profile,
        'user_points': user_points,
    }
    return render(request, 'profiles/view_user_profile.html', context)


@login_required
def account_update(request):
    """View to update the user's account information."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_image = ProfilePictureForm(
            request.POST, request.FILES, instance=profile
            )
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid() and profile_image.is_valid():
            form.save()
            profile_image.save()
            return redirect("view_user_profile")
    else:
        form = AccountForm(instance=request.user)
        profile_image = ProfilePictureForm(
            request.POST, request.FILES
            )

    return render(
        request, "profiles/update.html",
        {"form": form, "profile_image": profile_image}
        )
