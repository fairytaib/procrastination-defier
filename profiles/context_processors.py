from .models import UserProfile


def user_profile_context(request):
    """Add user profile information to the context."""
    if UserProfile.objects.filter(user=request.user).exists():
        user_profile = UserProfile.objects.get(user=request.user)
        return {"user_profile": user_profile}
    else:
        return {"user_profile": False}
