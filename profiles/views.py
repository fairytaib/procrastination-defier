from django.shortcuts import render, redirect
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from .forms import AccountForm


@login_required
def view_user_profile(request):
    """View to display the user's profile."""
    profile = UserProfile.objects.get(user=request.user)
    context = {
        'profile': profile,
    }
    return render(request, 'profiles/view_user_profile.html', context)


@login_required
def account_update(request):
    if request.method == "POST":
        form = AccountForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect("view_user_profile")
    else:
        form = AccountForm(instance=request.user)
    return render(request, "profiles/update.html", {"form": form})
